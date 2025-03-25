import streamlit as st
from agno.agent import Agent
from agno.tools.youtube import YouTubeTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini
from dotenv import load_dotenv
from textwrap import dedent
import os
import re
import time
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

# Load environment variables
#load_dotenv()

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

# Check if the API key is set
if not api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set.")
    st.stop()

# Load environment variables
#load_dotenv()
#api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
#if not api_key:
#    st.error("⚠️ API Key not found. Please set GEMINI_API_KEY in .env or Streamlit secrets.")
#    st.stop()

# Custom YouTube Functions (since YouTubeTools doesn't accept api_key)
def extract_video_id(text):
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def get_youtube_data(video_url):
    try:
        yt = YouTube(video_url)
        return {
            'title': yt.title,
            'author': yt.author,
            'length': yt.length,
            'views': yt.views,
            'publish_date': yt.publish_date.strftime("%Y-%m-%d") if yt.publish_date else None,
            'thumbnail_url': yt.thumbnail_url,
            'description': yt.description
        }
    except Exception as e:
        st.error(f"❌ YouTube data fetch error: {str(e)}")
        return None

def get_youtube_captions(video_url):
    try:
        video_id = extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return "\n".join([entry['text'] for entry in transcript])
    except TranscriptsDisabled:
        return None
    except Exception as e:
        st.warning(f"⚠️ Couldn't get captions: {str(e)}")
        return None

# Initialize YouTubeTools without API key
youtube_tools = YouTubeTools(
    get_video_captions=True,
    get_video_data=True,
    languages=["en", "hi", "te", "ta"]
)

# Create a separate agent for web searching
searcher = Agent(
    name="Searcher",
    role="Searches the web for information related to YouTube videos",
    model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key),
    instructions=[...],  # Keep your existing instructions
    tools=[DuckDuckGoTools],
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

# Create main agent with YouTube capabilities
agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key),
    tools=[youtube_tools],
    show_tool_calls=True,
    instructions=dedent("""\
    You are an expert YouTube content analyst with a keen eye for detail! 🎓
    Your role is to analyze YouTube videos and present captions in a well-structured format...
    """),
    add_datetime_to_instructions=True,
    markdown=True,
)

# Streamlit UI Configuration
st.set_page_config(page_title="🎥 AI YouTube Video Summarizer", page_icon="📺", layout="centered")

# Custom CSS
st.markdown("""
    <style>
        /* Your existing CSS styles */
        .stApp {
            background: linear-gradient(135deg, #ffecd2, #fcb69f, #a1c4fd, #c2e9fb);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        /* Add your remaining CSS */
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "captions" not in st.session_state:
    st.session_state.captions = None
if "article" not in st.session_state:
    st.session_state.article = None

# Main UI
st.title("🎥 AI YouTube Video Summarizer")
user_input = st.text_input("🔗 Enter YouTube Video URL or Key Points:", "")

if st.button("Summarize Video"):
    video_id = extract_video_id(user_input)
    
    if video_id:
        st.session_state.video_id = video_id
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with st.spinner("📊 Fetching video data and generating content..."):
            try:
                # Get metadata
                metadata = get_youtube_data(video_url)
                if not metadata:
                    st.error("❌ Failed to fetch video metadata")
                    st.stop()
                st.session_state.metadata = metadata
                
                # Get captions with fallback
                captions = get_youtube_captions(video_url)
                if not captions:
                    st.warning("⚠️ No captions available. Using description only.")
                    captions = metadata.get('description', 'No content available')
                
                # Generate all content
                st.session_state.summary = agent.run(
                    f"Summarize this video: {video_url}"
                ).content
                
                st.session_state.captions = agent.run(
                    f"Format captions for this video: {video_url}\n\nRaw content:\n{captions}"
                ).content
                
                st.session_state.article = agent.run(
                    f"Create article from this video: {video_url}"
                ).content
                
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")
                st.stop()
    else:
        st.error("⚠️ Invalid YouTube URL or ID")

# Display results if available
if st.session_state.metadata:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📌 Metadata", 
        "📰 Summary", 
        "🗣 Captions", 
        "📝 Article",
        "▶️ Video"
    ])
    
    with tab1:
        st.json(st.session_state.metadata)
    
    with tab2:
        st.markdown(st.session_state.summary)
    
    with tab3:
        st.markdown(st.session_state.captions)
    
    with tab4:
        st.markdown(st.session_state.article)
    
    with tab5:
        st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")

# Sidebar search functionality
st.sidebar.title("🔍 Web Search")
search_query = st.sidebar.text_input("Ask a Question:")
if st.sidebar.button("Search"):
    if search_query:
        with st.spinner("Searching..."):
            try:
                search_results = searcher.run(search_query).content
                st.sidebar.markdown(search_results)
            except Exception as e:
                st.sidebar.error(f"Search error: {str(e)}")
    else:
        st.sidebar.warning("Please enter a search query")

# Footer
st.markdown("""
    🛠️ Built with AI | 📅 Updated: 2024 | 
    [<img src='https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg' width='20' height='20'>](https://www.linkedin.com/in/nk-analytics/)
""", unsafe_allow_html=True)