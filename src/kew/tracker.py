"""Lightweight person tracking across adjacent video frames."""

from __future__ import annotations

from math import hypot

from kew.models import Detection, Track


class CentroidTracker:
    """Associate detections by nearest centroid with bounded track persistence."""

    def __init__(self, max_distance: float = 80, max_missed_frames: int = 5) -> None:
        """Configure spatial matching and stale-track removal."""
        if max_distance <= 0 or max_missed_frames < 0:
            raise ValueError("tracker limits must be positive")
        self.max_distance = max_distance
        self.max_missed_frames = max_missed_frames
        self._tracks: dict[int, Track] = {}
        self._next_id = 1

    def update(self, detections: list[Detection]) -> list[Track]:
        """Match current detections to tracks and return visible tracks."""
        unmatched_tracks = set(self._tracks)
        visible: list[Track] = []
        for detection in detections:
            track_id = self._nearest_track(detection, unmatched_tracks)
            if track_id is None:
                track_id = self._next_id
                self._next_id += 1
            else:
                unmatched_tracks.remove(track_id)
            track = Track(track_id, detection.bounds, detection.confidence)
            self._tracks[track_id] = track
            visible.append(track)

        for track_id in unmatched_tracks:
            previous = self._tracks[track_id]
            missed = previous.missed_frames + 1
            if missed > self.max_missed_frames:
                del self._tracks[track_id]
            else:
                self._tracks[track_id] = Track(
                    previous.id, previous.bounds, previous.confidence, missed
                )
        return visible

    def _nearest_track(self, detection: Detection, candidates: set[int]) -> int | None:
        """Return the closest eligible track identifier for a detection."""
        center = detection.bounds.center
        distances = (
            (
                hypot(center.x - self._tracks[track_id].bounds.center.x,
                      center.y - self._tracks[track_id].bounds.center.y),
                track_id,
            )
            for track_id in candidates
        )
        eligible = [item for item in distances if item[0] <= self.max_distance]
        return min(eligible)[1] if eligible else None
