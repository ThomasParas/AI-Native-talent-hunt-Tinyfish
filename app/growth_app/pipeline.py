"""Claim Receipts: route every landing-page claim to the primitive that can prove it.

  Fetch   -> read the landing page as clean text
  Claude  -> extract claims, route each one (outside | funnel)
  Browser -> pixel proof: highlight each claim where it appears on the live page
  Search  -> find outside evidence for 'outside' claims (Fetch reads the top hits)
  Agent   -> walk the signup funnel like a prospect for 'funnel' claims (never submits)
  Claude  -> verdict per claim: verified | contradicted | unverifiable
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

from tinyfish import ProgressEvent, StreamingUrlEvent

from . import llm
from . import primitives as tf

OUTPUT = Path(__file__).resolve().parent.parent / "output"
EVIDENCE_CHARS = 6000  # per-page excerpt sent to the judge

FUNNEL_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"action": {"type": "string"}, "url": {"type": "string"}},
                "required": ["action", "url"],
            },
        },
        "signup_url": {"type": "string"},
        "gate_type": {"type": "string", "enum": ["email_form", "oauth_only", "payment", "contact_sales", "none_found"]},
        "auth_options": {"type": "array", "items": {"type": "string"}},
        "required_fields_visible": {"type": "array", "items": {"type": "string"}},
        "credit_card_requested_before_account": {"type": "boolean"},
        "offer_text_seen": {"type": "array", "items": {"type": "string"}},
        "claim_observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"claim_id": {"type": "string"}, "observation": {"type": "string"}},
                "required": ["claim_id", "observation"],
            },
        },
    },
    "required": ["steps", "signup_url", "gate_type", "credit_card_requested_before_account", "claim_observations"],
}


def funnel_goal(claims: list[llm.Claim]) -> str:
    listed = "\n".join(f"- [{c.id}] {c.claim}" for c in claims)
    return f"""You are a first-time visitor checking this website's signup and pricing claims.

1. From this page, click the main call-to-action that leads to signing up or getting started.
2. Keep clicking only links/buttons that move toward creating an account or seeing pricing/free-tier terms.
3. Stop at the first page that asks the visitor to type information or sign in.

HARD RULES: never type into any field, never submit any form, never click Google/GitHub/SSO sign-in buttons,
never enter payment details, never create an account.

While you go, check these claims and report what you actually observed for each:
{listed}

