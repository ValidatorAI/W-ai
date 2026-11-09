# Project overview

Type: action skill
Purpose: owning the project record surface: reading projects and maintaining milestones, todos, and bottlenecks.

## Tools

| Entity | Read | Create | Edit | Delete |
|---|---|---|---|---|
| Projects | `get_projects` (filters/paging), `get_single_project` (`project_id`/`project_name`/`project_slug`), `get_project_users`, `get_user_projects` | — (creation is a human/UI flow; `project_created` event notifies you) | — | — |
| Milestones | `project_milestones` (`project_id`, `milestone_id`) | `add_project_milestone` (req `title`; opt `status`, `active`, `target_date`) | `edit_project_milestone` | `delete_project_milestone` |
| Todos | `project_todos` (`project_id`, `todo_id`) | `add_project_todo` (req `title`; opt `meta_text`, `completed`) | `edit_project_todo` (req `todo_id`) | `delete_project_todo` |
| Bottlenecks | `project_bottlenecks` (`project_id`, `bottleneck_id`) | `add_project_bottleneck` (req `title`; opt `description`, `severity`, `resolved`) | `edit_project_bottleneck` | `delete_project_bottleneck` |

All list tools page with `page`/`per_page`; all create/edit/delete accept `project_id` or `project_name` (fuzzy).

## Rules

1. Project scoping: resolve once per event with `get_single_project`; every write below carries that `project_id`.
2. Milestones are commitments — creating or moving a `target_date` is user-visible and high-impact: approval first. Todos and bottlenecks can be recorded without approval when they come directly from an event with a human actor, because they are captures of human statements, not decisions by you.
3. `severity` on bottlenecks: use the event's own wording; when inventing a level, stay conservative (`low`/`medium`).
4. Reuse over recreate: a reopened todo (see input skill) means `edit_project_todo(completed: false)`, not a new row.
5. Never delete project records you didn't create; flag them (`add_mentions` to the owner) instead.

## Example — bottleneck from a task failure report

```json
{"tool": "project_bottlenecks", "arguments": {"project_id": 2}}
→ none citing bridge timeouts

{"tool": "add_project_bottleneck", "arguments": {"project_id": 2,
  "title": "w-bridge long-poll hangs under concurrent load",
  "severity": "high",
  "description": "300s MCP bridge hangs observed while processing events (see task 77, risk 143)",
  "resolved": false}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "add_project_bottleneck",
  "project_id": 2, "target_entity_id": "<bottleneck id>",
  "why_was_it_required": "task 77 blocked report",
  "change_log": "recorded load-timeout bottleneck"}}
```
