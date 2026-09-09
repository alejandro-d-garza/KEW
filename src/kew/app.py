"""Command-line application for Kew's video-processing pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

from kew.analytics import QueueEstimator
from kew.config import Settings, load_settings
from kew.detector import HumanDetector, draw_tracks, frames, open_video
from kew.models import QueueState
from kew.tracker import CentroidTracker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config/default.yaml"


def parse_source(value: str) -> int | str:
    """Interpret an integer as a camera index and any other input as a path."""
    return int(value) if value.isdecimal() else value


def write_state(path: Path, state: QueueState) -> None:
    """Atomically publish queue state for the desktop application."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    ) as temporary_file:
        json.dump(state.as_dict(), temporary_file)
        temporary_path = Path(temporary_file.name)
    os.replace(temporary_path, path)


def build_parser() -> argparse.ArgumentParser:
    """Build the Kew command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--source", default="0", help="camera index or video file")
    parser.add_argument("--model", type=Path, help="override the configured model")
    parser.add_argument("--state-file", type=Path, help="override the configured state file")
    parser.add_argument("--headless", action="store_true", help="disable the OpenCV preview")
    return parser


def run(args: argparse.Namespace, settings: Settings) -> None:
    """Process frames until the source ends or the operator presses Q."""
    import cv2

    model_path = args.model.expanduser().resolve() if args.model else settings.model_path
    state_path = args.state_file.expanduser().resolve() if args.state_file else settings.state_path
    detector = HumanDetector(model_path, settings.confidence_threshold)
    tracker = CentroidTracker(
        settings.tracker_max_distance, settings.tracker_max_missed_frames
    )
    estimator = QueueEstimator(settings.seconds_per_person)
    capture = open_video(parse_source(args.source), settings.frame_rate)
    frame_interval = 1 / settings.frame_rate if settings.frame_rate > 0 else 0
    try:
        for frame in frames(capture):
            started_at = time.monotonic()
            tracks = tracker.update(detector.detect(frame))
            queue_tracks = settings.queue_region.filter_tracks(tracks)
            write_state(
                state_path,
                QueueState(
                    person_count=len(queue_tracks),
                    queue_time_seconds=estimator.estimate_seconds(len(queue_tracks)),
                    updated_at=time.time(),
                ),
            )
            if not args.headless:
                cv2.imshow("Kew - press Q to quit", draw_tracks(frame, queue_tracks))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            time.sleep(max(0, frame_interval - (time.monotonic() - started_at)))
    finally:
        capture.release()
        cv2.destroyAllWindows()


def main() -> int:
    """Load configuration, run Kew, and present concise operational errors."""
    args = build_parser().parse_args()
    try:
        settings = load_settings(args.config.expanduser().resolve(), PROJECT_ROOT)
        run(args, settings)
    except (FileNotFoundError, ImportError, RuntimeError, TypeError, ValueError) as error:
        print(f"kew: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
