import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.title("🔴 Zion Trivia: Player Portal")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CACHED FETCH (Saves Quota) ---
@st.cache_data(ttl=120) # Only checks team names once every 2 minutes
def get_teams():
    df = conn.read(worksheet="Scores")
    return df.iloc[:, 0].tolist()

# --- LIVE FETCH (Fast for Question Sync) ---
try:
    state_df = conn.read(worksheet="Game_State", ttl=10)
    current_idx = int(state_df.iloc[0, 0])
    # Question data is static, so we cache it for 5 minutes
    questions_df = conn.read(worksheet="Trivia_Master", ttl=300)
    
    if current_idx < len(questions_df):
        current_q = questions_df.iloc[current_idx, 1]
        st.subheader(f"📋 Current Question: {current_q}")
    else:
        st.success("Waiting for the next round...")
except:
    st.info("Syncing with Host...")

# --- PLAYER INPUTS ---
team_options = get_teams()
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.radio("Select Your Team", team_options, horizontal=True)
player_answer = st.text_input("Type your answer here...", key="p_ans")

if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        try:
            # We only pull current subs to append, using a small TTL
            existing_data = conn.read(worksheet="Submissions", ttl=2) 
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Player": player_name,
                "Team": selected_team,
                "Answer": player_answer,
                "IsCorrect": "" # Apps Script will fill this!
            }])
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Submissions", data=updated_df)
            st.success(f"Sent! Good luck, {player_name}.")
            st.balloons()
        except Exception as e:
            st.error("Google is busy. Wait 5 seconds and click Submit again.")
