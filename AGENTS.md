# Project context (for Codex / Claude / any coding agent)

Hackathon: AI-Native Talent Hunt, TinyFish track. **Submit by 3:30 PM PDT, Oct 11 2026.**
Role: Founding DevRel & PMM at TinyFish, reporting to Sky Zhang (Head of Growth).

Deliverable: `tinyfish-growth-app.zip` containing `app.zip`, `README.md`, `demo-video.mp4`, `launch-post.md`.
Build it with `scripts/package.sh`.

Rules that shape the code:
- >= 3 TinyFish primitives (Search, Fetch, Agent, Browser, Vault), each doing a job only it suits.
- Workflow a marketer/seller would actually run, end-to-end against ONE real target (not rigged).

Layout:
- `app/` — runnable app (uv, Python 3.12). `app/growth_app/primitives.py` wraps each primitive + trace.
- `docs/tinyfish-llms-full.txt` — full TinyFish API docs. Grep here before guessing SDK signatures.
- `docs/PROCESS.md` — timestamped log of decisions and AI usage (judged). Append as you go.
