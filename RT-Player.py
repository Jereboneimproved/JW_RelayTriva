import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ... (keep your existing title and input fields) ...

if st.button("SUBMIT ANSWER"):
    if player_name and player_answer:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 1. Prepare the new row
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Player": player_name,
            "Team": selected_team,
            "Answer": player_answer,
            "IsCorrect": "" # Host can mark this later
        }])

        try:
            # 2. READ the existing submissions first
            existing_subs = conn.read(worksheet="Submissions")
            
            # 3. Combine old data with the new entry
            updated_df = pd.concat([existing_subs, new_entry], ignore_index=True)
            
            # 4. UPDATE the sheet (instead of .create)
            conn.update(worksheet="Submissions", data=updated_df)
            
            st.success(f"Nice job, {player_name}! Answer submitted.")
            st.balloons()
        except Exception as e:
            # Fallback: if the sheet is totally empty/missing, then use create
            conn.create(worksheet="Submissions", data=new_entry)
            st.success("First submission recorded!")
    else:
        st.warning("Please enter your name and an answer!")
