import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")
st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. FETCH GAME STATE (Cached)
try:
    state_df = conn.read(worksheet="Game_State", ttl=15)
    current_idx = int(state_df.iloc[0, 0])
    questions_df = conn.read(worksheet="Trivia_Master", ttl=300)
    
    if not questions_df.empty and current_idx < len(questions_df):
        current_q = questions_df.iloc[current_idx, 1]
        st.subheader(f"📋 Current Question: {current_q}")
    else:
        st.success("Stand by for the next question or the final results!")
except:
    st.info("Connecting to Host...")

# 2. DYNAMIC TEAM FETCH
try:
    scores_df = conn.read(worksheet="Scores", ttl=60)
    team_options = scores_df.iloc[:, 0].dropna().tolist()
except:
    team_options = ["Team A", "Team B"]

# 3. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.radio("Select Your Team", team_options, horizontal=True)
player_answer = st.text_input("Type your answer here...", key="p_ans")

# 4. SUBMISSION LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        with st.spinner("Sending to scoreboard..."):
            try:
                # 2-second TTL to ensure we append to the absolute latest list
                existing_data = conn.read(worksheet="Submissions", ttl=2) 
                
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Player": player_name,
                    "Team": selected_team,
                    "Answer": player_answer,
                    "IsCorrect": "" # Left blank for Apps Script logic
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Submissions", data=updated_df)
                
                st.success(f"Submitted! Good luck, {player_name}.")
                st.balloons()
                
            except Exception as e:
                st.error("Server busy. Please wait a moment and try again.")
    else:
        st.warning("Both name and answer are required!")
