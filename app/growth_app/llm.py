"""Claude: turns page text into routed claims, and evidence into verdicts.

Claude never browses. Every fact it judges arrives from a TinyFish primitive.
"""

from __future__ import annotations

import json
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

MODEL = "claude-opus-5-5"
_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


class Claim(BaseModel):
    id: str = Field(description="short slug, e.g. 'mind2web-score'")
    claim: str = Field(description="the claim restated as one checkable sentence")
    quote: str = Field(description="3-8 consecutive words copied EXACTLY from the page text, used to locate the claim on screen")
    route: Literal["outside", "funnel"] = Field(
        description="'funnel' if a visitor can test it by walking the site's signup/pricing flow; otherwise 'outside'"
    )
    search_query: str = Field(description="web search query that would find independent evidence for or against the claim")


class Claims(BaseModel):
    claims: list[Claim]


class Verdict(BaseModel):
    status: Literal["verified", "contradicted", "unverifiable"]
    reasoning: str = Field(description="1-2 sentences, plain language, cite what the evidence says")
    evidence_quote: str = Field(description="short verbatim quote from the evidence that drove the verdict, or '' if none")
    source_url: str = Field(description="URL of the evidence that drove the verdict, or '' if none")


def _parse(prompt: str, schema: type[BaseModel], effort: str) -> BaseModel:
    response = client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
        output_format=schema,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request")
    return response.parsed_output


def extract_claims(url: str, page_text: str, max_claims: int = 8) -> list[Claim]:
    prompt = f"""You are a product marketing manager auditing the claims a landing page makes to buyers.

Landing page: {url}
Page text (rendered and extracted by TinyFish Fetch):
<page>
{page_text}
</page>

Pick the {max_claims} most decision-relevant, checkable claims (numbers, benchmarks, pricing/free offers,
compatibility, customer results, guarantees). Skip vague slogans and illustrative demo content.
Include every claim about signing up, free credits, credit cards, or pricing as route 'funnel'.
The quote must be copied exactly from the page text so it can be found on screen."""
    return _parse(prompt, Claims, effort="low").claims


def judge(claim: Claim, evidence: list[dict], target_url: str) -> Verdict:
    blocks = "\n\n".join(
        f"<evidence url=\"{e['url']}\" source=\"{e['source']}\">\n{e['text']}\n</evidence>" for e in evidence
    ) or "<evidence>none found</evidence>"
    prompt = f"""Decide whether the evidence supports this claim made on {target_url}.

Claim: {claim.claim}

{blocks}

Rules:
- 'verified' only if the evidence directly supports the claim. Independent sources count more than the target's own pages.
- 'contradicted' if the evidence directly conflicts with the claim.
- 'unverifiable' if the evidence is missing, off-topic, or only restates the claim from the same page. Do not guess."""
    return _parse(prompt, Verdict, effort="medium")


def evidence_from_agent(result: object, signup_url: str) -> dict:
    return {"url": signup_url, "source": "TinyFish Agent funnel walk", "text": json.dumps(result, indent=1)[:8000]}
