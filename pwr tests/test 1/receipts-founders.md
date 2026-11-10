# Room: receipts-founders

**Type:** decision_room · **Workstream:** judgment, approval, money, scope
**Parent doc:** [project.md](../project.md) — "The four project rooms", room 3

## Description (paste-ready)

> The judgment room for the company: pricing changes, spend above $200, legal
> and contract sign-off, the month-2 pivot decision, hire #3. Every approval
> request raised in any other room lands here; the accountable human's yes/no is
> recorded as a decision message and auto-captured as an ADR. Work is never
> marked done while an item sits waiting-for-approval here.

## What this room is for

This room is the company's accountability spine — literally the product we're
building, run on ourselves. Everything ambiguous, expensive, irreversible, or
cross-cutting terminates here with a named human decision and a durable record.
It exists so the other three rooms can move fast without drifting.

## Who is here

| Member | Kind | Role |
|---|---|---|
| Founder #1 | human | accountable for build/scope decisions |
| Founder #2 | human | accountable for GTM/pricing decisions |
| Agents (`main`, `coder`, `market_research`, `w_ai`) | Hermes profiles | may post INTO this room (approval requests, escalations) — never decide, never `add_decision_message` |

## The decision inventory (what needs to land here)

1. **Money** — any single spend > $200, any budget reallocation, pricing tier
   changes, the burn-vs-plan table (monthly review against project.md budget)
2. **Scope & sequence** — acceptance-criteria changes, milestone moves, dropping
   a 90-day-plan item
3. **The pivot call (month 2)** — "≥5 installs wired" verdict, based solely on
   evidence filed in `receipts-partners`; decision + auto-ADR either way
4. **Legal/external commitments** — entity paperwork, DPA language, contracts
   with design partners, anything touching the fail-open liability note
5. **People** — hire #3 trigger (defined: 3 paying teams sustained 60 days)
6. **Standing policy** — approval thresholds ($200 spend, destructive verbs,
   external sends) live here as explicit numbers, not folklore

## How an item enters

Only one sanctioned way: another room raises
`add_approve_request_with_message` carrying — target, scope, boundary, evidence
(the requesting message link), and the acceptance criteria the requester will
consider "done". No verbal approvals in other rooms count; the ledger is the
memory.

## How an item leaves

- The accountable human posts `add_decision_message` (yes/no, conditions, owner
  of follow-through). Approved decisions auto-capture a
  `project_decision_record` (ADR).
- Denied/cancelled → the originating room is notified with the reason; the
  requester updates the task state.
- Nothing here may be marked done while its approval sits `waiting-for-approval`
  — that state distinction is the room's core discipline.

## Cadence

- Daily, 5 minutes: clear `decisions_waiting` attention queue (target: no item
  older than 24h).
- Weekly (Friday): `outcomes_review` — this week's approved decisions vs their
  claimed effects; `ai_task_cost` rollup; next week's spend pre-authorization.
- Monthly: full burn review against the $42,100 plan; KPI dashboard from all
  three work rooms.

## Tools this room lives on

`add_approve_request_with_message`, `approval_requests`,
`get_approval_request`, `edit_approval_request`, `add_decision_message`,
`decisions`, `decisions_waiting` (attention category), `add_project_decision_record`,
`room_decision_context`, `outcomes_review`, `ai_task_cost`, `room_economics`.

## Rules of engagement

1. **Agents request, humans decide.** An agent submitting its own decision here
   is a red-line event; SOULs enforce it, this room documents it.
2. **Every decision cites its evidence** — the approval request id, the partner
   messages, the cost figure. No "sound good to me" verdicts.
3. **Decision text is short and dated:** what was decided, why, who is
   accountable, what changes, when we re-check. (It becomes the ADR body.)
4. **If two founders disagree**, the owner-of-domain decides; the dissent is
   recorded in the ADR, not smoothed over.

## KPIs

- Median approval wait time (< 24h)
- % of decisions with linked evidence (target 100%)
- Waiting-for-approval items > 48h (target 0)
- Pivot-test verdict on time (month 2, ±1 week)

## Starter messages (for test 1)

1. Founder #1: "Standing thresholds, effective now: spend gate $200; external
   send = always human; destructive file verbs = reservation + approval. ADR-001."
2. From `receipts-build` (example inbound): "APPROVAL REQ #4 — change acceptance
   criteria of mvp-proxy to defer SSE support to w5. Evidence: build thread msg
   87. Requested by coder via main. Waiting on: founders decision."
