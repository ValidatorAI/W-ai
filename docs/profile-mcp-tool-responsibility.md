# Profile MCP Tool Responsibility

This document defines which MCP tools should be considered core skills of each profile, with primary ownership focused on the `main` profile set:
- `delegator`
- `action`
- `knowledge`
- `normal message`
- `company`
- `company_project`
- `not_known_task`
- `cron_profile`

It also suggests secondary ownership for bot profiles (`project manager`, `business analyst`, `market research`, `coder`, `ask from w`) where role fit is strong.

## Assignment Principles

1. Keep `delegator` focused on routing and coordination, not heavy domain operations.
2. Keep write-heavy operational tools in `action`.
3. Keep read-heavy knowledge and retrieval tools in `knowledge`.
4. Keep conversational and room UX signaling in `normal message`.
5. Give bot profiles a specialized subset, not full platform-wide ownership.
6. Route unclear or ambiguous tasks to `not_known_task` for triage before execution.
7. Keep cron ownership as governance and delegation in `cron_profile`, not direct execution.
8. Tag or name cron cards explicitly so recurring workflows are machine-detectable.

## Main Profile Responsibilities

| MCP Tool Group | Delegator | Action | Knowledge | Normal Message | Company | Company Project | Not Known Task | Cron Profile |
|---|---|---|---|---|---|---|---|---|
| Core (`hello`) | Secondary | Secondary | Secondary | Primary | Secondary | Secondary | Secondary | Secondary |
| Room Interaction (`add_message`, `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_action_message`) | Secondary | Primary | Primary | Primary | Secondary | Secondary | Primary | Secondary |
| Approval Requests (`add_approval_request`, `add_approve_request_with_message`, `approval_requests`, `get_approval_request`, `edit_approval_request`, `delete_approval_request`, `add_decision_message`) | Primary | Primary | Secondary | Secondary | Secondary | Secondary | Secondary | Secondary |
| Company Home (mentions, blockers, AI confirm, outcomes review, knowledge proposals, material changes, decisions waiting + add/edit/list variants) | Primary | Secondary | Secondary | Secondary | Primary | Secondary | Secondary | Secondary |
| Company Status (`company_status_period`, `add_company_status_period`, `edit_company_status_period`, `changes`, `decisions`, `dependencies`, `learnings`, `priorities`, `progress`, `risks`) | Secondary | Primary | Secondary | None | Primary | Secondary | Secondary | Secondary |
| Project Milestones (`project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone`) | Secondary | Primary | Secondary | None | Secondary | Primary | Secondary | Secondary |
| Project Bottlenecks (`project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck`) | Secondary | Primary | Secondary | None | Secondary | Primary | Secondary | Secondary |
| Project Todos (`project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo`) | Secondary | Primary | Secondary | None | Secondary | Primary | Secondary | Secondary |
| Project All Hands (action items, decisions, takeaways + add/edit/delete/list variants) | Secondary | Primary | Secondary | None | Secondary | Primary | Secondary | Secondary |
| Project Decision Records (`project_decision_records`, `add_project_decision_record`, `edit_project_decision_record`, `delete_project_decision_record`) | Secondary | Secondary | Primary | None | Secondary | Secondary | Secondary | Secondary |
| Project Knowledge Items (`project_knowledge_items`, `add_project_knowledge_item`, `edit_project_knowledge_item`, `delete_project_knowledge_item`) | Secondary | Secondary | Primary | None | Secondary | Secondary | Secondary | Secondary |
| Knowledge Summary Items (`knowledge_summary_items`, `add_knowledge_summary_item`, `edit_knowledge_summary_item`, `delete_knowledge_summary_item`) | None | Secondary | Primary | None | Secondary | Secondary | Secondary | Secondary |
| Knowledge Activity Log (`knowledge_activity_log`, `add_knowledge_activity_log`, `edit_knowledge_activity_log`, `delete_knowledge_activity_log`) | None | Secondary | Primary | None | Secondary | Secondary | Secondary | Secondary |
| External Knowledge Assets (`external_knowledge_assets`, `add_external_knowledge_asset`, `edit_external_knowledge_asset`, `delete_external_knowledge_asset`) | None | Secondary | Primary | None | Secondary | Secondary | Secondary | Secondary |
| Project Obsidian Notes (`project_obsidian_note`, `add_project_obsidian_note`, `edit_project_obsidian_note`, `delete_project_obsidian_note`) | None | Secondary | Primary | None | Secondary | Secondary | Secondary | Secondary |
| Tree Directory (`tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item`) | Secondary | Primary | Primary | None | Secondary | Primary | Secondary | Secondary |
| Unclear Task Triage (classify unclear cards, request missing detail, delegate to best-fit owner) | Secondary | None | None | Secondary | Secondary | Secondary | Primary | Secondary |
| Cron Card Governance (define cron card, review cron tags/names, delegate recurring work to non-cron owner) | Secondary | Secondary | Secondary | None | Secondary | Secondary | Secondary | Primary |

