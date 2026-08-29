from dataclasses import dataclass
from typing import Any


@dataclass
class ChatResponse:

    message: str

    response_type: str = "text"

    payload: Any = None

    workflow_completed: bool = False