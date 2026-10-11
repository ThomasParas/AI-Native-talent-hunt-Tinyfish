"""Record demo-video.mp4: drives the real web UI through one live run and screen-records it.

    (terminal 1) cd app && uv run uvicorn server:app --port 8000
    (terminal 2) cd app && uv run python ../scripts/record_demo.py
"""

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
TARGET = sys.argv[1] if len(sys.argv) > 1 else "https://www.tinyfish.ai"
W, H = 1440, 900


async def main() -> None:
    video_dir = ROOT / "dist" / "video"
    shutil.rmtree(video_dir, ignore_errors=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(video_dir), record_video_size={"width": W, "height": H})
        page = await ctx.new_page()
        await page.goto("http://localhost:8000")
        await page.wait_for_timeout(2500)
        await page.fill("#url", "")
        await page.type("#url", TARGET, delay=60)
        await page.wait_for_timeout(800)
        await page.click("#go")
        # Live run: wait for the pipeline to finish (Agent funnel walk is the long pole).
        await page.wait_for_function("document.querySelector('#log')?.innerText.includes('Done.')", timeout=300_000)
        await page.wait_for_timeout(2000)
        # Tour the receipts: scroll the claims, open one screenshot full size.
        shot = page.locator(".shot").first
        if await shot.count():
            await shot.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            await shot.click()
            await page.wait_for_timeout(3500)
            await shot.click()
        for _ in range(6):
            await page.mouse.wheel(0, 450)
            await page.wait_for_timeout(1200)
        await page.locator("#trace").scroll_into_view_if_needed()
        await page.wait_for_timeout(4000)
        await ctx.close()
        await browser.close()
    webm = next(video_dir.glob("*.webm"))
    out = ROOT / "demo-video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-movflags", "+faststart", str(out)], check=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    asyncio.run(main())
