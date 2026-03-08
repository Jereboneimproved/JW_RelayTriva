import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh # NEW: Requires 'pip install streamlit-autorefresh'

st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")

# --- 0. AUTO-REFRESH TRIGGER ---
# This forces the app to rerun every 15 seconds to catch question changes
st_autorefresh(interval=15000, limit=1000, key="zion_heartbeat")

st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. FETCH GAME STATE (Cached)
try:
    # Read the current question index
    state_df = conn.read(worksheet="Game_State", ttl=15)
    current_idx = int(state_df.iloc[0, 0])
    
    # Read the master question list
    # NOTE: Ensure your tab is named "Trivia_Master" or change to "Questions"
    questions_df = conn.read(worksheet="Trivia_Master", ttl=300)
    
    if not questions_df.empty and current_idx < len(questions_df):
        # Column 1 is the Question text based on your layout
        current_q = questions_df.iloc[current_idx, 1] 
        st.subheader(f"📋 Question #{current_idx + 1}")
        st.info(f"{current_q}")
    else:
        st.success("Stand by for the next question or the final results!")
except Exception as e:
    st.info("Waiting for Host to start the round...")

# 2. DYNAMIC TEAM FETCH WITH PERSISTENCE
# We use st.session_state to "remember" the teams so the UI doesn't flicker
if 'teams_list' not in st.session_state:
    st.session_state.teams_list = ["Loading Teams..."]

try:
    # We still fetch from the sheet, but we save it to the session memory
    scores_df = conn.read(worksheet="Scores", ttl=60)
    fetched_teams = scores_df.iloc[:, 0].dropna().tolist()
    if fetched_teams:
        st.session_state.teams_list = fetched_teams
except:
    # If Google is "cooling down", we keep the last successful list 
    # instead of reverting to "Team A"
    pass 

# 3. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", key="p_name")

# Use the persistent list from memory
selected_team = st.selectbox("Select Your Team", st.session_state.teams_list)

player_answer = st.text_area("Type your answer here...", key="p_ans")

# 4. SUBMISSION LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        with st.spinner("Sending to scoreboard..."):
            try:
                # 2-second TTL to avoid overwriting other players
                existing_data = conn.read(worksheet="Submissions", ttl=2) 
                
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Player": player_name,
                    "Team": selected_team,
                    "Answer": player_answer,
                    "IsCorrect": "" # Left blank for your Apps Script Grading
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Submissions", data=updated_df)
                
                st.success(f"Submitted! Good luck, {player_name}.")
                st.balloons()
                
            except Exception as e:
                st.error("Server busy. Please wait a moment and try again.")
    else:
        st.warning("Both name and answer are required!")
