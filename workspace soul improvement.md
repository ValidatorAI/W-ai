# Workspace SOUL Improvement Plan

Target file: `W-ai/possible workspace soul.md` (the PWR workspace action-router SOUL)
Standard used for comparison: `W-ai/message analyzer soul.md`
Prepared: 2026-10-25. All tool facts below were verified against the live server on localhost:3000 (tools/list snapshots per endpoint) and against `W/pwr` source (`config/routes.rb`, `app/services/mcp.rb`, `app/services/mcp/registry.rb`, `app/services/mcp/tools/*.rb`). Re-verify against `tools/list` before applying any name/schema line to the SOUL.

---

## 1. Verdict on the current draft

The draft is structurally sound (identity, routing categories, workflow, tool-selection rules, approval rule, examples) and its recent "native MCP endpoints" section is factually real — all five endpoints exist and answer. But it is not yet executable as a program for a low-end model (28B class):

1. One live-surface contradiction: project-knowledge write tools are mapped to `/knowledge-mcp`, where they do not exist.
2. One impossible instruction: workflow step 10 says "update the task result or task status" — the task update tool has no status or result field.
3. One agent-level impossibility: the SOUL tells the model to "route work to the matching domain endpoint" per call, but endpoints are chosen at MCP-connection config time; the model sees only one static toolset.
4. Two mis-mapped message tools: `add_action_message` takes no body (it is a room action/typing indicator), and `add_decision_message` records a decision against an existing `approval_request_id` — neither is a "send an update / announce a decision" tool.
5. Everything that makes the message-analyzer SOUL reliable for small models is missing: scored rubric, entity field dictionary with required args, dedup/idempotency rule, per-run caps, worked JSON traces, approval run-lifecycle, closed outcome vocabulary, named context-lookup tools.

## 2. Wave ordering and why

Order matters: a small model obeys exact tool names and copyable templates before it obeys prose rules. Fix facts first (Wave 1), because every later edit would inherit the contradictions; then give the model copyable payloads (Wave 2); then decision quality (Wave 3); then examples and layout polish (Wave 4); then the test harness that proves the result (Wave 5). Each wave has a gate; do not start the next wave until the gate passes.

Execution order: **Wave 1 → 2 → 3 → 4 → 5**, improvements in numeric order inside each wave.

Workflow constraints that apply to every wave (standing rules):
- Edit the W-ai source tree first, mirror to loaded profiles after.
- Additive edits only: extend or replace defective lines, never delete working content without a recorded decision.
- Produce a unified-diff patch per round for review before mirroring.
- SOUL.md is read per session; no restart needed after mirroring.

---

## 3. Wave 1 — Live-surface corrections (P0, blocking)

### IMP-01 Fix the knowledge-endpoint mapping
- Problem: "knowledge capture and project knowledge retrieval: `/knowledge-mcp`" is wrong for half the family. Verified live: `/knowledge-mcp` (29 tools) contains the topics/analysis family (`search_topics`, `room_topic_tree`, `message_analysis`, `room_history_topics`, `topic_tool_call_logs`). It does NOT contain the project-knowledge writes the SOUL lists (`add_project_knowledge_item`, `add_project_decision_record`, `add_external_knowledge_asset`, `add_knowledge_activity_log`, `add_tree_based_project_directory_item` — these register only `all action` scopes in `app/services/mcp.rb` and live on `/action-mcp`, 142 tools).
- Change: split the bullet into two: "project knowledge records (add/edit): `/action-mcp`" and "topics, message analysis, room history, tool-call logs: `/knowledge-mcp`".
- Acceptance: every tool named next to an endpoint appears in that endpoint's `tools/list`.

### IMP-02 Replace per-call endpoint routing with a connection contract
- Problem: "The profile should route work to the matching domain endpoint" is not actionable by the model; a Hermes profile connects to one MCP server URL and cannot switch endpoints per call. Scope enforcement lives server-side (`registry.rb#find_tool` errors with "Tool not found in scope").
- Change: rewrite the section as a deployment contract, not agent behavior:
  - State which endpoint this profile is intended to be connected to (recommendation below).
  - Add the rule: "Only call tools present in your current tool list. A tool you expect but do not see means the endpoint connection is missing — record that reason in the task and stop; never invent a call."
