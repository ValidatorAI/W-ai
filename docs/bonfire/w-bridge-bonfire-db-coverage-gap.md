# W-bridge MCP support matrix for Bonfire models

## Scope

This matrix is intentionally model-based and ignores naming language such as "get all", "list", or "fetch". It answers a simpler question:

- Which Bonfire tables/models are reachable through W-bridge MCP?
- For each model, is there support for a single-record read?
- Is there support for all-record reads?
- Are there filters or search paths?
- Which exact W-bridge tools back that model?

## Legend

- ✅ = supported
- ⚠️ = partial support
- ❌ = not exposed by W-bridge MCP
- ✅ = needed for Knowledge MCP
- ❌ = not needed for Knowledge MCP
- — = no direct W-bridge path found

## Real Bonfire tables and W-bridge support

Important: for database coverage, the target should be the actual underlying tables, not STI subtype classes such as `rooms::open`, `rooms::closed`, etc. Those are class variants of the same underlying room table and are not independent DB support targets.

| Actual Bonfire table / model | Single record | All records | Filters | Search | Need for knowledge MCP | Paginated | W-bridge MCP tools | Status |
|---|---|---:|---|---|---|---|---|---|
| `rooms` | ✅ | ✅ | `project_id`, `room_id`, `room_name`, room type / parent context | ✅ | ✅ | ✅ | `list_rooms`, `get_room`, `list_room_threads`, `search_rooms` | Supported |
| `accounts` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `agents` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `ai_profile_mcps` | ✅ | ✅ | `ai_profile_id`, `mcp_id` | ❌ | ❌ | ✅ | `list_ai_profile_mcps`, `get_ai_profile_mcp` | Supported |
| `ai_profile_skills` | ✅ | ✅ | `ai_profile_id`, `skill_id` | ❌ | ❌ | ✅ | `list_ai_profile_skills`, `get_ai_profile_skill` | Supported |
| `ai_profile_tools` | ✅ | ✅ | `ai_profile_id`, `tool_id` | ❌ | ❌ | ✅ | `list_ai_profile_tools`, `get_ai_profile_tool` | Supported |
| `ai_profiles` | ✅ | ✅ | profile/config filters | ❌ | ❌ | ✅ | `list_ai_profiles`, `get_ai_profile` | Supported |
| `ai_settings` | ✅ | ✅ | config-scoped filters | ❌ | ❌ | ✅ | `list_ai_settings`, `get_ai_setting` | Supported |
| `approval_request_actions` | ❌ | ❌ | — | ❌ | ✅ | ❌ | — | Not exposed |
| `approval_requests` | ✅ | ✅ | room/project approval filters | ❌ | ✅ | ✅ | `approval_requests`, `get_approval_request`, `add_approval_request`, `edit_approval_request`, `delete_approval_request` | Supported |
| `attention_items` | ✅ | ✅ | `project_id`, `room_id`, `user_id`, `status`, `overdue`, `ai_confirm` | ❌ | ✅ | ✅ | `decisions_waiting`, `blockers`, `outcomes_review`, `mentions`, `material_changes`, `ai_confirm`, `knowledge_proposals` and create/edit variants | Supported |
| `bans` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `boosts` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `company_status_items` | ✅ | ✅ | period / status category / project context | ❌ | ✅ | ✅ | `priorities`, `progress`, `risks`, `dependencies`, `changes`, `decisions`, `learnings` | Supported |
| `company_status_periods` | ✅ | ✅ | slug / name / period identity | ❌ | ✅ | ✅ | `company_status_period`, `add_company_status_period`, `edit_company_status_period`, `delete_company_status_period` | Supported |
| `file_reservations` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `mcps` | ✅ | ✅ | metadata filters | ❌ | ✅ | ✅ | `list_mcps`, `get_mcp` | Supported |
| `memberships` | ❌ | ❌ | — | ❌ | ✅ | ❌ | — | Not exposed |
| `messages` | ✅ | ✅ | `room_id`, message filters | ⚠️ | ✅ | ✅ | `list_messages`, `get_message`, `get_message_by_id`, message create/edit/delete tools | Supported |
| `opengraph_documents` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `opengraph_fetches` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `opengraph_locations` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `opengraph_metadata` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `output_events` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `project_adrs` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_decision_records`, `add_project_decision_record`, `edit_project_decision_record`, `delete_project_decision_record` | Supported |
| `project_all_hands_action_items` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_all_hands_action_item`, `add_project_all_hands_action_item`, `edit_project_all_hands_action_item`, `delete_project_all_hands_action_item` | Supported |
| `project_all_hands_decisions` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_all_hands_decision`, `add_project_all_hands_decision`, `edit_project_all_hands_decision`, `delete_project_all_hands_decision` | Supported |
| `project_all_hands_takeaways` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_all_hands_takeaway`, `add_project_all_hands_takeaway`, `edit_project_all_hands_takeaway`, `delete_project_all_hands_takeaway` | Supported |
| `project_bottlenecks` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck` | Supported |
| `project_directory_items` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item` | Supported |
| `project_external_assets` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `external_knowledge_assets`, `add_external_knowledge_asset`, `edit_external_knowledge_asset`, `delete_external_knowledge_asset` | Supported |
| `project_knowledge_activities` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `knowledge_activity_log`, `add_knowledge_activity_log`, `edit_knowledge_activity_log`, `delete_knowledge_activity_log` | Supported |
| `project_knowledge_items` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_knowledge_items`, `add_project_knowledge_item`, `edit_project_knowledge_item`, `delete_project_knowledge_item` | Supported |
| `project_milestones` | ✅ | ✅ | project scope, milestone identity | ❌ | ✅ | ✅ | `project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone` | Supported |
| `project_obsidian_notes` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_obsidian_note`, `add_project_obsidian_note`, `edit_project_obsidian_note`, `delete_project_obsidian_note` | Supported |
| `project_todos` | ✅ | ✅ | project scope | ❌ | ✅ | ✅ | `project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo` | Supported |
| `project_users` | ❌ | ❌ | — | ❌ | ✅ | ❌ | — | Not exposed |
| `projects` | ✅ | ✅ | project lookup | ❌ | ✅ | ✅ | `list_projects`, `get_project` | Supported |
| `purchasers` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `pushes` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `room_ai_activity_states` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `searches` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `sessions` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `skills` | ✅ | ✅ | skill lookup filters | ❌ | ✅ | ✅ | `list_skills`, `get_skill` | Supported |
| `sounds` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `system_messages` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |
| `tools` | ✅ | ✅ | tool lookup filters | ❌ | ✅ | ✅ | `list_tools`, `get_tool` | Supported |
| `users` | ❌ | ❌ | — | ❌ | ✅ | ❌ | — | Not exposed |
| `webhooks` | ❌ | ❌ | — | ❌ | ❌ | ❌ | — | Not exposed |

