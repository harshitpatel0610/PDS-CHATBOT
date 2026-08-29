from chatbot.conversation.session import ConversationSession
from chatbot.workflow.engine import WorkflowEngine

session = ConversationSession(
    session_id="user1",
    current_intent="ration_card_apply"
)

session.entities["states"] = "Karnataka"
session.entities["districts"] = "Bengaluru Urban"
session.entities["card_types"] = "BPL"

print(WorkflowEngine.process(session))