- Connection recommendation: connect `/task-mcp` (9 tools) + `/action-mcp` (142) OR a single `/mcp` (163) plus Hermes per-server tool filters (`mcp_servers.<name>.tools.include`) narrowed to the ~40 tools in this SOUL's tool-selection section. The endpoint split is the token-weapon: a 28B model should never see 163 schemas.
- Acceptance: the SOUL names exactly one intended connection set, and every tool in the SOUL is inside that set.

### IMP-03 Fix step 10 — the task writeback convention
- Problem: "Update the task result or task status" — verified live, `update_ai_task` accepts only `task_id` (required), `description`, `adder_profile`, `assigneee_profile`, `added_to_kanban`, `runned`. There is no status/result field anywhere in the task tool family.
- Change: define the writeback convention explicitly:
  - Close every run with `update_ai_task`: set `runned: true`; append an outcome line to `description`, e.g. `WS-OUTCOME: acted — blocker #123 created, approval #45 pending`.
  - Keep the outcome vocabulary closed (IMP-14): `nothing_to_do | routed | acted | pending_approval | unclear_escalated`.
  - "keep the task visible" maps to a real field: `added_to_kanban: true`.
- Also fix Example 1, which repeats the impossible "update the task status" step.
- Acceptance: every workflow step in the SOUL resolves to a tool call whose arguments exist in the live schema.

### IMP-04 Fix the message-tool mappings
- Problem (verified schemas): `add_action_message` takes `room_id/room_name`, `project_id/project_name`, `action_type` — no body; it is a room action indicator, not "action-oriented updates". `add_decision_message` requires `approval_request_id` + `decision` (+ optional `note`) — it records a human's decision on an existing approval request, not general "decision communication".
- Change:
  - Content into a room → `add_message` (required: `body`).
  - `add_action_message` → labeled as typing/action indicator; remove the "action-oriented updates" claim.
  - `add_decision_message` → usable only when relaying a recorded human decision on an approval request; the agent must never invent the decision value on its own (standing approval discipline: the accountable human decides).
- Acceptance: no SOUL bullet claims a capability a required argument forbids.

### IMP-05 Define the audit trail concretely
- Problem: "log it through the relevant record or task trail" — "task trail" is undefined; "relevant record" names nothing.
- Change: name the two real trail tools and when each applies:
  - `create_topic_tool_call_log` (on `/action-mcp` and `/knowledge-mcp`; required: `used_tool_name`; fields: `topic_id`, `room_id`, `project_id`, `target_entity_id`, `change_log`, `why_was_it_required`) — for tool actions tied to a topic/room/project; this is the same entity the message-analyzer standard defines, so the two SOULs share one audit model.
  - `add_knowledge_activity_log` (required: `actor_name`, `action_text`; optional `project_id/project_name`, `target_path`, `target_url`) — for project-level knowledge state changes.
- Acceptance: workflow steps 9 and "log the action" in examples resolve to one of these two calls with exact fields.

---

## 4. Wave 2 — Executability scaffolding (P0/P1 for 28B)

### IMP-06 Add an entity dictionary with verified call templates
- Problem: the SOUL lists ~30 entity names and zero fields. A small model cannot build a payload it has never seen. The standard file defines every entity field-by-field with example values — copy that discipline for the entities this router actually writes.
- Change: add a "Tool call templates" reference section. Use the verified schemas (all name-resolution arguments below are confirmed live; prefer passing names and letting the tool fuzzy-match):

