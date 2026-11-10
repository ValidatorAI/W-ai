# PWR — what it is, its functionalities, and its intended behaviour

> Written 2026-11-09. Everything marked **verified** was checked against the live
> repo (`~/Documents/codes/Pavel/W/pwr`, branch `installation`) and the running
> server (`localhost:3000`). Everything marked **design intent** comes from the
> strategy docs (`pwr/team-pack-en-2026-10-01/`, `W-ai/questions on PWR.md`) and
> is not yet a shipped-claim.

---

## 1. What PWR is

**One sentence:** PWR is an open-source workspace where people and actionable AI
agents share one authoritative project context, coordinate work in rooms, delegate
tasks with visible human judgment, and learn from measured outcomes.

**Product frame (design intent).** The name comes from the "PWR Work" strategy pack:
a *power team* is a small group of people plus AI agents organized around a
measurable outcome. The product follows the W Method / W Manifesto principles —
outcomes over output, shared context where decisions happen, human accountability
for delegated action, removal of unnecessary work, organizational learning, and
company control of its own system and memory. The strategy is explicit that PWR
Work's positioning is NOT "chat + agents"; the differentiator to test is whether it
connects a team's decisions, delegated action, human attention, cost, and measured
outcomes better than the team's current tool mixture (Notion Agents, Asana AI
Teammates, ClickUp Super Agents, Plane, n8n are named as comparators).

**Engineering reality (verified).** PWR is a Ruby on Rails application that acts as
the *authoritative state store* for a company: `company → projects → rooms →
messages / tasks / knowledge / approvals`. Its entire operational surface is
exposed as MCP (Model Context Protocol) servers so external agents — Hermes
profiles — read and write that state. The public product name is **Space** (older
docs say **W-space**); the repository is `https://github.com/ValidatorAI/bonfire`
(the app began as a Bonfire/Campfire fork, hence legacy "bonfire" identifiers),
and the local directory was renamed to `W/pwr` to match the PWR brand. The sibling
repo `W/W-ai` (`ValidatorAI/W-ai`) holds the agents that operate it: Hermes profile
sources (SOULs, skills), the MCP tool/profile maps, and the product docs.

| Piece | Path / remote | Role |
|---|---|---|
| PWR app | `W/pwr` → `ValidatorAI/bonfire` | Rails state store + MCP servers + installer |
| W-ai | `W/W-ai` → `ValidatorAI/W-ai` | Hermes profiles (workspace, message_analyzer, bots), SOULs, skills, tool maps, PWR docs/tests |
| W-bridge | `W-bridge/` | Python FastAPI MCP bridge + "space" Rails backend (feature parity branch: `merge-with-bridge`) |
| Team pack | `pwr/team-pack-en-2026-10-01/` | Strategy, brief, discussion questions — product, not code |

---

## 2. Functionalities, layer by layer

### 2.1 Rooms and messaging (the collaboration core) — verified
- Project-scoped **rooms** and thread child-rooms; messages are Rails ActionText
  rich blocks (stored in `action_text_rich_texts`), so they carry HTML, mentions
  (`application/vnd.campfire.mention` attachments) and file attachments.
- **Topics** over messages: `create_topic`, `message_topics`, `room_history_topics`
  (topic-scoped room history snapshots), `room_topic_tree`, `search_topics` — this
  is how a room's stream is carved into threads and durable subject areas.
- **Room context tools** for agents: `room_context_summary`, `room_decision_context`,
  `room_evidence`, `room_economics` — an agent can ask "what is this room about,
  what was decided, what is the evidence and the cost" without dumping full history.
- Presence: users and agent identities (`User` bot accounts) carry online/idle/offline
  state; room membership is explicit (`get_room_members`).

### 2.2 Agent work tracking — verified
- **AI tasks** (`create_ai_task`, `ai_tasks`, `get_ai_task`, `update_ai_task`,
  `delete_ai_task`, `get_ai_task_children/_parents`, `ai_task_cost`): hierarchical
  agent work units with parent/grand-parent chains, `usd_budget` and `token_budget`
  fields, `importance`, level, and `dispatched`/`finished` flags. Cost per task is
  queryable (`ai_task_cost`).
