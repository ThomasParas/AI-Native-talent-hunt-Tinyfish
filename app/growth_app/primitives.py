"""Thin wrappers around the live TinyFish primitives.

Each wrapper does one job and records a trace entry (primitive, purpose, latency)
so the UI/README can show exactly which primitive handled which step.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from tinyfish import CompleteEvent, TinyFish

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_client: TinyFish | None = None


def client() -> TinyFish:
    global _client
    if _client is None:
        if not os.getenv("TINYFISH_API_KEY"):
            raise RuntimeError("TINYFISH_API_KEY is not set. Copy .env.example to .env and add your key.")
        _client = TinyFish()
    return _client


@dataclass
class TraceEntry:
    primitive: str
    purpose: str
    seconds: float
    ok: bool
    detail: str = ""


@dataclass
class Trace:
    entries: list[TraceEntry] = field(default_factory=list)

    def add(self, primitive: str, purpose: str, started: float, ok: bool, detail: str = "") -> None:
        self.entries.append(TraceEntry(primitive, purpose, round(time.time() - started, 1), ok, detail))


def search(query: str, trace: Trace, purpose: str, **kwargs: Any) -> list[dict[str, Any]]:
    """Search: discover URLs/signals we don't already know about."""
    t = time.time()
    try:
        res = client().search.query(query, **kwargs)
        results = [r.model_dump() if hasattr(r, "model_dump") else dict(r) for r in res.results]
        trace.add("Search", purpose, t, True, f"{len(results)} results for {query!r}")
        return results
    except Exception as e:
        trace.add("Search", purpose, t, False, str(e))
        raise


def fetch(urls: list[str], trace: Trace, purpose: str, **kwargs: Any) -> dict[str, Any]:
    """Fetch: pull clean text from up to 10 known URLs in one call."""
    t = time.time()
    try:
        res = client().fetch.get_contents(urls=urls[:10], **kwargs)
        data = res.model_dump() if hasattr(res, "model_dump") else dict(res)
        trace.add("Fetch", purpose, t, True, f"{len(data.get('results', []))} pages, {len(data.get('errors', []) or [])} errors")
        return data
    except Exception as e:
        trace.add("Fetch", purpose, t, False, str(e))
        raise


def agent(url: str, goal: str, trace: Trace, purpose: str, on_progress=None, **kwargs: Any) -> Any:
    """Agent: execute a multi-step natural-language goal on a live site (streams progress)."""
    t = time.time()
    result = None
    try:
        with client().agent.stream(url=url, goal=goal, **kwargs) as stream:
            for event in stream:
                if on_progress is not None:
                    on_progress(event)
                if isinstance(event, CompleteEvent):
                    result = event.result_json
        # COMPLETED != goal succeeded: check for block signals.
        blocked = any(s in str(result).lower() for s in ("captcha", "access denied", "blocked"))
        trace.add("Agent", purpose, t, not blocked, "possible block signal in result" if blocked else "")
        return result
    except Exception as e:
        trace.add("Agent", purpose, t, False, str(e))
        raise


_HIGHLIGHT_JS = """el => {
  el.style.outline = '4px solid #ff3b6b';
  el.style.outlineOffset = '4px';
  el.style.background = 'rgba(255, 59, 107, 0.12)';
  el.scrollIntoView({block: 'center'});
}"""


async def browser_claim_shots(url: str, quotes: dict[str, str], out_dir: Path, trace: Trace, purpose: str) -> dict[str, Path | None]:
    """Browser: one cloud session; find each claim's exact text on the live page, highlight it, screenshot it."""
    from playwright.async_api import async_playwright

    t = time.time()
    shots: dict[str, Path | None] = {}
    try:
        session = client().browser.sessions.create(url=url)
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(session.cdp_url)
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            await page.set_viewport_size({"width": 1280, "height": 800})
            if not page.url.startswith("http"):
                await page.goto(url, wait_until="domcontentloaded")
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            out_dir.mkdir(parents=True, exist_ok=True)
            for claim_id, quote in quotes.items():
                shots[claim_id] = None
                try:
                    loc = page.get_by_text(quote, exact=False).first
                    await loc.wait_for(state="attached", timeout=4000)
                    await loc.evaluate(_HIGHLIGHT_JS)
                    await page.wait_for_timeout(300)
                    path = out_dir / f"claim-{claim_id}.png"
                    await page.screenshot(path=str(path))
                    shots[claim_id] = path
                    await loc.evaluate("el => { el.style.outline = ''; el.style.background = ''; }")
                except Exception:
                    continue  # claim text not rendered as a single visible node; recorded as "not located"
            await browser.close()
        found = sum(1 for v in shots.values() if v)
        trace.add("Browser", purpose, t, True, f"located {found}/{len(quotes)} claims on the live page")
        return shots
    except Exception as e:
        trace.add("Browser", purpose, t, False, str(e))
        return shots


async def browser_screenshot(url: str, out_path: Path, trace: Trace, purpose: str, full_page: bool = True) -> Path:
    """Browser: deterministic CDP control of a remote browser (e.g. evidence screenshots)."""
    from playwright.async_api import async_playwright

    t = time.time()
    try:
        session = client().browser.sessions.create(url=url)
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(session.cdp_url)
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            if page.url in ("", "about:blank"):
                await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(out_path), full_page=full_page)
            await browser.close()
        trace.add("Browser", purpose, t, True, str(out_path.name))
        return out_path
    except Exception as e:
        trace.add("Browser", purpose, t, False, str(e))
        raise
