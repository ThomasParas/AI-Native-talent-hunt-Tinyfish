# Claim Receipts: run instructions

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env            # paste TINYFISH_API_KEY (https://agent.tinyfish.ai/api-keys) and ANTHROPIC_API_KEY
uv sync
uv run python smoke_test.py     # confirms Search, Fetch, Agent, Browser all respond

# Web UI (live Agent view, receipts, primitive trace)
uv run uvicorn server:app --port 8000      # open http://localhost:8000, press "Check claims"

# CLI
uv run python run.py https://www.tinyfish.ai
```

Each run writes `output/<run_id>/report.md`, `report.json` and highlighted claim screenshots.
A full run on tinyfish.ai takes 1.5–2 minutes (the Agent funnel walk is the long pole).
See the top-level README.md for what each primitive does and why.
