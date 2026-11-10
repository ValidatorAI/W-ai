# Project: Receipts — the accountability layer for AI agent fleets

> Startup concept, 2-employee scope. Written 2026-11-09 for `pwr tests/test 1`.
> Budget figures are planning estimates (12 months, USD), not quotes.

---

## One-liner

**Receipts** turns every AI-agent action into a signed, costed, human-approved
record — so a company can answer "what did our agents do, who allowed it, and what
did it cost?" in one click.

*Alternative names if Receipts is taken: SignOff, WitnessLedger, Co-sign.*

## The problem (why this is real now)

- Companies are bolting autonomous agents onto real work (coding, support, ops,
  marketing). Dashboards show *activity*; almost nothing shows **accountability**.
- The three questions every founder/CTO gets asked after the first agent mistake
  ("what did it touch?", "who said that was OK?", "how much did that burn?") have
  no good answer today. Tracing tools (Langfuse, W&B Weave) show tokens and spans —
  not approval chains or dollar accountability per decision.
- Regulation (EU AI Act documentation duties, internal audit) is arriving with
  nobody's chat logs ready to satisfy it.

## The product

A small SaaS + drop-in MCP server that sits between agents and the world:

1. **Ledger** — append-only log of agent actions: who (agent identity), what
   (tool call + arguments hash), outcome, cost in $, and the human who approved it.
2. **Approval gates** — a risky action (spend over $X, external send, prod deploy,
   file delete) blocks the agent mid-call and raises a one-tap approve/deny to a
   human (Slack/email/mobile). The decision becomes part of the receipt.
3. **Fleet cost analytics** — per agent, per task, per customer: what did
   autonomy cost us, what did it save.
4. **Audit export** — one-click SOC2/AI-Act-style evidence packet: every action
   with its approver and timestamp.

Drop-in via MCP is the wedge: an agent using any MCP server gets guarded by
pointing `tools.call` through Receipts' proxy — no code rewrite. (This is exactly
the pattern PWR/W-ai already proves: scoped endpoints, call logging, approval
requests, task cost.)

## Why two people can ship it

The hard parts — an event ledger, a proxy with policies, a cost calculator, a
notification flow — are all small, well-underned surfaces. The moat is not
engineering volume; it's policy templates and integrations that compound later.
Model: open-source core (the proxy + ledger CLI) + paid hosted dashboard + paid
policy packs. Self-hostable, which is a selling point, not a support burden, if
the core stays a single container.

## Target customer (first 18 months)

Founder-led teams (3–30 people) that have already deployed agents against real
systems: AI dev shops, agent-consultancies, SaaS teams with internal copilots.
Buyer: the CTO who will personally be asked to explain the incident.
ICP we can reach cheaply: the same communities building on MCP/LangGraph/CrewAI.

## Business model

- Free: OSS proxy + local ledger, unlimited self-host.
- Pro: $49/team/mo hosted dashboard, 90-day retention, Slack approvals.
- Scale: $299/mo, 1-yr retention, SSO, policy packs, audit export.
- Future: per-"guarded call" pricing once integrations exist (usage rides the AI
  spend curve).

## Team & 12-month budget (2 full-time employees)

Two generalist engineers/co-founders; roles: (1) proxy/server/ledger,
(2) dashboard/integrations/GTM-content. No salaries at market — lean bootstrapped
assumption, low-cost geography.

| Line (12 months)              | Assumption                          | Est. cost |
|-------------------------------|-------------------------------------|-----------|
| Founder salaries (2 × $1,200/mo) | sweat-equity-plus, 24 founder-months | $28,800 |
| Infra (VPS, managed Postgres, alerts) | ≤$150/mo first year            | $1,500  |
| LLM/API budget for demos & cost-mapping | $50/mo                      | $600    |
| Domain, email, GitHub, tooling | ~$40/mo                            | $500    |
| Legal (entity, ToS/DPA templates, one consult) | flat                 | $1,500  |
| Design assets + landing (one-off) | template-driven, AI-assisted      | $800    |
| Marketing: content, OSS sponsorships, conference booth (1) |    | $4,000  |
| Support/customer tooling (Zammad/plain, Slack Connect) |    | $600    |
| Contingency (10%)             |                                     | $3,800  |
| **Total cash need (12 months)** |                                   | **≈ $42,100** |

- **Bootstrapped floor:** ~$30k if founders take $800/mo and marketing is pure
  content/OSS. 
- **Comfortable runway with one contractor month:** ~$55k.
- Path to self-funding: ~35 Pro teams or 6 Scale teams by month 9 ≈ $4.6k MRR —
  covers the whole budget line for two salaries.

## 90-day plan (the actually-difficult part: speed)

1. Weeks 1–3: MCP proxy that forwards + records every call with agent identity and
   cost estimate; CLI to inspect the local ledger. Ship as OSS with a demo video.
2. Weeks 4–6: approval gate on "danger" policy (spend/egress/destructive verbs),
   Slack one-tap approve/deny; hosted ledger alpha (5 design partners recruited via
   the OSS repo).
