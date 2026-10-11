#!/usr/bin/env bash
# Builds dist/tinyfish-growth-app.zip = app.zip + README.md + demo-video.mp4 + launch-post.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"; STAGE="$DIST/stage"
rm -rf "$DIST"; mkdir -p "$STAGE"
# Zip from inside app/ so README.md (run instructions) sits at the root of app.zip
(cd "$ROOT/app" && zip -qr "$STAGE/app.zip" . -x '.venv/*' '.env' 'output/*' '__pycache__/*' '*/__pycache__/*' '*.pyc' '*.DS_Store')
for f in README.md launch-post.md demo-video.mp4; do
  if [ -f "$ROOT/$f" ]; then cp "$ROOT/$f" "$STAGE/"; else echo "WARNING: missing $f"; fi
done
(cd "$STAGE" && zip -qr "$DIST/tinyfish-growth-app.zip" .)
unzip -l "$DIST/tinyfish-growth-app.zip"
# Extra uploads for judging ("how you got there"), submitted alongside the zip
cp "$ROOT/docs/PROCESS.md" "$DIST/PROCESS.md"
printf 'Repo (full history + process log): https://github.com/ThomasParas/AI-Native-talent-hunt-Tinyfish\n' > "$DIST/repo-link.txt"
