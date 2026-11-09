# Progress (any action)

Type: input-processing skill
Apply when: `progress_<action>` events on company-status `progress` items.

## Procedure

1. Read: `progress(item_id: <event_id>)` — fields: `title`, `percent`, `status`, `health`, `evidence`, `owner_name`.
2. Progress events usually mean a human moved a claim forward — your job is coherence, not duplication:
   - if a Hermes task or project todo drives this progress item and it is now effectively done (`percent: 100` or `status` closed in the record) → close/complete the tracker (`update_ai_task finished`, `edit_project_todo completed: true`) only when the record itself proves completion;
   - if progress contradicts an open claim elsewhere (item says 0% but a task reported done) → do not edit either side blindly: add `add_outcomes_review` citing both ids and let a human arbitrate.
3. `health` degradation (red/named-worse value) with an owner → route a status-check task to the owner's profile, don't post commentary into the room.
4. No contradiction, no tracker: verification log only.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `progress` | read-mcp + action-mcp | list = read-only filters; get/edit/delete = `item_id`; create = `title` (+`details`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`) |
| `company_status_period` | read-mcp | find the current period via list + `current`; there is no dedicated "get current" arg |
| `add_company_status_period` / `edit_company_status_period` | action-mcp | create requires `name`; edit requires `period_id` |
| `tool_cal_logs` | knowledge-mcp | dedupe your own footprint (`target_entity_id`) |
| `progress` | read+action-mcp | percent/health/status live here |
| `update_ai_task` / `edit_project_todo` | task/action-mcp | close trackers on proven completion |
| `add_outcomes_review` | action-mcp | arbitrate contradictions |

## Example

```json
{"event_type": "progress_updated", "event_id": 150,
 "event_data": {"actor": {"username": "alice"}, "target_type": "CompanyStatusItem",
   "content": "progress item 'task-mcp rollout' -> 60%",
   "content_payload": {"company_status_item_id": 150, "category": "progress", "status": "active", "percent": 60}}}
```

Run: `progress(item_id: 150)` → 60%, no health flag → `ai_tasks(finished=false, description-mention)` → none; open todo "integrate task-mcp" not completed → contradiction-free, tracker-consistent → `create_tool_cal_log(used_tool_name: "progress", target_entity_id: "150", change_log: "verified 60%; no follow-up")`. No writes.
## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