3. Weeks 7–10: dashboard — timeline, cost per agent, approver column; audit-export
   MVP (PDF).
4. Weeks 11–13: first paid tier, Product Hunt + agent-framework integrations docs
   (LangGraph, CrewAI, Hermes-style profile configs). Target: 3 paying teams.

## The four project rooms (PWR workspace setup)

The project runs on exactly four rooms — one per workstream, with clear routing
rules so nothing dies in the wrong chat. Descriptions are paste-ready for room
creation (via the web UI or `create room` on `/action-mcp`).

### 1. Receipts Build — technical execution
- **Room name:** `receipts-build`
- **Type:** room (project-scoped)
- **Description:** *"Technical execution for Receipts: the MCP proxy, the ledger,
  the dashboard, framework integrations. Agents and engineers post progress
  updates, planned file changes (with reservations), and incident findings here.
  Blockers and risks are filed to the attention queue; anything that changes
  scope, sequence, or acceptance criteria escalates to Receipts Founders."*
- **Who lives here:** the two founders, `coder` agent.
- **Feeds:** the 90-day plan's weeks 1–10; milestones `mvp-proxy`, `approvals`,
  `dashboard`.

### 2. Receipts Growth — marketing, launch, design-partner recruiting
- **Room name:** `receipts-growth`
- **Type:** room
- **Description:** *"Marketing and adoption: OSS visibility, launch content,
  Product Hunt, and recruiting the 20 design partners from the validation test.
  market_research posts competitor and community evidence with sources; every
  campaign idea becomes a project todo with an owner and a deadline. No
  decisions here — only proposals that move to Receipts Founders."*
- **Who lives here:** founder #2 (GTM), `market_research`, `w_ai` for outreach drafts.
- **Feeds:** the validation check ("≥5 installs") and the month-13 GTM targets.

### 3. Receipts Founders — judgment and approval (decision room)
- **Room name:** `receipts-founders`
- **Type:** decision_room
- **Description:** *"The judgment room for the company: pricing changes, spend
  above $200, legal and contract sign-off, the month-2 pivot decision, hire #3.
  Every approval request raised in any other room lands here; the accountable
  human's yes/no is recorded as a decision message and auto-captured as an ADR.
  Work is never marked done while an item sits waiting-for-approval here."*
- **Who lives here:** both founders only — agents post *into* it but never decide
  in it.
- **Feeds:** attention categories `decisions_waiting` and `outcomes_review`; the
  whole "Risks & mitigations" list lives or dies by this room's cadence.

### 4. Receipts Partners — design partners and early-customer signal
- **Room name:** `receipts-partners`
- **Type:** room
- **Description:** *"Front line with the first teams: their agent horror stories,
  install evidence, feature requests, and churn signals — each one tagged and
  routed to a project todo, an attention item, or the pivot evidence set. `w_ai`
  answers scoped to this room; a weekly digest of unresolved items goes to the
  Founders room. This room is the source of truth for the validation test."*
- **Who lives here:** `w_ai` (user-facing), founder #2 triaging, design partners
  as guest users.
- **Feeds:** `add_project_bottleneck`, `edit_*` on blockers, and the falsifiable
  month-1–2 check ("5 installs or pivot the ledger to post-hoc compliance").

**Routing rules that make the four rooms one system:**
- Execution chatter stays in its workstream room; only *decisions, money, and
  scope* cross into Founders.
- Any room can raise an approval request; only Founders resolves it.
- Partner-originated work items must cite their `receipts-partners` message id —
  the same "evidence-linked todo" discipline Receipts itself sells.
- Cost: each room's agent tasks carry `usd_budget`; `ai_task_cost` is reviewed in
  Founders weekly, alongside the burn table above.

## Risks & honest mitigations

- **Framework-native guardrails swallow us** (LangSmith policies, vendor
  approval flows). Mitigation: be cross-framework and human-approval-centric, not
  trace-centric; our artifact is *evidence for a human*, which tracing tools won't
  own.
- **Proxy = liability surface** (we sit in front of prod actions). Mitigation:
  fail-open toggle, signed ledger, formal DPA from day one; sell "guardrail"
  posture via the audit export.
- **Approval fatigue.** Mitigation: policy packs that learn thresholds; batch
  approvals; escalate only irreversible actions.
- **Two-person key-person risk.** Mitigation: everything single-container, runbooks
  as code, no enterprise SLAs until hire #3.

## Why "valid" (falsifiable check, not hype)

Test in month 1–2 without building much: pitch the demo to 20 agent-using teams
(they all have a horror story ready); if ≥5 design partners install the OSS proxy
and wire it into one real workflow, the wedge is proven. If nobody installs a
proxy in front of their prod actions, the pain isn't acute enough — pivot the same
ledger to *post-hoc* compliance reporting, which needs no interception.

---

*Note on origin: the core insight (action → approval → cost → durable receipt, all
over MCP) is the exact discipline PWR enforces internally. Receipts is "PWR's
accountability spine, sold separately."*
