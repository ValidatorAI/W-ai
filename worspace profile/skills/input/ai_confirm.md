# AI work awaiting confirmation (resolved / dismissed)

Type: input-processing skill
Apply when: events `ai_confirm_resolved` or `ai_confirm_dismissed`.

## Procedure

1. Read the item: `ai_confirm(item_id: <event_id>)`. These items exist because **an AI (possibly you, possibly another profile) made a change that needs human sign-off** — the tool defaults `ai_confirm: true` when the category is `ai_confirm`.
2. `ai_confirm_resolved` — a human confirmed the AI action. It is now authoritative state:
   - propagate downstream only if the confirmed action was partial: e.g. confirmed todo/milestone → `progress` merge; confirmed knowledge → ensure the knowledge item exists (`add_project_knowledge_item` with dedupe);
   - close the creating task, if the confirmation event references a task-tracked action (`ai_tasks(input_event_entity_id: <event_id>)`): `ai_task_cost` then `update_ai_task(finished: true)`.
3. `ai_confirm_dismissed` — a human **rejected** the AI action. Rollback discipline:
   - identify what the AI created (the item's `meta_text`/`source`);
   - if *this workspace profile* created it and it was rejected: delete your artifact (`delete_project_todo`, `delete_project_milestone`, `delete_attention_item`, `delete_project_knowledge_item` — one per rejected entity);
   - if another profile created it: do not delete their artifact — route `create_ai_task(assigneee_profile: <creator>, description: "Revert rejected ai_confirm item <id>: <what was created> — confirmation dismissed")`;
   - record the rejection as a `learning` status item when it signals a pattern ("AI-created X rejected twice → stop auto-creating X").
4. Verification log only when nothing was left dangling.

## Tools used

| Tool | Endpoint | Key arguments |
|---|---|---|
| `ai_confirm` (generic) | read-mcp + action-mcp | list = no args beyond filters; get/edit/delete = `item_id`; create = `title` |
| `add_ai_confirm` | action-mcp | required: `title`; optional: `meta_text`, `action_label`, `due_at`, `overdue`, `project_id`/`project_name`, `room_id`/`room_name`, `user_id`/`user_name` |
| `edit_ai_confirm` | action-mcp | required: `item_id`; writable: `title`, `meta_text`, `status`, `action_label`, `due_at`, `overdue` |
| `attention_items` | read-mcp | cross-category list: `category`, `status`, `project_id`, `user_id` |
| `delete_attention_item` | action-mcp | required: `item_id` — only for duplicate/erroneous items you created |
| `tool_cal_logs` | knowledge-mcp | dedupe: `target_entity_id`... |
| `delete_project_todo` / `delete_project_milestone` / `delete_project_knowledge_item` | action-mcp | revert your own rejected creations |
| `learning` items | read+action-mcp | pattern capture |
| `create_ai_task` | task-mcp | route reverts to the creating profile |

## Example

```json
{"event_type": "ai_confirm_dismissed", "event_id": 80,
 "event_data": {"actor": {"username": "alice"}, "target_type": "AttentionItem",
   "content": "AI-created milestone 'Beta by Nov 15' confirmation dismissed",
   "content_payload": {"attention_item_id": 80, "project_id": 2, "meta_text": "created milestone id 12 via add_project_milestone"}}}
```

Run: `ai_confirm(item_id: 80)` → dismissed, artifact = milestone 12, creator = this profile (footprint in `tool_cal_logs(used_tool_name: "add_project_milestone", target_entity_id: "12")`) → `project_milestones(milestone_id: 12)` → exists, not referenced elsewhere → `delete_project_milestone(milestone_id: 12)` → `add_knowledge_activity_log(actor_name: "w-ai", action_text: "reverted milestone 12 after ai_confirm 80 dismissed", project_id: 2)` → 2 logs.

## Logging rule

After **each** state-changing tool call, call `create_tool_cal_log` (knowledge-mcp):
`{"used_tool_name": "<tool>", "project_id": ..., "room_id": ..., "topic_id": ..., "target_entity_id": "<entity touched>", "why_was_it_required": "<event_type>", "change_log": "<one line>"}`.

## Guardrails

- Read-before-write: never `add_*` into a category without listing that category for the same scope first — PWR has no dedupe tool.
- Never overwrite existing text with `edit_*`: fetch, merge, write back.
- Attention statuses are exactly `pending` / `resolved` / `dismissed`.
- Event delivery is at-least-once: re-delivery has the same `group_id` / `event_type` / `event_id`. Check `tool_cal_logs` filtered by `target_entity_id` before acting a second time.
