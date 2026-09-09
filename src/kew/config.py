"""Configuration loading for Kew's processing pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from kew.models import Point
from kew.queue_region import QueueRegion


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated runtime settings loaded from YAML."""

    model_path: Path
    confidence_threshold: float
    frame_rate: float
    seconds_per_person: float
    tracker_max_distance: float
    tracker_max_missed_frames: int
    state_path: Path
    queue_region: QueueRegion


def load_settings(path: Path, project_root: Path) -> Settings:
    """Load settings and resolve relative paths from the project root."""
    with path.open(encoding="utf-8") as config_file:
        data: dict[str, Any] = yaml.safe_load(config_file) or {}
    detector = data.get("detector", {})
    tracker = data.get("tracker", {})
    analytics = data.get("analytics", {})
    output = data.get("output", {})
    vertices = tuple(Point(*vertex) for vertex in data.get("queue_region", {}).get("vertices", []))
    return Settings(
        model_path=_resolve(project_root, detector.get("model", "assets/models/best.pt")),
        confidence_threshold=float(detector.get("confidence_threshold", 0.65)),
        frame_rate=float(detector.get("frame_rate", 10)),
        seconds_per_person=float(analytics.get("seconds_per_person", 60)),
        tracker_max_distance=float(tracker.get("max_distance", 80)),
        tracker_max_missed_frames=int(tracker.get("max_missed_frames", 5)),
        state_path=_resolve(project_root, output.get("state_file", "runtime/queue_state.json")),
        queue_region=QueueRegion(vertices),
    )


def _resolve(project_root: Path, value: str) -> Path:
    """Resolve a configured filesystem path without depending on the working directory."""
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (project_root / path).resolve()
