"""
simpleAIAgent_ChatGpt.py

A lightweight AI agent that interacts with the Drink Service microservice.
This script loads environment variables and connects to the OpenAI API.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not_set")

def get_agent_status():
    """
    Simple test function to verify the AI agent environment is ready.
    """
    if OPENAI_API_KEY == "not_set":
        return "⚠️ No API key found. Check your .env file."
    return "✅ AI Agent ready with configured API key."

if __name__ == "__main__":
    print(get_agent_status())
