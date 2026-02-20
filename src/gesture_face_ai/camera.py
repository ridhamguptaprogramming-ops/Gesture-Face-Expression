from __future__ import annotations

import cv2


class Camera:
    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self.cap: cv2.VideoCapture | None = None

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Unable to open camera index {self.camera_index}")

    def read(self):
        if self.cap is None:
            raise RuntimeError("Camera not started")
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("Failed to read frame from camera")
        return frame

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
