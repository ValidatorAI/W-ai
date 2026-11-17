# Test 2 — required changes (from P0'–P2')

Owner tags: `[COPILOT]` = PWR repo (W/pwr, branch installation). `[HERMES]` = W-ai SOUL/skill lane (assistant-owned). `[TESTSIDE]` = fixture/mapping correction (assistant-owned).

---

## F26 [COPILOT] — approval decisions must wake the agents (MUST)

Both human decision lanes fail to emit any output event, so an approved plan never reaches the bot that must execute it. Live proof: approvals 27/28 approved at 08:38Z (nested API PATCH — resolved_at/resolved_by/decision_text all set correctly) → `output_events` rows after that decision: **zero**; no archive, no cost accrual executed; S7 follow-through cannot fire.

Requirements:
1. Mirror the WEB approve/deny/confirm/cancel lane exactly: read how the web member routes (`/approval_requests/:id/approve` etc.) publish their decision (event name, payload, broadcast) and replicate the SAME publication from the API nested update path when a status transition enters a resolved state (status_resolved? is already computed there — reuse it, single shared concern).
2. Fix `edit_approval_request` (MCP) to route through the same shared decision service instead of `req.update!(status:)`: must set `resolved_at` (blank-safe), `resolved_by` from the acting identity when provided, refuse re-deciding an already-resolved request unless `force: true` (report current state in the rejection), and emit the same decision event.
3. Event: one `approval_decided` (or the exact web event name if it differs) per decision with approval id, decision, decider, room_id, message_id. Dedupe: if the web lane already emitted for the same resolved transition, do not double-emit (idempotent on resolved_at).
4. Required tests: (1) nested API PATCH approve → decision event row exists with same shape as web-lane event; (2) MCP edit_approval_request → same; (3) re-decide without force → clear error, no second event; (4) bot delivery: event dispatches to the requesting agent (the one that raised it) — verify via dispatch group; (5) no events for non-resolving updates (payload-only edits).
Constraints: shared concern/service only — no parallel publication code; keep existing ValidationError/422 contracts; don't touch strike/parking logic elsewhere.

## F27 [COPILOT] — reserve_file success render crashes (SHOULD)

`reserve_file` MCP tool: reservation row persists (verified live, row 4) but the reply is an error: `I18n::MissingInterpolationArgument: missing interpolation argument :agent_name in "<strong>%{agent_name}</strong> reserved files: <code>%{patterns}</code>" ({patterns: ...} given)`. Caller cannot distinguish success from failure — invites duplicate reservations. Fix: pass `agent_name` (holder display name / bot name) into that interpolation at every call site of this string (grep the i18n key; likely renewal/release share the template — audit all three), or degrade gracefully to holder name. Required tests: reserve/renew/release happy paths return success JSON (no raise); conflict path keeps returning the held-by shape (`conflict: <name> on <patterns>` — that worked).

## F25 [COPILOT] — company priorities/learnings write surface (SHOULD)

`POST /api/attention_items` with category `priorities` or `learning` → 422 "Category is not included in the list"; MCP exposes read-only `priorities`/`learnings` tools. The company plane can raise blockers/proposals but cannot record priorities or learnings from any automated lane — CP-02/03 untestable. Fix: decide and implement the write surface consistent with existing semantics: if priorities/learnings are AttentionItem categories in the web model, add them to the API category allowlist + emit the standard `*_created` event family; if they are a different model (pinned/company-scoped), expose MCP add/edit tools mirroring the web controller's service call. Constraints: mirror existing web-controller semantics; single shared path; events per emitter-parity rule (M8).

## [TESTSIDE] corrections (done by assistant, recorded here)

- CP-05 mapping wording: `by_name` is exact-match only (404 on partial) — mapping-t2 corrected, no app change required. Ambiguity test becomes: two periods sharing a name → deterministic pick or clear error (re-test only if product later allows dup names).
- Company Home beats (D01–D03): Company Home is not a room; re-scoped to API/MCP company lanes (CP-08 proves company-scoped attention works).
- CP-06 (close current period with bound items): deferred — must not damage the live November period during functional runs; scheduled into P6' chaos/cleanup window instead.
- A07 re-grade: server wall (F24) now rejects outsider room posts; agent-gate battery re-scoped to DM18 (flux is a participant there) for P5'.

## Status ledger (as of 08:45Z)

| item | state |
|---|---|
| F24/L2 server wall | LIVE + verified (uncommitted in repo — operator to commit) |
| L1 agent hard gate | DEPLOYED + GATE-EFFECTIVE verified |
| F25/F26/F27 | filed; F26 CONFIRMED by 08:50 exec audit (approved 27/28 never executed, zero decision events) — P4' gated on it |
| M9 (deps write), F22/F23 (burst idempotence/attribution), O-5, S9/F17/F18 | carried from Test 1 — unchanged |


---

# VERIFICATION ROUND (2026-11-16 10:08Z, HEAD 87696ed) — F25/F26/F27 re-check

## F26 — ✅ SOLVED + VERIFIED LIVE
- Code: shared `ApprovalFlow.decide!` (status guard, force, human-actor enforcement, echo via SystemMessage.approval_decided); MCP `edit_approval_request` routes decisions through it; nested API lane publishes.
- Live: approval 30 approve via nested API → `resolved_at`/`resolved_by` set + event **915 approval_request_approved** + echo msg 714 in room 8. Approval 31 deny via MCP (human actor) → event **916 approval_request_denied** + resolved fields. Payload-only edit → 200, no event. Re-decide w/o force → 422 "already approved. Use force: true to override."
- Re-drive note: `force: true` on an already-resolved approval intentionally short-circuits (no second event) — for post-fix re-drives the request must be reset to pending (test-side surgery performed on 27/28: reset → decide → events 921/922 `decision_approved`, groups 647/648 → execution watch running).
- Minor consistency note (GOOD-to-fix): two event names carry the same semantic — `approval_request_approved/denied` (915/916) and `decision_approved` (921/922). Confirm consumers handle both, or unify.

## F27 — ✅ SOLVED + VERIFIED LIVE
- reserve_file → OK payload with holder name (interpolation fixed); renew by holder → OK; renew by non-holder → clean "not holder"; release → OK (row removed). No raises on any success path; conflict shape preserved.

## F25 — ❌ RETRACTED (finding was mis-scoped by the test harness — NOT an app defect)
- The write surface exists and works: `CompanyStatusItem::CATEGORIES` includes priorities/learnings; MCP `priorities`/`learnings` action tools (rows 3/4) AND `POST /api/company_status_items` (rows 5/6) both create; emitter parity confirmed — events `priority_created` (917/919) + `learning_created` (918/920).
- My probe used the wrong endpoint (attention_items), singular "learning", and omitted company_status_period_id. TESTSIDE correction logged; mapping-t2 CP-02/03 driver updated to the company-status surface.

## F28 [COPILOT, SHOULD→MUST-adjacent] — closed tasks are not frozen; cost PATCH even reopens them
Live: task 94 (finished=1, project relay): PATCH /api/tasks/94 {"token_used":500} → 200, token_used=500 written AND finished flipped to 0 (verified (500,0) after). Budget/audit integrity hole: (a) reject writes to cost fields on finished tasks with 422 (mirror web lane semantics), (b) never let a partial PATCH touch finished/dispatched lifecycle flags by omission (the reopen suggests update with default false for an unset boolean — check the controller/service for mass-assignment of finished), (c) MCP cost lane same guard. Tests: cost write on finished → 422 + flags unchanged; cost write on open → ok; partial PATCH without finished key must not change finished.
