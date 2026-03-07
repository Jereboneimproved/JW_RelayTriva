import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.title("Zion Trivia: Player Portal")

# 1. Setup Connection (uses the same secrets you already fixed!)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Player Input
team = st.selectbox("Select Your Team", ["Team A", "Team B"])
answer = st.text_input("Your Answer")

if st.button("Submit Answer"):
    # Create a small dataframe for the new row
    new_data = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Team": team,
        "Answer": answer
    }])
    
    # Append it to the 'Submissions' worksheet
    conn.create(worksheet="Submissions", data=new_data)
    st.success("Answer Sent! Watch the Host screen.")
