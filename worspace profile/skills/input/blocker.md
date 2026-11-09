# Blocker (resolved / dismissed)

Type: input-processing skill
Apply when: events `blocker_resolved` or `blocker_dismissed`.

## Procedure

1. Read the item: `blockers(item_id: <event_id>)`; confirm status.
2. `blocker_resolved` — the unblock is already applied in PWR. Your job is to unstick the work it held:
   - `ai_tasks(project_id: <item.project_id>, finished=false)` — find tasks whose `description`/`actual_task_context` reference the blocker; append "<blocker id> resolved <date>, can proceed" via `update_ai_task`.
   - If the blocked work belongs to another profile and no task exists, route one: `create_ai_task(description: "Resume <work> — blocker <id> resolved", assigneee_profile: <owner>, input_event_entity_id: <event_id>)`.
   - Update related open `risks`/`dependencies` status items if the blocker was their evidence (`edit` with `item_id`, merge).
3. `blocker_dismissed` — the blocker was cancelled, not cleared. Record why in the referencing tasks ("dismissed <date> by <actor>: <item.meta_text>") so nobody assumes it was fixed.
4. No open work referenced the item: verification log only.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `blockers` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_blockers` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_blockers` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `ai_tasks` / `update_ai_task` / `create_ai_task` | task-mcp | merge into `description`; close the loop |
| `risks` / `dependencies` | read+action-mcp | status items that may cite the blocker |

## Example

```json
{"event_type": "blocker_resolved", "event_id": 42,
 "event_data": {"actor": {"username": "carol"}, "target_type": "AttentionItem",
   "content": "Blocker 'task-mcp not attached to workspace profile' resolved",
   "content_payload": {"attention_item_id": 42, "project_id": 2}}}
```

Run: `blockers(item_id: 42)` → resolved → `ai_tasks(project_id: 2, finished=false)` → task 88 description says "blocked by 42" → `update_ai_task(task_id: 88, description: "<existing text>\n\n[2026-11-02] blocker 42 resolved by carol — unblocked, can proceed")` → `create_tool_cal_log(used_tool_name: "update_ai_task", target_entity_id: "88", change_log: "notified task 88 blocker cleared")`.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
