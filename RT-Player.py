import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh


st.set_page_config(page_title="Zion Trivia: Player Portal", layout="centered")

# --- 0. AUTO-REFRESH TRIGGER ---
# Reruns every 20 seconds to check for question changes and update the submission log
count = st_autorefresh(interval=20000, limit=1000, key="zion_heartbeat")

#GUIDE TO THE AUTO-REFRESH LIMIT:
#In the st_autorefresh function, the limit parameter acts as a safety fuse for your application.
#Specifically, limit=1000 means the page is allowed to automatically refresh itself 1,000 times before it stops.
#
#🛡️ Why is the Limit Necessary?
#- Browser Protection: If you left a tab open on your monitor overnight without a limit, the app would keep 
#  "pinging" Google Sheets forever. This could eventually crash the browser tab or eat up unnecessary data.
#- API Quota Management: Since you are using a 20-second interval (20000ms), a limit of 1000 gives you 
#  about 5.5 hours of continuous live gameplay per session.
#- The Math: 1000 refreshes x 20 seconds = 20,000 seconds (roughly 333 minutes).
#- Cost/Resource Control: For hosted apps on Streamlit Cloud, it prevents "runaway" apps from consuming 
#  server resources indefinitely if a user forgets to close the window.
#
#🚦 What happens when the limit is reached?
#Once the counter hits 1,000, the "heartbeat" simply stops. The player's screen will stay on the current 
#question and will not check for updates again until the player manually refreshes their browser page.
#
#💡 Recommendation for Zion Trivia:
#For a standard trivia night, 1,000 is a very safe "buffer." Even if your event lasts 3 hours, you’ll only 
#use about 540 of those refreshes.

# --- 1. SYNC INDICATOR ---
# Shows a pulsing heart and refresh count so players know the sync is active
st.markdown(
    f"""
    <div style="text-align: right; color: #ff4b4b; font-size: 0.8rem; font-weight: bold;">
        <span style="animation: blinker 1.5s linear infinite;">❤️</span> 
        SYNC ACTIVE (Update #{count})
    </div>
    <style>
        @keyframes blinker {{ 50% {{ opacity: 0; }} }}
    </style>
    """, 
    unsafe_allow_html=True
)

# --- 2. INITIALIZE SESSION STATE ---
if 'teams_list' not in st.session_state:
    st.session_state.teams_list = ["Loading..."]

st.title("🔴 Zion Trivia: Player Portal")

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FETCH GAME STATE
try:
    state_df = conn.read(worksheet="Game_State", ttl=15)
    current_idx = int(state_df.iloc[0, 0])
    questions_df = conn.read(worksheet="Trivia_Master", ttl=300)
    
    if not questions_df.empty and current_idx < len(questions_df):
        current_q = questions_df.iloc[current_idx, 1] 
        st.subheader(f"📋 Question #{current_idx + 1}")
        st.info(f"{current_q}")
    else:
        st.success("Stand by for the next question or final results!")
except Exception:
    st.info("Syncing with Host...")

# 4. PERSISTENT TEAM FETCH
try:
    scores_df = conn.read(worksheet="Scores", ttl=60)
    fetched_teams = scores_df.iloc[:, 0].dropna().tolist()
    if fetched_teams:
        st.session_state.teams_list = fetched_teams
except:
    pass

# 5. PLAYER INPUTS
player_name = st.text_input("Enter Your Name", key="p_name")
selected_team = st.selectbox("Select Your Team", st.session_state.teams_list)
player_answer = st.text_area("Type your answer here...", key="p_ans_input")

# 6. SUBMISSION LOGIC
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        with st.spinner("Sending to scoreboard..."):
            try:
                # Append to Submissions
                existing_data = conn.read(worksheet="Submissions", ttl=2) 
                
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Player": player_name,
                    "Team": selected_team,
                    "Answer": player_answer,
                    "IsCorrect": "" # Left blank for your Apps Script
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Submissions", data=updated_df)
                
                st.success(f"Submitted! Good luck, {player_name}.")
                st.balloons()
                
                # Use session state to clear the box
                st.session_state.p_ans_input = "" 
                st.rerun() 
                
            except Exception:
                st.error("Google is busy. Please wait 5 seconds and click Submit again.")

# --- 7. RECENT SUBMISSIONS FEED ---
st.divider()
st.caption("🏁 Recent Activity (Last 5 Submissions)")
try:
    log_df = conn.read(worksheet="Submissions", ttl=10)
    if not log_df.empty:
        recent_log = log_df.tail(5).iloc[::-1]
        st.table(recent_log[["Timestamp", "Player", "Team"]])
    else:
        st.write("No submissions yet for this round.")
except:
    st.caption("Refreshing log...")
