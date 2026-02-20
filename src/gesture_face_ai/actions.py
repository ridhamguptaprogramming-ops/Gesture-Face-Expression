from __future__ import annotations

import time
import webbrowser
from pathlib import Path

import cv2

from .models import ActionCommand


class ActionExecutor:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self._pyautogui = None
        try:
            import pyautogui  # type: ignore

            self._pyautogui = pyautogui
        except Exception:
            self._pyautogui = None

    def execute(self, command: ActionCommand, frame=None) -> str:
        if command.name == "open_website":
            url = str(command.params.get("url", "https://www.google.com"))
            webbrowser.open(url, new=2)
            return f"Opened {url}"

        if command.name == "switch_window":
            keys = command.params.get("keys", ["alt", "tab"])
            if self._pyautogui is None:
                return "pyautogui unavailable; cannot switch window"
            self._pyautogui.hotkey(*keys)
            return f"Sent hotkey {keys}"

        if command.name == "capture_photo":
            if frame is None:
                return "No frame available for capture"
            output_dir = self.base_dir / str(command.params.get("output_dir", "captures"))
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_dir / f"capture_{int(time.time() * 1000)}.jpg"
            cv2.imwrite(str(filename), frame)
            return f"Saved {filename}"

        if command.name == "print_message":
            message = str(command.params.get("message", "Action triggered"))
            return message

        if command.name == "toggle_armed":
            return f"State: {command.params.get('state', 'UNKNOWN')}"

        return f"Unknown action: {command.name}"
