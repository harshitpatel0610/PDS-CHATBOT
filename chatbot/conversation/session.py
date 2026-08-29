from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional,Any


@dataclass
class ConversationSession:
    """
    Represents one user's conversation session.
    """

    session_id: str

    current_intent: Optional[str] = None

    confidence: float = 0.0

    entities: Dict[str, Any] = field(default_factory=dict)

    history: List[dict] = field(default_factory=list)

    state: str = "START"

    created_at: datetime = field(default_factory=datetime.now)

    updated_at: datetime = field(default_factory=datetime.now)

    def add_entity(self, entity_type: str, value: str):
        self.entities[entity_type] = value
        self.updated_at = datetime.now()

    def add_message(self, role: str, message: str):
        self.history.append(
            {
                "role": role,
                "message": message,
                "time": datetime.now().isoformat()
            }
        )
        self.updated_at = datetime.now()

    def set_intent(self, intent: str, confidence: float):
        self.current_intent = intent
        self.confidence = confidence
        self.updated_at = datetime.now()

    def clear(self):
        self.current_intent = None
        self.confidence = 0.0
        self.entities.clear()
        self.history.clear()
        self.state = "START"
        self.updated_at = datetime.now()