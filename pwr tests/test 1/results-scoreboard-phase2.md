# results-scoreboard-phase2.md — Tier 1 (message/event-handler battery)

Interim run: 2026-11-13, naive sequential, 15 scenarios, ledger
~/.hermes/cache/scratch/phase2_ledger.jsonl (raw evidence bundles per scenario).
World: HEAD b197057 (Z, X, Y, R, T, B, C, E, D, M1/M1a/M5/M6/F13 fixes merged),
M2/M3/M4 SOULs deployed, gateway slots=8.

## Tier-1 verdicts

| scenario | items | result | read |
|---|---|---|---|
| HA-29 blocker-resolved | EV-04 | NOT-EVALUATED | trigger produced NO event (F14) |
| HA-30 blocker-dismissed | EV-05 | NOT-EVALUATED | same |
| HA-31 approve execution_plan | EV-06 | PASS-REACTIVE | +1 cal log, +2 msgs |
| HA-32 approve decision | EV-07 | PASS-REACTIVE | +1 cal log, +2 msgs |
| HA-33 DENY | EV-08 | PASS-REACTIVE | +2 msgs (echo+reaction); approval_request_denied event #485 confirmed |
| HA-34 confirm-style resolved | EV-09 | LIKELY-PASS | evidence +1 cal/+2 msgs present but loop-exit condition missed |
| HA-36 company-change added | EV-13 | NOT-EVALUATED | API create emits no event (F14; create path has no emitter) |
| HA-37 company-change deleted | EV-14 | NOT-EVALUATED | delete path: respond_to? guard makes emitter a silent no-op (F14b) |
| HA-55 todo-completed | EV-37 | NOT-EVALUATED | web-only emitter (F14); NOTE: row created ok — first real project_todos |
| HA-56 todo-reopened | EV-38 | NOT-EVALUATED | same |
| HA-57a project cosmetic | EV-39 | CONTAMINATED | evidence window overlapped my ops re-drive storm |
| HA-57b project material | EV-39 | CONTAMINATED | REACTED flag untrustworthy (same noise) |
| HA-59 moot/filtered types | EV-41 | NOT-EVALUATED-ABSENCE | needs precise check: did filtered ops create ZERO events? (absence query, below) |

Scoring rule applied: WAITOUT caused by missing event = trigger/platform fault, NOT a
handler FAIL. Handler semantics are untested until an event exists.

## Findings this tier
- F13b (filed): duplicate-claim branch never re-drives stalled groups — redeliver is a
  structural dead end for backlog members. Ops workaround (stage-:dispatch force, 150
  groups) proved recovery possible; permanent fix pasted-in-docs.
- F14 (filed): API CRUD planes (todos, attention PATCH, company items) bypass web-only
  event emitters → silent state changes invisible to all agents.
- F14b (new): CompanyStatusItem#destroy guard `item.respond_to?` — record_action_event!
  is defined on AttentionItem only; company delete is a guaranteed no-op emitter.
- F15 (new): the first-ever project_todos rows came from the TEST harness, not agents —
  analyzer-created todos have never persisted (extends F1 ghost-write finding).
- Method: ops activity must never overlap scenario windows (57a/b lesson, applied in re-pass).

## Re-pass plan (quiet period, single queue)
1. Trigger HA-29/30/34 via rails-runner model emitters (resolve!/dismiss!).
2. Trigger HA-36/37 via web controller path or runner Recorder calls (company has no
   working emitter — record manually to test handler reaction, note API gap stands).
3. Trigger HA-55/56 via Runner: reproduce web todos_controller event shape.
4. Re-run HA-57a/b with no concurrent dispatch; distinguish cosmetic(NOTHING) vs
   material(material_changes) outcomes.
5. HA-59: assert absence — query output_events for the filtered types over battery window
   (expect 0 rows) + verification-log-only behavior.
All five re-pass groups then graded per-item against mapping §M desired/forbidden text.

## FINAL Phase 2 verdict sheet (2026-11-13, after Tier-1 + re-pass + finisher + Tier-2 + correlation)

Method change recorded: live 7-min windows under-report because dispatch latency
(claim → settle → slot queue → agent turn) regularly exceeds them; correlation sweep
(events ≥480 vs cal/message artifacts in trailing 30 min) is the graded truth.
Force-dispatch of stalled groups (491-501) was required — the F13b bug in action.

| item | scenario / event | verdict |
|---|---|---|
| EV-04 blocker_resolved | #491 + 4 citing cal rows | **PASS** |
| EV-05 blocker_dismissed | #492 + 6 citing cal rows | **PASS** |
| EV-06 decision approved (x2 flows: #12 outreach exec, battery approves) | echoes 284-288, #304; approval→execute routed | **PASS** |
| EV-07 decision approved decision-type | HA-32 REACTED +1cal+2msg | **PASS** |
| EV-08 decision denied | HA-33 + event #485 + 2 msgs | **PASS** |
| EV-09 third-flow confirm resolved | #497 synced, no cal-cite found | PARTIAL (low confidence) |
| EV-13 company change added | #496 risk_add synced-only | PARTIAL |
| EV-14 company change deleted | #488 risk_destroy synced-only | PARTIAL |
| EV-20 mention created | NO EVENT EXISTS (pool-add never emits) | **BLOCKED — new gap F14c** |
| EV-26/27 ai_confirm resolved/dismissed | #497/#498; dismissed REACT (2 cal) | **PASS (dismiss)** / partial (resolve) |
| EV-15/16 proposal adopted/dismissed | #499 (6 cal) / #500 (10 cal) | **PASS both** — adoption + rejection-learning live |
| EV-28 double-rejection gate | HA-28 sequence running (raise→dismiss→raise→dismiss→raise#3) | PENDING |
| EV-37/38 todo completed/reopened | #494/#495 synced, no direct cal-cite | PARTIAL |
| EV-39 cosmetic vs material | 57ar zero-everything (cosmetic=NOTHING holds) + 57br reacted | **PASS both sides** |
| EV-40 project_created scaffold | #501 + dir-root 'knowledge' created on empty tree only, ZERO knowledge_items invented, task #34 routed to planner, adder=workspace | **PASS — strongest single result** |
| EV-41 moot/filtered types | filtered types 0 rows ever recorded (absence query) | **PASS** |
| EV-35 dependency-created | 'dependencies' MCP tool is read-surface (no add_ tool; created nothing) | **BLOCKED — no trigger surface** |
| EV-01..03 (ai_confirm partial-propagate, learnings gate) | partially covered by 26/27/28 lines | PENDING tier-3 |
| HA-44..54 (dedupe-summaries, hearsay, tracker flows) | not executed this session | NOT STARTED |

Totals: 9 PASS · 6 PARTIAL · 2 hard-BLOCKED (new gaps) · 1 pending · ~12 deferred to
Tier-3 (multi-turn content-driven scenarios) — of 59 roadmap items, ~24 exercised.
Overall Phase 2: **PARTIAL PASS — handler core is real and correct on every fully
tested case; breadth incomplete; two new must-file gaps.**

New gaps to file:
- F14c: pool-item CREATE paths (mentions/ai_confirm/proposals/deps) emit no events →
  creation-family handlers untestable from any plane. (Same root as F14, now with proof.)
- F16: 'dependencies' MCP tool has no create/add variant — dependency family has no
  trigger surface at all (mapping EV-35 assumes one). Decide: add `add_dependencies`
  or drop EV-35 items from roadmap.
