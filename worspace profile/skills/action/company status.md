# Company status

Type: action skill
Purpose: owning the status period and its seven item categories: `priorities`, `progress`, `risks`, `dependencies`, `changes`, `decisions`, `learnings`.

## Periods

- `company_status_period` (read+action): list, get by `period_id`, create by passing `name`, edit by `period_id` + fields, delete with `delete: true`. Fields: `name`, `slug`, `starts_on`, `ends_on`, `current` (boolean).
- `add_company_status_period` (required `name`) / `edit_company_status_period` (required `period_id`).
- There is no "get current" parameter — list periods and take the one with `current: true`; if the company has none, the first-ordered period acts as current (mirrors server behavior in `company_status.rb`).

## Items

Seven category tools, all shaped identically (see `priorities` etc. schemas): read/list with `company_status_period_id`, paging; create by passing `title` (+ `details`, `summary`, `owner_name`, `evidence`, `impact`, `badge`, `health`, `percent`, `status`); edit by `item_id` + changed fields; delete with `item_id` + `delete: true`.

Item statuses for company-status categories are lifecycle strings (`active`, `open`, `done`, `approved`, `denied`… driven by record) — distinct from the attention layer's `pending/resolved/dismissed`.

## Rules

1. Always bind items to the current `company_status_period_id` explicitly; never rely on a server default when writing.
2. `owner_name` resolves via fuzzy matcher to a user — pass it only when the event names an owner.
3. Never delete a period with items; reassign items first (edit each `item_id`) — deletion of periods is human-only in practice.
4. Approvals for status changes go through `add_approve_request_with_message`; the approval event (not your judgement) flips items to `approved`/`denied`.
5. `percent` is a string/integer 0-100 on progress items; when correcting, write the new value with a `details` note — history lives in `tool_cal_logs`, not in the item.

## Example — open a period and seed a priority

```json
{"tool": "company_status_period", "arguments": {"name": "Q4 2026", "slug": "q4-2026",
  "starts_on": "2026-10-01", "ends_on": "2026-12-31", "current": true}}
→ {"id": 3}

{"tool": "priorities", "arguments": {"company_status_period_id": 3,
  "title": "Cut triage latency 50%", "owner_name": "alice",
  "evidence": "baseline measured 2026-10-15; see learning 166",
  "impact": "high", "badge": "q4"}}

{"tool": "create_tool_cal_log", "arguments": {"used_tool_name": "priorities",
  "project_id": null, "target_entity_id": "<item id>",
  "why_was_it_required": "period kickoff after approval 55 confirmed",
  "change_log": "opened q4-2026 period + first priority"}}
```
