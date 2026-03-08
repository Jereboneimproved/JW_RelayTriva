import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.title("🛡️ Zion Game: Host Command Center")
conn = st.connection("gsheets", type=GSheetsConnection)

# Slower refresh (30s) to guarantee quota safety for players
@st.fragment(run_every=30)
def live_dashboard():
    try:
        # BATCH READ: One request for everything
        # We use a 10s TTL so manual edits in Sheets don't cause a loop
        scores_df = conn.read(worksheet="Scores", ttl=10)
        subs_df = conn.read(worksheet="Submissions", ttl=10)
        master_df = conn.read(worksheet="Trivia_Master", ttl=300)

        # --- LEADERBOARD ---
        if not scores_df.empty:
            fig = px.bar(scores_df, x=scores_df.columns[0], y=scores_df.columns[1], template="plotly_dark")
            st.plotly_chart(fig, key="host_chart")

        # --- LIVE FEED ---
        st.subheader("📥 Live Player Feed")
        st.dataframe(subs_df.tail(10), use_container_width=True)

        # --- NEXT QUESTION CONTROL ---
        if st.button("⏭️ Next Question", key="next_q"):
            # Update local state index
            st.session_state.q_index += 1
            state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
            conn.update(worksheet="Game_State", data=state_update)
            st.rerun()
            
    except Exception as e:
        st.error("Connecting to Google...")

if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

live_dashboard()
