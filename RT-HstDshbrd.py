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
        # FORCE CLEAN HEADERS: lowercase and remove hidden spaces
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception:
        return None

# 4. SIDEBAR CONFIG
with st.sidebar:
    st.header("Event Configuration")
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    
    st.divider()
    if st.button("🗑️ Reset Game & Submissions"):
        conn = st.connection("gsheets", type=GSheetsConnection)
        state_update = pd.DataFrame([[0]], columns=["currentindex"])
        conn.update(worksheet="Game_State", data=state_update)
        empty_df = pd.DataFrame(columns=["timestamp", "player", "team", "answer", "iscorrect"])
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
    scores_df = load_data(conn, "Scores")
    if scores_df is not None:
        # Use whatever names were found in the sheet
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
            # Dynamically find the Team column
            team_col = scores_df.columns[0]
            target_team = st.selectbox("Select Team", scores_df[team_col].unique(), key="score_team_select")
        with col_s2:
            points_to_add = st.number_input("Points", value=100, step=50, key="score_input")
        with col_s3:
            st.write(" ") 
            if st.button("➕ Award Points", use_container_width=True):
                pts_col = scores_df.columns[1]
                scores_df.loc[scores_df[team_col] == target_team, pts_col] += points_to_add
                conn.update(worksheet="Scores", data=scores_df)
                st.toast(f"Awarded {points_to_add} to {target_team}!")
                st.rerun()

live_dashboard()

# 6. QUESTION MANAGEMENT
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    master_df = load_data(conn, "Trivia_Master")
    
    if master_df is not None:
        questions = master_df.to_dict('records')
        idx = st.session_state.q_index
        if idx < len(questions):
            curr_q = questions[idx] 
            # Safe retrieval using cleaned keys
            q_text = curr_q.get('question', 'Missing Question Column')
            a_text = curr_q.get('answer', 'Missing Answer Column')
            
            st.info(f"**Question {idx + 1}:** {q_text}")
            st.success(f"**Correct Answer:** {a_text}")
        else:
            st.success("🎉 All questions completed!")
    else:
        st.error("🚨 Error: Could not read 'Trivia_Master' tab.")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.session_state.q_index += 1
        state_update = pd.DataFrame([[st.session_state.q_index]], columns=["currentindex"])
        conn.update(worksheet="Game_State", data=state_update)
        st.rerun()
