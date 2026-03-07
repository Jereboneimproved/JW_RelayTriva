import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Zion Trivia: Player Portal", page_icon="🎮")
st.title("🔴 Zion Trivia: Player Portal")

# 1. Setup Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. QUESTION DISPLAY (Fragmented so it doesn't reset your typing)
@st.fragment(run_every=5)
def show_active_question():
    try:
        # Pull Master Questions and current Game State
        all_q = conn.read(worksheet="Trivia_Master")
        state_df = conn.read(worksheet="Game_State")
        
        # Get index from cell A2
        current_index = int(state_df.iloc[0, 0]) 
        active_text = all_q.iloc[current_index]['Question']
        
        st.info(f"📋 **Current Question:** {active_text}")
    except Exception:
        st.warning("🎮 Waiting for the Host to start the round...")

# Call the display function
show_active_question()

st.divider()

# 3. PLAYER INPUTS (Added unique keys to prevent Duplicate ID error)
player_name = st.text_input("Enter Your Name", placeholder="e.g., Jeremiah", key="p_name")
team_choice = st.radio("Select Your Team", ["Team A", "Team B"], horizontal=True, key="p_team")
player_answer = st.text_input("Type your answer here...", placeholder="Be quick!", key="p_ans")

if st.button("SUBMIT ANSWER", use_container_width=True, key="p_submit"):
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
