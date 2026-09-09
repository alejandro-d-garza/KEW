"""Human detection and video capture adapters."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from kew.models import BoundingBox, Detection, Track


def _opencv() -> Any:
    """Import OpenCV only when video processing is requested."""
    import cv2

    return cv2


class HumanDetector:
    """Lazy-loading Ultralytics adapter for a human-detection model."""

    def __init__(self, model_path: Path, confidence_threshold: float) -> None:
        """Configure detection without loading the model during application startup."""
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._model: Any | None = None

    def _load_model(self) -> Any:
        """Load and cache the configured model."""
        if self._model is None:
            if not self.model_path.is_file():
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            from ultralytics import YOLO

            self._model = YOLO(str(self.model_path))
        return self._model

    def detect(self, frame: Any) -> list[Detection]:
        """Return detections above the configured confidence threshold."""
        detections: list[Detection] = []
        for result in self._load_model()(frame, verbose=False):
            for box in result.boxes:
                confidence = float(box.conf[0])
                if confidence < self.confidence_threshold:
                    continue
                coordinates = (int(value) for value in box.xyxy[0])
                detections.append(Detection(BoundingBox(*coordinates), confidence))
        return detections


def open_video(source: int | str, frame_rate: float) -> Any:
    """Open a camera index or video path and fail with an actionable error."""
    cv2 = _opencv()
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Could not open video source: {source}")
    if frame_rate > 0:
        capture.set(cv2.CAP_PROP_FPS, frame_rate)
    return capture


def frames(capture: Any) -> Iterator[Any]:
    """Yield frames from a capture until its stream ends."""
    while True:
        success, frame = capture.read()
        if not success:
            return
        yield frame


def draw_tracks(frame: Any, tracks: list[Track]) -> Any:
    """Draw tracked people and identifiers onto a frame in place."""
    cv2 = _opencv()
    for track in tracks:
        bounds = track.bounds
        cv2.rectangle(frame, (bounds.x1, bounds.y1), (bounds.x2, bounds.y2), (0, 200, 80), 2)
        cv2.putText(
            frame,
            f"person #{track.id}",
            (bounds.x1, max(20, bounds.y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 200, 80),
            1,
            cv2.LINE_AA,
        )
    return frame
