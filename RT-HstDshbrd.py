import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. SIDEBAR CONFIG
with st.sidebar:
    st.header("Event Configuration")
    # Note: These sliders are visual; the actual team names are now driven by your Sheets 'Zion Admin' menu
    num_teams = st.slider("Number of Teams (Display)", 1, 15, 2)
    max_players = st.slider("Max Players per Team", 1, 50, 10) 
    
    st.divider()
    
    if st.button("🚀 START LIVE SESSION", use_container_width=True, key="start_session_btn"):
        st.balloons()
        st.success("Session Started!")

    st.divider()
    
    if st.button("🗑️ Reset Game & Submissions", use_container_width=True, key="reset_game_sidebar"):
        # Reset Game State index to 0
        state_update = pd.DataFrame([[0]], columns=["CurrentIndex"])
        conn.update(worksheet="Game_State", data=state_update)
        
        # Reset Scores to 0
        scores_df = conn.read(worksheet="Scores", ttl=0)
        scores_df.iloc[:, 1] = 0 
        conn.update(worksheet="Scores", data=scores_df)
        
        # Clear Submissions (Keep Headers)
        empty_df = pd.DataFrame(columns=["Timestamp", "Player", "Team", "Answer", "IsCorrect"])
        conn.update(worksheet="Submissions", data=empty_df)
        
        st.session_state.q_index = 0
        st.toast("Game reset successfully!")
        st.rerun()

# 4. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")

# Refresh every 20 seconds to manage Google Quota
@st.fragment(run_every=20)
def live_dashboard():
    try:
        # Pull data with a 10s TTL to prevent "double-dipping" quota on every click
        scores_df = conn.read(worksheet="Scores", ttl=10)
        subs_df = conn.read(worksheet="Submissions", ttl=10)
        master_df = conn.read(worksheet="Trivia_Master", ttl=60) # Questions rarely change

        # --- LIVE LEADERBOARD ---
        st.subheader("📊 Live Team Standings")
        if not scores_df.empty:
            fig = px.bar(scores_df, x=scores_df.columns[0], y=scores_df.columns[1], 
                         color=scores_df.columns[1], color_continuous_scale='Viridis')
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, key="host_leaderboard_chart")

        # --- LIVE PLAYER FEED ---
        st.divider()
        st.subheader("📥 Live Player Feed")
        if not subs_df.empty:
            # Displays the last 10 entries
            st.table(subs_df.tail(10)) 
        else:
            st.info("Waiting for players to buzz in...")

        # --- SCORING STATION ---
        st.divider()
        st.subheader("🏆 Scoring Station")
        if not scores_df.empty:
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                target_team = st.selectbox("Select Team", scores_df.iloc[:, 0].unique(), key="score_team_select")
            with col_s2:
                points_to_add = st.number_input("Points", value=100, step=50, key="score_points_input")
            with col_s3:
                st.write(" ") 
                if st.button("➕ Award Points", use_container_width=True, key="award_points_btn"):
                    # Math handled here for manual overrides; Apps Script handles the "Yes/No" scoring
                    scores_df.loc[scores_df.iloc[:, 0] == target_team, scores_df.columns[1]] += points_to_add
                    conn.update(worksheet="Scores", data=scores_df)
                    st.toast(f"Awarded {points_to_add} to {target_team}!")
                    st.rerun()

        # --- QUESTION MANAGEMENT ---
        st.divider()
        col_q1, col_q2 = st.columns([2, 1])
        with col_q1:
            st.subheader("🎯 Active Question")
            if not master_df.empty:
                idx = st.session_state.q_index
                if idx < len(master_df):
                    q_text = master_df.iloc[idx, 1] 
                    a_text = master_df.iloc[idx, 2]
                    st.info(f"**Question {idx + 1}:** {q_text}")
                    st.success(f"**Correct Answer:** {a_text}")
                else:
                    st.success("🎉 All questions completed!")
        with col_q2:
            st.subheader("🕹️ Controls")
            if st.button("⏭️ Next Question", use_container_width=True, key="next_q_button_main"):
                st.session_state.q_index += 1
                state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
                conn.update(worksheet="Game_State", data=state_update)
                st.rerun()

    except Exception as e:
        if "429" in str(e):
            st.error("Google's Quota exceeded. Waiting 30 seconds to reset...")
        else:
            st.error(f"Sync Error: {e}")

# Call the fragment
live_dashboard()