- **Project todos** (`add_project_todo`, `project_todos`, …): the human/kanban-facing
  task surface. AI tasks and project todos are separate surfaces — a common
  confusion; picking the wrong one was an explicit finding in earlier reviews.
- **The dispatcher (push execution):** `AiTaskDispatchLoop` polls about every second
  (`AI_TASK_DISPATCH_INTERVAL_SECONDS`) and `AiTaskDispatcher` POSTs an OpenAI-style
  chat completion to the Hermes API (`HERMES_BASE_URI`, default
  `http://127.0.0.1:8642`) targeting a profile (`HERMES_DEFAULT_PROFILE`, default
  `delegator`; `HERMES_MAX_ACTIVE_AGENTS` caps concurrency, default 2). The wake
  message is effectively "you have a new task with id N"; then the loop flips
  `dispatched=true`. **PWR wakes the agent; the agent pulls its real context via
  `get_ai_task`.** This is the single most important behaviour that distinguishes
  PWR from a passive work tracker.
- **AI configuration as data:** `AiProfile`, `AiSetting`, `Mcp`, `Tool`, `Skill`
  models + join tables mean PWR itself knows which Hermes profile has which MCP
  servers, tools, and skills attached (`list_ai_profiles`, `get_ai_profile_tools`,
  `list_ai_profile_mcps`, …). Profiles can be inspected and managed through the
  same MCP surface.

### 2.3 Human oversight: approvals, decisions, attention — verified
- **Approval requests** with a transition ledger; `add_approve_request_with_message`
  bundles the request with its explanation message; approval of a decision can
  auto-produce an ADR (`add_project_decision_record`).
