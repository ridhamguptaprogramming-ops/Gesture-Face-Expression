from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "global": {
        "camera_index": 0,
        "cooldown_ms": 800,
        "confidence_threshold": 0.8,
        "show_preview": True,
    },
    "mappings": {"gesture": {}, "expression": {}},
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        parsed = json.load(f)

    config = _deep_merge(DEFAULT_CONFIG, parsed)
    globals_cfg = config["global"]

    cooldown_ms = int(globals_cfg["cooldown_ms"])
    confidence_threshold = float(globals_cfg["confidence_threshold"])

    if cooldown_ms < 0:
        raise ValueError("global.cooldown_ms must be >= 0")
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("global.confidence_threshold must be between 0 and 1")

    if "mappings" not in config or not isinstance(config["mappings"], dict):
        raise ValueError("mappings section is required")

    for source in ("gesture", "expression"):
        config["mappings"].setdefault(source, {})
        if not isinstance(config["mappings"][source], dict):
            raise ValueError(f"mappings.{source} must be an object")

    return config
