from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DetectionEvent:
    source: str
    label: str
    confidence: float
    timestamp: float


@dataclass(frozen=True)
class ActionCommand:
    name: str
    params: dict[str, Any] = field(default_factory=dict)

