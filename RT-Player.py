import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Zion Trivia: Player Portal", page_icon="🎮")
st.title("🔴 Zion Trivia: Player Portal")

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Zion Trivia: Player Portal", page_icon="🎮")
st.title("🔴 Zion Trivia: Player Portal")

# Connect using your existing secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NEW: QUESTION DISPLAY SECTION ---
@st.fragment(run_every=5) # Checks for a new question every 5 seconds
def show_active_question():
    try:
        # Pull from the 'Trivia_Master' sheet
        all_q = conn.read(worksheet="Trivia_Master")
        
        # Pull from 'Game_State' to see which question the host has active
        # (Assuming cell A2 in 'Game_State' holds the current row index)
        state_df = conn.read(worksheet="Game_State")
        current_index = int(state_df.iloc[0, 0]) 
        
        active_q_text = all_q.iloc[current_index]['Question']
        st.info(f"📋 **Current Question:** {active_q_text}")
    except:
        st.warning("🎮 Waiting for the Host to display the next question...")

show_active_question()
st.divider()
# --- END QUESTION DISPLAY ---

# Player Interface
player_name = st.text_input("Enter Your Name", placeholder="e.g., Jeremiah")
team_choice = st.radio("Select Your Team", ["Team A", "Team B"], horizontal=True)
player_answer = st.text_input("Type your answer here...", placeholder="Be quick!")

if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Player": player_name,
            "Team": team_choice,
            "Answer": player_answer
        }])
        
        conn.create(worksheet="Submissions", data=new_entry)
        st.success(f"Sent! Great job, {player_name}!")
        st.balloons()
    else:
        st.warning("Please enter both your name and an answer.")

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
