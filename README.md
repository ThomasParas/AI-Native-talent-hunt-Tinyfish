# 🧾 Claim Receipts

**Paste a landing page. Get a receipt for every claim on it.**

Claim Receipts reads a landing page, pulls out the claims a buyer would make a decision on (benchmarks, prices,
free offers, "no credit card", "the only platform that…"), and then **checks each one with the TinyFish primitive
that can actually prove it**. Every claim ends in one of three explicit states, each tied to a source and a screenshot:

| State | Meaning |
|---|---|
| ✅ **verified** | Evidence directly supports the claim |
| ❌ **contradicted** | Evidence directly conflicts with the claim |
| ⚠️ **unverifiable** | Evidence is missing or only repeats the claim. The app says so instead of guessing |

## Who it's for

- **Product marketers** checking their own copy before a launch ("can we still say that?")
- **Sellers** prepping for a call ("is the competitor's 'free tier, no card' actually true?")
- **DevRel / growth teams** who want proof attached to every number on the homepage

## We ran it on ourselves first

The target for this build is **TinyFish's own homepage, [tinyfish.ai](https://www.tinyfish.ai)**. It isn't a sandbox
or a rigged page. This is the run in `demo-video.mp4` (run `20261011-131046`, ~95 seconds end to end):

| | Claim on tinyfish.ai | What the evidence said | Checked by |
|---|---|---|---|
| ✅ | 89.9% overall on Online-Mind2Web | Benchmarks page says 89.9%; the independent Steel leaderboard says 90.0% | Search + Fetch |
| ✅ | 81.9% on hard tasks vs Operator 43.2%, Claude 32.4% | Hacker News launch post has the split; Steel leaderboard corroborates the Claude figure. Verdict notes the post is from a TinyFish employee | Search + Fetch |
| ✅ | All 300 benchmark runs are open-sourced | Public spreadsheet, plus a Hacker News user who checked it | Search + Fetch |
| ✅ | New users get $8 free credit | The **Agent** walked to pricing → sign-up and saw "Get $8 free"; stopped at the email form, no card requested | **Agent** |
| ✅ | Search and Fetch are free on every plan | The Agent reached pricing: Search $0.00/request, Fetch $0.00/url | **Agent** |
| ✅ | Agent $0.016/step, Browser $0.002/min | Matches the live pricing page | **Agent** |
| ⚠️ | "The only platform" with all four behind one key | One key: independently confirmed. "Only": no independent comparison | Search + Fetch |
| ⚠️ | Search hits Google's live index, never cached | Only TinyFish's own page says so; no independent source | Search + Fetch |

Every claim also got a **Browser** pass that tries to highlight it on the live page. That located 4 of 8 this run;
the rest are marked "not located" rather than faked.

### Same target, four runs

We ran tinyfish.ai four times in a row. The *shape* holds and the borderline calls move, which is what you want from
a tool that weighs live evidence:

| Run | ✅ verified | ❌ contradicted | ⚠️ unverifiable | Flagged 89.9% vs blog's "40 failures of 300" (≈86.7%) |
|---|---|---|---|---|
| 12:54 | 5 | 0 | 3 | yes |
| 13:05 | 5 | 0 | 3 | yes |
| 13:08 | 6 | 0 | 2 | no |
| 13:10 (video) | 6 | 0 | 2 | no |

The funnel claims (Agent) and "the only platform" (⚠️) came out the same in every run. The benchmark claims swing
between ✅ and ⚠️ depending on which sources Search surfaces that minute. In two runs the judge caught that the
89.9% headline and a TinyFish blog post's "40 failures out of 300" don't agree (~86.7%). A tool that can say
"I couldn't prove this" is one you can trust when it says ✅.

## Which primitive does which job, and why that one

Each claim is **routed** by *how it can be proven*. The routing is the product, not an afterthought.

