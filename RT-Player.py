import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")

# --- 0. AUTO-REFRESH TRIGGER ---
# Reruns every 20 seconds to check for question changes and update the submission log
st_autorefresh(interval=20000, limit=1000, key="zion_heartbeat")

# --- 1. INITIALIZE SESSION STATE ---
if 'teams_list' not in st.session_state:
    st.session_state.teams_list = ["Loading..."]

st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. FETCH GAME STATE
try:
    state_df = conn.read(worksheet="Game_State", ttl=15)
    current_idx = int(state_df.iloc[0, 0])
    questions_df = conn.read(worksheet="Trivia_Master", ttl=300)
    
    if not questions_df.empty and current_idx < len(questions_df):
        current_q = questions_df.iloc[current_idx, 1] 
        st.subheader(f"📋 Question #{current_idx + 1}")
        st.info(f"{current_q}")
    else:
        st.success("Stand by for the next question or final results!")
except Exception:
    st.info("Syncing with Host...")

# 3. PERSISTENT TEAM FETCH
try:
    scores_df = conn.read(worksheet="Scores", ttl=60)
    fetched_teams = scores_df.iloc[:, 0].dropna().tolist()
    if fetched_teams:
        st.session_state.teams_list = fetched_teams
except:
    pass

# 4. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.selectbox("Select Your Team", st.session_state.teams_list)
# Using a unique key allows us to clear this box later
player_answer = st.text_area("Type your answer here...", key="p_ans_input")

# 5. SUBMISSION LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        with st.spinner("Sending to scoreboard..."):
            try:
                # Append to Submissions
                existing_data = conn.read(worksheet="Submissions", ttl=2) 
                
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"), # Shortened for the log
                    "Player": player_name,
                    "Team": selected_team,
                    "Answer": player_answer,
                    "IsCorrect": ""
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Submissions", data=updated_df)
                
                st.success(f"Submitted! Good luck, {player_name}.")
                st.balloons()
                
                # Clear the answer box and refresh the page to show the log update
                st.session_state.p_ans_input = "" 
                st.rerun() 
                
            except Exception:
                st.error("Google is busy. Please wait 5 seconds and click Submit again.")
    else:
        st.warning("Both name and answer are required!")

# --- 6. NEW: RECENT SUBMISSIONS FEED ---
st.divider()
st.caption("🏁 Recent Activity (Last 5 Submissions)")
try:
    # Fetch submissions with a low TTL to keep the log "live"
    log_df = conn.read(worksheet="Submissions", ttl=10)
    if not log_df.empty:
        # Show the most recent 5 submissions, newest at the top
        recent_log = log_df.tail(5).iloc[::-1]
        # Only show Timestamp, Player, and Team to keep it clean
        st.table(recent_log[["Timestamp", "Player", "Team"]])
    else:
        st.write("No submissions yet for this round.")
except:
    st.caption("Refreshing log...")
