# Project todo reopened

Type: input-processing skill
Apply when: a `project_todo_reopened` event arrives.

## Procedure

1. Verify: `project_todos(todo_id: <event_id>)` — `completed` false again.
2. If a Hermes task referenced the todo (`ai_tasks(project_id, finished=false)` + description mention) → append "todo <id> reopened <date>" to its `description` via `update_ai_task` (merge).
3. If the reopen breaks a claimed progress item for the current period → edit the matching `progress` item (with `item_id`) to reflect reality; never delete the old claim, correct it.
4. If nothing tracked it and no status claim exists → verification log only.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `project_todos` | read-mcp | `todo_id` |
| `ai_tasks` / `update_ai_task` | task-mcp | `description` merge |
| `progress` | read+action-mcp | list; `item_id` to edit; create with `title` |

## Example

```json
{"event_type": "project_todo_reopened", "event_id": 88,
 "event_data": {"actor": {"username": "dana"}, "content": "todo reopened",
   "content_payload": {"id": 88, "project_id": 2}}}
```

Run: read → reopened → no open task references it → `progress(company_status_period_id: current)` shows item 14 "task-mcp integration done" → `progress(item_id: 14, status: "open", details: "88 reopened 2026-11-02 — claim withdrawn")` → `create_tool_cal_log(used_tool_name: "progress", target_entity_id: "14", change_log: "corrected progress claim after todo reopen")`.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`; company-status item and approval flows add `approved` / `denied` / `canceled` via events.
- If the target profile or room is ambiguous, prefer minimal justified action or route a clarification task; never guess identities.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
