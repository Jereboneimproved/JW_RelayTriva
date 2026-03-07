import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

# 3. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.fragment(run_every=5)
def live_dashboard():
    # --- LIVE LEADERBOARD ---
    st.subheader("📊 Live Team Standings")
    try:
        scores_df = conn.read(worksheet="Scores")
        # Map Team to Col A and Points to Col B
        fig = px.bar(scores_df, x=scores_df.columns[0], y=scores_df.columns[1], 
                     color=scores_df.columns[1], color_continuous_scale='Viridis')
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, key="leaderboard_chart")
    except:
        st.warning("⚠️ Checking 'Scores' tab...")

    # --- LIVE PLAYER FEED ---
    st.divider()
    st.subheader("📥 Live Player Feed")
    try:
        subs_df = conn.read(worksheet="Submissions")
        if not subs_df.empty:
            st.table(subs_df.tail(5))
        else:
            st.info("Waiting for players...")
    except:
        st.info("No submissions yet.")

    # --- SCORING STATION ---
    st.divider()
    st.subheader("🏆 Scoring Station")
    try:
        scores_df = conn.read(worksheet="Scores")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            target_team = st.selectbox("Select Team", scores_df.iloc[:, 0].unique(), key="score_team_select")
        with col_s2:
            points_to_add = st.number_input("Points", value=100, step=50, key="score_input")
        with col_s3:
            st.write(" ") 
            if st.button("➕ Award Points", use_container_width=True):
                # Update Column B (Index 1) for the matched team in Column A (Index 0)
                scores_df.iloc[scores_df.iloc[:, 0] == target_team, 1] += points_to_add
                conn.update(worksheet="Scores", data=scores_df)
                st.toast(f"Awarded {points_to_add} to {target_team}!")
                st.rerun()
    except:
        st.error("Verify your 'Scores' tab has Team and TotalPoints columns.")

live_dashboard()

# --- 6. QUESTION MANAGEMENT (POSITIONS MAPPED TO YOUR SCREENSHOT) ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    try:
        master_df = conn.read(worksheet="Trivia_Master")
        if not master_df.empty:
            idx = st.session_state.q_index
            if idx < len(master_df):
                # POSITIONAL MAPPING:
                # master_df.iloc[row, column_index]
                # Column A = 0 (ID), Column B = 1 (Question), Column C = 2 (Answer)
                q_text = master_df.iloc[idx, 1] 
                a_text = master_df.iloc[idx, 2]
                
                st.info(f"**Question {idx + 1}:** {q_text}")
                st.success(f"**Correct Answer:** {a_text}")
            else:
                st.success("🎉 All questions completed!")
    except Exception as e:
        st.error(f"Error accessing sheet: {e}")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.session_state.q_index += 1
        # Sync with Player app via Game_State tab
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()
