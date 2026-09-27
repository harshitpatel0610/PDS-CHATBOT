import sys
from dotenv import load_dotenv
load_dotenv()
from chatbot.dialogue.manager import DialogueManager
from chatbot.conversation.session import ConversationSession

def test_rag():
    queries = [
        "How can I apply for a new ration card?",
        "How do I download my ration card?",
        "I lost my ration card, what can I do?",
        "Can I apply for a ration card online?",
        "How can I check my ration card status?",
        "How do I add a family member?",
        "What is the weather like today?",
        "How can I apply for a ration card in Karnataka?"
    ]
    
    for q in queries:
        print("=" * 80)
        print(f"QUERY: {q}")
        session = ConversationSession(session_id="test_session")
        response = DialogueManager.process(session, q)
        print("\nRESPONSE:\n")
        print(response)

if __name__ == "__main__":
    test_rag()
