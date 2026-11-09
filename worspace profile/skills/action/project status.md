# Project status

Type: action skill
Purpose: keeping a project's operational state coherent with reality: todo/bottleneck/milestone state vs company status claims vs tracked tasks.

This skill owns no new entities — it reads across `project_todos`, `project_bottlenecks`, `project_milestones`, `ai_tasks`, `attention_items`, and the company-status categories, then fixes incoherence with the narrowest write, using `project overview` / `company status` tools as its hands.

## Checks (run per project event or on demand)

1. Claim check: every `progress` company item citing a project should have ≥ 1 supporting completed todo/milestone/task. Unsupportable claim → correct the `progress` item with `details`, don't delete it.
2. Stale open: `project_todos(completed: false)` + `ai_tasks(finished: false, project_id)` with no movement — if `due_at`/`target_date` passed → `add_outcomes_review` or refresh blocker, per severity.
3. Contradiction pairs: open bottleneck + `milestone.status: "on_track"` + `target_date` imminent → raise `add_decisions_waiting(title: "Milestone <m> at risk: bottleneck <b> open past <date>", action_label: "Approve")` — a human decides slip vs mitigate; you never silently move `target_date`.
4. Orphan sweep: items resolved via events but trackers still open (see input skills project_todo_*/all_hands_*) — close trackers with cost + `actual_task_context`.

## Rules

- You may write: `edit_*` on todos/bottlenecks when the fact is directly given by a human event; `add_*` attention items; corrections to company-status items with a `details` provenance note; task closes. You may NOT: change milestone dates, delete project records, resolve attention items on behalf of humans.
- Every fix carries provenance in the write itself ("per event X / task Y / blocker Z") so the merge is auditable later without the log table.

## Example — contradiction sweep on `project_updated`

```json
{"tool": "project_milestones", "arguments": {"project_id": 2, "status": "active"}}
→ milestone 5 "Beta" target 2026-11-15 on_track

{"tool": "project_bottlenecks", "arguments": {"project_id": 2}}
→ bottleneck 9 high, open, created 2026-11-02 (load hangs)

{"tool": "add_decisions_waiting", "arguments": {"project_id": 2, "room_id": 9,
  "title": "Beta milestone vs open high bottleneck — slip or mitigate?",
  "meta_text": "bottleneck 9 (load hangs, 11-02) contradicts milestone 5 on_track for 11-15; owner to decide",
  "action_label": "Approve", "due_at": "2026-11-08T17:00:00Z"}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "add_decisions_waiting",
  "project_id": 2, "target_entity_id": "<item id>",
  "why_was_it_required": "project_updated sweep found bottleneck/milestone conflict",
  "change_log": "escalated conflict instead of moving dates"}}
```
