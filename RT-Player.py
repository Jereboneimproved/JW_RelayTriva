import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. PAGE SETUP (Must come before other st commands)
st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")
st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. FETCH GAME STATE
try:
    state_df = conn.read(worksheet="Game_State")
    current_idx = int(state_df.iloc[0, 0])
    questions_df = conn.read(worksheet="Trivia_Master")
    
    if current_idx < len(questions_df):
        current_q = questions_df.iloc[current_idx, 1] # Col B
        st.subheader(f"📋 Current Question: {current_q}")
    else:
        st.success("Waiting for the next round...")
except:
    st.info("Syncing with Host...")

# 3. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.radio("Select Your Team", ["Team A", "Team B"], horizontal=True)
player_answer = st.text_input("Type your answer here...", key="p_ans")

# 4. THE ULTIMATE APPEND FIX (Using run_script)
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        try:
            # 1. Define the append operation
            def append_player_row(client):
                # Ensure "Trivia_Master" matches your Google Sheet name exactly
                sh = client.open("Trivia_Master")
                ws = sh.worksheet("Submissions")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                ws.append_row([timestamp, player_name, selected_team, player_answer, ""])

            # 2. Tell the connection to run this specific script
            conn.run_script(append_player_row)
            
            st.success(f"Sent! Good luck, {player_name}.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Submission Error: {e}")
    else:
        st.warning("Please enter your name and an answer!")
