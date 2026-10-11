# Process Log

Judging covers the result *and how we got there*. Add short, timestamped entries as we work.

## Problem
TinyFish (Sky Zhang, Head of Growth): ship an agent-led growth app on live TinyFish primitives + launch package
(app.zip, README.md, demo-video.mp4, launch-post.md). Due 3:30 PM PDT.

## Log

| Time | What we did | AI tool / prompt approach | Outcome |
|---|---|---|---|
| 12:15 | Read TinyFish docs (llms.txt, For Coding Agents) and the participant handbook | Claude Code + Firecrawl scrape | Saved full API docs to `docs/tinyfish-llms-full.txt` |
| 12:20 | Scaffolded repo: uv Python app, primitive wrappers with per-step trace, smoke test, packaging script | Claude Code; introspected SDK signatures instead of guessing | `app/`, `scripts/package.sh` |
| 12:35 | Mapped existing TinyFish customer stories + cookbook to avoid duplicating them | Claude Code + Firecrawl (summaries of 6 stories, cookbook, docs, Pulse) | `docs/tinyfish-landscape.md`; dropped battlecard + lead-outreach ideas (already covered) |
| 12:50 | Chose workflow B "Claim Receipts" + funnel walk from A; target = tinyfish.ai homepage | Compared A vs B on primitive fit, demo reliability, abuse risk, reuse | Claim router: Fetch reads page, Browser pixel proof, Search outside evidence, Agent walks funnel (stops before pay/submit); Claude judges |

## Decisions and trade-offs
- Workflow B over A: every primitive has an essential job, failures degrade to "unverifiable" instead of breaking the demo, no risk of submitting real forms.
- Target is TinyFish's own homepage: "we went first on ourselves" is credible DevRel and avoids looking adversarial.
- Python + uv + official `tinyfish` SDK (0.9.0): SDK handles SSE, retries, typed responses.
- Browser primitive via `client.browser.sessions.create` + Playwright `connect_over_cdp`.
- Every primitive call records a trace entry, so the demo can show which primitive did which job.

## What we'd do with more time
-
