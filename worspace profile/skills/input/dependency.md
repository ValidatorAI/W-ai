# Dependency (any action)

Type: input-processing skill
Apply when: `dependency_<action>` events on company-status `dependencies` items.

## Procedure

1. Read: `dependencies(item_id: <event_id>)`; identify both sides (provider and consumer — usually in `details`/`evidence`).
2. New/active dependency → the consumer's open work inherits a precondition:
   - find consumer tasks (`ai_tasks` by project, descriptions referencing the consumed project) and merge "depends on <dependency title> (item <id>)" into `description`;
   - if the dependency is on a *profile's* deliverable, route a coordination task to that profile with the dependency item id in `input_event_entity_id`.
3. Removed/resolved dependency → clear the precondition notes from consumer tasks (merge edit; don't rewrite whole descriptions).
4. Broken/failed dependency (status signals blocked) → this is a company-home event: `add_blockers(title: "Dependency <id> broken: <summary>", meta_text: ...)` after checking `blockers` for an equivalent open item.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `dependencies` | read-mcp + action-mcp | list = read-only filters; get/edit/delete = `item_id`; create = `title` (+`details`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`) |
| `company_status_period` | read-mcp | find the current period via list + `current`; there is no dedicated "get current" arg |
| `add_company_status_period` / `edit_company_status_period` | action-mcp | create requires `name`; edit requires `period_id` |
| `tool_cal_logs` | knowledge-mcp | dedupe your own footprint (`target_entity_id`) |
| `dependencies` | read+action-mcp | dependency item lifecycle |
| `add_blockers` | action-mcp | escalate broken dependency to company home |
| `ai_tasks` / `update_ai_task` / `create_ai_task` | task-mcp | precondition propagation |

## Example

```json
{"event_type": "dependency_created", "event_id": 155,
 "event_data": {"actor": {"username": "bob"}, "target_type": "CompanyStatusItem",
   "content": "w-bridge release depends on pwr task-mcp rollout",
   "content_payload": {"company_status_item_id": 155, "category": "dependencies", "status": "active"}}}
```

Run: `dependencies(item_id: 155)` → active → consumer = w-bridge tasks → `ai_tasks(project_id: 5, finished=false)` → task 61 → `update_ai_task(task_id: 61, description: "<existing>\n[precondition] company dependency 155: blocked until pwr task-mcp rollout (progress item 150)")` → log.
## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
