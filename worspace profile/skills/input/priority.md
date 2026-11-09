# Priority (approved / denied / other actions)

Type: input-processing skill
Apply when: events `priority_approved` or `priority_denied` (and any `priority_<action>`) — company-status `priorities` items, `event_data.target_type: "CompanyStatusItem"`, `content_payload.category: "priorities"`.

## Procedure

1. Parse: `content_payload.company_status_item_id` + `action` + `status` from the event; company-status events name themselves `<singular-category>_<normalized-action>` — bases: `priority`, `progress`, `risk`, `dependency`, `change`, `decision`, `learning` (verified in `CompanyStatusItem#action_event_type`).
2. `priority_approved` — the item is now a live company priority. Propagate to work state:
   - projects whose scope this priority governs: check `get_projects`; for each clearly affected project route or update — `create_ai_task(description: "Align project <name> with newly approved company priority: <title>", assigneee_profile: <PM profile>)`;
   - never re-create the priority item itself — it exists and is already approved in PWR (`priorities(item_id: ...)` shows the record).
3. `priority_denied` — removal or rejection of a proposed priority. Sweep open tasks/todos that assumed it (`ai_tasks`, `project_todos` referencing the title) and merge a "priority denied <date>" correction into anything stale.
4. `decision_approved` collision: this same event name also comes from ApprovalRequest and AttentionItem flows. Always gate on `event_data.target_type == "CompanyStatusItem"` before applying this skill; other shapes route to `decision_waiting.md` / approval flow.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `<category>` (e.g. `priorities`) | read-mcp + action-mcp | list = read-only filters; get/edit/delete = `item_id`; create = `title` (+`details`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`) |
| `company_status_period` | read-mcp | find the current period via list + `current`; there is no dedicated "get current" arg |
| `add_company_status_period` / `edit_company_status_period` | action-mcp | create requires `name`; edit requires `period_id` |
| `tool_cal_logs` | knowledge-mcp | dedupe your own footprint (`target_entity_id`) |
| `priorities` | read+action-mcp | the priorities category tool |
| `get_projects` | read-mcp | affected project sweep |
| `create_ai_task` / `update_ai_task` | task-mcp | route alignment work |

## Example

```json
{"event_type": "priority_approved", "event_id": 140,
 "event_data": {"actor": {"username": "alice"}, "target_type": "CompanyStatusItem",
   "content": "Q4 priority: cut triage latency 50%",
   "content_payload": {"type": "company_status_item_action", "company_status_item_id": 140,
     "category": "priorities", "status": "approved", "action": "approve",
     "company_status_period_id": 3}}}
```

Run: `priorities(item_id: 140)` → approved in period 3 → `get_projects()` → pwr + atlas affected → `ai_tasks(project_id: 2, finished=false)` → nothing cites the priority → `create_ai_task(project_id: 2, adder_profile: "workspace", assigneee_profile: "planner", description: "Align pwr roadmap with approved company priority 140: cut triage latency 50%", proposed_task_context: "period 3, approved 2026-11-02 by alice", input_event_entity_id: 140)` → log. Same for atlas (one task per project).
## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
