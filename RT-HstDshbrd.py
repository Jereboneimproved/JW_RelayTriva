import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE (Prevents errors when the app first loads)
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
        # Reset the Sheet index to 0
        state_update = pd.DataFrame([[0]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        # Clear submissions
        empty_df = pd.DataFrame(columns=["Timestamp", "Player", "Team", "Answer"])
        conn.create(worksheet="Submissions", data=empty_df)
        st.session_state.q_index = 0
        st.success("Game Reset!")
        st.rerun()

# 5. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")

@st.fragment(run_every=5)
def live_dashboard():
    # --- LIVE LEADERBOARD ---
    st.subheader("📊 Live Team Standings")
    team_data = pd.DataFrame({
        'Team': [f"Team {chr(65+i)}" for i in range(num_teams)],
        'Score': [random.randint(500, 5000) for _ in range(num_teams)]
    })
    fig = px.bar(team_data, x='Team', y='Score', color='Score', 
                 color_continuous_scale='Viridis', text_auto='.2s')
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, key="leaderboard_chart")

    # --- LIVE PLAYER FEED ---
    st.divider()
    st.subheader("📥 Live Player Feed")
    submissions = get_latest_submissions()
    if not submissions.empty:
        st.table(submissions.tail(5))
    else:
        st.info("Waiting for players...")

live_dashboard()

# 6. QUESTION MANAGEMENT
st.divider()
col1, col2 = st.columns([2, 1])
conn = st.connection("gsheets", type=GSheetsConnection)

with col1:
    st.subheader("🎯 Active Question")
    try:
        questions = load_master_questions()
        # Use the session state to show the current question
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
        # Update local index
        st.session_state.q_index += 1
        # Update Google Sheet for players
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()

    if st.button("⏹️ End Game", use_container_width=True):
        st.warning("Game Over screen triggered.")
