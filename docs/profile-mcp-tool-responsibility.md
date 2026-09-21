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

Related document:
- `profile-description.md` for concise role descriptions of each main and bot profile.
- `profile-workflows-and-interactions.md` for workflow and interaction charts.
- `bonfire/docs/MCP_ENTITY.md` and `bonfire/docs/AI_PROFILE_MCP_ENTITY.md` (mirrored under `W-ai/docs/bonfire/docs/`) for persistence details.

It also suggests secondary ownership for bot profiles (`project manager`, `business analyst`, `market research`, `coder`, `ask from w`) where role fit is strong.

## MCP Persistence Mapping

The profile-to-MCP ownership model is persisted in Bonfire with two tables:

- `mcps`: MCP endpoint configuration catalog (`name`, `transport`, `url`, `authentication`, optional `bearer_token`, `status`).
- `ai_profile_mcps`: join table from `ai_profiles` to `mcps` with per-profile activation via `active`.

Key constraint:

- Unique assignment per profile and MCP endpoint (`ai_profile_id`, `mcp_id`).

Practical routing impact:

- Profile responsibility in this document defines who should use tools.
- `ai_profile_mcps.active` defines which MCP integrations are actually enabled per profile at runtime.

## Assignment Principles

1. Keep `delegator` focused on routing and coordination, not heavy domain operations.
2. Keep write-heavy operational tools in `action`.
3. Keep read-heavy knowledge and retrieval tools in `knowledge`.
4. Keep `normal message` focused on capturing conversational content into OV, not sending direct user replies.
5. Give bot profiles a specialized subset, not full platform-wide ownership.
6. Route unclear or ambiguous tasks to `not_known_task` for triage before execution.
7. Keep cron ownership as governance and delegation in `cron_profile`, not direct execution.
8. Tag or name cron cards explicitly so recurring workflows are machine-detectable.
9. Main profiles should interact with each other primarily through company kanban card assignment.

## Responsibility Labels

- `Primary`: default owner for the tool group; first routing choice.
- `Secondary`: support owner; can use tools when context requires it.
- `Not-Using`: profile should not use that tool group in normal operation.

## Main Profile Responsibilities

