from chatbot.llms.factory import get_llm
from chatbot.memory import get_messages
from chatbot.prompts import SYSTEM_PROMPT
from chatbot.guardrails import is_pds_related
from chatbot.config import MODEL_NAME


DOMAIN_RESPONSE = """
I'm RationAI 🤖, a specialized assistant for India's Public Distribution System (PDS).

I can help you with:

• Ration Card Services
• NFSA
• ONORC
• Fair Price Shops
• Government Food Schemes
• Eligibility
• Complaints
• Subsidized food distribution

Please ask a PDS-related question.
"""

def build_prompt() -> str:
    messages = get_messages()  # Get complete chat history

    conversation = ""  # Store formatted conversation

    for message in messages:
        role = message["role"].capitalize()  # User / Assistant
        content = message["content"]  # Message text

        conversation += f"{role}: {content}\n"

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{conversation}"
    )  # Build final prompt

    return prompt  # Return complete prompt


def get_ai_response() -> str:
    messages = get_messages()  # Get chat history

    user_message = messages[-1]["content"]  # Latest user message

    if not is_pds_related(user_message):
        return DOMAIN_RESPONSE

    llm = get_llm()  # Get configured LLM

    prompt = build_prompt()  # Build prompt

    response = llm.generate_response(prompt)  # Generate AI response

    return response

def get_ai_response():
    print("1. get_ai_response() called")

    messages = get_messages()

    user_message = messages[-1]["content"]

    print("2. User Message:", user_message)

    llm = get_llm()
    print(type(llm))
    print(llm)

    print("3. LLM Created")

    prompt = build_prompt()

    print("4. Prompt Built")

    response = llm.generate_response(prompt)

    print("5. Gemini Returned")

    return response

