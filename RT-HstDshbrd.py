import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

# 3. FUNCTIONS
def load_data(conn, sheet_name):
    try:
        df = conn.read(worksheet=sheet_name)
        return df
    except Exception:
        return None

# 4. SIDEBAR CONFIG (FULL RESTORATION)
with st.sidebar:
    st.header("Event Configuration")
    
    # Restoring the team slider
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    
    st.divider()
    
    # Restoring the Reset functionality
    if st.button("🗑️ Reset Game & Submissions", use_container_width=True):
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Reset current index to 0
        state_update = pd.DataFrame([[0]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        
        # Reset Scores to 0 for all teams
        # Assumes Column A is 'Team' and Column B is 'TotalPoints'
        scores_df = conn.read(worksheet="Scores")
        scores_df.iloc[:, 1] = 0 
        conn.update(worksheet="Scores", data=scores_df)
        
        # Clear submissions
        empty_df = pd.DataFrame(columns=["Timestamp", "Player", "Team", "Answer", "IsCorrect"])
        conn.create(worksheet="Submissions", data=empty_df)
        
        st.session_state.q_index = 0
        st.success("Game, Scores, and Submissions Reset!")
        st.rerun()

# 5. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.fragment(run_every=5)
def live_dashboard():
    # --- LIVE LEADERBOARD ---
    st.subheader("📊 Live Team Standings")
    scores_df = load_data(conn, "Scores")
    if scores_df is not None:
        fig = px.bar(scores_df, x=scores_df.columns[0], y=scores_df.columns[1], 
                     color=scores_df.columns[1], color_continuous_scale='Viridis')
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, key="leaderboard_chart")

    # --- LIVE PLAYER FEED ---
    st.divider()
    st.subheader("📥 Live Player Feed")
    subs_df = load_data(conn, "Submissions")
    if subs_df is not None and not subs_df.empty:
        st.table(subs_df.tail(5))
    else:
        st.info("Waiting for players to buzz in...")

    # --- SCORING STATION ---
    st.divider()
    st.subheader("🏆 Scoring Station")
    if scores_df is not None:
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            target_team = st.selectbox("Select Team", scores_df.iloc[:, 0].unique(), key="score_team_select")
        with col_s2:
            points_to_add = st.number_input("Points", value=100, step=50, key="score_input")
        with col_s3:
            st.write(" ") 
            if st.button("➕ Award Points", use_container_width=True):
                scores_df.loc[scores_df.iloc[:, 0] == target_team, scores_df.columns[1]] += points_to_add
                conn.update(worksheet="Scores", data=scores_df)
                st.toast(f"Awarded {points_to_add} to {target_team}!")
                st.rerun()

live_dashboard()

# --- 6. QUESTION MANAGEMENT ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    master_df = load_data(conn, "Trivia_Master")
    if master_df is not None:
        idx = st.session_state.q_index
        if idx < len(master_df):
            # Positional mapping: Col B (1) = Question, Col C (2) = Answer
            q_text = master_df.iloc[idx, 1] 
            a_text = master_df.iloc[idx, 2]
            st.info(f"**Question {idx + 1}:** {q_text}")
            st.success(f"**Correct Answer:** {a_text}")
        else:
            st.success("🎉 All questions completed!")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.session_state.q_index += 1
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()
