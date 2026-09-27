from chatbot.conversation.session import ConversationSession
from chatbot.dialogue.manager import DialogueManager

session = ConversationSession(
    session_id="user1"
)

print(DialogueManager.process(
    session,
    "I want a BPL ration card"
))

print(session.entities)