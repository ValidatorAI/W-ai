# All-hands action item completed

Type: input-processing skill
Apply when: an `all_hands_action_item_completed` event arrives (`event_id` = the action-item id).

## Procedure

1. Verify state: `project_all_hands_action_item` with `action_item_id: <event_id>` — `completed` is already true; PWR flipped it, the event is a notification. Never re-apply the completion.
2. Consequence check (in order, most end here):
   - Did a Hermes task track this item? `ai_tasks(input_event_entity_id: <event_id>)` or search by title in `description` — if found and open: `ai_task_cost(task_id, token_used, usd_used)` then `update_ai_task(task_id, finished: true, actual_task_context: "closed because all-hands action item <id> completed 2026-11-02")`.
   - Did completion produce a durable conclusion others must know? Only then `add_project_all_hands_takeaway(text: ...)` or `add_project_all_hands_decision(text: ..., basis: ...)` — with approval discipline if project-visible.
   - Does a status progress item deserve the fact? Merge via `progress` (create only if `progress` list shows nothing equivalent for the current period).
3. Default outcome for a plain completion with no tracked work: log verification and stop.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `project_all_hands_action_item` | read-mcp | `action_item_id`, or list with `project_id` |
| `ai_tasks` | task-mcp | filter `input_event_entity_id`, `finished=false` |
| `ai_task_cost` | task-mcp | `task_id`, `token_used`, `usd_used` (rolls up ancestors) |
| `update_ai_task` | task-mcp | required `task_id` |
| `add_project_all_hands_takeaway` / `add_project_all_hands_decision` | action-mcp | required: `text` |
| `progress` | read+action-mcp | list = read; `title` = create; `item_id` = edit |

## Example

```json
{"event_type": "all_hands_action_item_completed", "event_id": 66,
 "event_data": {"actor": {"username": "alice"}, "content": "action item 'Ship MCP docs' completed",
   "content_payload": {"id": 66, "project_id": 2}}}
```

Run: `project_all_hands_action_item(action_item_id: 66)` → completed confirmed → `ai_tasks(input_event_entity_id: 66, finished=false)` → none → conclusion check: no durable decision → `create_tool_cal_log(used_tool_name: "project_all_hands_action_item", project_id: 2, target_entity_id: "66", change_log: "verified completion; no follow-up")` → stop.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`; company-status item and approval flows add `approved` / `denied` / `canceled` via events.
- If the target profile or room is ambiguous, prefer minimal justified action or route a clarification task; never guess identities.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
