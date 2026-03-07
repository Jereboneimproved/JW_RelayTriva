import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Zion Trivia: Player Portal", page_icon="🎮")
st.title("🔴 Zion Trivia: Player Portal")

# Connect using your existing secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Player Interface
player_name = st.text_input("Enter Your Name", placeholder="e.g., Jeremiah") # New Field!
team_choice = st.radio("Select Your Team", ["Team A", "Team B"], horizontal=True)
player_answer = st.text_input("Type your answer here...", placeholder="Be quick!")

if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer: # Check for name too
        # Prepare the new row with the Name included
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Player": player_name,  # Added to the data
            "Team": team_choice,
            "Answer": player_answer
        }])
        
        # Append to the Google Sheet
        conn.create(worksheet="Submissions", data=new_entry)
        st.success(f"Sent! Great job, {player_name}!")
        st.balloons()
    else:
        st.warning("Please enter both your name and an answer.")
