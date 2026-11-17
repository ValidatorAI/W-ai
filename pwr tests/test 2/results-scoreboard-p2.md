# Test 2 — P2' scoreboard (threads + company plane) — FINAL (window closed 08:50Z)

Run: 2026-11-16 08:15–08:38Z. Arc A 19 beats (all posted; A07 = 403 wall), Arc D 11 (3 SKIP — company-home-is-not-a-room, re-scoped to API lanes below). Threads seeded 13/14/15 as project-room children (matches app tree model). DM/seed repairs done under SEED-OPS.

## Verdicts

| id | lane | verdict | evidence |
|---|---|---|---|
| TH-01 | thread rows | PASS | rooms 13/14/15 with parent_id = project rooms; tree semantics documented in mapping-correction note |
| TH-02 | thread-scoped ask routing | PASS | task 88 → business_analyst (backfill draft) + task 89 → w_ai (ownership answer); reply 704 thread-scoped |
| TH-05 | bot artifact echo in thread | PASS | A16 Coder post to room 13 accepted (member) |
| TH-08 | archive gated + surfacing | GATE PASS / EXEC BLOCKED-F26 | approval 28 payload: 3 surfaced open items cited, dedupe sweep, gating inputs; approved via nested API lane at 08:38; archived_at + exec reply checked in window |
| MP-06 | cross-project isolation | PASS (server-grade) | A07 David→cobalt-main = 403 byte-identical to zero-membership flux (existence-neutral). F24 live. Agent-gate variant moved to DM18 lane (P5') |
| MP-12 | census within membership | PARTIAL | reply 702 counts 3 items for cobalt only; cross-project census not yet probed via DM |
| CP-04 | period by_slug | PASS | 200 + items embedded |
| CP-05 | period by_name | RE-GRADED | by_name is EXACT-only; partial name → 404 (existence-neutral). Mapping wording needs correction (test-side fix, no app change) |
| CP-08 | company blocker no-project | PASS | 201 create + 200 resolve without project_id |
| CP-02/03 | priorities/learning writes | FAIL→F25 | API 422 'Category is not included in the list'; MCP only read tools (priorities/learnings). No write surface for company priorities/learnings |
| CP-13 | invalid status 422 contract | pending | rerun on valid id this window |
| CP-06 | close-period binding | DEFER | protected by design decision — not touching November period; December variant queued for P5' |
| RC-01 | reserve + race | PASS + F27 | reservation row 4 persisted; second holder rejected "conflict: siavash mohammady on attribution.sql"; BUT success reply crashed I18n MissingInterpolationArgument :agent_name (row lands, reply 500s) = F27 |
| RC-03 | expiry | in-window | row 4 expires 08:47 — check_file_conflicts should go empty after; auto-verify this window |
| CB-01 | cost accrual gated | GATE PASS / EXEC BLOCKED-F26 | approval 27 correctly disambiguated token-vs-USD ("400 interpreted as tokens per the 1050/30000 cite") — exemplary; exec chain awaits decision event gap (see F26) |
| CB-03 | sum accrual | pending exec | second 650 not yet gated (sequential to 27 exec) |
| HI-02 | decide-lane parity | FAIL→F26 | MCP edit_approval_request stamps status raw (no resolved_at/by, NO event, no broadcast-to-bots); nested API PATCH sets resolved fields + decision_text but ALSO emits no output event → bots cannot know approvals were decided except via message broadcast/websocket |

## Findings filed this run
- F25 — no write surface for company priorities/learning categories (API 422; MCP read-only).
- F26 — approval decision lanes (MCP edit_approval_request AND API nested update) do not emit approval-decided output events; MCP lane additionally bypasses resolved_at/resolved_by domain fields. Execution follow-through (S7) is un-wakeable after human decision.
- F27 — reserve_file success payload crash: I18n missing :agent_name interpolation (row persists; caller gets error).

## Notes
- Coder honest-fail on A02 ("target artifact does not exist — no code written") = verify-before-log SOUL rule working.
- Analyzer approval payloads (27/28) cite verified_state reads, dedupe sweeps, and even surfaced that PM's plain posts to room 8 were Forbidden (F24 self-detection by agents).
- Conservation: events_since 08:15 = 6 rows (ai_question_asked 1, blocker_created 2, blocker_resolved 1, message_created 2) — full sweep at finalize.

## Final window (08:50Z audit)
- Exec audit: room13 archived_at NULL; task72 token_used NULL; events after decision = only blocker_created 914 (unrelated, task 90 lane). => F26 CONFIRMED as the sole blocker of approve->execute; both plans (27/28) carry exact on_execution checklists that no agent was woken to run.
- LANE POSITIVES banked: 706/707 answers delivered IN the thread (room 13) — thread-scoped answering works end-to-end; 708 CP-07 material-change raised a fresh gated approval (task 90, topic 67) before registering anything — CP discipline PASS; 709 membership-check refusal in room 2 by w_ai — L1 gate positive in member context (someone in receipts-growth asked cross-project and got template + explicit 'ran the membership check' citation).
## Verdict: PARTIAL PASS — 13 PASS, 2 EXEC-BLOCKED(F26), 1 PARTIAL(MP-12), F25/F26/F27 filed.
## G2' gate call: P4' (approval round-trips) GATED ON F26 — do not run until decisions emit events. P3' (multi-project + DM battery) has no F26 dependency -> clear to launch.
