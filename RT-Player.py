# --- UPDATED SUBMISSION LOGIC ---
if st.button("SUBMIT ANSWER", use_container_width=True):
    if player_name and player_answer:
        # 1. Create the NEW row
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Player": player_name,
            "Team": selected_team,
            "Answer": player_answer,
            "IsCorrect": "" 
        }])
        
        try:
            # 2. READ the current sheet (Pull Team A's existing data)
            existing_subs = conn.read(worksheet="Submissions")
            
            # 3. COMBINE (Stack the new answer on top of existing ones)
            # This ensures that if Team A is already there, Team B is just added to Row 3
            if not existing_subs.empty:
                updated_df = pd.concat([existing_subs, new_entry], ignore_index=True)
            else:
                updated_df = new_entry
                
            # 4. SEND the whole list back
            conn.update(worksheet="Submissions", data=updated_df)
            
            st.success(f"Submitted! Good luck, {player_name}.")
            st.balloons()
        except Exception as e:
            # Fallback for the very first submission of the game
            conn.update(worksheet="Submissions", data=new_entry)
            st.success("First submission recorded!")
    else:
        st.warning("Please enter your name and an answer!")
