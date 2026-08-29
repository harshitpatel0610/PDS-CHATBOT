from dataclasses import dataclass, field


@dataclass
class WorkflowStep:

    slot: str

    question: str

    required: bool = True


@dataclass
class Workflow:

    intent: str

    workflow_name: str

    authentication_required: bool

    steps: list[WorkflowStep]