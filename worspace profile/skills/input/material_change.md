# Material change (resolved / dismissed)

Type: input-processing skill
Apply when: events `material_change_resolved` or `material_change_dismissed`.

## Procedure

1. Read the item: `material_changes(item_id: <event_id>)`.
2. `material_change_resolved` = someone acknowledged the change. Acknowledgement is a human act — do not acknowledge on anyone's behalf. Your job:
   - sweep work that assumed the pre-change state: `ai_tasks(project_id, finished=false)` + `project_todos(project_id, ...)` referencing the changed entity; append a "material change <id> acknowledged <date> — re-verify assumptions" note where open work touches it;
   - if the change invalidated a status claim (e.g. a `progress` item based on the old plan) → correct it with `edit`-style merge on the `progress`/`priorities` item.
3. `material_change_dismissed` — the change was deemed immaterial by a human. Close any of your own follow-ups that were raised solely from it (`edit_blockers` → dismiss the derived blocker, `delete_attention_item` only for items *you* created); leave third-party items alone.
4. Nothing references it: verification log only.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `material_changes` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_material_changes` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_material_changes` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `ai_tasks` / `update_ai_task` | task-mcp | assumption sweep |
| `project_todos` / `edit_project_todo` | read/action-mcp | merge note into `meta_text` |
| `progress` / `priorities` | read+action-mcp | correct stale claims |

## Example

```json
{"event_type": "material_change_dismissed", "event_id": 71,
 "event_data": {"actor": {"username": "bob"}, "target_type": "AttentionItem",
   "content": "material change 'rename MCP endpoints' dismissed",
   "content_payload": {"attention_item_id": 71, "project_id": 2}}}
```

Run: `material_changes(item_id: 71)` → dismissed → `ai_tasks(project_id: 2, finished=false)` → none reference rename → `blockers(project_id: 2, status: "pending")` shows item 43 *you* created ("endpoint rename blocks docs") with `source` this change → `edit_blockers(item_id: 43, status: "dismissed", meta_text: "root change 71 dismissed — no longer applicable")` → log.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
