import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")

# --- 0. AUTO-REFRESH TRIGGER ---
# Reruns every 15 seconds to check for question changes
st_autorefresh(interval=15000, limit=1000, key="zion_heartbeat")

# --- 1. INITIALIZE SESSION STATE ---
# This prevents the UI from flickering when the connection is busy
if 'teams_list' not in st.session_state:
    st.session_state.teams_list = ["Loading..."]
if 'last_submit_status' not in st.session_state:
    st.session_state.last_submit_status = False

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
    # If Google is busy, we use the list already in memory (no flicker!)
    pass

# 4. PLAYER INPUTS
# We use 'p_ans_key' to allow us to clear the text area after submission
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.selectbox("Select Your Team", st.session_state.teams_list)
player_answer = st.text_area("Type your answer here...", key="p_ans_input")

# 5. SUBMISSION LOGIC (With Reset)
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        with st.spinner("Sending to scoreboard..."):
            try:
                # Append to Submissions
                existing_data = conn.read(worksheet="Submissions", ttl=2) 
                
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Player": player_name,
                    "Team": selected_team,
                    "Answer": player_answer,
                    "IsCorrect": ""
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Submissions", data=updated_df)
                
                # Success Actions
                st.success(f"Submitted! Good luck, {player_name}.")
                st.balloons()
                
                # CLEAR THE BOX: This resets the text area so they don't double-submit
                st.session_state.p_ans_input = "" 
                st.rerun() 
                
            except Exception:
                st.error("Google is busy. Please wait 5 seconds and click Submit again.")
    else:
        st.warning("Both name and answer are required!")
