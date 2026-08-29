from dataclasses import dataclass


@dataclass
class Entity:

    entity_type: str

    value: str

    confidence: float