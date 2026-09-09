"""Operator-defined queue-region geometry."""

from __future__ import annotations

from dataclasses import dataclass

from kew.models import Point, Track


@dataclass(frozen=True, slots=True)
class QueueRegion:
    """A polygon delimiting the part of a frame considered to be the queue."""

    vertices: tuple[Point, ...] = ()

    def contains(self, point: Point) -> bool:
        """Return whether a point lies inside the polygon using ray casting."""
        if not self.vertices:
            return True
        inside = False
        previous = self.vertices[-1]
        for current in self.vertices:
            crosses = (current.y > point.y) != (previous.y > point.y)
            if crosses:
                edge_x = (previous.x - current.x) * (point.y - current.y) / (
                    previous.y - current.y
                ) + current.x
                if point.x < edge_x:
                    inside = not inside
            previous = current
        return inside

    def filter_tracks(self, tracks: list[Track]) -> list[Track]:
        """Return tracks whose bounding-box centers are in this region."""
        return [track for track in tracks if self.contains(track.bounds.center)]
