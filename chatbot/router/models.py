from dataclasses import dataclass, field


@dataclass
class RouteResult:

    is_pds: bool

    intent: str | None

    confidence: float

    entities: list = field(default_factory=list)