# Learning (any action)

Type: input-processing skill
Apply when: `learning_<action>` events on company-status `learnings` items.

## Procedure

1. Read: `learnings(item_id: <event_id>)` — the event content is the lesson text.
2. Learnings are perishable in status views but permanent in knowledge: adopt the lesson into project knowledge so it survives the period:
   - dedupe: `knowledge_summary_items(project_id)` / `project_knowledge_items(project_id)`;
   - create: `add_knowledge_summary_item(title: "<short lesson>", description: "<full text> (learning item <id>, <date>)", project_id)` — pick the project from the item's scope; company-wide lessons go under the company's primary project per its convention, else route a `knowledge` task;
   - `add_knowledge_activity_log(actor_name: "w-ai", action_text: "adopted learning <id> into summaries")`.
3. If the learning forbids something you (or a profile) currently automate, raise a `decisions_waiting` attention item ("revoke auto-X per learning <id>?") instead of silently changing behavior.
4. Rejected/deleted learning event → if you already adopted it, edit the summary item to mark "withdrawn (learning <id> deleted)" — delete only if it was created solely from that item.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `learnings` | read-mcp + action-mcp | list = read-only filters; get/edit/delete = `item_id`; create = `title` (+`details`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`) |
| `company_status_period` | read-mcp | find the current period via list + `current`; there is no dedicated "get current" arg |
| `add_company_status_period` / `edit_company_status_period` | action-mcp | create requires `name`; edit requires `period_id` |
| `tool_cal_logs` | knowledge-mcp | dedupe your own footprint (`target_entity_id`) |
| `add_knowledge_summary_item` / `knowledge_summary_items` | action/read-mcp | permanent adoption |
| `add_project_knowledge_item` | action-mcp | durable rule-shaped lessons |
| `add_knowledge_activity_log` | action-mcp | adoption trail |
| `add_decisions_waiting` | action-mcp | behavior changes needing sign-off |

## Example

```json
{"event_type": "learning_created", "event_id": 166,
 "event_data": {"actor": {"username": "bob"}, "target_type": "CompanyStatusItem",
   "content": "learning: never mark ai_confirm items resolved without owner visibility",
   "content_payload": {"company_status_item_id": 166, "category": "learnings", "status": "active"}}}
```

Run: `knowledge_summary_items(project_id: 2)` → none equivalent → `add_knowledge_summary_item(project_id: 2, title: "ai_confirm requires owner visibility before resolve", description: "Never mark ai_confirm items resolved without the artifact owner seeing it — learning 166, 2026-11-02")` → `add_knowledge_activity_log(project_id: 2, actor_name: "w-ai", action_text: "adopted learning 166")` → 2 logs.
## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
