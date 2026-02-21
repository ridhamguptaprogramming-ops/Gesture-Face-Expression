# Gesture + Face Expression Controlled AI System

Python MVP for real-time camera control using:

- Hand gestures
- Face expressions
- Configurable action mapping

## What It Does

- Detects hand gestures with `MediaPipe Hands`:
  - `open_palm`
  - `thumbs_up`
  - `fist`
- Detects face expressions with `MediaPipe Face Mesh` heuristics:
  - `smile`
  - `surprised`
- Maps detections to actions from `config/mappings.json`
- Uses cooldown and confidence threshold controls
- Runs a simple state machine: `IDLE`, `ARMED`, `EXECUTE`

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make run
```

Press `q` to quit.

## Make Targets

```bash
make install   # install dependencies
make run       # run app
make test      # run unit tests
make clean     # remove local cache/captures
```

## Default Controls

- `open_palm` -> `switch_window` (`alt+tab`)
- `thumbs_up` -> `open_website` (default: Google)
- `smile` -> `capture_photo` (saves to `captures/`)
- `surprised` -> `toggle_armed` (`ARMED` <-> `IDLE`)

## Configure Mappings

Edit `config/mappings.json`.

Example:

```json
"thumbs_up": {
  "action": "open_website",
  "params": {
    "url": "https://openai.com"
  }
}
```

Supported actions:

- `open_website`
- `switch_window`
- `capture_photo`
- `print_message`
- `toggle_armed`

## Project Layout

```text
run.py
config/mappings.json
src/gesture_face_ai/
  main.py         # app loop
  camera.py       # camera wrapper
  gesture.py      # hand gesture detector
  expression.py   # facial expression detector
  mapper.py       # cooldown/threshold/state mapping
  actions.py      # action execution
  config.py       # config loading/validation
tests/test_mapper.py
```

## macOS Permissions

For full behavior on macOS:

- Allow camera access for Terminal/Python.
- Allow Accessibility access for Terminal/Python (needed for keypress actions like `alt+tab`).

## Troubleshooting

- `ModuleNotFoundError: cv2`:
  - Run `pip install -r requirements.txt`.
- Camera fails to open:
  - Try changing `global.camera_index` in `config/mappings.json` (for example `0` to `1`).
- Gestures trigger too often:
  - Increase `global.cooldown_ms`.
- Gesture/expression not detected reliably:
  - Improve lighting and face/hand framing.
  - Adjust classifier thresholds in code if needed.
