# Run instructions

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env          # add your TINYFISH_API_KEY (free credits: https://agent.tinyfish.ai)
uv sync
uv run playwright install chromium
uv run python smoke_test.py   # confirms Search, Fetch, Agent, Browser all respond
```
