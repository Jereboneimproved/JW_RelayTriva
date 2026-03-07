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

# 4. STACKING SUBMISSION LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        # Create the new row as a DataFrame
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Player": player_name,
            "Team": selected_team,
            "Answer": player_answer,
            "IsCorrect": "" 
        }])
        
        try:
            # PULL: Get everything currently in the Submissions tab
            existing_subs = conn.read(worksheet="Submissions")
            
            # MERGE: Add the new answer to the existing list
            # This is what stops Team B from deleting Team A
            updated_df = pd.concat([existing_subs, new_entry], ignore_index=True)
            
            # PUSH: Send the full list back to Google Sheets
            conn.update(worksheet="Submissions", data=updated_df)
            
            st.success(f"Sent! Good luck, {player_name}.")
            st.balloons()
        except:
            # Fallback if the sheet is empty
            conn.update(worksheet="Submissions", data=new_entry)
            st.success("First submission recorded!")
    else:
        st.warning("Please fill out both name and answer!")
