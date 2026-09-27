from chatbot.config import LLM_PROVIDER
from chatbot.llms.gemini import gemini

def get_llm():
    if LLM_PROVIDER == "gemini":
        return gemini

    raise ValueError(f"Unsupported model provider: {LLM_PROVIDER}")