| Tool (endpoint) | Required | Optional (most-used) |
|---|---|---|
| `get_ai_task` (task) | `task_id` | — |
| `ai_tasks` (task) | — | `project_id`, `room_id`, `parent_task_id`, `runned`, `added_to_kanban`, `page/per_page` |
| `create_ai_task` (task) | `description` | `project_id`, `room_id`, `parent_task_id`, `adder_profile`, `assigneee_profile`, `importance`, `level` |
| `update_ai_task` (task) | `task_id` | `description`, `assigneee_profile`, `added_to_kanban`, `runned` |
| `add_blockers` / `add_decisions_waiting` / `add_mentions` / `add_material_changes` / `add_ai_confirm` / `add_knowledge_proposals` / `add_outcomes_review` (action) | `title` | `meta_text`, `action_label`, `due_at`, `overdue`, `project_id|project_name`, `room_id|room_name`, `user_id|user_name` |
| `attention_items` (action/read) | — | `item_id`, `category`, `status`, `project_id`, `user_id`, `delete`, paging |
| `add_project_todo` (action) | `title` | `project_id|project_name`, `completed`, `meta_text` |
| `add_project_milestone` (action) | `title` | `project_id|project_name`, `target_date`, `status`, `active` |
| `add_project_bottleneck` (action) | `title` | `project_id|project_name`, `description`, `severity`, `resolved` |
| `add_company_status_period` (action) | `name` | `slug`, `starts_on`, `ends_on`, `current` |
| `priorities`/`progress`/`risks`/`dependencies`/`changes`/`decisions`/`learnings` (action/read) | see IMP-07 | `item_id`, `company_status_period_id`, `title`, `summary`, `details`, `status`, `health`, `badge`, `owner_name`, `percent`, `evidence`, `impact`, `delete` |
| `add_message` (action) | `body` | `room_id|room_name`, `project_id|project_name`, `user_id|user_name`, `bot_id|bot_name` |
| `add_approval_request` (action) | — (defaults: `request_type` "action", `payload` {}, `status` "pending") | `room_id|room_name`, `project_id|project_name`, `message_id`, `request_type`, `payload` |
| `add_approve_request_with_message` (action) | `body` | same as above — the one-call pattern the router should prefer for the approval gate |
| `approval_requests` (action/read) | — | `request_id`, `room_id`, `status`, `delete`, paging |
| `add_project_knowledge_item` (action) | `title` | `project_id|project_name`, `description`, `badge`, `active` |
| `add_project_decision_record` (action) | `title`-family, see live schema | per tools/list |
| `create_topic_tool_call_log` (action, knowledge) | `used_tool_name` | `topic_id`, `room_id`, `project_id`, `target_entity_id`, `change_log`, `why_was_it_required` |
| `add_knowledge_activity_log` (action) | `actor_name`, `action_text` | `project_id|project_name`, `target_path`, `target_url`, `actor_color` |
| `get_single_project` (read) | — | `project_id|project_name|project_slug` |
| `search_rooms` (read) | `query` | `project_id`, paging |
| `get_project_users` (read) | — | `project_id|project_name` |

- Name-resolution rule to state explicitly: when the task carries a name instead of an id, pass `project_name` / `room_name` / `user_name` directly — these tools fuzzy-match natively. The agent must not probe the backend for ids first, and must never invent ids.
- Acceptance: for each of the router's create/update verbs, the SOUL shows required fields and one example payload.

### IMP-07 Document the implicit verb dispatch of multi-verb tools
- Problem: `priorities`, `progress`, `risks`, ... have no `action` parameter (verified). Dispatch is by argument presence (verified in `company_status.rb` `StatusItemCategoryBaseTool#execute`):
  - no args → list; `title` (without `item_id`) → create into the current period (auto-creating "Current Period" if none); `item_id` → get; `item_id` + field(s) → update; `item_id` + `delete: true` → delete.
  Same pattern for `attention_items`, `approval_requests`, `ai_tasks`.
- Change: state this dispatch table once, short form, under the tool templates; the SOUL's current phrasing "use `priorities` ... to update the current status view" is under-specified.
- Acceptance: a reader can answer "what exact args create vs update vs list?" from the SOUL alone.

### IMP-08 Add the dedup / idempotency rule
- Problem: none exists; re-runs duplicate blockers, todos, approvals, messages. The standard's "check existing by key first, never create a duplicate; always search before creating" has no counterpart here.
- Change: add a rule per entity family before any create:
  - attention items → `attention_items` filtered by `project_id`/`category`, match on subject;
  - todos/milestones/bottlenecks → `project_todos`/`project_milestones`/`project_bottlenecks` list, match on title;
  - approvals → `approval_requests` with `status: "pending"` for the same room/message;
  - tasks → `ai_tasks` filtered by `parent_task_id`/`room_id`, and check the incoming task's `runned` flag first (already-runned task → no action).
  - If a matching record exists: update it (`edit_*` / merged writeback), never create a second one.
- Acceptance: every `add_*`/`create_*` instruction in the SOUL is preceded by the matching list/search step.

### IMP-09 Add per-run caps
- Problem: unbounded output; the standard caps ("at most 1 new topic", "at most 3 links").
- Change: "Per task run: at most 1 primary PWR record; at most 2 secondary records (message, trail log); at most 1 room message; at most 1 approval request."
- Acceptance: caps stated once, quoted in examples.

---

## 5. Wave 3 — Decision quality (P1)

