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

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

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


# Create a separate agent for web searching
searcher = Agent(
    name="Searcher",
    role="Searches the web for information related to YouTube videos",
    model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key),
    instructions=[
        "Given a topic or YouTube video URL, find relevant web information and present it in an engaging, easy-to-digest format.",
        "For each result, provide:",

        "🎥 SPECIAL YOUTUBE PROCESSING:",
        "If the input is a YouTube video URL:",
        "1. 🧐 Search for context/background about the video's topic",
        "2. 🔎 Research the creator/channel history",
        "3. 📊 Look for related controversies or discussions",
        "4. 🌐 Find authoritative sources analyzing the content",
        "",
        "STANDARD OUTPUT FORMAT:",
        "For each result, provide:",
        "1️⃣ A concise summary with 3-5 key points (each with a relevant emoji)",
        "2️⃣ The source URL in brackets",
        "3️⃣ A relevance rating (⭐️⭐️⭐️⭐️⭐ being most relevant)",
        "",
        "1️⃣ A concise summary with 3-5 key points (each with a relevant emoji)",
        "2️⃣ The source URL in brackets",
        "3️⃣ A relevance rating (⭐️⭐️⭐️⭐️⭐ being most relevant)",
        "",
        "Execution steps:",
        "1. Generate 3 optimized search terms based on the query/video",
        "2. Use DuckDuckGo to find top 3 authoritative sources per term",
        "3. For each source:",
        "   - Extract core insights (not full articles)",
        "   - Format as:",
        "     🔍 [Search Term Used]",
        "     ✨ Title/Header",
        "     📌 Key Point 1 [🌐 URL]",
        "     📌 Key Point 2",
        "     ...",
        "     ⭐ Relevance: X/5",
        "",
        "Special rules:",
        "- Use varied emojis matching content type (🎥 for videos, 📚 for articles, etc)",
        "- Never copy full paragraphs - only distilled insights",
        "- Highlight controversies/opposing views when present",
        "- Add 🚨 for surprising/important facts",
        "- For video URLs, find background about creators/context",
    ],
    tools=[DuckDuckGoTools],
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

# Set Streamlit page config with a vibrant theme
st.set_page_config(page_title="🎥 AI YouTube Video Summarizer", page_icon="📺", layout="centered")

