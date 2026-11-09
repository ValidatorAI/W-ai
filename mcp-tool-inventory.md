# MCP Tool Inventory

This document records the MCP servers and tool catalogs visible from the current repo evidence.

## Sources used
- `W-ai/default-profile-mcp.xml`
- `bonfire/config/ai/ai_config.xml`
- `bonfire/config/routes.rb`
- `bonfire/docs/W_BRIDGE_FEATURES_AND_PORTING_PLAN.md`
- `W-ai/docs/W-bridge/docs/mcp/TOOLS_REFERENCE.md`
- `bonfire/config/ai/ai_config.xml` memory MCP notes

## 1) Bonfire native MCP endpoints
These are the built-in Bonfire HTTP MCP endpoints defined in the app:

- `POST /mcp`
- `POST /action-mcp`
- `POST /read-mcp`
- `POST /knowledge-mcp`
- `POST /task-mcp`

These are the app-native MCP entrypoints, not separate external server names.

## 2) Configured MCP servers
The generated default profile includes three configured servers:

### A. `w-bridge`
- URL: `http://0.0.0.0:8031/mcp`
- Transport: `http`
- Authentication: `none`
- Tool selection: `all`
- Status: `enabled`

This is the main Bonfire/W-bridge MCP server.

The repo documentation states the registry contains:
- 171 total tools
- 112 canonical tools
- 59 alias tools

Major tool families documented:

#### Core
- `hello`

#### Company Home
- `add_ai_confirm`
- `add_blockers`
- `add_decisions_waiting`
- `add_knowledge_proposals`
- `add_material_changes`
- `add_mentions`
- `add_outcomes_review`
- `ai_confirm`
- `blockers`
- `decisions_waiting`
- `knowledge_proposals`
- `material_changes`
- `mentions`
- `outcomes_review`
- `edit_ai_confirm`
- `edit_blockers`
- `edit_decisions_waiting`
- `edit_knowledge_proposals`
- `edit_material_changes`
- `edit_mentions`
- `edit_outcomes_review`

#### Company Status
- `add_company_status_period`
- `company_status_period`
- `edit_company_status_period`
- `priorities`
- `progress`
- `risks`
- `dependencies`
- `changes`
- `decisions`
- `learnings`

#### Project milestones
- `add_project_milestone`
- `edit_project_milestone`
- `delete_project_milestone`
- `project_milestones`

#### Project bottlenecks
- `add_project_bottleneck`
- `edit_project_bottleneck`
- `delete_project_bottleneck`
- `project_bottlenecks`

#### Project todos
- `add_project_todo`
- `edit_project_todo`
- `delete_project_todo`
- `project_todos`

#### Project knowledge items
- `add_project_knowledge_item`
- `edit_project_knowledge_item`
- `delete_project_knowledge_item`
- `project_knowledge_items`

#### Project all-hands records
- `add_project_all_hands_action_item`
- `add_project_all_hands_decision`
- `add_project_all_hands_takeaway`
- `edit_project_all_hands_action_item`
- `edit_project_all_hands_decision`
- `edit_project_all_hands_takeaway`
- `delete_project_all_hands_action_item`
- `delete_project_all_hands_decision`
- `delete_project_all_hands_takeaway`
- `project_all_hands_action_item`
- `project_all_hands_decision`
- `project_all_hands_takeaway`

#### Project decision records
- `add_project_decision_record`
- `edit_project_decision_record`
- `delete_project_decision_record`
- `project_decision_records`

#### External knowledge assets
- `add_external_knowledge_asset`
- `edit_external_knowledge_asset`
- `delete_external_knowledge_asset`
- `external_knowledge_assets`

#### Knowledge activity log
- `add_knowledge_activity_log`
- `edit_knowledge_activity_log`
- `delete_knowledge_activity_log`
- `knowledge_activity_log`

#### Tree directory
- `add_tree_based_project_directory_item`
- `edit_tree_based_project_directory_item`
- `delete_tree_based_project_directory_item`
- `tree_based_project_directory_data`

#### Knowledge summary items
- `add_knowledge_summary_item`
- `edit_knowledge_summary_item`
- `delete_knowledge_summary_item`
- `knowledge_summary_items`

#### Project Obsidian notes
- `add_project_obsidian_note`
- `edit_project_obsidian_note`
- `delete_project_obsidian_note`
- `project_obsidian_note`

#### Room interaction
- `add_action_message`
- `add_decision_message`
- `add_loading_message`
- `add_message`
- `delete_loading_message`
- `edit_loading_message`

#### Approval requests
- `add_approval_request`
- `add_approve_request_with_message`
- `approval_requests`
- `delete_approval_request`
- `edit_approval_request`
- `get_approval_request`

#### AI config
- `list_ai_profiles`
- `get_ai_profile`
- `list_ai_settings`
- `get_ai_setting`
- `list_mcps`
- `get_mcp`
- `list_tools`
- `get_tool`

### B. `Workspace memory`
- URL: `http://127.0.0.1:1933/mcp`
- Transport: `http`
- Authentication: `none`
- Tool selection: `all`
- Status: `enabled`

Repo docs identify this as the OpenViking-backed memory MCP. On a healthy session boot, the server registers 19 tools:

- `find`
- `search`
- `grep`
- `glob`
- `read`
- `list`
- `tree`
- `remember`
- `write`
- `edit`
- `add_resource`
- `list_watches`
- `cancel_watch`
- `forget`
- `health`
- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

Notes:
- In-session these appear as `mcp__memory__...` names.
- They are session-start-bound; if the server is not healthy when the session starts, they may be absent even if the server later recovers.

### C. `obisidian`
- URL: `http://127.0.0.1:27123/mcp/`
- Transport: `http`
- Authentication: `bearer`
- Tool selection: `all`
- Status: `enabled`

The repo references mention Obsidian MCP as a configured knowledge integration, but the Bonfire/W-bridge docs do not provide a confirmed tool catalog for it. So this server is configured and active, but its per-tool list is not explicitly documented in the repo evidence.

## 3) Summary
The confirmed MCP inventory in this repo is:

- `w-bridge` — full Bonfire tool catalog
- `Workspace memory` — OpenViking memory tools, 19 documented tools
- `obisidian` — configured, but no explicit repo-documented tool list
- native Bonfire endpoints — `/mcp`, `/action-mcp`, `/read-mcp`, `/knowledge-mcp`, `/task-mcp`

## 4) Practical guidance
For implementation and automation, treat the following as the source of truth:

- `w-bridge` for Bonfire domain actions and read/write operations
- `Workspace memory` for memory and knowledge retrieval/editing
- `obisidian` as an availability-dependent integration that should be checked at runtime rather than assumed from static docs

