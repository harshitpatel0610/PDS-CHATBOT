import requests
from chatbot.config import GROQ_API_KEY, MODEL_NAME, IS_TESTING, GROQ_BASE_URL

class GroqClient:
    def __init__(self):
        self.api_key = None
        self.model_name = MODEL_NAME
        self.url = f"{GROQ_BASE_URL.rstrip('/')}/chat/completions"

    def _ensure_client(self):
        if self.api_key is None:
            if not GROQ_API_KEY:
                if IS_TESTING:
                    raise RuntimeError("Live API testing is blocked because no dedicated test API configuration is available.")
                else:
                    raise ValueError("GROQ_API_KEY not found. Please add it to your .env file.")
            self.api_key = GROQ_API_KEY
            from urllib.parse import urlparse
            parsed_url = urlparse(self.url)
            print(f"Provider: groq\nBase URL host: {parsed_url.hostname}\nModel: {self.model_name}")

    def generate_response(self, prompt: str) -> str:
        self._ensure_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        response = requests.post(self.url, headers=headers, json=data)
        
        # If the request is successful, return the text
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            # Raise an exception mirroring what Gemini does or just a standard Exception
            # with the status code and text so rag_service can handle it
            raise RuntimeError(f"{response.status_code} ERROR. {response.text}")

groq_client = GroqClient()
