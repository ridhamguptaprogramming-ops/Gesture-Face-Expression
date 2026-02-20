# Gesture + Face Expression Controlled AI System

This project is a Python MVP for:

- Camera input
- Hand gesture detection
- Face expression detection
- Gesture/expression to action mapping
- OS/browser actions

## Features

- `MediaPipe Hands` for gesture recognition (`open_palm`, `thumbs_up`, `fist`)
- `MediaPipe Face Mesh` heuristics for expression recognition (`smile`, `surprised`)
- Config-driven mapping in `config/mappings.json`
- Cooldown + confidence threshold gating
- State machine: `IDLE`, `ARMED`, `EXECUTE`

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py --config config/mappings.json
```

Press `q` to stop.

## Default Mapping

- `open_palm` -> `switch_window` (`alt+tab`)
- `thumbs_up` -> `open_website`
- `smile` -> `capture_photo` (saved in `captures/`)
- `surprised` -> `toggle_armed`

## Configure Actions

Edit `config/mappings.json`.

Example action entry:

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

## Notes

- On macOS, give camera and Accessibility permissions to Terminal/Python for keypress actions.
- Gesture and expression heuristics vary by camera angle and lighting; tune thresholds in code/config for your setup.

