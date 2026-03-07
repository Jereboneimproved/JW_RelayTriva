import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

# 3. FUNCTIONS
def load_master_questions():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Trivia_Master")
    return df.to_dict('records')

def get_latest_submissions():
    try:
        sub_conn = st.connection("gsheets", type=GSheetsConnection)
        sub_df = sub_conn.read(worksheet="Submissions")
        return sub_df
    except:
        return pd.DataFrame()

# 4. SIDEBAR CONFIG
with st.sidebar:
    st.header("Event Configuration")
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    
    st.divider()
    if st.button("🗑️ Reset Game & Submissions"):
        conn = st.connection("gsheets", type=GSheetsConnection)
        state_update = pd.DataFrame([[0]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        empty_df = pd.DataFrame(columns=["Timestamp", "Player", "Team", "Answer"])
        conn.create(worksheet="Submissions", data=empty_df)
        st.session_state.q_index = 0
        st.success("Game Reset!")
        st.rerun()

# 5. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")

@st.fragment(run_every=5)
def live_dashboard():
    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- LIVE LEADERBOARD (Reading from 'Scores' tab) ---
    st.subheader("📊 Live Team Standings")
    try:
        live_scores = conn.read(worksheet="Scores")
        fig = px.bar(live_scores, x='Team', y='TotalPoints', color='TotalPoints', 
                     color_continuous_scale='Viridis', text_auto='.2s')
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, key="leaderboard_chart")
    except:
        st.warning("Please create a 'Scores' tab in your Google Sheet.")

    # --- LIVE PLAYER FEED ---
    st.divider()
    st.subheader("📥 Live Player Feed")
    submissions = get_latest_submissions()
    if not submissions.empty:
        st.table(submissions.tail(5))
    else:
        st.info("Waiting for players...")

    # --- SCORING STATION (Integrated here) ---
    st.divider()
    st.subheader("🏆 Scoring Station")
    try:
        scores_df = conn.read(worksheet="Scores")
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            target_team = st.selectbox("Select Team to Award", scores_df['Team'].unique(), key="score_team_select")
        with col_s2:
            points_to_add = st.number_input("Points", value=100, step=50, key="score_input")
        with col_s3:
            st.write(" ") # Alignment space
            if st.button("➕ Award Points", use_container_width=True):
                # Add points to the selected team
                scores_df.loc[scores_df['Team'] == target_team, 'TotalPoints'] += points_to_add
                conn.update(worksheet="Scores", data=scores_df)
                st.toast(f"Awarded {points_to_add} to {target_team}!")
                st.rerun()
    except:
        st.error("Error connecting to Scoring tab.")

live_dashboard()

# 6. QUESTION MANAGEMENT
st.divider()
col1, col2 = st.columns([2, 1])
conn = st.connection("gsheets", type=GSheetsConnection)

with col1:
    st.subheader("🎯 Active Question")
    try:
        questions = load_master_questions()
        idx = st.session_state.q_index
        if idx < len(questions):
            curr_q = questions[idx] 
            st.info(f"**Question {idx + 1}:** {curr_q['Question']}")
            st.write(f"**Correct Answer:** {curr_q['Answer']}")
        else:
            st.success("🎉 All questions completed!")
    except:
        st.error("Error loading questions.")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.session_state.q_index += 1
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()

    if st.button("⏹️ End Game", use_container_width=True):
        st.warning("Game Over screen triggered.")
