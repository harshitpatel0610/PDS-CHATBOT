import requests
from chatbot.config import FOUNDRY_API_KEY, FOUNDRY_MODEL, IS_TESTING, FOUNDRY_BASE_URL

class FoundryClient:
    def __init__(self):
        self.api_key = None
        self.model_name = FOUNDRY_MODEL
        # Use exact base url, but ensure it points to chat/completions
        if FOUNDRY_BASE_URL:
            self.url = f"{FOUNDRY_BASE_URL.rstrip('/')}/chat/completions"
        else:
            self.url = None

    def _ensure_client(self):
        if self.api_key is None:
            if not FOUNDRY_API_KEY:
                if IS_TESTING:
                    raise RuntimeError("Live API testing is blocked because no dedicated test API configuration is available.")
                else:
                    raise ValueError("FOUNDRY_API_KEY not found. Please add it to your .env file.")
            if not FOUNDRY_BASE_URL:
                raise ValueError("FOUNDRY_BASE_URL not found. Please add it to your .env file.")
            if not self.model_name:
                raise ValueError("FOUNDRY_MODEL not found. Please add it to your .env file.")
            self.api_key = FOUNDRY_API_KEY
            from urllib.parse import urlparse
            parsed_url = urlparse(self.url)
            print(f"Provider: foundry\nBase URL host: {parsed_url.hostname}\nModel: {self.model_name}")

    def generate_response(self, prompt: str) -> str:
        self._ensure_client()
        headers = {
            "api-key": f"{self.api_key}", # Azure Foundry sometimes expects api-key instead of Bearer, but let's try Bearer and fallback, or try both. Wait, "If the Foundry API is OpenAI-compatible". Azure OpenAI uses `api-key`. Normal OpenAI compatible uses Bearer.
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
        elif response.status_code == 401 or response.status_code == 403:
            raise RuntimeError(f"{response.status_code} ERROR. Authentication failed. Please check your FOUNDRY_API_KEY.")
        elif response.status_code == 429:
            raise RuntimeError(f"{response.status_code} RESOURCE_EXHAUSTED. {response.text}")
        else:
            raise RuntimeError(f"{response.status_code} ERROR. {response.text}")

foundry_client = FoundryClient()
