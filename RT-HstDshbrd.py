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
def load_master_questions(conn):
    try:
        df = conn.read(worksheet="Trivia_Master")
        if df.empty:
            return []
        # Standardize column names to lowercase to avoid KeyErrors
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df.to_dict('records')
    except Exception:
        return None

# 4. SIDEBAR CONFIG
with st.sidebar:
    st.header("Event Configuration")
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    
    st.divider()
    if st.button("🗑️ Reset Game & Submissions"):
        conn = st.connection("gsheets", type=GSheetsConnection)
        state_update = pd.DataFrame([[0]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        empty_df = pd.DataFrame(columns=["timestamp", "player", "team", "answer"])
        conn.create(worksheet="Submissions", data=empty_df)
        st.session_state.q_index = 0
        st.rerun()

# 5. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.fragment(run_every=5)
def live_dashboard():
    # --- LIVE LEADERBOARD ---
    st.subheader("📊 Live Team Standings")
    try:
        live_scores = conn.read(worksheet="Scores")
        # Ensure column names are clean
        live_scores.columns = [str(c).strip() for c in live_scores.columns]
        fig = px.bar(live_scores, x='Team', y='TotalPoints', color='TotalPoints', 
                     color_continuous_scale='Viridis', text_auto='.2s')
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, key="leaderboard_chart")
    except:
        st.warning("⚠️ Checking 'Scores' tab...")

    # --- LIVE PLAYER FEED ---
    st.divider()
    st.subheader("📥 Live Player Feed")
    try:
        submissions = conn.read(worksheet="Submissions")
        if not submissions.empty:
            st.table(submissions.tail(5))
        else:
            st.info("Waiting for players...")
    except:
        st.info("Waiting for 'Submissions' tab...")

    # --- SCORING STATION ---
    st.divider()
    st.subheader("🏆 Scoring Station")
    try:
        scores_df = conn.read(worksheet="Scores")
        scores_df.columns = [str(c).strip() for c in scores_df.columns]
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            target_team = st.selectbox("Select Team", scores_df['Team'].unique(), key="score_team_select")
        with col_s2:
            points_to_add = st.number_input("Points", value=100, step=50, key="score_input")
        with col_s3:
            st.write(" ") 
            if st.button("➕ Award Points", use_container_width=True):
                scores_df.loc[scores_df['Team'] == target_team, 'TotalPoints'] += points_to_add
                conn.update(worksheet="Scores", data=scores_df)
                st.toast(f"Awarded {points_to_add} to {target_team}!")
                st.rerun()
    except:
        st.error("Check 'Scores' tab for 'Team' and 'TotalPoints' columns.")

live_dashboard()

# 6. QUESTION MANAGEMENT
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    questions = load_master_questions(conn)
    
    if questions is None:
        st.error("🚨 Error: Could not find 'Trivia_Master' tab.")
    elif len(questions) == 0:
        st.warning("⚠️ 'Trivia_Master' tab is empty.")
    else:
        idx = st.session_state.q_index
        if idx < len(questions):
            curr_q = questions[idx] 
            # We lowercase the keys here to match our standardized columns
            q_text = curr_q.get('question', 'Column "Question" not found')
            a_text = curr_q.get('answer', 'Column "Answer" not found')
            
            st.info(f"**Question {idx + 1}:** {q_text}")
            st.write(f"**Correct Answer:** {a_text}")
        else:
            st.success("🎉 All questions completed!")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.session_state.q_index += 1
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()
