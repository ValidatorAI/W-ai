# Mention / requested review (resolved / dismissed)

Type: input-processing skill
Apply when: events `mention_resolved` or `mention_dismissed`.

## Procedure

1. Read the item: `mentions(item_id: <event_id>)` — it carries `user_id` (who was mentioned) and often a room.
2. This family is usually **someone else's turn**, not yours:
   - if the mentioned user is represented by a profile you coordinate (check `get_ai_profile` / naming convention), route: `create_ai_task(description: "Respond to mention: <item title>", room_id: <item.room_id>, project_id: <item.project_id>, assigneee_profile: <profile>, input_event_entity_id: <event_id>, proposed_task_context: "<mention context>")`;
   - if the mention is resolved (the human already replied), verify nothing is left untracked: `search_messages_of_room(room_id: <item.room_id>)` recent messages for follow-up commitments; if a commitment exists that no todo/task carries, create the todo or task — not both.
3. `mention_dismissed` — nobody owed a response. Verification log only.
4. Never answer a mention by posting messages as the mentioned person.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `mentions` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_mentions` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_mentions` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `get_ai_profile` | config-mcp | confirm the owning profile exists |
| `search_messages_of_room` | read-mcp | required: `room_id` |
| `create_ai_task` | task-mcp | required: `description` |
| `add_project_todo` | action-mcp | required: `title` |

## Example

```json
{"event_type": "mention_resolved", "event_id": 60,
 "event_data": {"actor": {"username": "dana"}, "target_type": "AttentionItem",
   "content": "mention of alice resolved",
   "content_payload": {"attention_item_id": 60, "room_id": 9, "project_id": 2}}}
```

Run: `mentions(item_id: 60)` → resolved → `search_messages_of_room(room_id: 9, from_message_id: <mention source>)` → alice's reply promises "docs by Friday", nothing tracks it → `add_project_todo(project_id: 2, title: "Ship integration docs by Friday (committed in room 9 reply)")` → log. If a matching open todo had existed: verification log only.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
