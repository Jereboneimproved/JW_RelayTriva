import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

# 1. PAGE CONFIG & LOGO (Must be before other UI elements)
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# Note: If st.logo gives an error, your Streamlit version is likely old. 
# You can comment it out with a # if the app crashes here.
try:
    st.logo("https://raw.githubusercontent.com/streamlit/docs/main/public/images/favicon.png")
except:
    pass

# 2. FUNCTIONS (Define how we get data)
def load_master_questions():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Trivia_Master")
    return df.to_dict('records')

def get_latest_submissions():
    try:
        sub_conn = st.connection("gsheets", type=GSheetsConnection)
        # Reads the tab where players send their names and answers
        sub_df = sub_conn.read(worksheet="Submissions")
        return sub_df
    except:
        return pd.DataFrame()

# 3. SIDEBAR & CONFIGURATION
with st.sidebar:
    st.header("Event Configuration")
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    
    st.divider()
    if st.sidebar.button("🗑️ Clear All Submissions"):
        conn = st.connection("gsheets", type=GSheetsConnection)
        empty_df = pd.DataFrame(columns=["Timestamp", "Player", "Team", "Answer"])
        conn.create(worksheet="Submissions", data=empty_df)
        st.sidebar.success("Board cleared!")
        st.rerun()

# 4. MAIN UI LAYOUT
st.title("🛡️ Zion Game: Host Command Center")

# This fragment refreshes the Leaderboard and Feed every 5 seconds
@st.fragment(run_every=5)
def live_dashboard():
    # --- LIVE LEADERBOARD ---
    st.subheader("📊 Live Team Standings")
    
    # Using your random simulation for now
    team_data = pd.DataFrame({
        'Team': [f"Team {chr(65+i)}" for i in range(num_teams)],
        'Score': [random.randint(500, 5000) for _ in range(num_teams)]
    })

    fig = px.bar(team_data, x='Team', y='Score', 
                 color='Score', color_continuous_scale='Viridis',
                 text_auto='.2s')
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, key="leaderboard_chart")

    # --- LIVE PLAYER FEED ---
    st.divider()
    st.subheader("📥 Live Player Feed (Last 5 Submissions)")
    submissions = get_latest_submissions()

    if not submissions.empty:
        # Displays: Timestamp, Player, Team, Answer
        st.table(submissions.tail(5))
    else:
        st.info("Waiting for players to buzz in...")

# Call the refreshing fragment
live_dashboard()

# 5. QUESTION MANAGEMENT (Static section, no auto-refresh needed)
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    # Pulling the first question from your Master Sheet logic
    try:
        questions = load_master_questions()
        curr_q = questions[0] 
        st.info(f"**Question:** {curr_q['Question']}")
        st.write(f"**Correct Answer:** {curr_q['Answer']}")
    except:
        st.error("Could not load questions from Google Sheets.")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
    # 1. Update your local state
    st.session_state.q_index = st.session_state.get('q_index', 0) + 1
    
    # 2. Update the Google Sheet so players see the change
    state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
    conn.update(worksheet="Game_State", data=state_update)
    
    st.success("Question Updated for all Players!")
    if st.button("⏹️ End Game", use_container_width=True):
        st.warning("Finalizing...")
