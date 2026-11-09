# Knowledge proposal (resolved / dismissed)

Type: input-processing skill
Apply when: events `knowledge_proposal_resolved` or `knowledge_proposal_dismissed`.

## Procedure

1. Read the item: `knowledge_proposals(item_id: <event_id>)` — proposals are captured knowledge awaiting human approval.
2. `knowledge_proposal_resolved` — approved; adopt the knowledge, this is your core write path here:
   - classify the proposal content into one of the 7 knowledge families (see `project knowledge` skill): fact/note → `add_project_note` or `add_project_knowledge_item`; decision → `add_project_decision_record`; reference/link → `add_external_knowledge_asset` (needs `url`); digest → `add_knowledge_summary_item`;
   - check the target family for an equivalent first;
   - `add_knowledge_activity_log(actor_name: "w-ai", action_text: "adopted proposal <id> into <family>", target_path: <matching knowledge_path line>)`;
   - close the tracking task if one existed (`input_event_entity_id` lookup).
3. `knowledge_proposal_dismissed` — rejected. Do not adopt. If the same proposal recurs, capture the rejection reason once as a `learnings` status item; reference the dismissed item id.
4. Never re-propose a dismissed item under a different title — that is how duplicates enter the knowledge base.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `knowledge_proposals` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_knowledge_proposals` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_knowledge_proposals` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `add_project_note` | action-mcp | required: `title`; optional `content`, `tags`, `html_source_path/type` |
| `add_project_knowledge_item` | action-mcp | required: `title`; optional `description`, `badge`, `active` |
| `add_project_decision_record` | action-mcp | required: `identifier`, `title` |
| `add_external_knowledge_asset` | action-mcp | required: `title`, `url`; optional `doc_type`, `source_type` |
| `add_knowledge_summary_item` | action-mcp | required: `title`, `description` |
| `add_knowledge_activity_log` | action-mcp | required: `actor_name`, `action_text` |

## Example

```json
{"event_type": "knowledge_proposal_resolved", "event_id": 91,
 "event_data": {"actor": {"username": "bob"}, "target_type": "AttentionItem",
   "content": "proposal: document task-mcp immutability rule",
   "content_payload": {"attention_item_id": 91, "project_id": 2,
     "meta_text": "update_ai_task only writes description/adder/assignee/actual_context/dispatched/finished/topic_id"}}}
```

Run: `knowledge_proposals(item_id: 91)` → resolved/approved → classification: durable fact → `project_knowledge_items(project_id: 2)` → no equivalent → `add_project_knowledge_item(project_id: 2, title: "task-mcp: update_ai_task field immutability", description: "<meta_text> — source proposal 91")` → `add_knowledge_activity_log(project_id: 2, actor_name: "w-ai", action_text: "adopted proposal 91 into knowledge items")` → 2 logs.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
