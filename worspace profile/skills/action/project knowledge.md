# Project knowledge

Type: action skill
Purpose: owning the seven knowledge families and the knowledge-path discipline for the project memory spine.

## Families → tools (all on read-mcp / action-mcp)

| Family | Read | Create (required) | Edit / Delete |
|---|---|---|---|
| Knowledge items | `project_knowledge_items` | `add_project_knowledge_item` (`title`; opt `description`, `badge`, `active`) | `edit_...` / `delete_...` |
| Decision records (ADRs) | `project_decision_records` | `add_project_decision_record` (`identifier`, `title`; opt `status`, `decision_date`, `file_path`) | `edit_...` / `delete_...` |
| Notes | `project_note` | `add_project_note` (`title`; opt `content`, `tags`, `html_source_path`, `html_source_type`) | `edit_...` / `delete_...` |
| Directory (tree) | `tree_based_project_directory_data` | `add_tree_based_project_directory_item` (`name`; opt `item_type`: directory|knowledge_item|adr|note, `parent_id`, `content`, `file_path`) | `edit_...` / `delete_...` |
| External assets | `external_knowledge_assets` | `add_external_knowledge_asset` (`title`, `url`; opt `doc_type`, `source_type`, `icon`, `meta_text`) | `edit_...` / `delete_...` |
| Activity log | `knowledge_activity_log` | `add_knowledge_activity_log` (`actor_name`, `action_text`; opt `target_path`, `target_url`, `actor_color`) | `edit_...` / `delete_...` |
| Summaries | `knowledge_summary_items` | `add_knowledge_summary_item` (`title`, `description`; opt `badge`) | `edit_...` / `delete_...` |

## Rules

1. **knowledge_path discipline**: when the event carries `event_data.knowledge_path`, every adoption must reference a matching line in `add_knowledge_activity_log.target_path` — that is the thread connecting PWR state to the memory mirror.
2. Naming: an ADR `identifier` continues the project's existing sequence (read `project_decision_records` first — e.g. last was ADR-6 → new is ADR-7); never renumber.
3. Placement: durable fact → knowledge item; ephemeral working context → note; references → external asset (needs a real `url`, never a description); digests → summary; directory items are structure, not content — don't put prose in `content` beyond a one-liner.
4. Every adoption of third-party content (proposals, learnings, meeting notes) logs an activity entry naming actor, source id, and destination — the activity log is the provenance ledger; if it would be empty after your work, you forgot it.
5. Dedupe per family (list + compare) — cross-family near-duplicates belong in the more specific family.
6. Knowledge writes follow approval discipline when the content would enter the published knowledge base (proposals already approved by humans are exempt — the approval event IS the sign-off).

## Example — adopt an approved proposal into the directory + item

Proposal adopted under project `pwr`; knowledge_path line: `/company/1/projects/2/knowledge`.

```json
{"tool": "tree_based_project_directory_data", "arguments": {"project_id": 2}}
→ node 14 = "integrations" (directory)

{"tool": "add_project_knowledge_item", "arguments": {"project_id": 2,
  "title": "workspace profile event envelope (OUTPUT_EVENTS_URL)",
  "description": "Envelope: id/event_type/event_id/group_id/event_data{actor,target_type,content,content_payload,occurred_at,knowledge_path}. Multipart only for attachments. — source proposal 91",
  "badge": "mcp", "active": true}}

{"tool": "add_tree_based_project_directory_item", "arguments": {"project_id": 2,
  "name": "workspace-profile-event-envelope", "item_type": "knowledge_item",
  "parent_id": 14}}

{"tool": "add_knowledge_activity_log", "arguments": {"project_id": 2,
  "actor_name": "w-ai",
  "action_text": "adopted proposal 91: event envelope reference filed under integrations",
  "target_path": "/company/1/projects/2/knowledge"}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "add_project_knowledge_item",
  "project_id": 2, "target_entity_id": "<item id>",
  "why_was_it_required": "knowledge_proposal_resolved 91",
  "change_log": "adopted proposal 91; +1 item, +1 directory node, +1 activity log"}}
```
