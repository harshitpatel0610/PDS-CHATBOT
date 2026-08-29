from google import genai
from google.genai import errors

from chatbot.config import GOOGLE_API_KEY, MODEL_NAME

class GeminiClient:
    def __init__(self):
        # Fail fast by disabling aggressive automatic retries for quota limits
        self.client = genai.Client(
            api_key=GOOGLE_API_KEY,
            http_options={'retry_options': {'attempts': 1}}
        )
        self.generation_config = {
            "temperature": "default",
            "max_output_tokens": "default",
            "timeout": "default",
            "retry_policy": "disabled (fail fast)"
        }

    def generate_response(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

gemini = GeminiClient()