"""Shared domain models for detections, tracks, and queue state."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Point:
    """A point in video-frame pixel coordinates."""

    x: float
    y: float


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """An axis-aligned bounding box in video-frame pixel coordinates."""

    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def center(self) -> Point:
        """Return the center point of the box."""
        return Point((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


@dataclass(frozen=True, slots=True)
class Detection:
    """A person detection produced by the object detector."""

    bounds: BoundingBox
    confidence: float


@dataclass(frozen=True, slots=True)
class Track:
    """A detected person associated with a stable identifier."""

    id: int
    bounds: BoundingBox
    confidence: float
    missed_frames: int = 0


@dataclass(frozen=True, slots=True)
class QueueState:
    """The serializable state consumed by the desktop application."""

    person_count: int
    queue_time_seconds: float
    updated_at: float

    def as_dict(self) -> dict[str, int | float]:
        """Return a JSON-compatible representation of this state."""
        return asdict(self)
