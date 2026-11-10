# PWR Intended-Functionality Checklist — fine-grained test plan

> Scope: the whole PWR repository (`W/pwr`, branch `installation`, live server
> localhost:3000) **plus** the Hermes agents that operate it: `workspace`,
> `message_analyzer`, and the AI-profile bots (`w_ai`, `market_research`, `pm`,
> `business_analyst`, `coder`, `main`).
> Tool names/counts verified against the live registry 2026-11-09
> (/mcp 163, /action-mcp 142, /read-mcp 78, /knowledge-mcp 29, /task-mcp 8,
> /config-mcp 16). Companion scripts: `pwr-feature-test-conversations.md`
> (message-level replay), `PWR explained.md` (feature map).
>
> **Item format:** `- [ ] <ID> — <test: exact call/entity> → <pass criterion>`.
> ⚠ marks a known/likely gap discovered while auditing — test it anyway; the
> checklist's job is to prove or disprove.

---

## 0. Prerequisites

- [ ] PRE-01 — `.env` present in repo root with `MCP_AUTH_TOKEN`, `HERMES_BASE_URI`, `HERMES_API_KEY` set → app boots, MCP auth passes
- [ ] PRE-02 — puma running from `W/pwr` → `GET /up` returns 200
- [ ] PRE-03 — dev DB `storage/db/development.sqlite3` exists and is the file touched by the running process (check `-shm`/`-wal` mtimes) → same DB asserted
- [ ] PRE-04 — Hermes API reachable at `HERMES_BASE_URI` (default `http://127.0.0.1:8642`) → dispatcher has a target
- [ ] PRE-05 — ⚠ README documents `GET /mcp/health` — assert it 404s and file the README fix (known stale doc)

## 1. MCP protocol & transport layer

- [ ] PRO-01 — `POST /mcp` with valid JSON-RPC `initialize` → 200 with `result.protocolVersion` + server capabilities incl. `tools`
- [ ] PRO-02 — response `Mcp-Session-Id` header returned by initialize → reuse it in follow-ups works; omitting it is rejected (assert exact behavior)
- [ ] PRO-03 — `tools/list` on each endpoint returns only that scope's tools (163/142/78/29/8/16) → counts match live baseline
- [ ] PRO-04 — `tools/list` advertises canonical names only → alias-only names absent (PRO-08 pairs)
- [ ] PRO-05 — `Accept: application/json` and `text/event-stream` both accepted for tools/call → content-type behavior asserted
- [ ] PRO-06 — malformed JSON-RPC (missing method) → JSON-RPC error object, not HTTP 500
- [ ] PRO-07 — unknown tool name → structured "tool not found" error, and `create_tool_cal_log`/CallLogger recorded the failed attempt (⚠ verify logging applies to failures)
- [ ] PRO-08 — call a tool by its alias → resolves via `Registry#tools_by_alias` to the same handler
- [ ] PRO-09 — every endpoint variant (`/action-mcp` etc.) hits the same `mcp#<scope>` controller → registry scoping honored per request
- [ ] PRO-10 — rate/size sanity: 1 MB rich-text message posts successfully → no silent body-size failure
- [ ] PRO-11 — concurrency: two parallel tools/call from different sessions → no cross-session bleed in returned context

## 2. Authentication & authorization

- [ ] AUT-01 — request without `Authorization: Bearer` → 401
- [ ] AUT-02 — wrong token → 401 (not 403 leak; assert message)
- [ ] AUT-03 — `DISABLE_API_ROUTES=true` in env → `/api/*` routes 404 while MCP still works; `false` re-enables → env contract holds
- [ ] AUT-04 — per-profile tool filter (Hermes `mcp_servers.<n>.tools.include`) → a profile attached to /read-mcp cannot call `add_message` (⚠ server-side scope is the real gate — verify the filter is client-side only and confirm server rejects action verbs on /read-mcp)
- [ ] AUT-05 — guest/scoped user (design-partner type) calling room tools for a non-member room → denied or filtered (assert current semantics)
- [ ] AUT-06 — ⚠ MCP tokens are shared-secret per server, not per agent → call logs attribute by `user_name`/`creator`, verify every mutating call carries an attributable identity in `tool_cal_logs`

