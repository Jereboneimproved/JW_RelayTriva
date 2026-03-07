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

# 4. DIRECT ROW APPEND (The Ultimate Fix)
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        try:
            # 1. Get the RAW gspread client from the connection
            # We use ._instance to get to the underlying 'open' method
            raw_client = conn._instance
            
            # 2. Open your specific spreadsheet and tab
            # Ensure "Trivia_Master" is the exact name of your Google Sheet
            sh = raw_client.open("Trivia_Master") 
            worksheet = sh.worksheet("Submissions")
            
            # 3. Create the row data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            row_to_add = [timestamp, player_name, selected_team, player_answer, ""]
            
            # 4. Direct Append (This avoids all "overwriting" issues)
            worksheet.append_row(row_to_add)
            
            st.success(f"Sent! Good luck, {player_name}.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Submission Error: {e}")
    else:
        st.warning("Please fill out both name and answer!")
