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
| 12:55 | Smoke test: all 4 primitives live (Search 0.4s, Fetch 1.0s, Agent 11.9s, Browser 15.3s) + Claude key OK | `smoke_test.py` | Unblocked to build the claim router |
| 13:20 | Built claim router (Fetch->Claude->Browser/Search/Agent->Claude) + CLI + web UI; first real run on tinyfish.ai | Claude Code; Claude Opus 5.5 via `messages.parse` + Pydantic for claims/verdicts; security hook forced DOM-safe rendering (no innerHTML) | 8 claims in ~90s: 5 verified, 3 unverifiable. Found the 89.9% Mind2Web figure vs a blog's 40/300 failures (~86.7%) |
| 13:15 | README + launch post from real run; scripted demo recording (Playwright drives the real UI, ffmpeg -> mp4); reviewed frames | Claude Code reviewed extracted video frames to QA | Found + fixed: broken claim images (`safeUrl(null)` resolved to `/null`), locator fallback to numeric tokens; verdicts vary run-to-run, so README now mirrors the recorded run |
| 13:20 | Final demo take recorded (98s); 4 runs tallied; README + post aligned to real numbers | Claude Code QA'd video frames; kept post 4 per user | Runs: 5–6 ✅ / 2–3 ⚠️ / 0 ❌; 86.7% flag in 2 of 4 runs, disclosed in README |

## Decisions and trade-offs
- Workflow B over A: every primitive has an essential job, failures degrade to "unverifiable" instead of breaking the demo, no risk of submitting real forms.
- Target is TinyFish's own homepage: "we went first on ourselves" is credible DevRel and avoids looking adversarial.
- Python + uv + official `tinyfish` SDK (0.9.0): SDK handles SSE, retries, typed responses.
- Browser primitive via `client.browser.sessions.create` + Playwright `connect_over_cdp`.
- Every primitive call records a trace entry, so the demo can show which primitive did which job.

## What we'd do with more time
- Reduce verdict variance: cache Search results per run and judge with several samples, reporting agreement.
- Batch mode across a competitor set; scheduled re-checks with TinyFish Monitor.
- Browser locator that handles text split across many DOM nodes (currently ~4/8 located).