| Step | Primitive | Its job here | Why this primitive and not another |
|---|---|---|---|
| 1 | **Fetch** | Read the landing page as clean text for claim extraction; read the top search hits as evidence | Rendered page → clean markdown in ~1s, up to 10 URLs per call, free. Running an Agent just to *read* would be slow and metered. |
| 2 | **Search** | Find independent evidence for "outside" claims (benchmarks, customer results, exclusivity) | Those claims are about things that live on *other* sites. Only Search discovers URLs we don't know yet (~0.5s, structured JSON, free). |
| 3 | **Agent** | Walk the sign-up / pricing funnel **like a prospect** to test "funnel" claims (free credit, no card, prices) | These claims can only be tested by *acting*: clicking CTAs, following the flow, seeing what the gate asks for. One goal-based run with `output_schema` returns per-claim observations, and its live `streaming_url` is embedded in the UI. |
| 4 | **Browser** | Open one cloud browser, find each claim's text on the live page, highlight it, screenshot it | Pixel proof of *what the visitor actually saw*. Fetch returns text, not pixels, and the Agent decides its own path. Highlighting an exact DOM node needs deterministic Playwright/CDP control. |
| — | Claude (`claude-opus-5-5`) | Extract + route claims; judge evidence → verdict | Claude never browses. Every fact it judges came from a TinyFish primitive. |

```
landing page URL
  └─ Fetch ── page text ──► Claude: extract claims, route each one
        ├─ Browser  → highlight + screenshot every claim on the live page         (all claims)
        ├─ Search → Fetch top hits → Claude verdict                               ("outside" claims)
        └─ Agent  → walk signup/pricing, stop at first gate → Claude verdict      ("funnel" claims)
  └─ receipts: verified / contradicted / unverifiable, each with source + screenshot
```

Browser, Agent, and every Search chain run **in parallel**, and results stream into the UI as each claim resolves.

## Guardrail: the agent acts, but never commits

The funnel goal hard-codes: **never type into a field, never submit a form, never click Google/GitHub/SSO, never
enter payment details, never create an account. Stop at the first gate.** It reports what the gate asked for
(`gate_type`, `credit_card_requested_before_account`, `required_fields_visible`). Point it at a competitor and you
won't spam their sales team.

## Run it

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), a [TinyFish key](https://agent.tinyfish.ai/api-keys)
(free credits on signup) and an [Anthropic key](https://console.anthropic.com/settings/keys).

```bash
unzip app.zip && cd app
cp .env.example .env                 # paste TINYFISH_API_KEY and ANTHROPIC_API_KEY
uv sync
uv run python smoke_test.py          # 1 call to each primitive: Search, Fetch, Agent, Browser
uv run uvicorn server:app --port 8000   # web UI → http://localhost:8000
uv run python run.py https://www.tinyfish.ai   # or the CLI
```

Each run writes `output/<run_id>/report.md`, `report.json`, and one highlighted screenshot per located claim.

**Cost per run (approximate):** Search + Fetch are free. One Agent funnel walk (~15–20 steps × $0.016 ≈ $0.30),
one Browser session (~30s, under $0.01), plus about 10 Claude calls.

## Code map

| File | What it does |
|---|---|
| `app/growth_app/pipeline.py` | The claim router: orchestration, funnel goal + `output_schema`, report writer |
| `app/growth_app/primitives.py` | Thin wrappers over Search / Fetch / Agent / Browser, each logging a trace entry (primitive, job, latency) |
| `app/growth_app/llm.py` | Claude: claim extraction and verdicts via `messages.parse` + Pydantic |
| `app/server.py`, `app/static/index.html` | FastAPI + SSE stream; receipts, live Agent view, primitive trace |
| `app/run.py`, `app/smoke_test.py` | CLI and four-primitive health check |

## Honest limits

- Verdicts are only as good as the evidence the web holds. That's why "unverifiable" is a first-class state.
- Self-reported sources (the target's own pages) are allowed but weighed below independent ones, and the verdict says so.
- Browser may not locate a claim whose text is split across many DOM nodes; the receipt then says "not located".
- Logged-in claims ("your dashboard shows…") are out of scope today. TinyFish Vault + Browser Context Profiles is the next step.

## What's next

Batch mode across a competitor set · scheduled re-checks with TinyFish **Monitor** (alert when a claim flips) ·
export receipts to a launch-review doc.
