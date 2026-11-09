# task management (improved)

Corrected version of `task management.md`. All field names, tool names, and constraints below are verified against the live surface: `db/schema.rb` (`ai_tasks` table), `app/services/mcp/tools/tasks.rb`, and `tools/list` on `POST http://localhost:3000/task-mcp` (2026-10-29).

# required MCP tools

* task-mcp exposes exactly these 8 tools: `ai_task_cost`, `ai_tasks`, `create_ai_task`, `delete_ai_task`, `get_ai_task`, `get_ai_task_children`, `get_ai_task_parents`, `update_ai_task`
* use the relevant task tools to read, create, update, and cost task records; never write directly to the `ai_tasks` table or any other backing store
* this skill only applies to profiles whose config has the `task management` MCP server (`http://localhost:3000/task-mcp`) — e.g. `message_analyzer` has it; `workspace` does not (add it there before expecting any rule below to be executable)

# field reference (the real ai_tasks schema)

* `description` — the only required field, and the only free-text field; use it as the task body (there is no `title`)
* `project_id`, `room_id`, `topic_id` — scope links (all nullable in DB; `project_id` required by convention below)
* `task_id` — nullable external or linked task identifier stored on the row itself; use it when the task is traceable back to a separate task or event workflow record
* `input_event_entity_id` — nullable source event/entity identifier for the originating input that created or triggered the task
* `level` — integer, root tasks are `0`; `parent_task_id`, `grand_parent_id` — hierarchy links (NOT `parent_id` / `grandparent_id`)
* `adder_profile` — creator profile; `assigneee_profile` — assigned profile (note the three e's in `assigneee`; there is no `assignee`)
* `proposed_task_context` — nullable summary of the information available when a task is proposed/created; this is the pre-work context and should capture what the task is about and what information is relevant to it
* `actual_task_context` — nullable summary of the information gathered while doing the task; this is the post-work context and should describe what was learned, confirmed, or discovered during execution
* `dispatched`, `finished` — the only state flags (there is no `status` field); legacy aliases `added_to_kanban` = dispatched and `runned` = finished exist but prefer the canonical names
* `importance` — integer >= 0, default 0 (replaces the invented `priority`)
* `token_used` (integer), `usd_used` (float), `usd_budget` (float), `token_budget` (integer) — there is no `budget_used` field
* `created_at` / `updated_at` are managed by Rails — never set them; there are no `created_by` / `updated_by` columns

# when you read a task and start applying it

* before starting work, verify the task exists (`get_ai_task`) and is not already `finished`; if it is finished, do not re-open or duplicate it
* if the task is blocked by missing information, dependencies, or unclear requirements, record the blocker by appending it to `description` via `update_ai_task` (there are no `notes` or `status` fields to record it in)
* when starting a task, call `update_ai_task` to set `dispatched = true` and `assigneee_profile` to your profile name; there is no start-timestamp field — the `updated_at` Rails stamp serves as the record
* while working, keep `description` aligned with actual progress; do not silently ignore required inputs or partial work
* when the task ends: first call `ai_task_cost` with the final `token_used` and `usd_used` (this writes the task's costs AND rolls the deltas up to every ancestor — updating costs any other way skips the roll-up), then call `update_ai_task` to set `finished = true` only after validation of the result
* if the task is a child, confirm the parent context is still valid via `get_ai_task_parents` before continuing; if the parent is complete or invalid, state that clearly in `description`
* keep all notes factual and tied to the task so later review can understand the result and the resources consumed

# on creating a new task

* before creating, run the duplicate check with `ai_tasks` filtered by `project_id` (and `room_id` / `topic_id` when known), paging with `page` / `per_page`; check whether a similar task already exists (use the `dispatched` / `finished` filters to see open vs closed)
* if a matching task already exists and is still relevant, reuse it; only create a new task when no equivalent exists, or the prior task is clearly finished/stale and needs a fresh follow-up
* always include `project_id` (required by convention; the schema itself only requires `description`); add `room_id` only when the task is room-related; `topic_id` only when topic-related
* hierarchy rules:
  * child of the current task: `parent_task_id` = current task's id, `level` = current task's `level + 1`, `grand_parent_id` = current task's `parent_task_id` (or `null` when the current task is root)
  * new root task (unrelated to the current task): `parent_task_id` = `null`, `grand_parent_id` = `null`, `level` = `0`
* call `create_ai_task` (not a DB write) with:
  * `description`: task details / instructions — mention related entities needed to do the task
  * `proposed_task_context`: short summary of the information relevant to the task before work begins; this is the proposed/initial context around the task
  * `project_id`: required; `room_id`, `topic_id`: when related
  * `level`, `parent_task_id`, `grand_parent_id`: per the hierarchy rules above (the tool defaults `level` to 0; state it explicitly for children)
  * `adder_profile`: your profile name
  * `assigneee_profile`: only when explicitly assigned
  * `dispatched`: `false`, `finished`: `false`
  * `importance`: only when explicitly provided (else defaults 0)
  * `usd_budget`: only when an allocation is explicitly given
  * `token_used` / `usd_used`: `0` at creation; all later cost updates go through `ai_task_cost`, never through direct writes
* `token_budget` CANNOT be set via `create_ai_task` (only `usd_budget` is accepted at creation; `token_budget` is not writable through task-mcp at all) — treat it as unallocated unless set outside this surface
* do not invent values for fields left empty; omit optional fields rather than guessing

# tool limits (what cannot be changed after creation)

* `update_ai_task` can change only: `description`, `adder_profile`, `assigneee_profile`, `actual_task_context`, `dispatched`, `finished` (+ legacy aliases), `topic_id`
* `actual_task_context` is the summary of information gathered during task execution; it should capture the facts, findings, and confirmed details discovered while doing the work
* costs change only via `ai_task_cost` (`task_id`, `token_used`, `usd_used`)
* `project_id`, `room_id`, `level`, `parent_task_id`, `grand_parent_id`, `usd_budget`, `importance`, `token_budget` are FIXED at creation — get them right in the `create_ai_task` call

# when not to create a task

* when the parent task's spent budget exceeds its allocation: `token_used` >= `token_budget`, or `usd_used` >= `usd_budget` (evaluate each only when that budget was allocated; `null` budget means no gate)
* when the task is a duplicate of an existing relevant task (see the `ai_tasks` check above)
* when the current task's `level` is 3 or higher — do not create deeper children

---

## corrections applied vs `task management.md`

1. `parent_id` → `parent_task_id`; `grandparent_id` → `grand_parent_id`
2. `budget_used` removed — real fields are `token_budget` / `usd_budget` / `token_used` / `usd_used`
3. `title` and `status` removed — no such columns; `description` is the only required field and `dispatched`/`finished` are the only state
4. "record the issue in notes or status" → append to `description` (no notes field exists)
5. `assignee` → `assigneee_profile` (three e's); added the real `importance` field; removed invented `priority` / `tags` / `notes` / `metadata`
6. `created_by` / `updated_by` removed — Rails manages timestamps
7. finish step now mandates `ai_task_cost` (ancestor roll-up), not raw cost writes
8. `hello` removed from the required-tools list (task-mcp exposes 8 tools)
9. "create a new row in the ai_task table" → "call `create_ai_task`"
10. root-level default corrected to `level = 0` (was "1"); child rule made consistent (child of root = level 1)
11. added the post-creation immutability list and the `token_budget` write gap (not accepted by `create_ai_task`)
12. added the per-profile server precondition (message_analyzer has task-mcp; workspace does not)
13. added `proposed_task_context` and `actual_task_context` as nullable task-context fields; `proposed_task_context` is the summary of relevant information at creation, while `actual_task_context` is the summary of what was learned while doing the task
