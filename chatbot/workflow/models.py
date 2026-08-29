from dataclasses import dataclass, field


@dataclass
class WorkflowState:

    intent: str

    current_step: int = 0

    completed: bool = False

    collected_entities: dict = field(default_factory=dict)