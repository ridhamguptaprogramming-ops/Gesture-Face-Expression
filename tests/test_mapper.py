import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from gesture_face_ai.mapper import EventMapper, SystemState
from gesture_face_ai.models import DetectionEvent


def _config():
    return {
        "global": {
            "camera_index": 0,
            "cooldown_ms": 800,
            "confidence_threshold": 0.8,
            "show_preview": False,
        },
        "mappings": {
            "gesture": {"thumbs_up": {"action": "open_website", "params": {"url": "https://example.com"}}},
            "expression": {"surprised": {"action": "toggle_armed"}},
        },
    }


class EventMapperTests(unittest.TestCase):
    def test_low_confidence_is_ignored(self):
        mapper = EventMapper(_config())
        event = DetectionEvent("gesture", "thumbs_up", 0.79, 10.0)
        self.assertIsNone(mapper.process_event(event))

    def test_cooldown_blocks_repeat_trigger(self):
        mapper = EventMapper(_config())
        first = DetectionEvent("gesture", "thumbs_up", 0.95, 10.0)
        second = DetectionEvent("gesture", "thumbs_up", 0.95, 10.4)
        third = DetectionEvent("gesture", "thumbs_up", 0.95, 10.9)
        self.assertIsNotNone(mapper.process_event(first))
        self.assertIsNone(mapper.process_event(second))
        self.assertIsNotNone(mapper.process_event(third))

    def test_surprised_toggles_state_and_blocks_actions_when_idle(self):
        mapper = EventMapper(_config())
        toggle = DetectionEvent("expression", "surprised", 0.92, 5.0)
        action = DetectionEvent("gesture", "thumbs_up", 0.93, 6.0)

        mapper.process_event(toggle)
        self.assertEqual(mapper.state, SystemState.IDLE)
        self.assertIsNone(mapper.process_event(action))

        mapper.process_event(DetectionEvent("expression", "surprised", 0.92, 7.0))
        self.assertEqual(mapper.state, SystemState.ARMED)
        self.assertIsNotNone(mapper.process_event(DetectionEvent("gesture", "thumbs_up", 0.93, 8.0)))


if __name__ == "__main__":
    unittest.main()
