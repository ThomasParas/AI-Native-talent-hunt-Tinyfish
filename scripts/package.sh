#!/usr/bin/env bash
# Builds dist/tinyfish-growth-app.zip = app.zip + README.md + demo-video.mp4 + launch-post.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"; STAGE="$DIST/stage"
rm -rf "$DIST"; mkdir -p "$STAGE"
(cd "$ROOT" && zip -qr "$STAGE/app.zip" app -x 'app/.venv/*' 'app/.env' 'app/output/*' '*/__pycache__/*' '*.pyc' '*.DS_Store')
for f in README.md launch-post.md demo-video.mp4; do
  if [ -f "$ROOT/$f" ]; then cp "$ROOT/$f" "$STAGE/"; else echo "WARNING: missing $f"; fi
done
(cd "$STAGE" && zip -qr "$DIST/tinyfish-growth-app.zip" .)
unzip -l "$DIST/tinyfish-growth-app.zip"
