from __future__ import annotations

from enum import Enum
from typing import Any

from .models import ActionCommand, DetectionEvent


class SystemState(str, Enum):
    IDLE = "IDLE"
    ARMED = "ARMED"
    EXECUTE = "EXECUTE"


class EventMapper:
    def __init__(self, config: dict[str, Any]) -> None:
        global_cfg = config["global"]
        self._mappings = config["mappings"]
        self._cooldown_seconds = float(global_cfg["cooldown_ms"]) / 1000.0
        self._confidence_threshold = float(global_cfg["confidence_threshold"])
        self._next_allowed_time = 0.0
        self.state = SystemState.ARMED

    def process_event(self, event: DetectionEvent) -> ActionCommand | None:
        if event.confidence < self._confidence_threshold:
            return None

        mapped = self._lookup(event.source, event.label)
        if mapped is None:
            return None

        action_name = str(mapped["action"])
        action_params = dict(mapped.get("params", {}))

        if action_name == "toggle_armed":
            if event.timestamp < self._next_allowed_time:
                return None
            self.state = SystemState.ARMED if self.state == SystemState.IDLE else SystemState.IDLE
            self._next_allowed_time = event.timestamp + self._cooldown_seconds
            return ActionCommand(name="toggle_armed", params={"state": self.state.value})

        if self.state != SystemState.ARMED:
            return None

        if event.timestamp < self._next_allowed_time:
            return None

        self.state = SystemState.EXECUTE
        command = ActionCommand(name=action_name, params=action_params)
        self._next_allowed_time = event.timestamp + self._cooldown_seconds
        self.state = SystemState.ARMED
        return command

    def _lookup(self, source: str, label: str) -> dict[str, Any] | None:
        source_mappings = self._mappings.get(source, {})
        mapped = source_mappings.get(label)
        if mapped is None:
            return None
        if "action" not in mapped:
            return None
        return mapped