| MCP Tool Group | Delegator | Action | Knowledge | Normal Message | Company | Company Project | Not Known Task | Cron Profile |
|---|---|---|---|---|---|---|---|---|
| Core (`hello`) | Secondary | Secondary | Secondary | Primary | Secondary | Secondary | Secondary | Secondary |
| Room Interaction (`add_message`, `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_action_message`) | Not-Using | Primary | Primary | Primary | Secondary | Secondary | Primary | Secondary |
| Approval Requests (`add_approval_request`, `add_approve_request_with_message`, `approval_requests`, `get_approval_request`, `edit_approval_request`, `delete_approval_request`, `add_decision_message`) | Primary | Primary | Secondary | Secondary | Secondary | Secondary | Secondary | Secondary |
| Company Home (mentions, blockers, AI confirm, outcomes review, knowledge proposals, material changes, decisions waiting + add/edit/list variants) | Primary | Secondary | Secondary | Secondary | Primary | Secondary | Secondary | Secondary |
| Company Status (`company_status_period`, `add_company_status_period`, `edit_company_status_period`, `changes`, `decisions`, `dependencies`, `learnings`, `priorities`, `progress`, `risks`) | Secondary | Primary | Secondary | Not-Using | Primary | Secondary | Secondary | Secondary |
| Project Milestones (`project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone`) | Secondary | Primary | Secondary | Not-Using | Secondary | Primary | Secondary | Secondary |
| Project Bottlenecks (`project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck`) | Secondary | Primary | Secondary | Not-Using | Secondary | Primary | Secondary | Secondary |
| Project Todos (`project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo`) | Secondary | Primary | Secondary | Not-Using | Secondary | Primary | Secondary | Secondary |
| Project All Hands (action items, decisions, takeaways + add/edit/delete/list variants) | Secondary | Primary | Secondary | Not-Using | Secondary | Primary | Secondary | Secondary |
| Project Decision Records (`project_decision_records`, `add_project_decision_record`, `edit_project_decision_record`, `delete_project_decision_record`) | Secondary | Secondary | Primary | Not-Using | Secondary | Secondary | Secondary | Secondary |
| Project Knowledge Items (`project_knowledge_items`, `add_project_knowledge_item`, `edit_project_knowledge_item`, `delete_project_knowledge_item`) | Secondary | Secondary | Primary | Not-Using | Secondary | Secondary | Secondary | Secondary |
| Knowledge Summary Items (`knowledge_summary_items`, `add_knowledge_summary_item`, `edit_knowledge_summary_item`, `delete_knowledge_summary_item`) | Not-Using | Secondary | Primary | Not-Using | Secondary | Secondary | Secondary | Secondary |
| Knowledge Activity Log (`knowledge_activity_log`, `add_knowledge_activity_log`, `edit_knowledge_activity_log`, `delete_knowledge_activity_log`) | Not-Using | Secondary | Primary | Not-Using | Secondary | Secondary | Secondary | Secondary |
| External Knowledge Assets (`external_knowledge_assets`, `add_external_knowledge_asset`, `edit_external_knowledge_asset`, `delete_external_knowledge_asset`) | Not-Using | Secondary | Primary | Not-Using | Secondary | Secondary | Secondary | Secondary |
| Project Obsidian Notes (`project_obsidian_note`, `add_project_obsidian_note`, `edit_project_obsidian_note`, `delete_project_obsidian_note`) | Not-Using | Secondary | Primary | Not-Using | Secondary | Secondary | Secondary | Secondary |
| Tree Directory (`tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item`) | Secondary | Primary | Primary | Not-Using | Secondary | Primary | Secondary | Secondary |
| Unclear Task Triage (classify unclear cards, request missing detail, delegate to best-fit owner) | Secondary | Not-Using | Not-Using | Secondary | Secondary | Secondary | Primary | Secondary |
| Cron Card Governance (define cron card, review cron tags/names, delegate recurring work to non-cron owner) | Secondary | Secondary | Secondary | Not-Using | Secondary | Secondary | Secondary | Primary |

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
- Room interaction tools are `Not-Using` for delegator; delegator routes instead of posting room interaction outputs.
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
- If Obsidian MCP is present, use it to maintain linked project knowledge structure in sync with knowledge records.
- Directory/file context:
- `tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item`
- Collaboration essentials:
- `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`

## `main/normal message` (must-have skills)

- Conversational content capture to OV:
- store normalized message context and intent summary in OV
- No direct user reply from this profile (`add_message` is Not-Using)
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

- Explicit @mention passthrough is bot-only (`project manager`, `business analyst`, `market research`, `coder`, `ask from w`).
- Explicit @mention of main profiles is not a direct command; delegator still classifies and routes to main profiles.
- Main-profile delegation should occur through company kanban card assignment, not direct profile invocation.
- Router fallback for unclear input: if user input is not clear enough, create a kanban card and assign it to `not_known_task` for triage.
- `not_known_task` must determine what should be done for an unclear card and delegate the card to the proper owner profile.
- Cron cards must be tagged or named as cron cards and should not be directly assigned to `cron_profile` as execution work.
- `cron_profile` is responsible for defining cron cards, reviewing cron cards, reassigning them on company kanban to proper owner profiles, and creating follow-up cards for repetitive schedules.
- Create/delete room and create/delete project tasks must also be delegated to `knowledge` so the OV structure stays consistent.
- Preserve room/project/company context and include delegation rationale in card updates.

## Workflow Diagrams

### 1) Explicit Profile Mention Routing

