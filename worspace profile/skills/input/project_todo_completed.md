# Project todo completed

Type: input-processing skill
Apply when: a `project_todo_completed` event arrives (`event_id` = the todo id).

## Procedure

1. Verify: `project_todos(todo_id: <event_id>)` — `completed` is already true.
2. Consequences in order:
   - tracked Hermes task (`ai_tasks(input_event_entity_id: <event_id>, finished=false)`) → cost then close it (`ai_task_cost`, `update_ai_task finished=true, actual_task_context=...`).
   - the todo was the last open item gating a milestone (`project_milestones(project_id, status...)`) → milestone state belongs to humans: route a task or raise `add_outcomes_review(title: "Milestone X: all todos complete, review outcome")` — do not mark milestones yourself.
3. Plain todos with nothing attached: verification log only.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `project_todos` | read-mcp | `todo_id` or list with `project_id` |
| `project_milestones` | read-mcp | `project_id`, `milestone_id` |
| `ai_tasks` / `ai_task_cost` / `update_ai_task` | task-mcp | see `task management` skill |
| `add_outcomes_review` | action-mcp | required: `title` |

## Example

```json
{"event_type": "project_todo_completed", "event_id": 88,
 "event_data": {"actor": {"username": "alice"}, "content": "todo 'wire task-mcp into workspace profile' completed",
   "content_payload": {"id": 88, "project_id": 2}}}
```

Run: read todo → true → `ai_tasks(input_event_entity_id: 88)` → task 90 open → `ai_task_cost(task_id: 90, token_used: 18300, usd_used: 0.12)` → `update_ai_task(task_id: 90, finished: true, actual_task_context: "closed: todo 88 completed")` → 2 logs (task close needs none for reads).

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`; company-status item and approval flows add `approved` / `denied` / `canceled` via events.
- If the target profile or room is ambiguous, prefer minimal justified action or route a clarification task; never guess identities.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
