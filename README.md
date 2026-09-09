# Kew

Kew detects and tracks people in a live video feed, determines which tracked
people are inside an operator-defined queue region, and publishes an estimated
wait time to a native Tauri desktop application.

The current throughput estimate is deliberately simple. The package boundaries
allow the estimator and centroid tracker to be replaced independently as real
queue observations become available.

## Project layout

```text
src/kew/             Python application and domain logic
  app.py             Video pipeline and CLI
  detector.py        YOLO and OpenCV adapters
  tracker.py         Cross-frame person association
  queue_region.py    Queue polygon membership
  analytics.py       Wait-time estimation
  models.py          Shared domain records
config/default.yaml  Runtime defaults and queue-region coordinates
assets/              Images and intentionally versioned model weights
scripts/train.py     Offline model training
tests/               Hardware-independent Python tests
ui/                  Tauri webview UI (TypeScript/CSS)
src-tauri/           Native Rust shell and IPC commands
```

## Ubuntu setup

Install Tauri's Linux prerequisites first. On current Ubuntu releases:

```bash
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev
```

Then install the project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
npm install
```

## Run locally

Run the detector and Tauri app in separate terminals:

```bash
source .venv/bin/activate
kew --source 0
```

```bash
npm run tauri dev
```

For a video file or headless processing:

```bash
kew --source path/to/video.mp4 --headless
```

Edit `config/default.yaml` to change the model, confidence, service rate, tracking
limits, or queue polygon. An empty `queue_region.vertices` list treats the full
frame as the queue. Coordinates are `[x, y]` video pixels.

The two processes exchange only an atomic JSON snapshot under `runtime/`. Set
`KEW_STATE_PATH` for the Tauri process and use `kew --state-file` when a different
location is needed. Packaging the Python pipeline as a Tauri sidecar is deferred
until its model/runtime distribution strategy is selected.

## Development

```bash
python -m unittest discover -s tests
ruff check .
npm run check
cargo test --manifest-path src-tauri/Cargo.toml
```

Build Linux AppImage and Debian packages with:

```bash
npm run tauri build
```

Train against any Ultralytics dataset configuration with:

```bash
python scripts/train.py path/to/data.yaml
```

Generated training runs are ignored. Keep only intentionally versioned weights in
`assets/models/`; use external artifact storage as the model lifecycle matures.
