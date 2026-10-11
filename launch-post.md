# Launch post: Claim Receipts

**Channel:** X (primary, developer audience) · LinkedIn variant below
**Author:** Sky Zhang, Head of Growth, TinyFish
**Attach:** `demo-video.mp4` (the funnel walk + receipts filling in) on post 1

---

## X thread

**1/**
We pointed an agent at our own homepage and asked it to fact-check every claim on it.

5 ✅ verified. 3 ⚠️ couldn't prove. 0 rigged.

It's called Claim Receipts, it's open source, and it runs in about 90 seconds. 🧾👇

[video]

**2/**
How it works: paste a landing page. It pulls out the claims buyers decide on (benchmarks, prices, "free", "no card", "the only…") and routes each one to the primitive that can actually prove it:

🔎 Search: outside evidence
📄 Fetch: reads the page and the sources
🤖 Agent: walks the signup funnel like a prospect
🖥️ Browser: screenshots the claim where the visitor saw it

**3/**
The part that made our team say "wait, you can do that?":

To check "$8 free credit, no card required", the agent clicks Get Started, follows the flow to the sign-up gate, and reports what it asks for.

It never types, submits, or signs in. It stops at the first gate.

**4/**
It was also honest about us.

It flagged that our 89.9% Online-Mind2Web headline and a blog post's "40 failures out of 300" don't line up (that's ~86.7%). And it wouldn't sign off on "the only platform" because nobody independent says so.

Fair. That's the job.

**5/**
Built for PMMs checking copy before launch, sellers checking a competitor's "free tier" before a call, and anyone who wants a source under every number.

Search + Fetch are free. New accounts get $8 for Agent + Browser. A full run costs about $0.30.

Repo + run in 4 commands → https://github.com/ThomasParas/AI-Native-talent-hunt-Tinyfish
Get a key → https://agent.tinyfish.ai

---

## LinkedIn variant

We fact-checked our own homepage with agents.

Claim Receipts reads a landing page, extracts every claim a buyer would act on, and checks each one with the TinyFish primitive built to prove it. Search finds outside evidence, Fetch reads it, an Agent walks the sign-up funnel the way a prospect would (and stops before submitting anything), and a cloud Browser screenshots the claim exactly where a visitor sees it.

Result on tinyfish.ai: 5 verified, 3 unverifiable. It caught that our 89.9% benchmark headline and a blog post's "40 failures out of 300" don't agree, and it refused to confirm "the only platform" without an independent source. We'd rather ship a tool that says "I can't prove this" than one that rubber-stamps us.

If you're in product marketing, run it on your own homepage before your next launch. If you sell against a competitor, run it on theirs before the call.

Open source, ~90 seconds, about $0.30 a run: https://github.com/ThomasParas/AI-Native-talent-hunt-Tinyfish

---

### Why this post (notes for Sky)

- **Hook = self-audit, not a feature list.** "We fact-checked ourselves and published the misses" earns trust with developers and is a far stronger "you can DO that?" moment than another Search/Fetch snippet.
- **Every number is from the real run** in the README (8 claims, 5 ✅ / 3 ⚠️, ~90s, $8 credit, free Search/Fetch). Re-run before posting and update the numbers if the homepage changes.
- **Judgment call:** post 4 calls out our own 89.9% vs 86.7% gap. Keep it, because it's the proof the tool isn't rigged. If it needs to come out, swap in the "only platform" example on its own.
- **Measure:** this launch is the first baseline. Track repo stars/clones, `agent.tinyfish.ai` signups tagged from the link, and first-run activation (smoke test → first report).