```mermaid
flowchart TD
	A[User message] --> B{Contains explicit @profile mention?}
	B -- No --> C[Continue to intent classification workflow]
	B -- Yes --> D{Mentioned profile type}
	D -- Bot profile --> E[delegator forwards original message unchanged]
	E --> F[project manager or business analyst or market research or coder or ask from w]
	D -- Main profile --> G[delegator ignores direct main-profile command]
	G --> C
```

### 2) Clear Intent Classification Routing

```mermaid
flowchart TD
	A[Incoming request] --> B[delegator classifies intent]
	B --> C{Request type}
	C -- execution or delivery --> D[action via company kanban assignment]
	C -- research or information --> E[knowledge via company kanban assignment]
	C -- conversational content capture to OV --> F[normal message via company kanban assignment]
	C -- company-level coordination --> G[company via company kanban assignment]
	C -- project-level planning --> H[company_project via company kanban assignment]
	C -- unclear --> I[not_known_task via company kanban assignment]
	C -- recurring or scheduled --> J[cron_profile via company kanban assignment]
	C -- create/delete room or project --> K[primary owner by intent]
	K --> L[also assign linked card to knowledge for OV structure update]
```

### 3) Unclear Input Triage and Delegation

```mermaid
flowchart TD
	A[Unclear user input] --> B[delegator creates kanban card]
	B --> C[assign card to not_known_task]
	C --> D[not_known_task triage]
	D --> E{Best-fit owner}
	E -- action --> F[reassign company kanban card to action]
	E -- knowledge --> G[reassign company kanban card to knowledge]
	E -- normal message OV capture --> H[reassign company kanban card to normal message]
	E -- company --> I[reassign company kanban card to company]
	E -- company_project --> J[reassign company kanban card to company_project]
	E -- cron governance --> K[reassign company kanban card to cron_profile]
	E -- still unclear --> L[request missing detail]
```

### 4) Company and Project Coordination Flow

```mermaid
flowchart TD
	A[New card or initiative] --> B{Scope}
	B -- company-wide --> C[company]
	B -- project-specific --> D[company_project]
	C --> E[align priorities blockers dependencies]
	D --> F[align milestones todos bottlenecks]
	E --> G{Needs execution?}
	F --> G
	G -- yes --> H[assign company kanban card to action]
	G -- knowledge needed --> I[assign company kanban card to knowledge]
	G -- OV conversational logging --> J[assign company kanban card to normal message]
	D --> K{create/delete room or project?}
	K -- yes --> I
```

### 5) Cron Card Lifecycle

```mermaid
flowchart TD
	A[Recurring need detected] --> B[cron_profile defines if card is cron]
	B --> C[tag or name card as cron]
	C --> D[reassign company kanban card to non-cron owner]
	D --> E{Owner profile}
	E -- action --> F[action executes]
	E -- knowledge --> G[knowledge executes]
	E -- company --> H[company executes]
	E -- company_project --> I[company_project executes]
	F --> J{Is repetitive?}
	G --> J
	H --> J
	I --> J
	J -- yes --> K[create follow-up cron card for next run]
	J -- no --> L[close card]
```

## Profile Tool Access Diagrams

### `main/delegator`

```mermaid
flowchart LR
	P[delegator] --> A[approval requests]
	P --> B[company home signals]
	P --> C[routing and kanban delegation]
	P --> D[cron governance routing]
	P -. Not-Using .-> E[room interaction tools]
```

### `main/action`

```mermaid
flowchart LR
	P[action] --> A[company status tools]
	P --> B[project todos milestones bottlenecks]
	P --> C[project all hands tools]
	P --> D[room interaction tools]
	P --> E[action messages]
```

### `main/knowledge`

```mermaid
flowchart LR
	P[knowledge] --> A[project knowledge items]
	P --> B[knowledge summary and activity log]
	P --> C[external knowledge assets]
	P --> D[decision records and obsidian notes]
	P --> E[obsidian MCP integration when available]
	P --> F[tree directory data]
	P --> G[room interaction tools]
```

### `main/normal message`

