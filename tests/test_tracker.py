"""Tests for tracking and queue-region membership."""

import unittest

from kew.models import BoundingBox, Detection, Point
from kew.queue_region import QueueRegion
from kew.tracker import CentroidTracker


def detection(x: int, y: int) -> Detection:
    """Create a compact detection fixture around a center coordinate."""
    return Detection(BoundingBox(x - 5, y - 5, x + 5, y + 5), 0.9)


class CentroidTrackerTests(unittest.TestCase):
    """Verify stable identities across nearby detections."""

    def test_preserves_nearby_track_identity(self) -> None:
        """Keep an identifier when a person moves a short distance."""
        tracker = CentroidTracker(max_distance=20)
        first_id = tracker.update([detection(20, 20)])[0].id
        self.assertEqual(tracker.update([detection(25, 24)])[0].id, first_id)

    def test_assigns_new_identity_to_distant_detection(self) -> None:
        """Create a new identifier outside the association radius."""
        tracker = CentroidTracker(max_distance=20)
        first_id = tracker.update([detection(20, 20)])[0].id
        self.assertNotEqual(tracker.update([detection(200, 200)])[0].id, first_id)


class QueueRegionTests(unittest.TestCase):
    """Verify polygon-based queue membership."""

    def test_filters_tracks_by_centroid(self) -> None:
        """Include only tracked people whose centers lie inside the polygon."""
        region = QueueRegion((Point(0, 0), Point(100, 0), Point(100, 100), Point(0, 100)))
        tracks = CentroidTracker().update([detection(50, 50), detection(150, 150)])
        self.assertEqual(len(region.filter_tracks(tracks)), 1)

    def test_empty_region_includes_entire_frame(self) -> None:
        """Treat an unconfigured region as the full video frame."""
        self.assertTrue(QueueRegion().contains(Point(1000, 1000)))


if __name__ == "__main__":
    unittest.main()