## Knowledge MCP tools

This table contains only the Bonfire tables/models where the `Need for knowledge MCP` column is true.

| Actual Bonfire table / model | Single record | All records | Filters | Search | Paginated | W-bridge MCP tools | Status |
|---|---|---:|---|---|---|---|---|
| `rooms` | ✅ | ✅ | `project_id`, `room_id`, `room_name`, room type / parent context | ✅ | ✅ | `list_rooms`, `get_room`, `list_room_threads`, `search_rooms` | Supported |
| `approval_request_actions` | ❌ | ❌ | — | ❌ | ❌ | — | Not exposed |
| `approval_requests` | ✅ | ✅ | room/project approval filters | ❌ | ✅ | `approval_requests`, `get_approval_request`, `add_approval_request`, `edit_approval_request`, `delete_approval_request` | Supported |
| `attention_items` | ✅ | ✅ | `project_id`, `room_id`, `user_id`, `status`, `overdue`, `ai_confirm` | ❌ | ✅ | `decisions_waiting`, `blockers`, `outcomes_review`, `mentions`, `material_changes`, `ai_confirm`, `knowledge_proposals` and create/edit variants | Supported |
| `company_status_items` | ✅ | ✅ | period / status category / project context | ❌ | ✅ | `priorities`, `progress`, `risks`, `dependencies`, `changes`, `decisions`, `learnings` | Supported |
| `company_status_periods` | ✅ | ✅ | slug / name / period identity | ❌ | ✅ | `company_status_period`, `add_company_status_period`, `edit_company_status_period`, `delete_company_status_period` | Supported |
| `mcps` | ✅ | ✅ | metadata filters | ❌ | ✅ | `list_mcps`, `get_mcp` | Supported |
| `memberships` | ❌ | ❌ | — | ❌ | ❌ | — | Not exposed |
| `messages` | ✅ | ✅ | `room_id`, message filters | ⚠️ | ✅ | `list_messages`, `get_message`, `get_message_by_id`, message create/edit/delete tools | Supported |
| `project_adrs` | ✅ | ✅ | project scope | ❌ | ✅ | `project_decision_records`, `add_project_decision_record`, `edit_project_decision_record`, `delete_project_decision_record` | Supported |
| `project_all_hands_action_items` | ✅ | ✅ | project scope | ❌ | ✅ | `project_all_hands_action_item`, `add_project_all_hands_action_item`, `edit_project_all_hands_action_item`, `delete_project_all_hands_action_item` | Supported |
| `project_all_hands_decisions` | ✅ | ✅ | project scope | ❌ | ✅ | `project_all_hands_decision`, `add_project_all_hands_decision`, `edit_project_all_hands_decision`, `delete_project_all_hands_decision` | Supported |
| `project_all_hands_takeaways` | ✅ | ✅ | project scope | ❌ | ✅ | `project_all_hands_takeaway`, `add_project_all_hands_takeaway`, `edit_project_all_hands_takeaway`, `delete_project_all_hands_takeaway` | Supported |
| `project_bottlenecks` | ✅ | ✅ | project scope | ❌ | ✅ | `project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck` | Supported |
| `project_directory_items` | ✅ | ✅ | project scope | ❌ | ✅ | `tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item` | Supported |
| `project_external_assets` | ✅ | ✅ | project scope | ❌ | ✅ | `external_knowledge_assets`, `add_external_knowledge_asset`, `edit_external_knowledge_asset`, `delete_external_knowledge_asset` | Supported |
| `project_knowledge_activities` | ✅ | ✅ | project scope | ❌ | ✅ | `knowledge_activity_log`, `add_knowledge_activity_log`, `edit_knowledge_activity_log`, `delete_knowledge_activity_log` | Supported |
| `project_knowledge_items` | ✅ | ✅ | project scope | ❌ | ✅ | `project_knowledge_items`, `add_project_knowledge_item`, `edit_project_knowledge_item`, `delete_project_knowledge_item` | Supported |
| `project_milestones` | ✅ | ✅ | project scope, milestone identity | ❌ | ✅ | `project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone` | Supported |
| `project_obsidian_notes` | ✅ | ✅ | project scope | ❌ | ✅ | `project_obsidian_note`, `add_project_obsidian_note`, `edit_project_obsidian_note`, `delete_project_obsidian_note` | Supported |
| `project_todos` | ✅ | ✅ | project scope | ❌ | ✅ | `project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo` | Supported |
| `project_users` | ❌ | ❌ | — | ❌ | ❌ | — | Not exposed |
| `projects` | ✅ | ✅ | project lookup | ❌ | ✅ | `list_projects`, `get_project` | Supported |
| `skills` | ✅ | ✅ | skill lookup filters | ❌ | ✅ | `list_skills`, `get_skill` | Supported |
| `tools` | ✅ | ✅ | tool lookup filters | ❌ | ✅ | `list_tools`, `get_tool` | Supported |
| `users` | ❌ | ❌ | — | ❌ | ❌ | — | Not exposed |

