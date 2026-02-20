from __future__ import annotations

import math
import time

import mediapipe as mp

from .models import DetectionEvent


class ExpressionDetector:
    def __init__(self, min_detection_confidence: float = 0.6, min_tracking_confidence: float = 0.6) -> None:
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def close(self) -> None:
        self._face_mesh.close()

    def detect(self, frame_rgb, timestamp: float | None = None) -> DetectionEvent | None:
        results = self._face_mesh.process(frame_rgb)
        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        label, confidence = self._classify(landmarks)
        if label is None:
            return None

        return DetectionEvent(
            source="expression",
            label=label,
            confidence=confidence,
            timestamp=timestamp if timestamp is not None else time.time(),
        )

    def _classify(self, landmarks) -> tuple[str | None, float]:
        eye_span = self._distance(landmarks[33], landmarks[263])
        if eye_span <= 1e-6:
            return None, 0.0

        mouth_open = self._distance(landmarks[13], landmarks[14]) / eye_span
        mouth_width = self._distance(landmarks[61], landmarks[291]) / eye_span
        brow_raise = (
            self._distance(landmarks[70], landmarks[159]) + self._distance(landmarks[300], landmarks[386])
        ) / (2.0 * eye_span)
        smile_ratio = mouth_width / max(mouth_open, 1e-4)

        if mouth_open > 0.34 and brow_raise > 0.22:
            confidence = min(0.99, 0.7 + (mouth_open - 0.34) * 1.5 + (brow_raise - 0.22) * 1.5)
            return "surprised", confidence

        if mouth_open > 0.08 and mouth_width > 1.02 and smile_ratio > 4.8:
            confidence = min(0.99, 0.68 + (smile_ratio - 4.8) * 0.05 + (mouth_width - 1.02) * 0.35)
            return "smile", confidence

        return None, 0.0

    @staticmethod
    def _distance(p1, p2) -> float:
        return math.hypot(p1.x - p2.x, p1.y - p2.y)