## Suggested Skill Mapping by Profile

## `main/delegator` (must-have skills)

- `approval_requests`, `get_approval_request`, `add_decision_message`
- `add_approval_request`, `add_approve_request_with_message`, `edit_approval_request`, `delete_approval_request`
- Company-home triage signals:
- `mentions`, `add_mentions`, `edit_mentions`
- `blockers`, `add_blockers`, `edit_blockers`
- `decisions_waiting`, `add_decisions_waiting`, `edit_decisions_waiting`
- `ai_confirm`, `add_ai_confirm`, `edit_ai_confirm`
- `material_changes`, `add_material_changes`, `edit_material_changes`
- `outcomes_review`, `add_outcomes_review`, `edit_outcomes_review`
- `knowledge_proposals`, `add_knowledge_proposals`, `edit_knowledge_proposals`
- Minimal room signaling: `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`
- Unclear-input handling: create a kanban card and assign to `not_known_task` when user intent is not clear enough for safe execution.
- Cron handling: ensure cron tasks are tagged/named as cron cards and routed to a non-cron execution owner profile.

## `main/action` (must-have skills)

- Company status execution:
- `company_status_period`, `add_company_status_period`, `edit_company_status_period`
- `changes`, `decisions`, `dependencies`, `learnings`, `priorities`, `progress`, `risks`
- Delivery and execution trackers:
- `project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo`
- `project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone`
- `project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck`
- `project_all_hands_action_item`, `add_project_all_hands_action_item`, `edit_project_all_hands_action_item`, `delete_project_all_hands_action_item`
- `project_all_hands_decision`, `add_project_all_hands_decision`, `edit_project_all_hands_decision`, `delete_project_all_hands_decision`
- `project_all_hands_takeaway`, `add_project_all_hands_takeaway`, `edit_project_all_hands_takeaway`, `delete_project_all_hands_takeaway`
- Shared collaboration tools:
- `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`, `add_action_message`

## `main/knowledge` (must-have skills)

- Knowledge base operations:
- `project_knowledge_items`, `add_project_knowledge_item`, `edit_project_knowledge_item`, `delete_project_knowledge_item`
- `knowledge_summary_items`, `add_knowledge_summary_item`, `edit_knowledge_summary_item`, `delete_knowledge_summary_item`
- `knowledge_activity_log`, `add_knowledge_activity_log`, `edit_knowledge_activity_log`, `delete_knowledge_activity_log`
- `external_knowledge_assets`, `add_external_knowledge_asset`, `edit_external_knowledge_asset`, `delete_external_knowledge_asset`
- `project_decision_records`, `add_project_decision_record`, `edit_project_decision_record`, `delete_project_decision_record`
- `project_obsidian_note`, `add_project_obsidian_note`, `edit_project_obsidian_note`, `delete_project_obsidian_note`
- Directory/file context:
- `tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item`
- Collaboration essentials:
- `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`

