import streamlit as st

# --- PLAYER SESSION STATE ---
# This simulates a player joining Team 3 and being assigned 'Player 4'
if 'player_team' not in st.session_state:
    st.session_state.player_team = "Team C" 
    st.session_state.seed_number = 4  # This would be dynamic in the real lobby

# --- THE PLAYER INTERFACE ---
st.title(f"🎮 {st.session_state.player_team} | Player {st.session_state.seed_number}")

# 1. LIVE SYNC WITH HOST
# In a real build, we pull 'current_q' and 'global_turn_count' from the Database
current_q = "What is the company's mission statement?"
global_turn_count = 13 # The Host increments this every time a question is answered

# 2. RELAY MATH
# This calculates who SHOULD be answering right now for this team
# If a team has 10 players, turn 13 belongs to Player 3 (13 % 10 = 3)
active_player_seed = (global_turn_count % 10) + 1 

# 3. DYNAMIC UI LOCKING
st.markdown("---")
st.subheader("Current Mission:")
st.info(current_q)

if st.session_state.seed_number == active_player_seed:
    st.success("🔥 IT IS YOUR TURN! ANSWER BELOW:")
    answer = st.text_input("Type your answer...")
    if st.button("SUBMIT ANSWER", use_container_width=True):
        st.balloons()
        # Logic to send '+Points' to the database
else:
    st.warning(f"⏳ Waiting for Player {active_player_seed} to answer...")
    st.write("Discuss the answer with your team! Only they can hit submit.")
