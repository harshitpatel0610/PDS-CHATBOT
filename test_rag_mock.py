from chatbot.dialogue.manager import DialogueManager
from chatbot.conversation.session import ConversationSession
import json

def test_conversation():
    session = ConversationSession(session_id="test_conv")
    
    turns = [
        "How can I apply for a new ration card?",
        "Gujarat",
        "Sabarkantha",
        "APL"
    ]
    
    for t in turns:
        print(f"\nUser: {t}")
        r = DialogueManager.process(session, t)
        print(f"Assistant: {r}")
        
        # print session entities cleanly
        print("Session State Entities:", json.dumps(session.entities, indent=2))

if __name__ == "__main__":
    test_conversation()
