from google import genai
from google.genai import errors
import sys

from chatbot.config import GOOGLE_API_KEY, MODEL_NAME, IS_TESTING

class GeminiClient:
    def __init__(self):
        self.client = None
        self.generation_config = {
            "temperature": "default",
            "max_output_tokens": "default",
            "timeout": "default",
            "retry_policy": "disabled (fail fast)"
        }

    def _ensure_client(self):
        if self.client is None:
            if not GOOGLE_API_KEY:
                if IS_TESTING:
                    raise RuntimeError("Live API testing is blocked because no dedicated test API configuration is available.")
                else:
                    raise ValueError("GOOGLE_API_KEY not found. Please add it to your .env file.")
                    
            self.client = genai.Client(
                api_key=GOOGLE_API_KEY,
                http_options={'retry_options': {'attempts': 1}}
            )

    def generate_response(self, prompt: str) -> str:
        self._ensure_client()
        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

gemini = GeminiClient()