## Important note on STI subtypes

Do not treat `rooms::open`, `rooms::closed`, `rooms::direct`, `rooms::project`, and `rooms::task` as independent table-level coverage targets unless the schema actually creates separate tables.

In practical Bonfire use, these are STI subtype classes and should be evaluated as room filters / room-type conditions on the `rooms` table, not as separate support rows.

## Why this matters

The useful DB question is:

- Is there a table-level MCP path for `rooms`?
- Is there a table-level path for `projects`?
- Is there a table-level path for `messages`?

Not:

- is `rooms::open` separately supported as an independent table.

That is the right framing for coverage and gap analysis.

## Readout

### Supported by W-bridge MCP

The W-bridge MCP currently covers the main collaboration and configuration surfaces of Bonfire, especially:

- AI config and MCP registry
- project/workflow records
- room/message collaboration
- company status / attention item flows
- project knowledge and project decision data

### Not yet covered as full database access

The current W-bridge MCP does not provide generic, model-wide DB access for the broader Bonfire schema. In particular, the unsupported models include identity, membership, session, auth, ban, push, notification, and many lower-level system tables.

### Practical conclusion

W-bridge MCP is not a full Bonfire DB interface today. It is a workflow-specific coverage layer for the domain objects that W-bridge itself needs to operate on.

A true full-database Bonfire bridge would need generic model coverage for the unsupported models above, plus a schema-driven single-record / all-record / filter / search contract across the entire Bonfire schema.
