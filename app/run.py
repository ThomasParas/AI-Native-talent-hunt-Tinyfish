"""CLI: uv run python run.py [url]   (default: https://www.tinyfish.ai)"""

import asyncio
import json
import sys

from growth_app import pipeline


def emit(ev: dict) -> None:
    t = ev["type"]
    if t in ("step", "agent_progress"):
        print(f"  {'·' if t == 'agent_progress' else '→'} {ev['message']}")
    elif t == "claims":
        print(f"  → {len(ev['claims'])} claims: " + ", ".join(f"{c['id']} ({c['route']})" for c in ev["claims"]))
    elif t == "agent_live":
        print(f"  → live agent view: {ev['url']}")
    elif t == "claim_update" and "status" in ev:
        print(f"  {pipeline.ICON.get(ev['status'], '')} {ev['id']}: {ev['status']}: {ev.get('reasoning', '')}")
    elif t == "done":
        print(f"\nReport: app{ev['report']}")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.tinyfish.ai"
    report = asyncio.run(pipeline.run(url, emit))
    print(json.dumps([{k: e[k] for k in ("primitive", "seconds", "ok")} for e in report["trace"]]))
