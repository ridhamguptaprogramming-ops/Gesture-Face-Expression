from __future__ import annotations

import math
import time

import mediapipe as mp

from .models import DetectionEvent


class GestureDetector:
    def __init__(self, min_detection_confidence: float = 0.6, min_tracking_confidence: float = 0.6) -> None:
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def close(self) -> None:
        self._hands.close()

    def detect(self, frame_rgb, timestamp: float | None = None) -> DetectionEvent | None:
        results = self._hands.process(frame_rgb)
        if not results.multi_hand_landmarks:
            return None

        landmarks = results.multi_hand_landmarks[0].landmark
        handedness_label = "Right"
        if results.multi_handedness:
            handedness_label = results.multi_handedness[0].classification[0].label

        label, confidence = self._classify(landmarks, handedness_label)
        if label is None:
            return None

        return DetectionEvent(
            source="gesture",
            label=label,
            confidence=confidence,
            timestamp=timestamp if timestamp is not None else time.time(),
        )

    def _classify(self, landmarks, handedness_label: str) -> tuple[str | None, float]:
        wrist = landmarks[0]

        def finger_extended(tip_idx: int, pip_idx: int, mcp_idx: int) -> bool:
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            mcp = landmarks[mcp_idx]
            return self._distance(tip, wrist) > self._distance(pip, wrist) * 1.08 and tip.y < mcp.y

        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]

        thumb_outward = thumb_tip.x < thumb_ip.x if handedness_label == "Right" else thumb_tip.x > thumb_ip.x
        thumb_extended = self._distance(thumb_tip, wrist) > self._distance(thumb_mcp, wrist) * 1.07 and thumb_outward

        index_extended = finger_extended(8, 6, 5)
        middle_extended = finger_extended(12, 10, 9)
        ring_extended = finger_extended(16, 14, 13)
        pinky_extended = finger_extended(20, 18, 17)

        non_thumb_extended = [index_extended, middle_extended, ring_extended, pinky_extended]
        extended_count = int(thumb_extended) + sum(non_thumb_extended)

        if thumb_extended and not any(non_thumb_extended):
            vertical_delta = landmarks[6].y - thumb_tip.y
            if vertical_delta > 0.04:
                confidence = min(0.99, 0.8 + min(vertical_delta * 2.0, 0.19))
                return "thumbs_up", confidence

        if extended_count >= 5:
            return "open_palm", 0.9

        folded_non_thumb = all(not value for value in non_thumb_extended)
        thumb_folded = not thumb_extended
        if folded_non_thumb and thumb_folded:
            tip_distances = [self._distance(landmarks[idx], wrist) for idx in (8, 12, 16, 20)]
            spread = max(tip_distances) - min(tip_distances)
            confidence = 0.78 + max(0.0, 0.12 - spread) * 0.5
            return "fist", min(0.95, confidence)

        return None, 0.0

    @staticmethod
    def _distance(p1, p2) -> float:
        return math.hypot(p1.x - p2.x, p1.y - p2.y)