## `main/normal message` (must-have skills)

- Conversational room output:
- `add_message`, `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_action_message`
- Optional lightweight reads only:
- `approval_requests` (read only)
- `mentions` (read only)

## `main/company` (must-have skills)

- Company coordination and status:
- `company_status_period`, `add_company_status_period`, `edit_company_status_period`
- `priorities`, `progress`, `risks`, `dependencies`, `changes`, `decisions`, `learnings`
- Company-home coordination signals:
- `mentions`, `blockers`, `decisions_waiting`, `ai_confirm`, `material_changes`, `outcomes_review`, `knowledge_proposals`
- Collaboration essentials:
- `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`

## `main/company_project` (must-have skills)

- Project planning and execution coordination:
- `project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo`
- `project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone`
- `project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck`
- `project_all_hands_action_item`, `project_all_hands_decision`, `project_all_hands_takeaway` (+ add/edit/delete variants)
- Shared collaboration tools:
- `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`, `add_action_message`

## `main/not_known_task` (must-have skills)

- Unclear-card triage and reassignment:
- `add_message`, `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_action_message`
- Optional decision/approval relay:
- `approval_requests`, `get_approval_request`, `add_decision_message`
- Required behavior:
- receive unclear cards, identify likely intent, and delegate the card to the proper profile with rationale.

## `main/cron_profile` (must-have skills)

- Cron governance and recurrence orchestration:
- `add_message`, `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_action_message`
- Optional project tracking updates when required by recurrence execution:
- `project_todos`, `edit_project_todo`, `project_milestones`, `edit_project_milestone`
- Required behavior:
- define what qualifies as a cron card, review cron-tagged/named cards, delegate execution to non-cron owner profiles, and create follow-up cards for repetitive invocations.

## Bot Profile Skill Suggestions

## `bots/project manager`

Primary tools:
- `project_milestones*`, `project_todos*`, `project_bottlenecks*`
- `project_all_hands_*`
- `company_status_period`, `progress`, `risks`, `dependencies`, `priorities`
- `project_decision_records*`

## `bots/business analyst`

Primary tools:
- `project_decision_records*`
- `project_knowledge_items*`, `knowledge_summary_items*`
- `learnings`, `changes`, `dependencies`, `risks`
- `knowledge_proposals*`, `outcomes_review*`

## `bots/market research`

Primary tools:
- `external_knowledge_assets*`
- `knowledge_activity_log*`
- `project_knowledge_items*`, `knowledge_summary_items*`
- `project_obsidian_note*`

## `bots/coder`

Primary tools:
- `project_todos*` (implementation tasks)
- `project_bottlenecks*` (technical blockers)
- `project_decision_records*` (technical ADRs)
- `project_knowledge_items*`, `project_obsidian_note*`
- `tree_based_project_directory_data` (project file context)

## `bots/ask from w`

Primary tools:
- `add_message`, `add_loading_message`, `edit_loading_message`, `delete_loading_message`
- Optional: `approval_requests` (read only) when acting as a request relay

## Notes on Aliases

- Prefer canonical snake_case names from `TOOLS_REFERENCE.md`.
- Treat PascalCase aliases as compatibility-only; do not assign aliases as profile skills.

## Routing and Card Lifecycle Rules

- Router fallback for unclear input: if user input is not clear enough, create a kanban card and assign it to `not_known_task` for triage.
- `not_known_task` must determine what should be done for an unclear card and delegate the card to the proper owner profile.
- Cron cards must be tagged or named as cron cards and should not be directly assigned to `cron_profile` as execution work.
- `cron_profile` is responsible for defining cron cards, reviewing cron cards, delegating them to proper owner profiles, and creating follow-up cards for repetitive schedules.
- Preserve room/project/company context and include delegation rationale in card updates.
