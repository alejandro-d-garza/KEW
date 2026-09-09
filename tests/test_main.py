"""Tests for command-line helpers and state publication."""

import json
import tempfile
import unittest
from pathlib import Path

from kew.app import parse_source, write_state
from kew.models import QueueState


class MainHelperTests(unittest.TestCase):
    """Verify portable CLI parsing and state I/O."""

    def test_parse_source(self) -> None:
        """Distinguish camera indices from video paths."""
        self.assertEqual(parse_source("2"), 2)
        self.assertEqual(parse_source("samples/line.mp4"), "samples/line.mp4")

    def test_write_state(self) -> None:
        """Publish the UI state in its documented JSON shape."""
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "nested" / "state.json"
            write_state(state_path, QueueState(3, 90, 1))
            state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["person_count"], 3)
        self.assertEqual(state["queue_time_seconds"], 90)
        self.assertEqual(state["updated_at"], 1)


if __name__ == "__main__":
    unittest.main()
