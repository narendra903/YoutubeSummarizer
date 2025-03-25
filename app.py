import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=api_key)

# Function to generate summary using Gemini 2.0 Flash
def generate_summary(transcript_text, summary_length):
    length_mapping = {
        'Short': 50,
        'Medium': 100,
        'Long': 150
    }
    max_tokens = length_mapping.get(summary_length, 100)

    model = genai.GenerativeModel(model='gemini-2.0-flash')
    response = model.generate_content(
        contents=f"Please summarize the following text:\n\n{transcript_text}",
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens
        )
    )
    
    return response.text.strip() if response else "Failed to generate summary."

# Streamlit UI
st.title("YouTube Video Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")
summary_length = st.selectbox("Select Summary Length:", ['Short', 'Medium', 'Long'])

if st.button("Generate Summary"):
    if youtube_link:
        try:
            # Extract video ID from YouTube URL
            video_id = youtube_link.split("v=")[1].split("&")[0]

            # Fetch transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join(segment["text"] for segment in transcript)

            # Generate summary
            summary = generate_summary(transcript_text, summary_length)
            
            st.write("**Summary:**")
            st.write(summary)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube link.")
