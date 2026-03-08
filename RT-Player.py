import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")
st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- QUOTA SAVING FETCH LOGIC ---
# We use a 10s TTL for Game State so players see question changes quickly
# but we use a longer 60s TTL for the Questions themselves since they don't change
try:
    state_df = conn.read(worksheet="Game_State", ttl=10)
    current_idx = int(state_df.iloc[0, 0])
    
    # Cache the trivia master for 5 minutes (300s) to save read requests
    questions_df = conn.read(worksheet="Trivia_Master", ttl=300)
    
    if not questions_df.empty and current_idx < len(questions_df):
        current_q = questions_df.iloc[current_idx, 1] # Col B
        st.subheader(f"📋 Current Question: {current_q}")
    else:
        st.success("Waiting for the next round...")
except Exception:
    st.info("Syncing with Host...")

# 2. DYNAMIC TEAM FETCH
# This now pulls whatever names you typed into your Google Sheets Ribbon button
try:
    # 60s TTL is safe here; team names don't change mid-game often
    scores_df = conn.read(worksheet="Scores", ttl=60)
    team_options = scores_df.iloc[:, 0].dropna().tolist()
    if not team_options:
        team_options = ["Team A", "Team B"]
except Exception:
    team_options = ["Team A", "Team B"]

# 3. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.radio("Select Your Team", team_options, horizontal=True)
player_answer = st.text_input("Type your answer here...", key="p_ans")

# 4. THE "PULL-ADD-PUSH" STACKING LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        # Use a status spinner so the player knows it's working
        with st.spinner("Submitting..."):
            try:
                # We use ttl=2 here to ensure we don't overwrite a teammate's 
                # answer that was submitted 3 seconds ago
                existing_data = conn.read(worksheet="Submissions", ttl=2) 
                
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Player": player_name,
                    "Team": selected_team,
                    "Answer": player_answer,
                    "IsCorrect": "" # Your Google Apps Script will handle this column
                }])
                
                if existing_data is not None and not existing_data.empty:
                    # Clean up any empty rows before concatenating
                    existing_data = existing_data.dropna(how='all')
                    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                else:
                    updated_df = new_row
                
                conn.update(worksheet="Submissions", data=updated_df)
                
                st.success(f"Sent! Good luck, {player_name}.")
                st.balloons()
                
            except Exception as e:
                if "429" in str(e):
                    st.error("Server is busy. Please wait 10 seconds and try clicking Submit again.")
                else:
                    st.error(f"Submission Error: {e}")
    else:
        st.warning("Please fill out both name and answer!")
