# TinyFish landscape: what already exists (avoid) and white space (build here)

Sources: tinyfish.ai/blog/category/customers, tinyfish-cookbook README, docs.tinyfish.ai, tinyfish.ai/pulse (read 2026-10-11).

## Platform facts worth using in README / launch post
- Five public APIs: Agent, Research, Search, Fetch, Browser (+ Vault for credentials, Browser Context Profiles for saved logins, Monitor for scheduled change tracking).
- **Search and Fetch are free** (daily allowance, no card). Agent, Research, Browser are metered from the wallet. New signups get $8 in wallet funds.
- Search: <0.5s, rank-stable JSON. Fetch: full-browser render -> clean markdown, failed URLs are free, up to 10 URLs per call.
- Agent: URL + goal -> JSON; `output_schema` for structured output; SSE stream includes a live `streaming_url` (embeddable browser view).
- Also: MCP server, CLI (`@tiny-fish/cli`), Agent Skill (`npx skills add ... --skill use-tinyfish`), n8n/Dify nodes, `tinyfi.sh` for sharing localhost demos.
- Enterprise trust: Google, DoorDash, ClassPass in production.

## Already covered (steer away)
| Who | What | Primitives |
|---|---|---|
| Photon (customer) | Live lead research -> personalized first iMessage | Search, Fetch, Agent |
| Hellyeah AIMA (customer) | One URL -> brand profile -> ad campaign in ~10 min | Search, Fetch, Agent |
| Okara (customer) | AI CMO onboarding research, crawls client + competitor sites | Search, Fetch |
| Ansur (customer) | AI workers find suppliers not in the database | Search, Browser |
| scam.ai Reality (customer) | Verify candidates/claims -> reviewer packet with explicit states, not verdicts | Search, Fetch |
| Glean, CREAO, Bonfire (customers) | Web grounding layer / default web layer / Tavily replacement | Search, Fetch |
| Cookbook | competitor-analysis, competitor-scout-cli, n8n Competitor Scout (competitive pricing intel) | Agent |
| Cookbook | ~20 "compare prices across N sites" consumer demos, Product Hunt tracker, tenders finder | Agent |

## White space (patterns nobody has shown)
1. **Agent that ACTS, not just reads.** Almost every story/recipe is read-only extraction. Forms, configurators, multi-step funnels = the "wait, you can DO that?" moment.
2. **Browser primitive is nearly invisible** in GTM stories (only Ansur). Pixel-proof evidence (screenshots / filmstrips) is unclaimed.
3. **Vault / Browser Context Profiles / Monitor** have zero GTM showcases.
4. **Looking at the buyer's experience** (how a prospect actually moves through a site) rather than at the company's data.
5. Borrowable pattern: scam.ai's "explicit states, not verdicts" (verified / contradicted / unverifiable, each bound to a source).
