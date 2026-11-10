# Room: receipts-build

**Type:** room (project-scoped) · **Workstream:** technical execution
**Parent doc:** [project.md](../project.md) — "The four project rooms", room 1

## Description (paste-ready)

> Technical execution for Receipts: the MCP proxy, the ledger, the dashboard,
> framework integrations. Agents and engineers post progress updates, planned
> file changes (with reservations), and incident findings here. Blockers and
> risks are filed to the attention queue; anything that changes scope, sequence,
> or acceptance criteria escalates to Receipts Founders.

## What this room is for

The room where the 90-day plan becomes commits: proxy weeks 1–3, approval gate
weeks 4–6, dashboard weeks 7–10, integration docs weeks 11–13. It is the only
place where build progress is authoritative — GitHub activity is an echo, this
room is the record.

## Who is here

| Member | Kind | Role in this room |
|---|---|---|
| Founder #1 (infra/backend) | human | owns proxy + ledger; reviews agent PRs |
| Founder #2 (dashboard/GTM-eng) | human | owns dashboard + integrations |
| `coder` | Hermes agent (profile) | executes assigned AI tasks, posts progress |
| `main` | Hermes agent (profile) | coordination, update exchange with `coder` |

## What gets posted here

- Progress updates tied to a task id (`update_ai_task` + `add_message` recap)
- Planned file changes **before** editing, with a file reservation held
  (`FileReservation`: inspect conflict → reserve → renew → release)
- Incidents and findings ("proxy fail-open misfired on egress verb X")
- Milestone evidence when `mvp-proxy` / `approvals` / `dashboard` is hit
- Daily standup digest: open tasks by state, blockers, cost-to-date

## What does NOT get posted here

- Pricing, spend, legal, or scope decisions → `receipts-founders`
- Launch/marketing chatter → `receipts-growth`
- Customer horror stories verbatim → `receipts-partners` (link, don't dump)

## Rules of engagement

1. **Reserve before you write.** No edit to shared files without an active
   reservation; conflicts are posted, not silently resolved.
2. **Read before write.** Agents hit `/read-mcp` for context
   (`room_context_summary`, `get_ai_task`, `get_project_users`) before any
   `add_*`/`edit_*` on `/action-mcp`.
3. **One task, one thread.** Every work item starts as an AI task
   (`create_ai_task` with `usd_budget`) and its updates reference the task id;
   parent/child chains show agent-to-agent subdivision.
4. **Escalate, don't improvise.** Acceptance-criteria ambiguity → approval
   request into `receipts-founders`; never mark done while waiting-for-approval.
5. **No auto-reply expectation.** Agents poll this room (`poll_messages`
   long-poll); if nobody is polling, silence means "no client attached", not "no".

## Tools this room lives on

`create_ai_task`, `get_ai_task`, `update_ai_task`, `get_ai_task_children`,
`ai_task_cost`, `add_message`, `room_context_summary`, `add_blockers`,
`add_risks`, `add_material_changes`, `add_approve_request_with_message`,
`create_room_history_topic` (topics: `proxy`, `ledger`, `dashboard`,
`integrations`).

## Cadence & budgets

- Daily: 1-line standup per active task (agent-posted).
- Weekly: `ai_task_cost` report vs `usd_budget` totals; overspend >10% →
  attention item + message.
- Task budget defaults: small fix $5, feature slice $25, integration doc $10.

## KPIs

- Weeks on plan (currently: proxy w1-3, approvals w4-6, dashboard w7-10)
- Blocked-task age (< 24h to escalation)
- Reservation conflicts per week (target 0; each one is a process bug)
- Cost per closed task vs estimate

## Starter messages (for test 1)

1. Founder: "Kickoff — milestones are mvp-proxy / approvals / dashboard.
   `main`, break down the proxy skeleton as an AI task tree under this room;
   `coder` takes the ledger CLI child."
2. Agent update template: "task #N · step 2/4 · files reserved: proxy/call_log.rb
   · next: policy hook wiring · ETA today 18:00."
