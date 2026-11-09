# Outcome review (resolved / dismissed)

Type: input-processing skill
Apply when: events `outcome_review_resolved` or `outcome_review_dismissed`.

## Procedure

1. Read the item: `outcomes_review(item_id: <event_id>)`.
2. `outcome_review_resolved` means a human recorded the outcome — capture the durable result, don't re-review it:
   - summarize into knowledge: `add_knowledge_summary_item(title: <item title>, description: "<outcome text> (item <id>, resolved by <actor> <date>)", project_id)` after checking `knowledge_summary_items(project_id)` for an equivalent;
   - if the outcome implies a status change (e.g. a launched feature) → create/merge `progress` item in the current period;
   - if the outcome was a failure → create a `learnings` item instead of `progress`.
3. `outcome_review_dismissed` — the review was waived. Log verification; only append context to referencing tasks if they were waiting on the review.
4. Never mark outcomes yourself from hearsay in message text — this skill acts only on the resolved/dismissed events.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `outcomes_review` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_outcomes_review` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_outcomes_review` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `add_knowledge_summary_item` | action-mcp | required: `title`, `description` |
| `knowledge_summary_items` | read-mcp | `project_id` — dedupe |
| `progress` / `learnings` | read+action-mcp | current-period status items |

## Example

```json
{"event_type": "outcome_review_resolved", "event_id": 51,
 "event_data": {"actor": {"username": "alice"}, "target_type": "AttentionItem",
   "content": "Outcome: pilot of MCP routing saved ~40% triage time",
   "content_payload": {"attention_item_id": 51, "project_id": 2}}}
```

Run: `outcomes_review(item_id: 51)` → resolved with outcome text → `knowledge_summary_items(project_id: 2)` → none equivalent → `add_knowledge_summary_item(project_id: 2, title: "MCP routing pilot outcome", description: "~40% triage time saved; reviewed 2026-11-02 by alice (item 51)")` → `progress(company_status_period_id: 3, title: "MCP routing pilot validated")` (list first → no equivalent) → 2 logs.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
