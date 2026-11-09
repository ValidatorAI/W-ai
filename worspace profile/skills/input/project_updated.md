# Project updated

Type: input-processing skill
Apply when: a `project_updated` event arrives.

## Procedure

1. Diff `event_data.content_payload` against `get_single_project` current record. Only material fields matter: description/scope change, status change, ownership change, visibility.
2. Cosmetic or self-explanatory edits → no action (this is the most common correct outcome).
3. Material change → propagate, do not restate:
   - check `attention_items(category: "material_changes", project_id: ..., status: "pending")`; if no equivalent item exists, `add_material_changes(title: "<what changed>", meta_text: "<actor + date + before/after>", project_id: ...)`.
   - if open tasks assumed the old scope (`ai_tasks` with `project_id, finished=false`), append a re-scope note to the affected task `description` via `update_ai_task` (merge — never replace).
4. Human-facing notification only when the room is an active work room: `add_message(body: "...", room_name: ..., user_name: "w-ai")`.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `get_single_project` | read-mcp | `project_id` / `project_name` |
| `attention_items` | read-mcp | `category`, `project_id`, `status` |
| `add_material_changes` | action-mcp | required: `title`; optional: `meta_text`, `due_at` |
| `ai_tasks` | task-mcp | filters: `project_id`, `finished` |
| `update_ai_task` | task-mcp | required: `task_id`; only the 9 writable fields |
| `add_message` | action-mcp | required: `body`; `room_id`/`room_name`; identity via `user_name: "w-ai"` |

## Example

```json
{"event_type": "project_updated", "event_id": 31,
 "event_data": {"actor": {"username": "bob"}, "target_type": "Project",
   "content": "atlas status moved to active",
   "content_payload": {"project_id": 31, "changed": {"status": "active"}}}}
```

Run: `attention_items(category: "material_changes", project_id: 31, status: "pending")` → no equivalent → `add_material_changes(project_id: 31, title: "Project atlas moved to active", meta_text: "by bob 2026-11-02; verify plan assumptions")` → `create_tool_cal_log(used_tool_name: "add_material_changes", target_entity_id: "<new item id>", change_log: "status move recorded")`. Open tasks unaffected → stop.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`; company-status item and approval flows add `approved` / `denied` / `canceled` via events.
- If the target profile or room is ambiguous, prefer minimal justified action or route a clarification task; never guess identities.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
