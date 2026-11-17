---
name: bot-approvals
description: Use when a bot action needs human approval before it runs.
version: 0.1.0
author: siavash (drafted by Hermes)
license: MIT
metadata:
  hermes:
    tags: [pwr, bots, approvals]
    related_skills: [pwr-entities, bot-messaging, task-management]
---

# Bot approvals — the requester's seat

Purpose: when and how a bot raises an approval request and behaves around its outcome. Distinct on purpose: workspace's action skills cover raising AND resolving/consuming approval events across the company; you are only ever the **requester**. Verified tools (workspace soul's approvals row): `add_approve_request_with_message`, `add_approval_request` + `add_message` (split form), `approval_requests`, `get_approval_request`, `edit_approval_request`, `delete_approval_request`. Statuses: `pending` → `approved` / `confirmed` / `denied` / `canceled`.

## Gate: does this action need approval?

Needs approval (user-visible, high-impact): company-home items, company/project status updates, milestones / todos / bottlenecks, decision records & ADRs, all-hands records, knowledge proposals, room-level decisions, releases/deployments, any external send (message to a room you don't own the thread of, third-party systems).

Does NOT need approval: work inside the explicit scope of a direct user request ("fix X", "add note Y" said by the user), private drafts, reads, logging writes.

When unsure, prefer one visible question via `add_action_message` over a silent guess or an over-cautious approval that trains users to rubber-stamp.

### Task-inbound ("Gated action:" in your AiTask description)

Message_analyzer routes gated chat work to you with a description beginning `Gated action:` and citing a source message id.

**Pre-flight (AP-11): is it REALLY gated?** Re-check the action itself against the gate section before raising — even when the description says `Gated action:`. A non-destructive, explicitly user-scoped instruction (a rename, title/wording fix, edit of a private draft, a note) needs NO approval: do the work and log it; if the target artifact does not exist, post ONE room message reporting the missing target and offer to register the intent as a todo — do NOT raise an approval for it. Wrong: approval #22 raised to rename a not-yet-filed FAQ draft title. Right: "No FAQ draft is filed yet — nothing to rename. Want me to note it as a todo for when it lands?" Only keep the gate when the action is destructive/irreversible, spends money, sends externally, or mutates shared state.

**Direct action:** descriptions beginning `Direct action:` are pre-cleared: execute (or report the missing target per above), log via `create_tool_cal_log`, close with cost — never raise an approval for them.

When you receive a genuinely gated one:
1. Your FIRST room-visible step is raising the approval: `add_approve_request_with_message` in the cited room, `body` = the exact action plus the 4-tuple (target+ids, scope, boundary, evidence), payload decision-text mirroring the requested outcome.
2. Record the approval id in `actual_task_context`, state in the room/task = **waiting-for-approval**, task stays open (never dispatched-closed).
3. Act only on an `approved` decision event for THAT approval id; cite it in your completion log. `denied` → record the reason, close the task per close-out, do not re-raise the same scope.
4. After the approved decision arrives: execute within the approved scope, then — BEFORE closing the task — produce the evidence the approval promised: the artifact/receipt for money or external sends (plus its `create_tool_cal_log` row), a completion message in the cited room citing approval id `<id>` (AP-14), and only then `ai_task_cost` → `update_ai_task(finished: true, actual_task_context: ...)`. A task closed without its promised evidence is a failed approval.


## Raising (the one-call rule)

Post the intended action and open the approval in the SAME call:

`add_approve_request_with_message(room_id | room_name, body, request_type, payload{title, decision-text})`

- `body` = the exact action you will perform — a human should be able to approve it without imagining the rest.
- The approval must carry: the **target** (entity + ids), the **scope** (project/room, budget if any), the **boundary** (what you will NOT touch), and the **evidence** you will produce on execution.
- Use the split form (`add_approval_request` + `add_message`) only when the message predates the approval decision.
- Dedupe first: list `approval_requests` for an existing pending request on the same target — never open a second gate for one action.

## While waiting

- Your state is **waiting-for-approval** — never "done", never "executed". Say exactly that in the room/task context.
- Keep the task open; record the pending approval id in `actual_task_context`. Do not pre-execute any part of the approved action "just in case".

## Outcome handling

The decision arrives as `approval_request_approved | confirmed | denied | canceled` (delivered through the workspace event flow; you'll learn of it via your task context, room message, or a follow-up task — you do not consume the raw event queue).

- approved / confirmed → execute exactly what was approved; then log every action with `create_tool_cal_log` and note the approval id you acted under.
- denied / canceled → **do not proceed at all**. Record the denial in the originating task's `actual_task_context`, dismiss any related attention item you created (`edit_<category>` with `status: "dismissed"`), close the task per task-management rules. A denial is a legitimate, complete outcome.

## Hard don'ts

- Never `add_decision_message` on your own request — that channel carries the human's decision.
- Never approve, confirm, or deny on a human's behalf.
- Never resubmit a denied action unchanged; if you believe the denial was a misunderstanding, raise a NEW request with the misunderstanding addressed in the body, or ask via `add_action_message`.
- Never let an approval lapse silently: if a pending request blocks your task, surface it (loading-message update or `add_action_message`) instead of idling.

## Worked example

```
User asks coder in Engineering room: "publish the new onboarding doc to company knowledge"
→ publishing to project knowledge is user-visible → needs approval
→ approval_requests(project 3): no pending match
→ add_approve_request_with_message(
     room_name "Engineering", request_type "knowledge_publish",
     body "Publish <doc> to /company/3/projects/3/knowledge as note 62 draft;
           will NOT touch ADRs or directory; evidence: item id + path after write",
     payload {title: "Publish onboarding doc", decision: "Approve publishing..."} )
→ room update: "Waiting for approval (request 41) — will publish on approval."
→ event: approval_request_confirmed → write the note → create_tool_cal_log(
     used_tool_name add_project_note, target_entity_id 62, change_log "published onboarding note")
→ final add_message with the id + path.
```
