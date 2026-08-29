from fastapi import APIRouter
from pydantic import BaseModel

from chatbot.conversation.session import ConversationSession
from chatbot.dialogue.manager import DialogueManager

router = APIRouter()

# Temporary in-memory sessions
SESSIONS = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.get("/health")
def health():
    return {"status": "ok", "vector_store": "available"}

@router.post("/chat")
def chat(request: ChatRequest):
    
    if not request.session_id:
        return {
            "reply": "Invalid request: missing session_id",
            "intent": None,
            "entities": {},
            "history": []
        }

    if not request.message or not request.message.strip():
        return {
            "reply": "Invalid request: empty message",
            "intent": None,
            "entities": {},
            "history": []
        }

    if request.session_id not in SESSIONS:
        SESSIONS[request.session_id] = ConversationSession(
            session_id=request.session_id
        )

    session = SESSIONS[request.session_id]

    try:
        reply = DialogueManager.process(
            session,
            request.message
        )
    except Exception as e:
        reply = "I apologize, but our backend service encountered an unexpected error."
        
    return {
        "reply": reply,
        "intent": getattr(session, "current_intent", None),
        "entities": getattr(session, "entities", {}),
        "history": getattr(session, "history", [])
    }