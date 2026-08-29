from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class ConversationState:

    session_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    intent: str | None = None

    current_step: int = 0

    slots: dict = field(default_factory=dict)

    completed: bool = False

    authenticated: bool = False

    last_message: str = ""

    context: dict = field(default_factory=dict)