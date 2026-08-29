from chatbot.config import MODEL_PROVIDER          # Read selected AI provider
from chatbot.llms.gemini import gemini             # Import Gemini client


def get_llm():
    if MODEL_PROVIDER == "gemini":
        return gemini                             # Return Gemini client

    raise ValueError(f"Unsupported model provider: {MODEL_PROVIDER}")