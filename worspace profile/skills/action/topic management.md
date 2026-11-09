# Topic management

Type: action skill
Purpose: owning topics, message analysis, room history topics, and — critically — the `tool_cal_logs` audit trail for every action you take.

Topics live on `/knowledge-mcp` (also reachable via `/mcp` and `/action-mcp`). The workspace profile creates topics sparingly: topics are the memory spine, so wrong topics are worse than no topics.

## Tools

| Tool | Endpoint | Required | Notes |
|---|---|---|---|
| `topics`, `get_topic`, `search_topics`, `room_topic_tree` | knowledge/read | — | list/get/search before creating anything |
| `create_topic` | knowledge+action | `name` | optional: `memory`, `state`, `importance_level`, `need_an_action`, `required_actions`, `parent_topic_id`, `related_topics`, `project_id`, `active` |
| `update_topic`, `delete_topic` | knowledge+action | — | merge semantics; delete only topics you created |
| `message_topics`, `get/create/update/delete_message_topic` | knowledge+action | create: message↔topic link | attach messages to topics when they extend a known thread |
| `message_analysis`, `get/create/update/delete_message_analysis` | knowledge+action | create: `message_id` | fields: `analysis`, `importance_level`, `message_content_summary`, `message_type`, `tags`, `is_a_response` |
| `room_history_topics`, `get/create/update/delete_room_history_topic` | knowledge+action | — | room-level historical clustering |
| `tool_cal_logs`, `get/create/update/delete_tool_cal_log` | knowledge+action | create: `used_tool_name` | your audit trail |

## Tool-call logging rules (binding for all skills)

After each successful state-changing call, `create_tool_cal_log`:
- `used_tool_name` = exactly the tool you called;
- scope: `project_id`, `room_id`, `topic_id` when applicable to the touched entity;
- `target_entity_id` = id string of the entity changed (dedupe anchor for event redelivery);
- `why_was_it_required` = triggering `event_type` or task id;
- `change_log` = one line, human-readable diff ("created milestone 12", "merged precondition into task 61").

Reads used purely for dedupe do not need logs; reads that drive a decision may be logged when the decision is non-obvious.

## Topic discipline

1. Never create a near-duplicate topic: `search_topics(name)` + `room_topic_tree(room_id)` first.
2. `importance_level` (integer) and `need_an_action` gate downstream automation — set them deliberately, copy them from the analysis that justifies the topic.
3. When an event or task belongs to an existing topic, link the task (`ai_tasks.topic_id` — settable ONLY at creation, so route new child tasks with `topic_id` rather than editing old ones) and add a `message_topic` link for the driving message.

## Example — record the footprint for a routed task

```json
{"tool": "create_ai_task", "arguments": {"description": "Draft MCP topic taxonomy", "project_id": 2,
  "topic_id": 7, "adder_profile": "workspace", "assigneee_profile": "knowledge",
  "input_event_entity_id": 456, "proposed_task_context": "message 456 in room 9 asks for taxonomy under topic 7"}}

{"tool": "create_message_topic", "arguments": {"message_id": 456, "topic_id": 7}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "create_message_topic",
  "project_id": 2, "room_id": 9, "topic_id": 7, "target_entity_id": "456",
  "why_was_it_required": "message_created -> routed taxonomy task",
  "change_log": "linked message 456 to topic 7; taxonomy task created under it"}}
```
