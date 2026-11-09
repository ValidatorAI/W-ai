# All-hands action item reopened

Type: input-processing skill
Apply when: an `all_hands_action_item_reopened` event arrives.

## Procedure

1. Verify: `project_all_hands_action_item(action_item_id: <event_id>)` — `completed` is now false.
2. A reopen is a signal that something committed is not done. Read context: `room_decision_context` / `room_evidence` if the item carries a room, plus the item's `assignee_name`.
3. Act on severity:
   - The reopen blocks a decision or deadline → `add_blockers(title: "All-hands item <id> reopened: <title>", meta_text: "<who/when/why>", project_id: ..., due_at: <if deadline known>)` (after checking `blockers` for an equivalent open item).
   - A task was closed on the assumption this was done → reopen is not possible via `update_ai_task` on a finished task (do not resurrect); instead `create_ai_task(description: "Follow-up for reopened all-hands item <id>", parent_task_id: <old task>, level: <old.level+1>, max level 3, input_event_entity_id: <event_id>)`.
   - Otherwise: log and stop.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `project_all_hands_action_item` | read-mcp | `action_item_id` |
| `room_decision_context` / `room_evidence` | read-mcp | `room_id`/`room_name`, `project_id` |
| `blockers` | read+action-mcp | list, create with `title`, edit with `item_id` |
| `add_blockers` | action-mcp | required: `title` |
| `create_ai_task` | task-mcp | required: `description`; child level ≤ 3 |

## Example

```json
{"event_type": "all_hands_action_item_reopened", "event_id": 66,
 "event_data": {"actor": {"username": "bob"}, "content": "action item 'Ship MCP docs' reopened",
   "content_payload": {"id": 66, "project_id": 2, "assignee_name": "carol"}}}
```

Run: read item → reopened confirmed, due 2026-11-05 → `blockers(project_id: 2, status: "pending")` → no equivalent → `add_blockers(project_id: 2, title: "All-hands item 66 'Ship MCP docs' reopened", meta_text: "by bob; owner carol; deadline 11-05 at risk", due_at: "2026-11-05")` → `create_tool_cal_log(...)`.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`; company-status item and approval flows add `approved` / `denied` / `canceled` via events.
- If the target profile or room is ambiguous, prefer minimal justified action or route a clarification task; never guess identities.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
