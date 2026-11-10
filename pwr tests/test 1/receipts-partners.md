# Room: receipts-partners

**Type:** room (project-scoped) · **Workstream:** design partners & early-customer signal
**Parent doc:** [project.md](../project.md) — "The four project rooms", room 4

## Description (paste-ready)

> Front line with the first teams: their agent horror stories, install
> evidence, feature requests, and churn signals — each one tagged and routed to
> a project todo, an attention item, or the pivot evidence set. w_ai answers
> scoped to this room; a weekly digest of unresolved items goes to the Founders
> room. This room is the source of truth for the validation test.

## What this room is for

The place where the startup's central hypothesis is proved or killed:
"teams will put a guard proxy in front of their agents' prod actions." Every
install story, every "we almost didn't because…", every workaround is evidence.
It is deliberately *outside* our internal rooms' politeness — real customer
mess, captured verbatim, then structured.

## Who is here

| Member | Kind | Role |
|---|---|---|
| Design partners (guest users) | humans, external, scoped membership | post stories, asks, install results |
| Founder #2 | human | triage owner; the only one who promises anything |
| `w_ai` | Hermes agent | first responder: answers product/how-to questions scoped to this room + its own projects; drafts, never commits |

Internal agents (`coder`, `market_research`) are NOT members; findings move to
`receipts-build` / `receipts-growth` as linked messages, by founders.

## What gets posted here

- **Install evidence:** team, stack, workflow wired, guard-policy snapshot,
  date — the unit of the validation count ("5 installs wired into a real
  workflow")
- **Horror stories** (the marketing gold and the spec source): what the agent
  did, what was unanswerable at the moment it mattered
- **Feature requests** — each tagged `add_project_todo`-bound with
  `importance` and cited by message id
- **Churn signals:** uninstalled, stalled-onboarding, "waiting for X to decide"
- **Weekly unresolved digest** → summarized and posted into `receipts-founders`

## What does NOT get posted here

- Internal debate about a partner (that's Founders/Growth; here we only post
  what we need *from* them or give *to* them)
- Pricing negotiation outcomes — proposals yes, commitments no (route to
  Founders approval first)

## Rules of engagement

1. **Every actionable item is tagged the day it lands:** todo, attention item
   (blocker/risk/mention), or pivot-evidence set. Untagged items age out and are
   reported as process failures, not lost silently.
2. **`w_ai` is scoped hard:** answers only about Receipts, only to this room's
   members, only from this project's knowledge items — and anything that smells
   like a commitment ("we'll ship that") goes to founder review, not to send.
3. **Evidence cites ids, not vibes:** build/growth work items referencing a
   partner need must link the partner message id — the same
   evidence-linked-todo discipline the product sells.
4. **Partner data is minimal and mappable:** store what a workflow needs, not
   the world; anything sensitive becomes an external_knowledge_asset with
   access notes, never inline secrets.

## Tools this room lives on

`w_ai` surface: `add_message`, `room_context_summary`, `search_messages_of_room`,
`get_users`/`get_room_members` (scoped). Founder triage: `add_project_todo`,
`add_blockers`, `add_mentions`, `add_project_knowledge_item` (as spec sources),
`add_external_knowledge_asset` (install snapshots), `create_message_topic`
(topics: `installs`, `stories`, `requests`, `churn`).

## Cadence

- Continuous: `w_ai` long-poll, reply SLA 4 business hours.
- Weekly (Tue): unresolved digest → `receipts-founders`; validation counter
  posted here (installs wired / 5).
- Per partner: month-2 check-in ("did the guard catch anything real?").

## KPIs

- Validation counter: teams with install wired into a real workflow (≥5 by month 2)
- Median first-reply time (agent + human combined)
- % actionable items tagged same-day (target ≥90%)
- Churn before second month (target ≤1 of first 5)
- Horror stories captured with source (each one is Growth's raw material)

## Starter messages (for test 1)

1. Founder: "Welcome — one question to start: last month, what did an agent do
   that you still can't fully explain to anyone? Answer here, raw."
2. `w_ai` first-touch template: "Thanks for installing. To count as 'wired', we
   need one guarded action in your real workflow — what's the first call you'd
   put behind the approval gate?"
