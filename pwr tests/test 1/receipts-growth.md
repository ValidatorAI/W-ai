# Room: receipts-growth

**Type:** room (project-scoped) · **Workstream:** marketing, launch, recruiting
**Parent doc:** [project.md](../project.md) — "The four project rooms", room 2

## Description (paste-ready)

> Marketing and adoption: OSS visibility, launch content, Product Hunt, and
> recruiting the 20 design partners from the validation test. market_research
> posts competitor and community evidence with sources; every campaign idea
> becomes a project todo with an owner and a deadline. No decisions here — only
> proposals that move to Receipts Founders.

## What this room is for

Everything that puts Receipts in front of its first 35 paying teams: the OSS
repo's public story, launch content, design-partner recruiting for the month-1–2
validation test ("≥5 installs wired into a real workflow or we pivot"), Product
Hunt execution in week 13, and the comparison narrative against LangSmith /
vendor-native guardrails / Plane-style bundling.

## Who is here

| Member | Kind | Role in this room |
|---|---|---|
| Founder #2 | human | owns GTM, approves all outbound copy |
| `market_research` | Hermes agent | competitor/community evidence, sourced |
| `w_ai` | Hermes agent | outreach drafts, FAQ/reply drafting for founder review |

Design partners do NOT sit here — they talk to us in `receipts-partners`.

## What gets posted here

- Evidence threads: community pain signals ("agent deleted staging" stories),
  competitor moves, MCP-ecosystem growth stats — **each with a source link**
  (external_knowledge_asset + message reference)
- Campaign proposals → instantly converted to `add_project_todo` with owner +
  deadline; ideas without owners die here, politely
- Content drafts (launch post, demo video script, README hero copy) for review
- Recruiting pipeline status: 20 targets → contacted → replied → installed
- Weekly funnel digest: stars, clones, proxy installs, partner conversions

## What does NOT get posted here

- Final pricing/spend decisions (ad budget > $200, tier changes) →
  `receipts-founders` (raise approval, don't ask in chat)
- Build status → `receipts-build`
- Customer commitments ("we'll ship X") — this room may propose, only
  Founders may commit

## Rules of engagement

1. **Claim ≠ source.** Any market number, competitor feature, or horror story
   posted here must carry a link or cite a `receipts-partners` message id.
2. **Everything actionable is a todo.** A suggestion that needs work gets
   `add_project_todo` before the conversation moves on.
3. **Human hands on outbound.** `w_ai` drafts; only a founder sends. External
   sends are approval-gated events, never agent-autonomous.
4. **No metric inflation.** Install counts come from the ledger/dashboard
   data, not vibes; label estimates as estimates.

## Tools this room lives on

`add_project_todo`, `project_todos`, `add_external_knowledge_asset`,
`add_knowledge_proposals`, `add_mentions`, `add_loading_message` (for long
research runs), `create_message_topic` (topics: `evidence`, `content`,
`partners-pipeline`, `launch`), `add_approve_request_with_message` (spend).

## Cadence

- Mon: weekly funnel digest (auto-posted by `market_research`).
- Wed: competitor/community scan, max 5 items, sourced.
- Event-driven: PH launch day takes over the room; archive as a room history
  topic afterward.

## KPIs

- Design-partner pipeline: contacted / replied / installed (target: 20 → 5)
- OSS proxy installs per week
- Content output vs plan (1 demo video by w4, launch post by w12)
- Cost of acquired design partner (task cost + any spend, from `ai_task_cost`)

## Starter messages (for test 1)

1. Founder: "Validation test starts now: list 20 agent-using teams with a
   horror story we can plausibly help; `market_research`, evidence per team."
2. `market_research` template: "Team X — evidence: [thread link] — pain:
   approver unknown after deploy rollback — fit: high — proposed first touch:
   (draft attached)."