- **Decisions**: `add_decision_message` (carries the *accountable human's* decision,
  never the agent's), `decisions`, `room_decision_context`.
- **Attention items**: company-home queue in canonical plural categories
  (decisions_waiting, blockers, risks, priorities, dependencies, mentions,
  outcomes_review — with matching tool families `*_blockers`, `*_risks`,
  `priorities`, `dependencies`, `learnings`, `material_changes`, …); items move
  pending → resolved/dismissed. This is the "human attention budget" instrument of
  the product: agents file what a human must look at, in a category, instead of
  pinging chat.
- **All-hands meetings**: `project_all_hands_meeting` records with action items,
  decisions, takeaways — company-level ritual captured as structured data.
- **Company status**: periods + status items (`add_company_status_period`,
  `company_status_items`) for reporting cadence.

### 2.4 Project knowledge (long-lived memory) — verified
Seven knowledge families, all CRUDable through MCP:
- `project_knowledge_items` (the general item store, incl. proposals flow
  `knowledge_proposals` for capture-then-approve)
- `external_knowledge_assets` (links/assets outside the system)
- `tree_based_project_directory_item` (directory structure, tree data)
- `project_note`, `project_adr` (decision records), `knowledge_activity_log`
  (audit of knowledge work), plus Obsidian-note mirroring conventions in W-ai.
- Message analysis: `create_message_analysis` / `update_message_analysis` — the
  `message_analyzer` Hermes profile scores room messages (importance) and turns
  actionable ones into tasks/attention items; its SOUL and skills live in W-ai.

### 2.5 Collision-safe parallel work — verified
**File reservations** (`FileReservation` model): inspect conflicts, reserve a file
for exclusive work, renew while editing, release when done. This is the mechanism
that makes "two agents in one repo" (the flagship demo scenario) safe.

### 2.6 Search, discovery, automation glue — verified
- Cross-entity search (`Search` model, `search_rooms`, `search_messages_of_room`),
  project/user discovery (`get_projects`, `get_single_project`, `get_user_projects`,
  `get_project_users`, `get_users`).
- **Output events plane:** `OutputEvents::Recorder` + deduplicator + delivery client
  with retries and per-event emission policy; payloads carry `knowledge_path`
  resolution. This is how business events flow *out* to external systems (webhooks,
  orchestration, monitoring) — completion of the "forward business events" promise.
- **Call logging:** every MCP call can be persisted via `create_tool_cal_log` /
  `tool_cal_logs` — the audit trail per agent action.

---

## 3. The MCP surface (how agents actually touch PWR)

**Verified 2026-11-09 against the live app** — 6 POST endpoints on
`localhost:3000`, served by one scope-filtered `Mcp::Registry` (per
`config/routes.rb:274-279`; the README's `GET /mcp/health` line is stale — no such
route; `/up` is the health check):

| Endpoint | Tools | Purpose |
|---|---|---|
| `/mcp` | 163 | everything (dev/demo convenience; production profiles should not need it) |
| `/action-mcp` | 142 | the full write ladder: add/edit/delete + most reads |
| `/read-mcp` | 78 | read-before-write ladder (`get_*`, `list_*`, `*_tasks`, context summaries) |
| `/knowledge-mcp` | 29 | knowledge families, topics, message analysis, call logs |
| `/task-mcp` | 8 | AI-task lifecycle only (`create_ai_task` … `ai_task_cost`, `hello`) |
| `/config-mcp` | 16 | AI-profile/MCP/tool/skill introspection |

Mechanics (verified in `app/services/mcp/`):
- **Verb convention:** `add_` (27) / `edit_` (23) / `delete_` (23) / `get_` (23) /
  `create_`+`update_` (12, newer families use create/update) / `list_` (9) /
  `search_` (3), plus 43 bare read/context names (`project_todos`, `blockers`,
  `room_economics`, …) — ~89 distinct entity domains overall.
- **FuzzyMatcher:** tools accept names as well as ids (`user_name`, `project_id`
  pairs resolve by fuzzy match) — agents do not need backend probing to find ids.
- **Aliases:** many tools self-register alternate names; `tools/list` shows
  canonical names only, so an alias seen in a SOUL still resolves at call time.
- **Auth:** `Authorization: Bearer ${MCP_AUTH_TOKEN}` (from the app's `.env`) plus
  a `Mcp-Session-Id` established via the JSON-RPC `initialize` handshake; requests
  are plain JSON-RPC 2.0 POSTs (`Accept: application/json, text/event-stream`).
- **Scoping is the policy layer:** a Hermes profile's `mcp_servers.<name>.tools.include`
  filter + which endpoint it is attached to determines what that agent may do at
  all (see `W-ai/mcp-profile-map.md`; the Nov-9 audit showed the workspace profile's
  90 referenced tools all resolve across its five scoped endpoints).

---

## 4. Intended behaviour (the operating model)

These are the behaviours a correct PWR deployment should exhibit. Items 1-8 are
verified in code; 9-11 are documented intent with gaps.

1. **The room is where work starts.** A human posts a request in a project room
   (with @mention where needed). The message — not a CLI — is the interface.
2. **Agents are participants, not tools bolted on.** Bots are `User` records with
   attached Hermes profiles; they announce presence, join rooms, and post updates
   in-thread. MCP agents never auto-respond: the client side must run a
   `poll_messages` long-poll; silence in PWR means "nobody is polling", not "the
   agent decided not to answer".
3. **Delegation is explicit and cheap to audit.** A task is created *inside* PWR
   (`create_ai_task` or a human action), the dispatcher wakes the target profile by
   HTTP, the agent pulls context via `get_ai_task`, works, writes progress back,
   and closes with `update_ai_task(finished)`. Parent/child chains make agent-to-agent
   subdivision visible; `ai_task_cost` makes the money visible.
4. **Read before write.** Profiles are attached `read-mcp` *and* `action-mcp`
   deliberately so the intended call order is: read the room/project/task context
   → then mutate. The scope split exists to make careless writes impossible on
   restricted profiles.
5. **Human judgment is a gate, never an afterthought.** Anything requiring approval
   (a decision, knowledge publication, an external send, a release) must be raised
   as an approval request with an accompanying message; the accountable human's
   answer arrives via `add_decision_message`; the agent must not self-approve and
   must park the state at `waiting-for-approval`, not `done`. Approved decisions
   can auto-capture an ADR.
6. **Attention is budgeted.** Instead of free-form pings, agents file categorized
   attention items (decisions_waiting, blockers, risks, priorities, dependencies,
   mentions, outcomes_review, material_changes, learnings) so the human sees one
   queue with owners and dispositions.
7. **Parallel edits are serialized by policy.** Before editing a shared artifact,
   an agent checks conflicts, reserves, renews during work, releases after. Two
   agents on the same file is a defined failure mode with a defined prevention.
8. **Memory outlives chat.** Decisions, knowledge items, ADRs, directory structure,
   and activity logs are first-class records; topic/room-history snapshots make the
   conversation itself queryable later. The company keeps this memory when tools or
   models change (a core W-Manifesto claim, structurally supported).
9. **Events flow outward.** Every meaningful state change is recorded as an output
   event and delivered (with dedupe + retries) to configured external endpoints,
   enabling monitoring/automation without polling.
10. **Two-agent cooperation is the flagship demonstration** (design intent, not yet
    reproducible from public instructions): a person posts a task in a room; two
    agents divide the work, exchange updates, make planned file changes visible;
    the person follows the handoff and checks the result. Open item #20 in
    `questions on PWR.md`.
11. **One-prompt install is the adoption promise** (new in the `installation`
    branch, first-run flow still under test): `install.sh` / `install.ps1` prompts
    credentials (Infisical integration with fallback), `bootstrap.sh` brings up app +
    Hermes via Docker Compose (`pwrwork/space` + `nousresearch/hermes-agent`),
    `profile-env-collect.sh` harvests required env-var *names* from a profile
    distribution and interactively fills its `.env` (values never leave the machine;
    secret values are prompted, hidden-input), `to-profile-dist.sh` converts a live
    Hermes profile into a shippable `hermes profile install <git-url>` repository.

---

## 5. Current state and honest limitations (2026-11-09)

- Live dev server runs from `W/pwr`, branch `installation` (17 commits ahead of
  `main`, synced with origin, clean tree). Older checkouts (`chat/bonfire`, the
  pre-rename `Pavel/bonfire`) are stale or deleted.
- The app is **not yet a single-installable public product** (open item #3 in
  `questions on PWR.md`): W-ai, W-space and W-bridge are independent repos whose
  installation paths are still converging on the `installation` branch.
- Brand cleanup incomplete: remote is still `bonfire.git`; README carries legacy
  naming notes and one stale documented route (`/mcp/health`).
- Some documented capabilities are model/UI-level only, verified by filenames and
  README claims, not exercised end-to-end (UI demo pages, room-economics math,
  reservation enforcement under real contention).
- Tool surface caveats found in earlier audits: `token_budget` is not writable
  through `/task-mcp`'s `create_ai_task` (only `usd_budget`); `update_ai_task` has
  a narrow writable field set — hierarchy/budget/level fields are fixed at creation.
- GitHub issues/discussions are disabled on the repo (open item #6), which sits
  badly next to the "known place to report issues" launch goal (#8).

---

## 6. Source map (for verification)

| Claim area | Where to check |
|---|---|
| Product framing | `pwr/team-pack-en-2026-10-01/PWR-Work-strategy.md`, `PWR-Work-team-brief.md` |
| App description | `W/pwr/README.md` (note stale bits) |
| MCP endpoints/counts | live `POST /mcp` … `POST /config-mcp` tools/list; `config/routes.rb:274-279` |
| Tool implementations | `W/pwr/app/services/mcp/tools/*.rb` (13 files), `registry.rb`, `fuzzy_matcher.rb`, `call_logger.rb` |
| Dispatch loop | `app/services/ai_task_dispatch_loop.rb`, `ai_task_dispatcher.rb`, `app/services/hermes/` |
| Events out | `app/services/output_events/`, models `output_event*.rb` |
| Env/deployment | `docs/ENVIRONMENT_VARIABLES.md`, `.env.example`, `docker-compose.hub.yml` / `.build.yml`, `install.sh` |
| Agent profiles & policies | `W/W-ai/` (`worspace profile/`, `bot-skills/`, `message_analyzer/`, `mcp-tool-inventory.md`, `mcp-profile-map.md`) |
| Open questions / launch gaps | `W/W-ai/questions on PWR.md` |