### IMP-10 Add a scored actionability rubric
- Problem: the Threshold section is qualitative ("a real decision", "routine noise"). The standard's 0-5 table + adjustment rules + tie-break is what makes classification stable on small models.
- Change: add an importance table for the incoming task's content (reuse the standard's wording where the semantics match):
  - 0 no content / 1 social-trivial / 2 informational-only / 3 substantive / 4 decision-action-assignment / 5 urgent-critical;
  - adjustments: raise 1 for decision, deadline, or named owner; short approve/reject replies score 4; when torn choose the lower unless a deadline/decision/blocker is present; bot failure = 4 (5 if production-facing);
  - hard routing thresholds: 0-2 → Nothing; 3-5 → eligible for routing/action.
- Acceptance: 8+ concrete message→score examples in the SOUL, like the standard's list.

### IMP-11 Add category precedence and a decision table
- Problem: "Task for other profiles" and "Interact with PWR" overlap with no tie-break.
- Change: a table: situation → category → first tool; and a precedence rule: if the work belongs to another profile but also changes shared state, route the task first (create/route via `create_ai_task` with `assigneee_profile`) and record one PWR pointer, do not double-act.
- Acceptance: every workflow branch names exactly one first tool.

### IMP-12 Make the approval lifecycle executable
- Problem: "wait for the approval event" cannot happen inside one task run; the high-impact list covers nearly everything, so the gate either blocks all or gets ignored.
- Change, two-run model:
  - Run A (needs approval): create the explanation message + approval in one call (`add_approve_request_with_message`, required `body`), record `WS-OUTCOME: pending_approval` on the task (`update_ai_task`), stop.
  - Run B (approval event task): check `approval_requests`/`get_approval_request` status; proceed only when the human's decision exists (relayed via `add_decision_message` — never self-decided); then perform the original PWR change.
  - Split the gate list explicitly: acts directly (Nothing classification, writebacks, routing a task, room messages answering a direct question) vs approval-first (company-home items, status items, milestones, decision records, knowledge proposals, room-level decisions).
- Acceptance: no instruction anywhere says "wait"; the never-claim-done-while-pending rule is stated.

### IMP-13 Add named context-resolution steps
- Problem: "Retrieve project context when continuity or ambiguity matters" names no tool.
- Change: step 2 of the workflow becomes: resolve project/room from the task payload ids; names resolve via `get_single_project` (`project_name`/`project_slug`), `search_rooms` (`query`), owner validation via `get_project_users`; never invent ids or names.
- Acceptance: each vague "check context" phrase is replaced with a tool call.

### IMP-14 Add a closed outcome vocabulary
- Problem: no terminal states; small models leave runs half-declared.
- Change: exactly five outcomes — `nothing_to_do`, `routed`, `acted`, `pending_approval`, `unclear_escalated` — each with its required writeback (IMP-03 description line + tool set). `unclear_escalated` means: raise `add_ai_confirm` (title = the open question, meta_text = context) in the room and stop.
- Acceptance: every workflow leaf ends in a named outcome.

---

## 6. Wave 4 — Examples and layout polish (P2, high value for 28B)

### IMP-15 Replace abstract examples with worked JSON traces
- Problem: the three examples are bullet instructions with no payloads; the standard's strength is input JSON → step-by-step tool calls → recorded outcome.
- Change: rewrite all three as traces using verified schemas:
  - Example 1 (route): task payload → `get_ai_task` → owner check (`get_project_users`) → `create_ai_task` with `assigneee_profile`, `description` = verbatim request + room/project context → `update_ai_task(runned: true, description += "WS-OUTCOME: routed ...")`.
  - Example 2 (act with approval-first): blocker event → dedup check (`attention_items` by category/project) → `add_approve_request_with_message` → pending writeback → (Run B) approval granted → `add_blockers` → `create_topic_tool_call_log`.
  - Example 3 (Nothing): low-value task → score 0-1 → writeback only (`runned: true`, `WS-OUTCOME: nothing_to_do`), zero records created.
- Acceptance: each example is copy-paste executable against the live server.

### IMP-16 Remove the cross-file reference to the message-analyzer SOUL
- Problem: "should follow the same core logic as the message-analyzer soul" is a dead pointer; the runtime never loads that file.
- Change: delete the reference; inline the four rules that matter (analysis-first, stop-on-low-value, search-before-create, read-merge-write on updates) — the SOUL already has a merge-rule section ("Update for action"), so add the standard's note that create/update tools do not auto-merge and the agent must send the merged value explicitly.
- Acceptance: SOUL is self-contained; zero references to other files.

