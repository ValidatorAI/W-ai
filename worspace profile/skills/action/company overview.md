# Company overview (attention items)

Type: action skill
Purpose: owning the company-home attention layer: the 7 categories and their lifecycle (`pending` → `resolved` / `dismissed`).

Categories (fixed list from `AttentionItem::CATEGORIES`): `decisions_waiting`, `blockers`, `outcomes_review`, `mentions`, `material_changes`, `ai_confirm`, `knowledge_proposals`.

## Tools

Per category `<c>`:
- `<c>` (generic, read-mcp + action-mcp): list (filters `project_id`, `room_id`, `user_id`, `status`, paging) — also creates when you pass `title` and no `item_id`, and edits when you pass `item_id` + fields; `delete: true` + `item_id` deletes.
- `add_<c>` (action-mcp): create only. Required `title`; optional `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name`. Status starts `pending`; `ai_confirm` is forced true for the `ai_confirm` category.
- `edit_<c>` (action-mcp): required `item_id`; may change `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue`.
- Cross-category: `attention_items` (read/list/get; `delete: true` + `item_id` deletes) and `delete_attention_item`.

CATEGORY_CONFIG defaults worth knowing when you set `action_label`: decisions_waiting → "Approve", blockers → "Assign & Unblock", outcomes_review → "Record Result", mentions → "Mark Reviewed", material_changes → "Acknowledge", ai_confirm → "Approve Action", knowledge_proposals → "Approve Knowledge".

## Rules

1. Dedupe by listing the category + scope before adding; prefer `edit` on the existing pending item.
2. One event should raise at most one item per category; if two categories both fit, the more specific one wins (a blocker beats an outcome review).
3. Resolve/dismiss is normally the human's act — you set `status` only when the PWR flow already did it (your event confirms it) or when you are closing an item **you** created that became moot.
4. Items without a `project_id`/`room_id` are company-wide noise; always attach the narrowest scope you can resolve from the event.
5. The user-facing list ("Company Home") is generated from these items — treat every `add_*` as publishing something to humans; high-impact ones go through approval discipline first (see soul).

## Example — raise a blocker from a stalled task

```json
{"tool": "blockers", "arguments": {"project_id": 2, "status": "pending"}}
→ []  (no equivalent)

{"tool": "add_blockers", "arguments": {
  "title": "task-mcp attachment missing for workspace profile",
  "meta_text": "blocks event routing rules in soul; found while processing event 456",
  "action_label": "Assign & Unblock", "project_id": 2, "room_id": 9,
  "user_name": "siavash", "due_at": "2026-11-05T17:00:00Z", "overdue": false}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "add_blockers",
  "project_id": 2, "room_id": 9, "target_entity_id": "<new item id>",
  "why_was_it_required": "ai_task 205 precondition failed",
  "change_log": "raised blocker for missing task-mcp attachment"}}
```
