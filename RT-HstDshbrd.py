import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import time
import random  

def load_master_questions():
    # 1. Establish connection to your Google Sheet
    # This uses the "Service Account" we discussed
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Read the data into a Dataframe
    # 'Trivia_Master' is the name of the worksheet tab
    df = conn.read(worksheet="Trivia_Master")
    
    # 3. Convert to a list of dictionaries for easier game logic
    return df.to_dict('records')

# --- USAGE ---
# questions = load_master_questions()
# first_q = questions[0]['Question']

# --- 1. THE DATA SOURCE (QUESTION PACKS) ---
# In the future, this pulls from Google Sheets.
# For now, we simulate a "Corporate Culture" pack.
def load_questions():
    return [
        {"q": "What year was the company founded?", "a": "1998"},
        {"q": "Who is the current Employee of the Month?", "a": "Sarah"},
        {"q": "What is our primary brand hex color?", "a": "#00FF41"}
    ]

# --- 2. HOST CONTROLS & SELECTION ---
st.title("🛡️ Zion Game: Host Command Center")

with st.sidebar:
    st.header("Event Configuration")
    num_teams = st.slider("Number of Teams", 1, 15, 2)
    players_per_team = st.slider("Max Players per Team", 1, 10, 10)
    
    st.divider()
    if st.button("🚀 START LIVE SESSION"):
        st.session_state.game_active = True
        st.toast("Game is now Live!")

# --- 3. LIVE LEADERBOARD (BAR CHART) ---
# We simulate live scores for 15 teams to show scalability
st.subheader("📊 Live Team Standings")

# Simulated score data
team_data = pd.DataFrame({
    'Team': [f"Team {chr(65+i)}" for i in range(num_teams)],
    'Score': [random.randint(500, 5000) for _ in range(num_teams)]
})

# Professional Bar Chart using Plotly
fig = px.bar(team_data, x='Team', y='Score', 
             color='Score', color_continuous_scale='Viridis',
             text_auto='.2s')

fig.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- 4. QUESTION MANAGEMENT ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Active Question")
    questions = load_questions()
    # Logic to track which question index we are on
    curr_q = questions[0] 
    st.info(f"**Question:** {curr_q['q']}")
    st.write(f"**Correct Answer:** {curr_q['a']}")

with col2:
    st.subheader("🕹️ Controls")
    if st.button("⏭️ Next Question", use_container_width=True):
        st.success("Broadcasted to all phones!")
    if st.button("⏹️ End Game & Email Report", use_container_width=True):
        st.warning("Generating Final Analytics...")

# --- 5. HOST ANALYTICS (REAL-TIME LOG) ---
with st.expander("📝 Real-Time Activity Log"):
    st.write("3:45 PM: Team Alpha - Sarah (Player 3) answered correctly (+500)")
    st.write("3:46 PM: Team Omega - Mike (Player 1) timed out.")
