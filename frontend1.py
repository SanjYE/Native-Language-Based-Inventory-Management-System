import streamlit as st
import requests
import json

st.title("Voice-Controlled Restaurant Management System")

# Button to record and process audio
if st.button("Record Audio"):
    with st.spinner("Recording audio..."):
        # Assuming you have an audio file named "recorded_audio.wav" after recording
        response = requests.post("http://localhost:5000/transcribe_and_process_audio")
        if response.status_code == 200:
            transcription = response.json().get("transcription", "")
            st.write("Transcription:", transcription)
            
            # Send transcription for processing the command
            process_response = requests.post(
                "http://localhost:5000/process_command",
                json={"transcription": transcription}
            )
            
            if process_response.status_code == 200:
                result = process_response.json()

                # Check if the result is a list (for multiple records like employees/customers)
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                    # Display the result as a table dynamically
                    st.table(result)  # Streamlit will automatically handle displaying the table in a readable format
                else:
                    st.write(result)  # For single items, just display as is
            else:
                st.error(f"Error processing the command: {process_response.text}")
        else:
            st.error("Error recording and transcribing audio.")