## 3. Registry, fuzzy matching, call logging

- [ ] REG-01 — `fuzzy_matcher` resolves `user_name="kian"` (case/whitespace variants) → uid resolved without probing
- [ ] REG-02 — ambiguous fuzzy input (two users "Kian M.") → documented behavior: error with candidates, NOT first-match guess
- [ ] REG-03 — non-existent name → clean "not found" (matches transcript probe #131)
- [ ] REG-04 — `project_id` + `user_name` mix on one call → both resolve independently
- [ ] REG-05 — every successful call writes a call log row retrievable via `tool_cal_logs` + `get_tool_cal_log` (fields: tool name, args digest, user, room/project, outcome)
- [ ] REG-06 — call log immutability: `edit_tool_cal_log`/`update_tool_cal_log` — check what's editable and whether deletion is allowed (`delete_tool_cal_log` exists → ⚠ audit trail deletable? assert policy)
- [ ] REG-07 — registry `reset!` (server reload) re-registers all 13 tool files → no tool missing after restart

## 4. Rooms, membership, messaging

- [ ] MSG-01 — create project room (web or `add_message` precondition) → `Room` with project scoping, appears in `list_rooms`
- [ ] MSG-02 — thread/child room semantics → parent-child membership and visibility asserted
- [ ] MSG-03 — `add_message` plain text → stored as ActionText, readable via `search_messages_of_room`
- [ ] MSG-04 — `add_message` with HTML/`<pre>` blocks → sanitized per policy but code preserved (compare stored `action_text_rich_texts` body)
- [ ] MSG-05 — `add_message` with `@name` mention → `application/vnd.campfire.mention` attachment recorded; mentioned bot only reacts if its poller runs (see AGT-02)
- [ ] MSG-06 — attachment upload 📎 → ActiveStorage blob attached, URL served by message; large file (≤ `HERMES_EVENT_MAX_ATTACHMENT_BYTES`-class) posts
- [ ] MSG-07 — `delete_message` by author → removed/soft-deleted; `delete_message` by non-author → rejected (transcript probe #146/#156)
- [ ] MSG-08 — ⚠ message EDIT: no `edit_message`/`update_message` in the 163-tool surface → assert: is edit only web/API? If yes, file as surface gap (transcript edits 130/156/174 depend on it)
- [ ] MSG-09 — `add_loading_message` / `edit_loading_message` / `delete_loading_message` lifecycle → ephemeral UX message works and never persists as content
- [ ] MSG-10 — `add_action_message` → action message (with approval-request attach slot, see APP-03)
- [ ] MSG-11 — `add_mentions`/`edit_mentions` batch mention family → multi-mention message
- [ ] MSG-12 — room membership: add/remove member via UI/API → `get_room_members` reflects within one call
- [ ] MSG-13 — presence: user states online/idle/offline (⚠ no MCP tool for presence — verify via API/UI only; file gap if agents can't set presence)
- [ ] MSG-14 — `boost` reaction on message (web) → ⚠ not in MCP surface; assert UI works + counts visible where promised
- [ ] MSG-15 — message ordering: ids strictly increase within a room, interleaved rooms share the global sequence (transcript invariant)
- [ ] MSG-16 — pagination/history: reading room history returns latest window; no cap surprises
- [ ] MSG-17 — unfurl/`opengraph`: posted link renders preview asset (web path) → served without error

## 5. Topics & room history

- [ ] TOP-01 — `create_topic` on a room → returned by `topics`/`get_topic`
- [ ] TOP-02 — `create_message_topic` linking message→topic; `update_message_topic`/`delete_message_topic` → link state consistent via `message_topics`, `get_message_topic`
- [ ] TOP-03 — parent/child topic structure → `room_topic_tree` renders the hierarchy correctly
- [ ] TOP-04 — `create_room_history_topic` snapshot → topic-scoped history content matches messages at snapshot time (the "topic-scoped room history snapshots" feature from branch `top-search`)
- [ ] TOP-05 — `update_room_history_topic` / `delete_room_history_topic` → snapshot mutation rules asserted (⚠ can an agent rewrite a history snapshot? check policy)
- [ ] TOP-06 — `search_topics` by keyword → returns topics across member rooms only
- [ ] TOP-07 — `room_context_summary` → summary grounded in actual recent messages (spot-check 3 facts against real stream)
- [ ] TOP-08 — context tools on empty room → graceful empty result, not exception

## 6. AI tasks & Hermes dispatch loop

- [ ] TSK-01 — `create_ai_task` minimal fields (description, profile target, room, level, budgets) → returns id; `dispatched=false` initially
- [ ] TSK-02 — ⚠ `create_ai_task` with `token_budget` → expect REJECTED/ignored (verified MCP gap; only `usd_budget` writable) — record actual behavior
- [ ] TSK-03 — dispatcher within `AI_TASK_DISPATCH_INTERVAL_SECONDS` → POST chat completion to `HERMES_BASE_URI` with wake text "you have new task with id N"; `dispatched` flips true (transcript 103→104)
- [ ] TSK-04 — wake routes by profile: target profile = `HERMES_DEFAULT_PROFILE` unless overridden → correct Hermes profile receives (assert `OUTPUT_*_PROFILE` envs respected)
- [ ] TSK-05 — `get_ai_task` from the woken agent → full context (room_id, project_id, parent chain, budgets)
- [ ] TSK-06 — `get_ai_task_children` / `get_ai_task_parents` → hierarchy traversal both directions (transcript 165/228)
- [ ] TSK-07 — `update_ai_task` writable set: `description`, profiles, `dispatched`, `finished`, `topic_id` → all succeed
- [ ] TSK-08 — `update_ai_task` locked set: `project_id`, `room_id`, `level`, `parent_task_id`, `grand_parent_id`, budgets, `importance` → all rejected/no-op (transcript 152/158); ⚠ assert error clarity
- [ ] TSK-09 — `delete_ai_task` → children behavior asserted (orphaned? cascade? blocked if dispatched?)
- [ ] TSK-10 — `ai_tasks` list filters (room, profile, state) → returns exactly the matching set
- [ ] TSK-11 — `ai_task_cost` → per-task cost rollup present after agent activity; ⚠ read-scope quirk (cost only on some scopes) — confirm which endpoint serves it
- [ ] TSK-12 — `HERMES_MAX_ACTIVE_AGENTS=2` → third simultaneous task waits; no lost dispatch (queue, not drop)
- [ ] TSK-13 — Hermes API down at dispatch → retries/no crash; task remains undispatched and recoverable (⚠ verify retry exists — dispatch loop may mark dispatched blindly)
- [ ] TSK-14 — task finished without update call → stays open; loop must NOT auto-close anything
- [ ] TSK-15 — task in `finished` state re-updated → assert transition legality
- [ ] TSK-16 — `add_ai_confirm`/`ai_confirm`/`edit_ai_confirm` → human-confirmation flow round-trip
- [ ] TSK-17 — importance/attention coupling: high-importance `create_message_analysis` → task or attention item actually created by the analyzer profile (see AGT-10)
- [ ] TSK-18 — budget gate: task exceeding `usd_budget` → what happens? (assert alert exists or file gap — the strategy claims economic visibility)

## 7. Approvals & decisions

- [ ] APP-01 — `add_approval_request` standalone → appears in `approval_requests`, state `waiting-for-approval`
- [ ] APP-02 — `add_approve_request_with_message` → approval + explanatory action message atomically linked (transcript 184)
- [ ] APP-03 — approval request carries: target, scope, boundary, evidence → all four fields present/required in schema (per approval discipline)
- [ ] APP-04 — `edit_approval_request` before decision → mutable; after decision → immutable (assert ledger lock)
- [ ] APP-05 — `delete_approval_request` → ⚠ allowed? audit trail must survive; assert tombstone or rejection
- [ ] APP-06 — `add_decision_message` by HUMAN (uid 2/3) → decision recorded; transitions ledger appended
- [ ] APP-07 — `add_decision_message` by BOT profile → rejected at server if possible, else flag as SOUL-only guard (⚠ current enforcement is behavioral, not server-side — transcript invariant "bots never call it")
- [ ] APP-08 — approval → auto-ADR: decision on an approval request produces `add_project_decision_record` / `project_decision_records` entry (transcript 110/187/249)
- [ ] APP-09 — `decisions` / `decisions_waiting` reads → categories populated correctly
- [ ] APP-10 — state machine: waiting → approved/denied/cancelled → no transitions beyond these; every transition has actor+timestamp
- [ ] APP-11 — cross-room approval: raised in build/partners, resolved only in decision_room (type `DecisionRoom`) → routing rules enforceable? assert what the model does vs what rooms docs promise
- [ ] APP-12 — `room_decision_context` in build → lists decisions affecting that room (ADR-001..N)
- [ ] APP-13 — waiting-for-approval work item status → project todo/task cannot be marked done while linked approval open (⚠ verify linkage exists; if not, file as gap: status discipline is SOUL-only)

## 8. Attention items — per-category coverage matrix

Canonical categories (AttentionItem::CATEGORIES, singular inbound → plural
normalized). For EACH category: add/edit/delete/resolve transition + pending/
resolved/dismissed states + `attention_items` filter.

- [ ] ATT-01 — decisions_waiting: `add_decisions_waiting`/`edit_decisions_waiting` → resolve/dismiss transitions pass
- [ ] ATT-02 — blockers: `add_blockers`/`edit_blockers` → same lifecycle (transcript 120/122)
- [ ] ATT-03 — mentions: `add_mentions`/`edit_mentions` → lifecycle pass
- [ ] ATT-04 — material_changes: `add_material_changes`/`edit_material_changes` → lifecycle pass
- [ ] ATT-05 — outcomes_review: `add_outcomes_review`/`edit_outcomes_review` → lifecycle pass (weekly review ritual, transcript 133/175/213/230)
- [ ] ATT-06 — knowledge_proposals: `add_knowledge_proposals`/`edit_knowledge_proposals` → approve→knowledge item promotion works
- [ ] ATT-07 — ⚠ risks: READ `risks` exists, NO `add_risks`/`edit_risks` on the live surface → verify: created only via API/web? file MCP gap (transcript #170 assumed add_risks)
- [ ] ATT-08 — ⚠ priorities: read-only like risks → same assertion
- [ ] ATT-09 — ⚠ dependencies: read-only → same
- [ ] ATT-10 — ⚠ learnings: read-only → same
- [ ] ATT-11 — ⚠ changes/decisions reads: distinguish from material_changes family
- [ ] ATT-12 — `delete_attention_item` works for any category → deletion vs resolve semantics asserted (⚠ deletion erases the trail — see REG-05)
- [ ] ATT-13 — singular input normalization ("decision_waiting") → canonical plural key used in storage/filter
- [ ] ATT-14 — per-item fields: owner/assignee, category, status, source link (message id) → evidence-linked attention works (partners #179 self-filed blocker)

## 9. Knowledge families (the long-lived memory plane)

- [ ] KNW-01 — `add_project_knowledge_item` → `project_knowledge_items`/get returns item; fields per schema
- [ ] KNW-02 — knowledge lifecycle: draft→review→approved→published→archived → each transition reachable & logged (status machine asserted)
- [ ] KNW-03 — `add_knowledge_proposals` → attention item raised (cross-check ATT-06) → approval promotes to knowledge item
- [ ] KNW-04 — `add_knowledge_summary_item` / `edit` / `delete` / `knowledge_summary_items` → summary CRUD + room-level summary generation
- [ ] KNW-05 — `add_knowledge_activity_log` / `edit` / `delete` / `knowledge_activity_log` → activity trail for knowledge work
- [ ] KNW-06 — `add_external_knowledge_asset` (title,url,description) → asset stored; fetch/unfurl tolerates dead URL (⚠ SSRF guard: `lib/restricted_http` exists — assert localhost/metadata endpoints blocked)
- [ ] KNW-07 — `add_tree_based_project_directory_item` → `tree_based_project_directory_data` renders tree; move/reparent via edit → order/parent updates
- [ ] KNW-08 — `add_project_note`/`project_note` CRUD → notes attach to project (and to other attachables per the rails_ext/action_text_attachables hook)
- [ ] KNW-09 — ADRs: `add_project_decision_record` + `project_decision_records` list/get/edit/delete → ADR fields (decision, deciders, context, consequences) enforced per template
- [ ] KNW-10 — `add_project_bottleneck`/`edit`/`delete`/`project_bottlenecks` → CRUD + link to milestone/room
- [ ] KNW-11 — `add_project_milestone`/`edit`/`delete`/`project_milestones` → due dates, completion state
- [ ] KNW-12 — `add_project_todo`/`edit`/`delete`/`project_todos` → owner+deadline; ⚠ no `kanban`-named surface — confirm `project_todos` IS the kanban board backing (Hermes `hermes kanban` vs PWR todos distinction)
- [ ] KNW-13 — knowledge scoping: per-project isolation → cross-project leakage negative test
- [ ] KNW-14 — Obsidian consistency (W-ai side): mirror workflow keeps knowledge items ↔ obsidian notes aligned (process check, not server)
- [ ] KNW-15 — message↔knowledge citation: knowledge item references message ids and `get` still resolves after message delete (tombstone/dangling behavior asserted)

## 10. Company-level entities

- [ ] CMP-01 — `add_company_status_period`/`edit_company_status_period`/`company_status_period` → period CRUD; ⚠ no delete tool — assert UI-only deletion
- [ ] CMP-02 — company status items (model exists, tool family thin) → verify items created how? file gap if UI-only while docs imply MCP
- [ ] CMP-03 — all-hands trio: `add/get/edit/delete` for action_item, decision, takeaway; meeting itself created where? ⚠ no `add_project_all_hands_meeting` tool — assert UI-only + linkage works
- [ ] CMP-04 — company home attention: attention_items aggregate across projects → the "company-home" queue view/API matches MCP counts
- [ ] CMP-05 — projects: read family `get_projects`, `get_single_project`, `get_user_projects`, `get_project_users` → ⚠ project CREATE/EDIT/DELETE not in MCP surface (human-only by design?) — assert intent and document
- [ ] CMP-06 — users/bots: `get_users` + fuzzy; bot users distinguished from humans in member lists (bots 4-7 vs humans 2,3)
- [ ] CMP-07 — first-run flow (`FirstRun` model + `first_runs_controller`) → fresh DB walk-through creates admin (DEFAULT_ADMIN_* envs) exactly once; subsequent hits redirect

## 11. AI configuration plane (PWR knows its agents)

- [ ] AIC-01 — `list_ai_profiles` / `get_ai_profile` → workspace/message_analyzer/bots present with attached MCPs/tools/skills (mirrors reality)
- [ ] AIC-02 — `list_ai_profile_mcps` / `get_ai_profile_mcp` → endpoint list per profile (the soul precondition)
- [ ] AIC-03 — `list_ai_profile_tools` / `get_ai_profile_tool`, `list_ai_profile_skills` / `get_ai_profile_skill` → attachment truth table
- [ ] AIC-04 — `list_tools` / `get_tool`, `list_skills` / `get_skill`, `list_mcps` / `get_mcp` → global catalog vs profile-scoped attachment distinction asserted
- [ ] AIC-05 — `list_ai_settings` / `get_ai_setting` → settings visible without leaking secret VALUES (names-only contract)
- [ ] AIC-06 — edit an attachment via UI (api `ai_profile_mcps_controller`) → MCP `get_ai_profile_mcp` reflects change without restart
- [ ] AIC-07 — `ENABLE_AI_CONFIG_PAGE=FALSE` → page disabled (env contract)
- [ ] AIC-08 — the cost quirk from the map doc (`ai_task_cost` read-scope) → still present or fixed? re-assert endpoint placement

## 12. File reservation & collision safety

- [ ] RES-01 — ⚠ **surface check**: no reservation tools in the 163-name MCP list → verify how agents reserve (API-only? model-only?). If absent from MCP while README promises "inspect conflicts / reserve / renew / release" for agents → FILE the top-priority surface gap (transcript #109/132/204/235 assume MCP reservations)
- [ ] RES-02 — reserve file → second reserver sees conflict (409-class) via whatever surface exists
- [ ] RES-03 — renew extends TTL; expiry auto-releases → timed test
- [ ] RES-04 — explicit release → other party can acquire
- [ ] RES-05 — release/expire while work open → behavior on dangling edits asserted

## 13. Search & discovery

- [ ] SRCH-01 — `search_rooms` scoped to membership → non-member rooms excluded
- [ ] SRCH-02 — `search_messages_of_room` by phrase → hits ordered; deleted messages excluded
- [ ] SRCH-03 — cross-entity `Search` model (web UI search box) → parity with MCP search results or documented difference
- [ ] SRCH-04 — search special chars / injection strings → no 500, sane escaping

## 14. Output events (business-event egress)

- [ ] OUT-01 — approve an approval → output event recorded (dedup key present)
- [ ] OUT-02 — delivery retry with dead endpoint → backoff, no event loss; `EVENT_RECOVERY_MAX_AGE_SECONDS` honored (stale events dropped per config)
- [ ] OUT-03 — `EVENT_MERGE_SETTLE_SECONDS` → rapid double events merge/dedupe (1.5s window)
- [ ] OUT-04 — payload carries `knowledge_path` resolution → path matches memory-hierarchy contract
- [ ] OUT-05 — attachment caps: `HERMES_EVENT_MAX_ATTACHMENTS=5`, `..._BYTES` → oversized attachment skipped with marker, event still delivered
- [ ] OUT-06 — per-event emission policy → disabled event type does not fire
- [ ] OUT-07 — `OUTPUT_*_PROFILE` routing (messages/ai settings/workspace) → events land on configured profile
- [ ] OUT-08 — legacy `OUTPUT_EVENTS_URL/TOKEN` present → still works or cleanly deprecation-warned (docs say legacy)

## 15. Notifications & web platform

- [ ] PSH-01 — VAPID keys set → browser subscribes, room message triggers web-push
- [ ] PSH-02 — missing VAPID keys → app boots; push silently disabled (no crash)
- [ ] PSH-03 — PWA routes (`pwa_controller`) → manifest/sw served
- [ ] PSH-04 — ⚠ MCP clients get NO push — reply expectation only via poll (long-poll contract asserted in AGT section)

## 16. Install, ops & deployment scripts

- [ ] INS-01 — `install.sh` on fresh clone: prompts credentials (hidden input for KEY/TOKEN/SECRET names), writes `.env`, idempotent on re-run ("write_or_keep_env")
- [ ] INS-02 — Infisical path: configured → values pulled; absent → fallback prompts (`generate_infisical_fallback`)
- [ ] INS-03 — `bootstrap.sh` → app + hermes containers via `docker-compose.hub.yml` (`pwrwork/space` + `nousresearch/hermes-agent`); persistent SQLite volume survives `down/up`
- [ ] INS-04 — `docker-compose.build.yml` builds local image → app healthy, MCP counts unchanged
- [ ] INS-05 — `profile-env-collect.sh --dry-run` on a distribution repo → lists env NAMES only, values never printed
- [ ] INS-06 — `profile-env-collect.sh --install` → profile installed + `.env` mode 600, merge-preserving (existing keys kept)
- [ ] INS-07 — `to-profile-dist.sh PROFILE` → distribution.yaml + owned files shipped; `.env`/memories/sessions/state.db NEVER shipped; secret VALUES never leave machine (names only in template)
- [ ] INS-08 — env rename tolerance: legacy `BASE_URI`/`STATUS_BASE_URI`/`MODEL`/`API_SERVER_KEY` still accepted (docs claim) → boot succeeds with legacy-only set
- [ ] INS-09 — `RESTART_TRIGGER_PATH` touch → app restarts (rolling restart hook)
- [ ] INS-10 — `install.ps1` parity spot-check (Windows path): same prompts, same env keys
- [ ] INS-11 — first-run after clean-install via installer → defaults (admin@pwrwork.local) work end-to-end — the launch claim under test (`questions on PWR.md` #4/#7)

## 17. Hermes-side integration & agent behaviour

Agents: profiles `workspace`, `message_analyzer`, bots `w_ai`, `market_research`, `pm`, `business_analyst`, `coder` (+ `main`).

- [ ] AGT-01 — each profile's `config.yaml`/`mcp.json` attaches the CORRECT scoped endpoints (workspace: action+read+knowledge+task+config; message_analyzer: knowledge+task; bots: per their skill map) → `list_ai_profile_mcps` mirrors it
- [ ] AGT-02 — **no auto-respond invariant**: human posts mention to a bot → bot replies ONLY when its client poller runs `poll_messages` long-poll; kill the poller → room silence (this is the documented platform behavior, verify it holds per agent)
- [ ] AGT-03 — MCP `${VAR}` headers resolve from the ACTIVE profile's own `.env` → wrong-profile env doesn't leak; missing var → clear auth failure
- [ ] AGT-04 — `hermes mcp configure` include/exclude filter actually removes tools from a profile's toolset (server-scope is still the hard gate — AUT-04)
- [ ] AGT-05 — no hot reload: change a profile's server config on a RUNNING profile → old connection persists; restart → new surface. Assert and document per agent
- [ ] AGT-06 — workspace read-before-write ladder: its SOUL-required sequence (context read → write) observed in `tool_cal_logs` ordering for a real task
- [ ] AGT-07 — workspace full-execution audit re-run: all ~90 tools its skills/SOUL v3 reference resolve on its 5 endpoints (regression of the Nov-9 clean audit)
- [ ] AGT-08 — w_ai scoping: answers only within asker's projects+rooms; out-of-scope question → refusal behavior asserted
- [ ] AGT-09 — market_research evidence rule: every claim posted carries source (external asset or link) — sample 5 messages
- [ ] AGT-10 — message_analyzer pipeline E2E: room message → `create_message_analysis` (importance≥4) → creates AI task and/or `decisions_waiting` attention item within one dispatch cycle
- [ ] AGT-11 — analyzer threshold edge: importance below threshold → NO task raised (false-positive check, 10 messages)
- [ ] AGT-12 — analyzer dedup: same message analyzed twice → single downstream artifact (dedup rule asserted)
- [ ] AGT-13 — coder executes a real file-change task: reservation step IF available (RES-01), progress updates cite task id, `update_ai_task(finished)` + evidence link
- [ ] AGT-14 — pm / business_analyst: requirement/todo outputs land as `add_project_todo` with owner+deadline (their skill contract), not chat-only
- [ ] AGT-15 — approval discipline per agent: no bot ever self-decides (APP-07) and none marks waiting-for-approval work `done` (APP-13) — sweep `tool_cal_logs` for violations
- [ ] AGT-16 — two-agent cooperation (flagship demo): two agents split one parent task, exchange updates visible in room, person approves handoff — full transcript replay of the "two agents" story from `PWR-Work-team-brief` (open item #13/#20)
- [ ] AGT-17 — dispatch storm: create 10 tasks → `HERMES_MAX_ACTIVE_AGENTS` respected across profiles, no profile double-woken on same task
- [ ] AGT-18 — profile wake target override: task created for `coder` wakes coder, not `delegator` default (TSK-04 extension)

## 18. Cross-cutting invariants & negative battery

- [ ] INV-01 — every mutating tool call is attributable (user id) in `tool_cal_logs` — sweep test
- [ ] INV-02 — message ids monotonic globally across rooms (transcript invariant) — `SELECT max(id)` growth check
- [ ] INV-03 — deletion semantics matrix: which deletes are tombstones vs erasures (messages, todos, tasks, knowledge, call logs, approvals) — document each
- [ ] INV-04 — timezone handling: timestamps stored/serialized +03:30-correct (user's TZ) — create at known time, read back, compare
- [ ] INV-05 — HTML-injection: `<script>` in message body → sanitized in render, harmless in `room_context_summary` output
- [ ] INV-06 — unicode/emoji/persian text in messages & knowledge titles → round-trip intact
- [ ] INV-07 — duplicate-name fuzzy hazard: two rooms "receipts-build " (trailing space) → resolution not silently ambiguous
- [ ] INV-08 — restart durability: restart puma mid-poll → sessions resume; undispatched tasks redelivered or not (assert exact)
- [ ] INV-09 — scope leak battery: `add_*` on /read-mcp, `create_ai_task` on /knowledge-mcp etc. → all rejected with clear errors
- [ ] INV-10 — alias drift: SOULs cite alias names; assert each alias still resolves (the 4 alias-only names from the audit: get_projects etc.)
- [ ] INV-11 — naming consistency: legacy "bonfire/campfire" identifiers visible to users? (`sgid gid://bonfire/...`, `vnd.campfire.mention`) → brand-cleanup checklist item, note every user-facing leak
- [ ] INV-12 — README/API-doc parity: every documented route/flag/env re-asserted against code (found already: `/mcp/health` stale — PRO-05)

## 19. Known-gap ledger (pre-filled from this audit — verify, then file)

1. `token_budget` not writable via task-mcp (TSK-02)
2. `update_ai_task` locked fields fail opaquely (TSK-08)
3. File reservation absent from MCP tool surface (RES-01) — README promises it to agents
4. Presence + boosts/reactions UI-only, not in MCP (MSG-13/14)
5. risks/priorities/dependencies/learnings attention categories read-only via MCP (ATT-07..10)
6. Message edit absent from MCP surface (MSG-08)
7. Project create/update/delete human-only by design? confirm + document (CMP-05)
8. All-hands "meeting" entity has no MCP tool (CMP-03)
9. Company status items thin vs model richness (CMP-02)
10. `delete_*` on audit trails (tool_cal_logs, approval requests) — immutability policy missing (REG-06, APP-05)
11. Server-side per-agent permission model beyond endpoint scoping (AUT-04/06) — decision-authorship is SOUL-enforced, not server-enforced (APP-07)
12. Legacy bonfire/campfire identifiers leaking in user-facing payloads (INV-11)

---

## Suggested execution order

1. PRO → AUT → REG (protocol trust first)
2. MSG → TOP → ATT → APP → TSK (the collaboration core, incl. dispatch E2E)
3. KNW → CMP → AIC → RES → SRCH → OUT → PSH (memory + periphery)
4. INS (fresh-VM clean install = the launch-critical path)
5. AGT (each profile in isolation, then AGT-16 two-agent flagship)
6. INV battery + §19 gap ledger → file as issues (once GitHub issues are enabled;
   see `questions on PWR.md` #6/#8)

Result template per run: `ID | PASS/FAIL/GAP | evidence (tool_cal_log id / message id / screenshot)`.
