# Results Scoreboard — Phase 3 (topic deepening & knowledge grammar) — 2026-11-13

Run: `~/.hermes/cache/scratch/phase3_runner.py` (+ follow-up probes) · ledger `phase3_ledger.jsonl`
summary `phase3_summary.json` · follow `phase3_follow.json` · 19 roadmap items (AN 4 / TP 9 / RH 1 / KN 5)

## Verdict: PARTIAL PASS — 9 hard PASS, 2 API-plane violations filed, 4 ungraded/fixture-pending, 4 content-graded items covered by analyzer rows (spot-checked)

## PASS (live-verified)
- TP-05 / HA-63: deactivated "Logo Rebrand" REACTIVATED by beat 306, no duplicate row (1 topic).
- TP-18 / HA-64: 4-level tree (40->41->42->43) + 200-message filler load created and persisted;
  `room_topic_tree` returns the nested structure intact.
- AN-12 / HA-79: event 523 redelivered twice -> analysis stayed SINGLE row (162). Update/dedupe,
  not create. (This is the strongest AN-12 evidence of the campaign.)
- AN-02: trivial beats 262/263 -> analysis rows exist but classified `message_type:"useless"`,
  importance 1, zero topic/task/attention side effects — correct low-value handling.
- TP-06/TP-07: hedged beat 311 ("AI-generated marketing video someday") -> topic "AI Marketing
  Video" (id 45) created as CHILD of existing topic 2, importance 2 (not spine-3), linked only to
  msg 312, history snapshot row present — exactly the hedge semantics.
- TP-09: compound beat 308 produced new topic "Churn Signal Tracking" (topic side captured).
- RH-02: history-vs-links consistency spot-check on topics 45/28/44/13 (snapshot rows present;
  full set-equality retest pending after proxy fixture was lost in the I2 wipe).
- KN-05: `POST /api/projects/2/knowledge_items` without description -> 422 "Description can't be blank"
  (real validation on this family).

## VIOLATIONS — new findings (API-plane validation gaps + broken destroy)
- F17 [COPILOT] (KN-06 parity): prose paragraph POSTed as directory_item name (id 7,
  item_type:"file") was ACCEPTED via API. Web plane enforces name-vs-prose placement rules;
  API bypasses them -> emitter/validation parity gap, same family as M8.
- F18 [COPILOT] (KN-07 parity): external_asset with dead URL `http://example.invalid/...`
  ACCEPTED (id 1) and 601-char title ACCEPTED (id 2) — no reachability/length validation on API.
  (If web never validated either, these are product-rule gaps, not parity — check model.)
- S9 [COPILOT] (functional): `DELETE /api/messages/137` returns an HTML error page and the message
  SURVIVES — REST destroy path for messages is broken (route/action or actor error).
  Blocks KN-08 (cited-knowledge degradation) retest.

## UNGRADED / PENDING (not failures)
- KN-04 + AN-09/15 recheck: attention query in probe used a wrong filter param (table has 16 rows
  but `category=` filter returned 0) — re-grade decisions/priorities for beats 264/308 with correct
  filter (no decisions_waiting rows from the 264 "decision: keep pricing hold..." message at
  ~02:29 run; may be analyzer-lane expectation, verify mapping wording before calling violation).
- KN-08: blocked by S9 (cannot delete a cited message to observe degradation).
- HA-65 full set-equality: 'proxy' fixture lost in I2; re-seed + rerun cheap.
- Bot emergent side of 307/313 (w_ai video verdict + summary): not asserted this pass (single-shot
  content beats, not HI arcs) — carry to Phase 5 cross-platform pass.

## Context
- I2 wipe happened BEFORE this run; Phase 3 regenerated its own event flow (216 events post-run,
  zero new Delete-All log lines during the run -> transient-code theory holds).
- Poison tasks 34/35 closed + M10 filed; no queue starvation during Phase 3.
- Gateway-restart status: S5/S6/S7 text changes NOT yet visible in behavior (no noop-verification
  rows; but no moot-event scenario ran this phase) — verify at Phase 4 start with a deliberate
  low-importance injection.

## Phase-4 readiness (privacy & access battery)
GO — F17/F18/S9 are content-validation/destroy-plane bugs that do not gate privacy tests.
Required first: M9 product decision still open (descope vs re-file).
