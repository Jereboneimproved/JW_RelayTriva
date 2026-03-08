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

# 3. PLAYER INPUTS & DYNAMIC TEAM FETCH
try:
    # Pull the list of teams from the 'Scores' worksheet
    scores_df = conn.read(worksheet="Scores", ttl=10)
    # Get the names from the first column (Column A)
    team_options = scores_df.iloc[:, 0].tolist()
except:
    # Fallback if the sheet can't be reached
    team_options = ["Team A", "Team B"]

player_name = st.text_input("Enter Your Name", key="p_name")

# Now the radio button uses the list we just pulled from the sheet!
selected_team = st.radio("Select Your Team", team_options, horizontal=True)

player_answer = st.text_input("Type your answer here...", key="p_ans")

# 4. THE "PULL-ADD-PUSH" STACKING LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        try:
            # 1. Pull the absolute latest data from the sheet
            # This ensures we see Team A's row before we add Team B's
            existing_data = conn.read(worksheet="Submissions", ttl=0) 
            
            # 2. Create your new row
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Player": player_name,
                "Team": selected_team,
                "Answer": player_answer,
                "IsCorrect": "" 
            }])
            
            # 3. Stack them (New row goes at the bottom)
            if existing_data is not None and not existing_data.empty:
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            else:
                updated_df = new_row
            
            # 4. Push the whole updated list back
            conn.update(worksheet="Submissions", data=updated_df)
            
            st.success(f"Sent! Good luck, {player_name}.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Submission Error: {e}")
    else:
        st.warning("Please fill out both name and answer!")