```mermaid
flowchart LR
	P[normal message] --> A[OV conversational content update]
	P --> B[lightweight reads: approval requests mentions]
	P -. Not-Using .-> C[add_message]
	P -. Not-Using .-> D[project and knowledge ownership tools]
```

### `main/company`

```mermaid
flowchart LR
	P[company] --> A[company status tools]
	P --> B[company home coordination signals]
	P --> C[cross project alignment]
	P --> D[assign tasks to other main profiles through company kanban]
```

### `main/company_project`

```mermaid
flowchart LR
	P[company_project] --> A[project todos milestones bottlenecks]
	P --> B[project all hands records]
	P --> C[project sequencing and assignment]
	P --> D[assign tasks to other main profiles through company kanban]
	P --> E[cron tagged project work delegation]
```

### `main/not_known_task`

```mermaid
flowchart LR
	P[not_known_task] --> A[unclear task triage]
	P --> B[reassign cards through company kanban]
	P --> C[approval read and decision relay]
	P --> D[delegation to best fit owner]
```

### `main/cron_profile`

```mermaid
flowchart LR
	P[cron_profile] --> A[cron definition and qualification]
	P --> B[cron tag and naming governance]
	P --> C[reassign cron cards through company kanban]
	P --> D[follow up recurring card creation]
	P -. Not-Using .-> E[direct profile invocation]
```

### `bots/project manager`

```mermaid
flowchart LR
	P[project manager] --> A[project milestones todos bottlenecks]
	P --> B[project all hands tools]
	P --> C[company status: progress risks dependencies priorities]
	P --> D[project decision records]
```

### `bots/business analyst`

```mermaid
flowchart LR
	P[business analyst] --> A[project decision records]
	P --> B[project knowledge and summary items]
	P --> C[learnings changes dependencies risks]
	P --> D[knowledge proposals and outcomes review]
```

### `bots/market research`

```mermaid
flowchart LR
	P[market research] --> A[external knowledge assets]
	P --> B[knowledge activity log]
	P --> C[project knowledge and summary items]
	P --> D[project obsidian notes]
```

### `bots/coder`

```mermaid
flowchart LR
	P[coder] --> A[project todos for implementation]
	P --> B[project bottlenecks for technical blockers]
	P --> C[project decision records for technical ADRs]
	P --> D[project knowledge and obsidian notes]
	P --> E[tree based project directory data]
```

### `bots/ask from w`

```mermaid
flowchart LR
	P[ask from w] --> A[add message]
	P --> B[loading message lifecycle]
	P --> C[approval requests read only relay]
	P -. Not-Using .-> D[project and knowledge ownership tools]
```

## Profile Interaction Graph (Kanban-Based)

```mermaid
flowchart TD
	D[delegator] -->|assign card| A[action]
	D -->|assign card| K[knowledge]
	D -->|assign card| N[normal message]
	D -->|assign card| C[company]
	D -->|assign card| CP[company_project]
	D -->|assign card| U[not_known_task]
	D -->|assign card| CR[cron_profile]

	C -->|reassign card| A
	C -->|reassign card| K
	C -->|reassign card| CP
	C -->|reassign card| U

	CP -->|reassign card| A
	CP -->|reassign card| K
	CP -->|reassign card| U
	CP -->|tag cron and reassign| CR

	U -->|triage and reassign| A
	U -->|triage and reassign| K
	U -->|triage and reassign| N
	U -->|triage and reassign| C
	U -->|triage and reassign| CP
	U -->|cron governance| CR

	CR -->|reassign cron card| A
	CR -->|reassign cron card| K
	CR -->|reassign cron card| C
	CR -->|reassign cron card| CP

	PM[project manager] -->|bot mention or delegated card| D
	BA[business analyst] -->|bot mention or delegated card| D
	MR[market research] -->|bot mention or delegated card| D
	CD[coder] -->|bot mention or delegated card| D
	AW[ask from w] -->|bot mention relay| D
```
