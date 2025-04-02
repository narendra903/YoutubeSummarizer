from agno.agent import Agent
from agno.tools.youtube import YouTubeTools
from agno.models.google import Gemini
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")   

agent = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25", api_key=api_key),
    tools=[YouTubeTools()],
    show_tool_calls=True,
    description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
)

agent.print_response("Summarize this video https://www.youtube.com/watch?v=Iv9dewmcFbs&t", markdown=True)