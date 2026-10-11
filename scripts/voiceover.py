"""Add an ElevenLabs voiceover to demo-video.mp4, one line per on-screen beat.

    python3 scripts/voiceover.py            # needs ELEVENLABS_API_KEY in app/.env

Keeps the silent original as dist/demo-video-silent.mp4 (first run only).
"""

import json
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "demo-video.mp4"
SILENT = ROOT / "dist" / "demo-video-silent.mp4"
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # "George", an ElevenLabs default voice available on the free tier
MODEL = "eleven_multilingual_v2"
GAP = 0.3  # minimum silence between lines

# (start second, line): timed to the recorded run in the video
SCRIPT = [
    (0.5, "This is Claim Receipts, built on TinyFish. Paste a landing page, and it fact-checks every claim a buyer "
          "would act on. We're running it on our own homepage."),
    (11.5, "Fetch reads the page. Claude pulls out eight claims, and routes each one to the primitive that can "
           "actually prove it. Search goes hunting for outside evidence."),
    (22.5, "For funnel claims, like eight dollars free with no card, the TinyFish Agent walks the site like a "
           "prospect. That's its live browser. It reaches the sign-up page, but it never types, submits, or signs in."),
    (41.0, "Now it's on the pricing page, checking that Search and Fetch really cost zero. Meanwhile, a cloud "
           "Browser opens the homepage and highlights each claim exactly where a visitor sees it. Every receipt "
           "shows which primitives checked it."),
    (57.0, "On the left, verdicts land as evidence comes in. The benchmark claims check out against an "
           "independent leaderboard, and the judge notes when a source is our own."),
    (71.5, "The agent's done. Final tally: six verified, zero contradicted, two it couldn't prove. Here's the "
           "proof for one claim, captured from the live page."),
    (85.0, "And the two warnings? Nobody independent says we're the only platform with all four primitives. "
           "That's the point. Run it on your homepage before your next launch."),
]


def env_key() -> str:
    for line in (ROOT / "app" / ".env").read_text().splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("ELEVENLABS_API_KEY missing from app/.env")


def tts(text: str, out: Path, key: str) -> None:
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": MODEL}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        out.write_bytes(r.read())


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> None:
    key = env_key()
    SILENT.parent.mkdir(exist_ok=True)
    if not SILENT.exists():
        shutil.copy(VIDEO, SILENT)
    total = duration(SILENT)
    tmp = Path(tempfile.mkdtemp(prefix="voiceover-"))

    clips, cursor = [], 0.0
    for i, (start, text) in enumerate(SCRIPT):
        path = tmp / f"line{i}.mp3"
        tts(text, path, key)
        start = max(start, cursor + GAP)
        length = duration(path)
        cursor = start + length
        clips.append((start, path))
        flag = "  <-- runs past video end" if cursor > total else ""
        print(f"line {i}: {start:5.1f}s -> {cursor:5.1f}s ({length:.1f}s){flag}")

    inputs, filters = ["-i", str(SILENT)], []
    for i, (start, path) in enumerate(clips, start=1):
        inputs += ["-i", str(path)]
        ms = int(start * 1000)
        filters.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(1, len(clips) + 1))
    filters.append(f"{mix}amix=inputs={len(clips)}:normalize=0,apad[aout]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-t", f"{total:.2f}", "-movflags", "+faststart", str(VIDEO)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {VIDEO} ({total:.1f}s)")


if __name__ == "__main__":
    main()
