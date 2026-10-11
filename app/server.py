"""Web UI: uv run uvicorn server:app --port 8000   then open http://localhost:8000"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from growth_app import pipeline

ROOT = Path(__file__).resolve().parent
pipeline.OUTPUT.mkdir(exist_ok=True)

app = FastAPI(title="Claim Receipts")
app.mount("/output", StaticFiles(directory=pipeline.OUTPUT), name="output")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/run")
async def run(url: str = "https://www.tinyfish.ai") -> StreamingResponse:
    queue: asyncio.Queue = asyncio.Queue()

    async def worker() -> None:
        try:
            await pipeline.run(url, queue.put_nowait)
        except Exception as e:
            queue.put_nowait({"type": "error", "message": str(e)})
        finally:
            queue.put_nowait(None)

    async def stream():
        task = asyncio.create_task(worker())
        try:
            while (ev := await queue.get()) is not None:
                yield f"data: {json.dumps(ev, default=str)}\n\n"
        finally:
            task.cancel()

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
