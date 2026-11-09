# Decision waiting (resolved / dismissed / approved)

Type: input-processing skill
Apply when: events `decision_waiting_resolved`, `decision_waiting_dismissed`, or `decision_approved` with `target_type: "AttentionItem"` (category `decisions_waiting`).

## Procedure

1. Identify the item: `event_id` = attention item id. Read it: `decisions_waiting(item_id: <event_id>)`. Status should already be `resolved` (or the decision `approved`).
2. Disambiguation trap: `decision_approved` is emitted by **two** flows — ApprovalRequest approvals (target_type `ApprovalRequest`) and company-status `decisions` items (target_type `CompanyStatusItem`). Route by `event_data.target_type`, never by event name alone. This skill owns the AttentionItem shape only.
3. On resolved/approved — the waiting decision was made. Consequences:
   - If the decision created follow-up work and an open Hermes task exists for the decider, nothing for you; the task flow owns it.
   - Record durable decisions into project knowledge: `add_project_decision_record(identifier: "ADR-<n>", title: <decision title>, project_id, status: "accepted", decision_date: <occurred_at date>, file_path: <from knowledge_path if an ADR path was supplied>)` — only when no equivalent record exists (`project_decision_records(project_id)` first).
   - Mirror into company status when the decision is company-level: `decisions(item_id: ...)` to update an existing claim, or create via `decisions(title: ...)` after listing; requires an active `company_status_period` (read `company_status_period` with `current: true` semantics — take the current period id).
4. On dismissed — the decision was cancelled without effect. Verify no now-orphaned follow-ups: search `ai_tasks(project_id, finished=false)` whose `description` references the item; append "decision dismissed <date>" to each via `update_ai_task`. Do not delete tasks on your own.
5. If the item is already handled in PWR and nothing tracks it: verification log only.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `decisions_waiting` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_decisions_waiting` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_decisions_waiting` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `add_project_decision_record` | action-mcp | required: `identifier`, `title`; optional: `status`, `decision_date`, `file_path` |
| `project_decision_records` | read-mcp | `project_id` — dedupe ADRs |
| `decisions` | read+action-mcp | company-status decisions category |
| `company_status_period` | read-mcp | find the current period id |

## Example

```json
{"event_type": "decision_approved", "event_id": 42,
 "event_data": {"actor": {"username": "alice"}, "target_type": "AttentionItem",
   "content": "Decision: freeze scope for v1 — approved",
   "content_payload": {"attention_item_id": 42, "category": "decisions_waiting", "project_id": 2}}}
```

Run: `decisions_waiting(item_id: 42)` → resolved, approved by alice → `project_decision_records(project_id: 2)` → no ADR for scope freeze → `add_project_decision_record(project_id: 2, identifier: "ADR-7", title: "Freeze scope for v1", status: "accepted", decision_date: "2026-11-02")` → `decisions(project_id...)` not applicable (project-level) → logs for the write.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
