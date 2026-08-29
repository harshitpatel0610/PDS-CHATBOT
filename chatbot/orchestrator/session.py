from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class ChatSession:

    session_id: str = field(default_factory=lambda: str(uuid4()))

    workflow_state = None

    history = field(default_factory=list)

    user_context = field(default_factory=dict)
    