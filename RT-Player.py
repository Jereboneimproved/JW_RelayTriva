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

# 4. DIRECT ROW APPEND (Prevents Overwriting & Schema Errors)
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        try:
            # 1. Access the underlying gspread client directly
            client = conn.client
            
            # 2. Open the specific worksheet
            # Make sure your spreadsheet name matches exactly (e.g., "Trivia_Master")
            sh = client.open("Trivia_Master") 
            worksheet = sh.worksheet("Submissions")
            
            # 3. Create a simple list of your data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            row_to_add = [timestamp, player_name, selected_team, player_answer, ""]
            
            # 4. Append the row directly to the bottom
            worksheet.append_row(row_to_add)
            
            st.success(f"Sent! Good luck, {player_name}.")
            st.balloons()
            
        except Exception as e:
            # This will show you exactly why it's failing if it happens again
            st.error(f"Submission Error: {e}")
    else:
        st.warning("Please fill out both name and answer!")
