import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

# 3. SIDEBAR CONFIG
with st.sidebar:
    st.header("Event Configuration")
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    max_players = st.slider("Max Players per Team", 1, 50, 10) 
    
    st.divider()
    
    if st.button("🚀 START LIVE SESSION", use_container_width=True):
        st.balloons()
        st.success("Session Started!")

    st.divider()
    
    if st.button("🗑️ Reset Game & Submissions", use_container_width=True):
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Reset Game State
        state_update = pd.DataFrame([[0]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        # Reset Scores to 0
        scores_df = conn.read(worksheet="Scores", ttl=0)
        scores_df.iloc[:, 1] = 0 
        conn.update(worksheet="Scores", data=scores_df)
        # Clear Submissions (Keep Headers)
        empty_df = pd.DataFrame(columns=["Timestamp", "Player", "Team", "Answer", "IsCorrect"])
        conn.update(worksheet="Submissions", data=empty_df) # Changed create to update
        
        st.session_state.q_index = 0
        st.rerun()

# 4. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.fragment(run_every=15) # Increased to 15 seconds to save quota
def live_dashboard():
    try:
        # 1. Pull EVERYTHING in one go at the start
        # This counts as only 2-3 requests total instead of 10+
        scores_df = conn.read(worksheet="Scores", ttl=0)
        subs_df = conn.read(worksheet="Submissions", ttl=0)
        
        # --- LIVE LEADERBOARD ---
        st.subheader("📊 Live Team Standings")
        if not scores_df.empty:
            fig = px.bar(scores_df, x=scores_df.columns[0], y=scores_df.columns[1], 
                         color=scores_df.columns[1], color_continuous_scale='Viridis')
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, key="leaderboard_chart")

        # --- LIVE PLAYER FEED ---
        st.divider()
        st.subheader("📥 Live Player Feed")
        if not subs_df.empty:
            st.table(subs_df.tail(10)) 
        else:
            st.info("Waiting for players to buzz in...")

        # --- SCORING STATION ---
        # (Uses the scores_df we already downloaded above)
        st.divider()
        st.subheader("🏆 Scoring Station")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            target_team = st.selectbox("Select Team", scores_df.iloc[:, 0].unique(), key="score_team_select")
        # ... rest of your scoring station code ...

    except Exception as e:
        if "429" in str(e):
            st.error("Google is tired! Waiting 30 seconds to reset quota...")
        else:
            st.error(f"Dashboard Error: {e}")

live_dashboard()

# --- 5. QUESTION MANAGEMENT ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    try:
        # Added ttl=0 for master sync
        master_df = conn.read(worksheet="Trivia_Master", ttl=0)
        if not master_df.empty:
            idx = st.session_state.q_index
            if idx < len(master_df):
                q_text = master_df.iloc[idx, 1] 
                a_text = master_df.iloc[idx, 2]
                st.info(f"**Question {idx + 1}:** {q_text}")
                st.success(f"**Correct Answer:** {a_text}")
            else:
                st.success("🎉 All questions completed!")
    except Exception as e:
        st.error(f"Sheet Error: {e}")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.session_state.q_index += 1
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()
