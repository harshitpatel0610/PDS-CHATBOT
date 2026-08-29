import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please add it to your .env file."
    )

MODEL_NAME = "gemini-3.6-flash"
APP_NAME = "PDS AI Assistant"
MODEL_PROVIDER = "gemini"      # AI provider (gemini/openai/claude...)