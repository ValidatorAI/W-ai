# Change (any action)

Type: input-processing skill
Apply when: `change_<action>` events on company-status `changes` items.

## Procedure

1. Read: `changes(item_id: <event_id>)` — a `changes` item is a declared change to how the company operates (process, scope, tooling).
2. Cross-check against the attention layer: a company-level change that others must notice belongs in `material_changes` — but the source may already have created it. `attention_items(category: "material_changes", status: "pending")` first; add only if absent, with the change item id in `meta_text`.
3. Sweep state that the change contradicts: status `progress`/`priorities` claims, open ADRs (`project_decision_records`), milestones — merge corrections where the record is *directly* contradicted, route tasks where judgement is needed (`assigneee_profile: "planner"`).
4. `change_deleted` → if artifacts exist citing it (your footprints in `tool_cal_logs` with the change id), annotate them with "source change deleted — re-validate".

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `changes` | read-mcp + action-mcp | list = read-only filters; get/edit/delete = `item_id`; create = `title` (+`details`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`) |
| `company_status_period` | read-mcp | find the current period via list + `current`; there is no dedicated "get current" arg |
| `add_company_status_period` / `edit_company_status_period` | action-mcp | create requires `name`; edit requires `period_id` |
| `tool_cal_logs` | knowledge-mcp | dedupe your own footprint (`target_entity_id`) |
| `attention_items` / `add_material_changes` | read/action-mcp | company-home visibility |
| `project_decision_records` / `project_milestones` | read-mcp | contradiction sweep |
| `ai_tasks` / `create_ai_task` | task-mcp | judgement work routing |

## Example

```json
{"event_type": "change_approved", "event_id": 160,
 "event_data": {"actor": {"username": "alice"}, "target_type": "CompanyStatusItem",
   "content": "change: kanban becomes the only cross-profile task channel",
   "content_payload": {"company_status_item_id": 160, "category": "changes", "status": "approved"}}}
```

Run: `changes(item_id: 160)` → approved → `attention_items(category: "material_changes", status: "pending")` → none → `add_material_changes(title: "Process change: kanban-only cross-profile tasking", meta_text: "company change item 160, approved by alice 2026-11-02")` → log.
## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