# Custom CSS for vibrant and light UI
st.markdown(
    """
    <style>
        /* Apply gradient background to the entire app */
        .stApp {
            background: linear-gradient(135deg, #ffecd2, #fcb69f, #a1c4fd, #c2e9fb);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            
        }
        /* Adjust horizontal line thickness */
        hr {
            border: none;
            height: 1px; /* Adjust thickness */
            background-color: #bbb; /* Lighter color */
            margin: 10px 0; /* Reduce space */
        }


        /* Animation effect for smooth gradient transitions */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
         /* Remove top margin only from the main container */
        .block-container {
            padding-top: 0px !important; /* Removes extra top padding */
            margin-top: 25px !important; /* Moves content up */
        }

        /* Style buttons with light color and green text */
        .stButton>button {
            background: linear-gradient(135deg, #fbd3e9, #bbd2c5);
            color: green !important;
            border: none;
            padding: 10px 15px;
            font-size: 35px;
            font-weight: bold;
            border-radius: 5px;
            transition: all 0.3s ease-in-out;
        }

        /* Remove white background from buttons */
        .stButton {
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        /* Ensure content is readable on the gradient */
        .stMarkdown, .stDataFrame, .stText, .stJson, .stButton, .stSubheader {
            background: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }

        * Custom CSS for tabs */
        div[data-baseweb="tab-list"] > button {
            font-size: 25px !important; /* Increase font size */
        }
        div[data-baseweb="tab-list"] > button[aria-selected="true"] {
            color: blue; /* Change color when selected */
            font-weight: bold;
        }
        /* Style the sidebar with a gradient background */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #f8f0fb, #f0f4c3, #d4f5ff, #f0f4c3);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }

        
        
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize the YouTubeTools with parameters
youtube_tools = YouTubeTools(
    get_video_captions=True,
    get_video_data=True,
    languages=["en", "hi", "te", "ta"]
)

# Create an agent with YouTube capabilities
agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key),
    tools=[youtube_tools],
    show_tool_calls=True,
    instructions=dedent("""\
    You are an expert YouTube content analyst with a keen eye for detail! 🎓
    Your role is to analyze YouTube videos and present captions in a **well-structured, readable format** with **proper headings, subheadings, and relevant emojis**.

    **🔍 Follow these steps for comprehensive video analysis:**

    ### **1️⃣ Video Overview**
    - Extract and display basic **video metadata** (title, duration, channel, upload date).
    - Identify the **video type** (📚 Educational, 💻 Technical, 🎮 Gaming, 📱 Tech Review, 🎨 Creative).
    - Note the **content structure** and key highlights.

    ### **2️⃣ Timestamp Creation 🕒**
    - Generate **precise, meaningful timestamps**.
    - Focus on **major topic transitions** and highlight key moments.
    - Use this format:
    ```
    [00:00 - 02:30] 🎯 Introduction to the Topic
    [02:31 - 05:45] 🛠️ Key Concepts Explained
    [05:46 - 10:15] 💡 Practical Demonstration
    [10:16 - 12:00] ❓ Q&A and Conclusion
    ```

    **🔹 Your analysis style should include:**
    - Clear and **descriptive segment titles**.
    - **Relevant emojis** to enhance readability.
    - Bullet points for **key takeaways**.
    - **Consistent formatting** for an easy-to-read summary.

    **⚡ Quality Guidelines:**
    - ✅ Verify **timestamp accuracy**.
    - ❌ Avoid **timestamp hallucination** (don’t generate timestamps not present in the video).
    - 📚 Ensure **comprehensive coverage** of the entire video.
    - 🎯 Maintain a **consistent level of detail** across all sections.


    💡 **Goal:** Transform messy captions into a **clean, structured format** that is **reader-friendly and visually engaging!** 🎥✨
    """),
    add_datetime_to_instructions=True,
    markdown=True,
)

# Function to extract YouTube video ID from input
def extract_video_id(text):
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", text)
    return match.group(1) if match else None


# Define a generator function for streaming search results
def search_results_generator(query):
    """
    Executes a search query and yields results in a streaming fashion.

    Args:
        query (str): The search query.

    Yields:
        str:  Search results, formatted for display.
    """
    st.sidebar.markdown(f"Searching the web for '{query}'...")
    results = searcher.run(query, markdown=True).content
    # Simulate streaming behavior (replace with actual streaming if your searcher supports it)
    for chunk in results.split('\n'):  # Split results into chunks (e.g., by line)
        time.sleep(0.1)  # Add a small delay to simulate streaming
        yield chunk + "\n" #keep line break, otherwise all text on same line.


# Initialize session state variables
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
if "active_tab" not in st.session_state:
    st.session_state.active_tab = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = ""

# Streamlit UI
st.title("🎥 AI YouTube Video Summarizer ")

# Input field for YouTube URL
user_input = st.text_input("🔗 Enter YouTube Video URL or Key Points:", "")

# Extract video ID
video_id = extract_video_id(user_input)

if st.button("Summarize Video",icon="😃"):
    if video_id:
        st.session_state.video_id = video_id
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        with st.spinner("📊 Fetching captions, metadata, and generating content... Please wait.",show_time=True):
            try:
                # Retrieve metadata
                metadata = youtube_tools.get_youtube_video_data(video_url)
                if metadata is None:
                    st.error("❌ Could not get video Metadata.")
                    st.stop()
                st.session_state.metadata = metadata

                # Generate AI summary
                run_response = agent.run(f"Summarize this video {video_url}")
                st.session_state.summary = run_response.content

                # ✅ Separate Instructions for Detailed Captions with Emojis
                instructions_captions = dedent("""\
                    You are an expert in transforming YouTube video captions into **structured, readable, and engaging text**! 🎬✨

                    **📌 Key Guidelines:**
                    - Organize captions **clearly** with **proper headings & subheadings**.
                    - Format them into **clean paragraphs**, avoiding messy transcript-style text.
                    - Add **timestamps** and **relevant emojis** to enhance readability. 🎯

                    **📝 Captions Formatting Style:**

                    ### **1️⃣ Introduction 🎤**
                    - Summarize the opening of the video.
                    - Include the speaker’s key message and context.

                    ### **2️⃣ Main Discussion 🔍**
                    - Break the content into **logical sections**.
                    - Use **timestamps** like:
                    ```
                    [00:00 - 02:30] 🎯 Topic Introduction
                    [02:31 - 05:45] 💡 Key Explanation
                    [05:46 - 10:15] 🛠️ Practical Insights
                    ```
                    - Add **important keywords** and **bullet points**.

                    ### **3️⃣ Conclusion & Takeaways 🚀**
                    - Summarize the final remarks.
                    - Highlight any **actionable insights or next steps**.

                    💡 **Goal:** Convert raw captions into a **reader-friendly, structured, and visually appealing format** with proper headings, timestamps, and relevant emojis!
                    """)
                # Generate AI captions formatting
                captions_response = agent.run(f"Format the captions of this video {video_url} using the following guidelines:\n\n{instructions_captions}", markdown=True)
                st.session_state.captions = captions_response.content


                # **New Instructions for Content Generation**

                instructions_content = dedent("""\
                    You are an expert content creator! 📝 Your task is to generate **high-quality, engaging, and informative content** based on the video script.

                    **📌 Key Guidelines:**
                    - Transform the video content into a structured article, blog, or post.
                    - Maintain a **clear and concise** writing style.
                    - Use **headings, subheadings, and bullet points** for better readability.
                    - Incorporate relevant **keywords** and **calls-to-action** (if applicable).

                    **📝 Content Structure:**

                    ### **1️⃣ Introduction 🎯**
                    - Provide a brief **overview** of the topic covered in the video.
                    - Hook the reader with an engaging statement.

                    ### **2️⃣ Key Takeaways & Insights 💡**
                    - Summarize the **most important points** from the video.
                    - Use **bullet points** to highlight key insights.

                    ### **3️⃣ In-Depth Explanation 🛠️**
                    - Provide a **detailed breakdown** of the main concepts.
                    - Use **examples, case studies, or practical applications**.

                    ### **4️⃣ Conclusion & Next Steps 🚀**
                    - Recap the key takeaways.
                    - Encourage the reader to **take action, explore further, or engage**.

                    💡 **Goal:** Convert raw video content into a **valuable, well-structured, and engaging article** that is easy to read and understand!
                    """)

                # Generate AI-generated article using separate instructions
                article_response = agent.run(
                    f"Generate a well-structured article for this video {video_url}.\n\n{instructions_content}",
                    markdown=True)
                st.session_state.article = article_response.content
                
                # Reset active tab to None (show buttons first)
                st.session_state.active_tab = None

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

    else:
        st.error("⚠️ Invalid YouTube link. Please enter a valid video URL.")

# Display content
if st.session_state.metadata and st.session_state.summary and st.session_state.captions and st.session_state.article:
    metadata_tab, summary_tab, captions_tab, article_tab,video_tab = st.tabs(["📌 Video Metadata", "📰 Generated Summary", "🗣 Video Captions", "📝 AI-Generated Article","▶️ Video"])

    with metadata_tab:
        st.subheader("📌 Video Metadata")
        st.json(st.session_state.metadata)

    with summary_tab:
        st.subheader("📰 AI-Generated Summary")
        with st.container(height=500,border=True):
            st.markdown(st.session_state.summary, unsafe_allow_html=True)

    with captions_tab:
        st.subheader("🗣 Video Captions ")
        with st.container(height=500,border=True):
            st.markdown(st.session_state.captions, unsafe_allow_html=True)

    with article_tab:
        st.subheader("📝 AI-Generated Article")
        with st.container(height=500,border=True):
            st.markdown(st.session_state.article, unsafe_allow_html=True)
    
    with video_tab:
        st.subheader("▶️ Video")
        # The video URL should come from user_input
        st.video(user_input,loop=True)
        
# Search functionality in the sidebar
st.sidebar.subheader("🔍 Web Search")
messages = st.sidebar.container(height=200,border=True) # put the container in the sidebar
st.session_state.search_query = st.sidebar.text_input("Ask a Question:", value=st.session_state.search_query)

# Create two columns inside the sidebar
col1, col2 = st.sidebar.columns(2)

# Add buttons to columns
with col1:
    search_button = st.button("Search")

with col2:
    clear_button = st.button("Clear")

if search_button:
    if st.session_state.search_query:
        #st.sidebar.write_stream(search_results_generator(st.session_state.search_query))
        for result in search_results_generator(st.session_state.search_query):
             messages.write(result)
    else:
        st.sidebar.warning("Please enter a search query.")

if clear_button:
    st.session_state.search_query = ""
    st.session_state.search_results = ""


# Sidebar
st.sidebar.title("📚 About")
st.sidebar.subheader("📞 Contact")
st.sidebar.markdown("💡 Created by: **AI & Finance Enthusiasts**")
st.sidebar.markdown("📩 Email: narendra.insights@gmail.com")



# Footer
st.markdown(
    "🛠️ **Built with AI ** | 📅 *Updated: 2025* | "
    "[<img src='https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg' width='20' height='20'>](https://www.linkedin.com/in/nk-analytics/)"
    " Connect on LinkedIn",
    unsafe_allow_html=True,
)
