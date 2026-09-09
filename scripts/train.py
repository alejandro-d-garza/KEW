"""Train a YOLO model from an existing Ultralytics dataset configuration."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build the model-training argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="path to an Ultralytics data.yaml file")
    parser.add_argument("--base-model", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--image-size", type=int, default=640)
    parser.add_argument("--output", type=Path, default=Path("assets/models/best.pt"))
    return parser


def main() -> None:
    """Train and save a model, selecting CUDA when it is available."""
    import torch
    from ultralytics import YOLO

    args = build_parser().parse_args()
    if not args.data.is_file():
        raise SystemExit(f"Dataset configuration not found: {args.data}")
    model = YOLO(args.base_model)
    model.train(
        data=str(args.data.resolve()),
        epochs=args.epochs,
        imgsz=args.image_size,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(args.output))


if __name__ == "__main__":
    main()