Return every step you took (action + URL), the signup URL, what kind of gate stopped you, the sign-in options
offered, any required fields visible, whether a credit card was requested before an account exists, and any
offer text (free credits, trials) you saw."""


async def run(url: str, emit: Callable[[dict], None], max_claims: int = 8) -> dict:
    run_id = time.strftime("%Y%m%d-%H%M%S")
    out_dir = OUTPUT / run_id
    trace = tf.Trace()
    host = urlparse(url).netloc

    def step(msg: str) -> None:
        emit({"type": "step", "message": msg})

    def push_trace() -> None:
        emit({"type": "trace", "entries": [e.__dict__ for e in trace.entries]})

    # 1. Fetch reads the landing page
    step(f"Fetch: reading {host}")
    page = await asyncio.to_thread(tf.fetch, [url], trace, "read the landing page as clean text")
    page_text = page["results"][0]["text"]
    push_trace()

    # 2. Claude extracts and routes claims
    step("Claude: extracting checkable claims and routing each to a primitive")
    claims = await asyncio.to_thread(llm.extract_claims, url, page_text, max_claims)
    emit({"type": "claims", "claims": [c.model_dump() for c in claims]})
    results: dict[str, dict] = {c.id: {"claim": c.model_dump(), "primitives": ["Fetch"]} for c in claims}

    def update(claim_id: str, **fields) -> None:
        results[claim_id].update(fields)
        emit({"type": "claim_update", "id": claim_id, **fields})

    # 3a. Browser: pixel proof of every claim as a visitor sees it
    async def browser_proofs() -> None:
        step("Browser: opening a cloud browser to screenshot each claim in place")
        shots = await tf.browser_claim_shots(url, {c.id: c.quote for c in claims}, out_dir, trace, "pixel proof of each claim on the live page")
        for cid, path in shots.items():
            prims = results[cid]["primitives"] + ["Browser"]
            update(cid, screenshot=f"/output/{run_id}/{path.name}" if path else None, primitives=prims)
        push_trace()

    # 3b. Search (+ Fetch) gathers outside evidence, Claude judges
    async def check_outside(c: llm.Claim) -> None:
        try:
            hits = await asyncio.to_thread(tf.search, c.search_query, trace, f"outside evidence for '{c.id}'")
            urls = [h["url"] for h in hits[:3]]
            evidence = [{"url": h["url"], "source": f"Search snippet ({h.get('site_name') or ''})", "text": h.get("snippet") or ""} for h in hits[:5]]
            if urls:
                pages = await asyncio.to_thread(tf.fetch, urls, trace, f"read top results for '{c.id}'")
                evidence += [{"url": r["url"], "source": "Fetch", "text": (r.get("text") or "")[:EVIDENCE_CHARS]} for r in pages.get("results", [])]
            push_trace()
            verdict = await asyncio.to_thread(llm.judge, c, evidence, url)
            update(c.id, primitives=results[c.id]["primitives"] + ["Search", "Fetch"], **verdict.model_dump())
        except Exception as e:
            update(c.id, status="unverifiable", reasoning=f"Evidence lookup failed: {e}", evidence_quote="", source_url="")

    # 3c. Agent walks the funnel once for all funnel claims, Claude judges each
    async def check_funnel(funnel: list[llm.Claim]) -> None:
        if not funnel:
            return
        step(f"Agent: walking the signup funnel to test {len(funnel)} claim(s), stopping before any submit")
        loop = asyncio.get_running_loop()

        def on_event(ev) -> None:
            if isinstance(ev, StreamingUrlEvent):
                loop.call_soon_threadsafe(emit, {"type": "agent_live", "url": ev.streaming_url})
            elif isinstance(ev, ProgressEvent):
                loop.call_soon_threadsafe(emit, {"type": "agent_progress", "message": ev.purpose})

        try:
            result = await asyncio.to_thread(
                tf.agent, url, funnel_goal(funnel), trace, "walk the signup funnel like a prospect",
                on_progress=on_event, output_schema=FUNNEL_SCHEMA,
            )
            push_trace()
            if isinstance(result, str):
                result = json.loads(result)
            emit({"type": "agent_result", "result": result})
            ev = llm.evidence_from_agent(result, (result or {}).get("signup_url") or url)
            verdicts = await asyncio.gather(*(asyncio.to_thread(llm.judge, c, [ev], url) for c in funnel))
            for c, v in zip(funnel, verdicts):
                update(c.id, primitives=results[c.id]["primitives"] + ["Agent"], **v.model_dump())
        except Exception as e:
            push_trace()
            for c in funnel:
                update(c.id, status="unverifiable", reasoning=f"Funnel walk failed: {e}", evidence_quote="", source_url="")

    outside = [c for c in claims if c.route == "outside"]
    funnel = [c for c in claims if c.route == "funnel"]
    await asyncio.gather(browser_proofs(), check_funnel(funnel), *(check_outside(c) for c in outside))

    report = {"run_id": run_id, "url": url, "claims": list(results.values()), "trace": [e.__dict__ for e in trace.entries]}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))
    (out_dir / "report.md").write_text(to_markdown(report))
    emit({"type": "done", "run_id": run_id, "report": f"/output/{run_id}/report.md"})
    push_trace()
    return report


ICON = {"verified": "✅", "contradicted": "❌", "unverifiable": "⚠️"}


def to_markdown(report: dict) -> str:
    lines = [f"# Claim Receipts: {report['url']}", "", f"Run `{report['run_id']}`", "",
             "| | Claim | Verdict | Checked by | Source |", "|---|---|---|---|---|"]
    for r in report["claims"]:
        c, status = r["claim"], r.get("status", "unverifiable")
        src = f"[link]({r['source_url']})" if r.get("source_url") else ""
        lines.append(f"| {ICON.get(status, '')} | {c['claim']} | **{status}**: {r.get('reasoning', '')} | {' + '.join(dict.fromkeys(r['primitives']))} | {src} |")
    lines += ["", "## Primitive trace", "", "| Primitive | Job | Secs | OK | Detail |", "|---|---|---|---|---|"]
    lines += [f"| {e['primitive']} | {e['purpose']} | {e['seconds']} | {e['ok']} | {e['detail'][:80]} |" for e in report["trace"]]
    return "\n".join(lines) + "\n"