### IMP-17 Front-load a one-page procedure
- Problem: ~95 lines of architecture prose precede the job; small models attend hardest to the beginning.
- Change: after "Who are you", insert a compact procedure box: input (task id) → `get_ai_task` → score (rubric) → threshold → category (table) → dedup check → first tool (template) → writeback (outcome). Then keep entity model / tool inventory / rules as reference sections below.
- Acceptance: the decision procedure fits one screen; nothing new is asserted in it that is not backed by a later reference section.

### IMP-18 Add a DON'T block
- Change, short and literal: no tools outside the listed set; no invented ids or names; no create without the matching list/search dedup check (IMP-08); no approval chains inside one run; no outcome words outside the five (IMP-14); no duplicate record for the same subject; no self-decided `add_decision_message`.
- Acceptance: one block, max 8 lines, each line testable.

### IMP-19 Style pass for low-end models
- Change: short literal sentences; one instruction per line; replace every filler phrase with a field or tool ("keep it visible" → `added_to_kanban: true`; "attach sufficient context" → "description must contain: verbatim source text, room_id, project_id, why it is being routed"; "do not guess wildly" → "if the owner is not in `get_project_users`, classify `unclear_escalated`"). Map each rubric triple ("blocker, risk, or dependency") to exactly one tool per row.
- Acceptance: a rule that cannot be rephrased as a tool call + arguments gets rewritten or dropped.

---

## 7. Wave 5 — Verification harness (done last, proves waves 1-4)

### IMP-20 Replay test on a 28B profile
- Build 6 task fixtures (route, act+approval, approval-granted run, Nothing, unclear-owner, duplicate re-run) against live rooms; run the profile; assert: correct first tool call; exact argument shape (required fields only + names for fuzzy match); no duplicate record on the re-run; every run ends with `runned: true` and a valid `WS-OUTCOME`; no call to a tool outside the SOUL's set.
- Token check: profile toolset ≤ ~50 tools (after IMP-02 connection/filter change); compare prompt tokens before/after (163-tool `/mcp` baseline vs filtered set).
- Consistency check: re-scan the SOUL and diff every named tool against the live `tools/list` per endpoint — zero contradictions, same as the snapshots this plan was built from.

---

## 8. Quick reference: verified live facts used above

- Endpoints (routes.rb:272-276, all answer live): `/mcp` 163 tools (superset, all scopes), `/action-mcp` 142, `/read-mcp` 78, `/knowledge-mcp` 29, `/task-mcp` 9.
- Scoping gaps to remember: project-knowledge writes are NOT on `/knowledge-mcp`; the topic/analysis family is. All task tools are on `/task-mcp`, `/action-mcp` (mutations) and `/mcp`.
- Canonical task tool names on live `tools/list`: `ai_tasks`, `get_ai_task`, `create_ai_task`, `update_ai_task`, `delete_ai_task`, `get_ai_task_children`, `get_ai_task_parents`, `ai_task_cost`. Short forms (`get_task`...) are aliases only, invisible in `tools/list`.
- `update_ai_task` fields: `task_id`*, `description`, `adder_profile`, `assigneee_profile`, `added_to_kanban`, `runned`. No status/result field.
- Attention `add_*` (7 tools) shared schema: `title`* + `meta_text`, `action_label`, `due_at`, `overdue`, project/room/user id-or-name pairs.
- Approval create defaults: `request_type` "action", `payload` {}, status "pending".
- Multi-verb tools dispatch by argument presence (no `action` param): item_id=update/get/delete (delete:true), title-only=create, none=list; status items attach to the current period, auto-creating "Current Period" if absent.
- `add_action_message`: no body param (indicator). `add_decision_message`: requires `approval_request_id` + `decision` (human decision relay only).
- Fuzzy name resolution exists on the tools themselves (`project_name`, `room_name`, `user_name`) — prefer it over backend id-probing.

## 9. Execution order summary

1. IMP-01, 02, 03, 04, 05 (facts; gate: zero live-surface contradictions)
2. IMP-06, 07, 08, 09 (payloads and guards; gate: every action has a template and a dedup check)
3. IMP-10, 11, 12, 13, 14 (decisions; gate: every branch ends in a named outcome with a named tool)
4. IMP-15, 16, 17, 18, 19 (examples, layout, style; gate: SOUL self-contained, procedure front-loaded)
5. IMP-20 (harness; gate: 6 fixtures pass, token budget met)

Each numbered round ends with: unified-diff patch of the W-ai source file → review → mirror to loaded profile SOUL.
