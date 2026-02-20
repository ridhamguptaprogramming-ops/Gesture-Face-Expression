from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

from .actions import ActionExecutor
from .camera import Camera
from .config import load_config
from .expression import ExpressionDetector
from .gesture import GestureDetector
from .mapper import EventMapper
from .models import DetectionEvent


def draw_overlay(frame, state: str, status: str) -> None:
    cv2.putText(frame, f"State: {state}", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 0), 2)
    cv2.putText(frame, status, (12, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)
    cv2.putText(frame, "Press Q to quit", (12, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gesture + face-expression controlled AI system")
    parser.add_argument(
        "--config",
        default="config/mappings.json",
        help="Path to JSON mapping config",
    )
    return parser.parse_args()


def run(config_path: str) -> None:
    config = load_config(config_path)

    camera = Camera(camera_index=int(config["global"]["camera_index"]))
    gesture_detector = GestureDetector()
    expression_detector = ExpressionDetector()
    mapper = EventMapper(config)
    executor = ActionExecutor(base_dir=Path.cwd())

    show_preview = bool(config["global"].get("show_preview", True))

    last_status = "Ready"
    camera.start()
    try:
        while True:
            frame = camera.read()
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            now = time.time()

            events: list[DetectionEvent] = []
            gesture_event = gesture_detector.detect(frame_rgb, timestamp=now)
            if gesture_event is not None:
                events.append(gesture_event)

            expression_event = expression_detector.detect(frame_rgb, timestamp=now)
            if expression_event is not None:
                events.append(expression_event)

            events.sort(key=lambda event: event.confidence, reverse=True)
            for event in events:
                command = mapper.process_event(event)
                if command is None:
                    continue
                action_status = executor.execute(command, frame=frame)
                last_status = f"{event.source}:{event.label} ({event.confidence:.2f}) -> {action_status}"
                break

            draw_overlay(frame, mapper.state.value, last_status)
            if show_preview:
                cv2.imshow("Gesture + Expression Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        gesture_detector.close()
        expression_detector.close()
        camera.stop()
        cv2.destroyAllWindows()


def main() -> None:
    args = parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
