# Risk (approved / denied)

Type: input-processing skill
Apply when: events `risk_approved` or `risk_denied` on `risks` company-status items.

## Procedure

1. Gate on `target_type: "CompanyStatusItem"` + `category: "risks"`. Read the item: `risks(item_id: <event_id>)`.
2. `risk_approved` — the risk is live company state:
   - link it to the work that carries it: if the risk references a project, find open tasks/todos on that thread and merge "risk <id> approved <date>: <evidence>" into their `description`;
   - if the risk has an owner (`owner_name`), route a mitigation task only when none exists: check `ai_tasks` and `add_blockers` footprint first.
3. `risk_denied` — the proposed risk was rejected. Close out the artifacts *the risk proposal created*: blockers you opened citing it (`edit_blockers(item_id, status: "dismissed")`), and correct any `progress` items that were hedged on it.
4. Never invent mitigation deadlines; `due_at` only when the event content states one.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `risks` | read-mcp + action-mcp | list = read-only filters; get/edit/delete = `item_id`; create = `title` (+`details`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`) |
| `company_status_period` | read-mcp | find the current period via list + `current`; there is no dedicated "get current" arg |
| `add_company_status_period` / `edit_company_status_period` | action-mcp | create requires `name`; edit requires `period_id` |
| `tool_cal_logs` | knowledge-mcp | dedupe your own footprint (`target_entity_id`) |
| `risks` | read+action-mcp | the risks category tool |
| `edit_blockers` | action-mcp | dismiss derived blockers |
| `ai_tasks` / `update_ai_task` / `create_ai_task` | task-mcp | carry risk context |

## Example

```json
{"event_type": "risk_approved", "event_id": 143,
 "event_data": {"actor": {"username": "bob"}, "target_type": "CompanyStatusItem",
   "content": "Risk: MCP bridge hangs on long-poll under load",
   "content_payload": {"company_status_item_id": 143, "category": "risks", "status": "approved", "company_status_period_id": 3}}}
```

Run: `risks(item_id: 143)` → approved, owner carol → `ai_tasks(finished=false)` → task 77 "stabilize bridge" exists, cite it: `update_ai_task(task_id: 77, description: "<existing>\n[2026-11-02] company risk 143 approved — this task is its mitigation")` → log. No new task: dedupe rule satisfied by reuse.
## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
