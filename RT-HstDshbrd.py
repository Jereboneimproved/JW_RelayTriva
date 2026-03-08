import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. SIDEBAR CONFIG
with st.sidebar:
    st.header("🛡️ Event Admin")
    st.info("Use the 'Zion Admin' menu in Google Sheets to Setup Teams or Reset the Session.")
    
    st.divider()
    
    if st.button("🚀 START LIVE SESSION", use_container_width=True, key="start_session_btn"):
        st.balloons()
        st.success("Session Active!")

    st.divider()
    # This button now simply syncs the local app with the Sheet's reset state
    if st.button("🔄 Sync with Sheet Reset", use_container_width=True, key="sync_reset"):
        try:
            state_df = conn.read(worksheet="Game_State", ttl=0)
            st.session_state.q_index = int(state_df.iloc[0, 0])
            st.toast("Synced with Spreadsheet!")
            st.rerun()
        except:
            st.error("Could not sync. Check sheet connection.")

# 4. MAIN UI
st.title("🛡️ Zion Game: Host Command Center")

# Refresh every 60 seconds to stay safely under Google's 60-req/min quota
@st.fragment(run_every=60)
def live_dashboard():
    try:
        # Pull data with a 10s TTL buffer
        scores_df = conn.read(worksheet="Scores", ttl=10)
        subs_df = conn.read(worksheet="Submissions", ttl=10)
        master_df = conn.read(worksheet="Trivia_Master", ttl=300)

        # --- LIVE LEADERBOARD ---
        st.subheader("📊 Live Team Standings")
        if not scores_df.empty:
            fig = px.bar(scores_df, x=scores_df.columns[0], y=scores_df.columns[1], 
                         color=scores_df.columns[1], color_continuous_scale='Viridis')
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, key="host_leaderboard_chart")

        # --- LIVE PLAYER FEED ---
        st.divider()
        st.subheader("📥 Recent Submissions")
        if not subs_df.empty:
            # We use st.dataframe here for a cleaner, scrollable view
            st.dataframe(subs_df.tail(15), use_container_width=True)
        else:
            st.info("Waiting for answers...")

        # --- QUESTION MANAGEMENT ---
        st.divider()
        col_q1, col_q2 = st.columns([2, 1])
        with col_q1:
            st.subheader("🎯 Active Question")
            if not master_df.empty:
                idx = st.session_state.q_index
                if idx < len(master_df):
                    q_text = master_df.iloc[idx, 1] 
                    a_text = master_df.iloc[idx, 2]
                    st.info(f"**Question {idx + 1}:** {q_text}")
                    st.success(f"**Answer:** {a_text}")
                else:
                    st.success("🎉 Final Scoreboard Ready!")
        with col_q2:
            st.subheader("🕹️ Controls")
            if st.button("⏭️ Next Question", use_container_width=True, key="next_q_main"):
                st.session_state.q_index += 1
                state_update = pd.DataFrame([[st.session_state.q_index]], columns=["CurrentIndex"])
                conn.update(worksheet="Game_State", data=state_update)
                st.rerun()

    except Exception as e:
        if "429" in str(e):
            st.error("Google is cooling down. Refreshing in 30s...")
        else:
            st.error(f"Sync Error: {e}")

live_dashboard()
