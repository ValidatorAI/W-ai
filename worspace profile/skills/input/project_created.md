# Project created

Type: input-processing skill
Apply when: a `project_created` event arrives (`event_data.target_type: "Project"`).

## Procedure

1. Read the new project record: `get_single_project` by `project_id` (or `project_slug`) from `event_data.content_payload`.
2. Decide what a brand-new project is missing that only structure requires:
   - `tree_based_project_directory_data` for this project — if empty, scaffold the knowledge root with `add_tree_based_project_directory_item(name: "knowledge", item_type: "directory", project_id: ...)`.
   - `add_knowledge_activity_log(actor_name: "w-ai", action_text: "project <slug> created", target_path: <line from event_data.knowledge_path>)`.
3. If the project needs first milestones/todos/status alignment, do **not** invent them — route: `create_ai_task(project_id: ..., adder_profile: "workspace", assigneee_profile: "planner", description: "Define initial milestones, todos, and status-period alignment for project <slug>", proposed_task_context: "<project payload summary>", input_event_entity_id: <event_id>, level: 0)`.
4. Never post a celebration message for this event; it is not a work signal.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `get_single_project` | read-mcp | `project_id` / `project_name` / `project_slug` |
| `tree_based_project_directory_data` | read-mcp | `project_id` |
| `add_tree_based_project_directory_item` | action-mcp | required: `name`; optional: `item_type` (`directory`\|`knowledge_item`\|`adr`\|`note`), `parent_id`, `content`, `file_path` |
| `add_knowledge_activity_log` | action-mcp | required: `actor_name`, `action_text`; optional: `target_path`, `target_url`, `actor_color` |
| `create_ai_task` | task-mcp | required: `description`; see `task management` skill |

## Example

```json
{"event_type": "project_created", "event_id": 31,
 "event_data": {"actor": {"username": "alice"}, "target_type": "Project",
   "content_payload": {"project_id": 31, "slug": "atlas"},
   "knowledge_path": "<knowledge_path>\n- /company/1/projects/31/knowledge\n</knowledge_path>"}}
```

Run: directory check → empty → `add_tree_based_project_directory_item(project_id: 31, name: "knowledge", item_type: "directory")` → `add_knowledge_activity_log(project_id: 31, actor_name: "w-ai", action_text: "project atlas created", target_path: "/company/1/projects/31/knowledge")` → `create_ai_task(project_id: 31, adder_profile: "workspace", assigneee_profile: "planner", description: "Define initial milestones/todos/status alignment for atlas", proposed_task_context: "created 2026-11-02 by alice; no structure yet", input_event_entity_id: 31)` → one `create_tool_cal_log` per write (3 logs).

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`; company-status item and approval flows add `approved` / `denied` / `canceled` via events.
- If the target profile or room is ambiguous, prefer minimal justified action or route a clarification task; never guess identities.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
