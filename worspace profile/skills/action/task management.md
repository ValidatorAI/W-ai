# Task management

Type: action skill
Purpose: owning the AI-task lifecycle on `/task-mcp` — creating, routing, tracking, and closing tasks for any profile.

Verified against `db/schema.rb` (`ai_tasks`), `app/services/mcp/tools/tasks.rb`, and live registry dump 2026-11-02. task-mcp exposes exactly 8 tools: `ai_tasks`, `get_ai_task`, `create_ai_task`, `update_ai_task`, `delete_ai_task`, `get_ai_task_children`, `get_ai_task_parents`, `ai_task_cost`.

## Field reference (the real ai_tasks schema)

- `description` — the only required field and only free-text body (there is no `title`).
- `project_id` / `room_id` / `topic_id` — scope links; `project_id` always set by convention.
- `task_id` — external/linked identifier; `input_event_entity_id` — originating event/entity id. Preserve both when routing from events.
- Hierarchy: `level` (root = 0), `parent_task_id`, `grand_parent_id` (not `parent_id`/`grandparent_id`).
- People: `adder_profile` (creator), `assigneee_profile` (assignee — three e's).
- Context: `proposed_task_context` (known at creation) and `actual_task_context` (learned while working).
- State: `dispatched` / `finished` are the only flags (no `status`; legacy `added_to_kanban`/`runned`).
- Cost: `token_used`, `usd_used`, `usd_budget`; `token_budget` is NOT writable through task-mcp; `importance` integer ≥ 0.

## Creating

1. Dedupe first: `ai_tasks(project_id, finished=false[, room_id, topic_id])` — reuse an equivalent open task instead of creating.
2. `create_ai_task(description, project_id, [room_id, topic_id, level, parent_task_id, grand_parent_id, adder_profile: "workspace", assigneee_profile, proposed_task_context, input_event_entity_id, task_id, importance, usd_budget], dispatched: false, finished: false, token_used: 0, usd_used: 0)`.
3. Hierarchy: child → `parent_task_id` = parent id, `level` = parent.level + 1, `grand_parent_id` = parent's `parent_task_id`; root → nulls and `level: 0`. Never create children deeper than `level` 3.
4. Never create when the (parent) task budget is exhausted: `usd_used >= usd_budget` (when allocated); `null` budget = no gate.
5. Omit optional fields you don't know — do not invent values.

## Working a task (any profile)

1. `get_ai_task` — confirm exists and not `finished`; never re-open finished tasks, create a follow-up child instead.
2. Start: `update_ai_task(task_id, dispatched: true, assigneee_profile: <you>)` (there is no start timestamp; `updated_at` serves).
3. Blocked: append the blocker to `description` via `update_ai_task` (no notes/status fields exist).
4. Child tasks: re-validate parent via `get_ai_task_parents` before deep work.
5. Finish: FIRST `ai_task_cost(task_id, token_used, usd_used)` — it writes the costs and rolls deltas up to every ancestor; then `update_ai_task(task_id, finished: true, actual_task_context: "<what was done/learned, ids touched, verdict if no action>")`.

## Update immutability

`update_ai_task` can change only: `description`, `adder_profile`, `assigneee_profile`, `actual_task_context`, `dispatched`, `finished` (+ legacy aliases), `topic_id`, `task_id`, `input_event_entity_id`. Costs move only via `ai_task_cost`. Everything else (`project_id`, `room_id`, `level`, parent links, budgets, `importance`, `token_budget`) is fixed at creation.

## Deletion

`delete_ai_task` is for erroneous duplicates you created — never for closing work; closing means finished + cost.

## Example — route a follow-up child

```json
{"tool": "create_ai_task", "arguments": {
  "description": "Re-verify ADR-7 scope freeze against reopened item 66",
  "project_id": 2, "parent_task_id": 88, "level": 1, "grand_parent_id": null,
  "adder_profile": "workspace", "assigneee_profile": "coder",
  "proposed_task_context": "all_hands item 66 reopened 2026-11-02; parent task 88 delivered ADR-7",
  "input_event_entity_id": 66, "dispatched": false, "finished": false,
  "token_used": 0, "usd_used": 0, "importance": 3}}
```

Close-out when done:

```json
{"tool": "ai_task_cost", "arguments": {"task_id": 91, "token_used": 24500, "usd_used": 0.19}},
{"tool": "update_ai_task", "arguments": {"task_id": 91, "finished": true,
  "actual_task_context": "ADR-7 still valid; note added to record; blocker 43 left open"}}
```
