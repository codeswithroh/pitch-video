#!/usr/bin/env bash
# One-time toolbox setup, shared by every project: ~/.cache/pitch-video
# Idempotent: re-running only fills in what is missing.
set -euo pipefail
TB="${PITCH_VIDEO_HOME:-$HOME/.cache/pitch-video}"
mkdir -p "$TB"
cd "$TB"

need() { command -v "$1" >/dev/null 2>&1 || { echo "MISSING: $1 ($2)"; MISSING=1; }; }
MISSING=0
need ffmpeg "brew install ffmpeg"
need ffprobe "brew install ffmpeg"
need whisper-cli "brew install whisper-cpp"
need node "brew install node"
need python3 "brew install python"
[ "$MISSING" = 1 ] && { echo "Install the missing tools above, then re-run."; exit 1; }

# Python venv: numpy for SFX/analysis, mediapipe + opencv for face framing and the lip-sync check.
if [ ! -x venv/bin/python ]; then python3 -m venv venv; fi
venv/bin/python -c "import numpy, mediapipe, cv2" 2>/dev/null || venv/bin/pip install -q numpy mediapipe opencv-python-headless

# Node: Playwright renders overlays/animations and films the app.
if [ ! -d node_modules/playwright ]; then
  [ -f package.json ] || echo '{"name":"pitch-video-toolbox","private":true,"type":"module"}' > package.json
  npm i -s playwright >/dev/null
fi
npx -y playwright install chromium >/dev/null

# Models.
[ -s ggml-small.en.bin ] || curl -sL -o ggml-small.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin
[ -s face_landmarker.task ] || curl -sL -o face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

echo "toolbox ready: $TB"
echo "PY=$TB/venv/bin/python"
