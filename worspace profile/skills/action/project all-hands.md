# Project all-hands

Type: action skill
Purpose: owning the three all-hands record families: takeaways, decisions, action items.

## Tools

| Family | Read | Create (required) | Edit | Delete |
|---|---|---|---|---|
| Takeaways | `project_all_hands_takeaway` | `add_project_all_hands_takeaway` (`text`; opt `tag`, `project_id`/`project_name`) | `edit_project_all_hands_takeaway` | `delete_project_all_hands_takeaway` |
| Decisions | `project_all_hands_decision` | `add_project_all_hands_decision` (`text`; opt `basis`, `impact`, `badge`) | `edit_project_all_hands_decision` | `delete_project_all_hands_decision` |
| Action items | `project_all_hands_action_item` | `add_project_all_hands_action_item` (`title`; opt `assignee_name` (fuzzy), `due_date`, `completed`) | `edit_project_all_hands_action_item` | `delete_project_all_hands_action_item` |

Read/list tools page with `page`/`per_page` and take `project_id`/`project_name` + their entity ids.

## Rules

1. All-hands decisions are the most-quoted records in a project: capture verbatim from the event/message `content` — do not paraphrase the human's wording; add interpretation only in a clearly-marked trailing note.
2. Decision families are distinct: all-hands decision (`add_project_all_hands_decision`) ≠ company-status decision (`decisions` item) ≠ ADR (`add_project_decision_record`). When one event spans layers (a decision taken in all-hands that becomes an ADR), write the record where the event says, and cross-reference ids in the other record's text — never copy blindly.
3. Action items assign humans (`assignee_name` fuzzy-resolves to users) — never assign a Hermes profile to an all-hands action item; profile work goes through `create_ai_task` routed with `input_event_entity_id` pointing at the action item.
4. Completion state is the assignee's to flip (events `all_hands_action_item_completed/reopened`); you may edit `title`/`due_date` corrections only.
5. Creating takeaways/decisions from a discussion is user-visible → approval discipline applies (`add_approve_request_with_message` with the drafted text in `payload`).

## Example — capture a decision from an all-hands thread

Message event quotes: "Decision: we ship task-mcp to the workspace profile first, kanban second — basis: routing latency; impact: coder queue unaffected."

Dedupe first:

```json
{"tool": "project_all_hands_decision", "arguments": {"project_id": 2}}
→ no equivalent

{"tool": "add_project_all_hands_decision", "arguments": {"project_id": 2,
  "text": "We ship task-mcp to the workspace profile first, kanban second.",
  "basis": "routing latency",
  "impact": "coder queue unaffected",
  "badge": "sequencing"}}

{"tool": "create_ai_task", "arguments": {"project_id": 2, "adder_profile": "workspace",
  "assigneee_profile": "coder",
  "description": "Implement task-mcp attachment for workspace profile per all-hands decision <id>",
  "proposed_task_context": "decision captured 2026-11-02; second step (kanban) explicitly deferred",
  "input_event_entity_id": "<decision id>", "level": 0}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "add_project_all_hands_decision",
  "project_id": 2, "target_entity_id": "<decision id>",
  "why_was_it_required": "message_created all-hands thread",
  "change_log": "captured sequencing decision + routed implementation task"}}
```
