import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")
st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. FETCH CURRENT QUESTION
try:
    # Get current index from Game_State tab (Row 1, Col A)
    state_df = conn.read(worksheet="Game_State")
    current_idx = int(state_df.iloc[0, 0])
    
    # Get questions from Trivia_Master
    questions_df = conn.read(worksheet="Trivia_Master")
    
    if current_idx < len(questions_df):
        # Match the Host: Col B (1) is Question
        current_q = questions_df.iloc[current_idx, 1]
        st.subheader(f"📋 Current Question: {current_q}")
    else:
        st.success("Waiting for the next round to start...")
except:
    st.error("Connecting to game server... please wait.")

# 3. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", placeholder="e.g., Jeremiah")
selected_team = st.radio("Select Your Team", ["Team A", "Team B"], horizontal=True)
player_answer = st.text_input("Type your answer here...", placeholder="Be quick!")

# 4. SUBMISSION LOGIC (THE FIX)
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        # Prepare data
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Player": player_name,
            "Team": selected_team,
            "Answer": player_answer,
            "IsCorrect": "" 
        }])
        
        try:
            # APPEND instead of CREATE to avoid APIErrors
            existing_subs = conn.read(worksheet="Submissions")
            updated_df = pd.concat([existing_subs, new_entry], ignore_index=True)
            conn.update(worksheet="Submissions", data=updated_df)
            
            st.success(f"Nice job, {player_name}! Answer sent.")
            st.balloons()
        except:
            # If Submissions tab is totally fresh/blank
            conn.update(worksheet="Submissions", data=new_entry)
            st.success("Submission recorded!")
    else:
        st.warning("Please fill out your name and answer first!")
