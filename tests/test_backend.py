from chatbot.dialogue.manager import DialogueManager
from chatbot.conversation.session import ConversationSession
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

session = ConversationSession(session_id="test_123")
query = "What documents are required to apply for a ration card in Gujarat?"

print("Processing query...")
try:
    reply = DialogueManager.process(session, query)
    print("Reply:", reply)
except Exception as e:
    print("Exception during process:", repr(e))
