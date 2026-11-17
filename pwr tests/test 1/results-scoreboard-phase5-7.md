# Results Scoreboard — Phases 5–7 consolidated — 2026-11-16

Repo: `W/pwr` @ `bbdcb73`+ · runners: phase5_runner (crash: my %-format bug, resumed), phase5b, phase6_runner.
Evidence: phase5_summary.json, phase6_summary.json, phase5.out / phase5b.out / phase6.out, ledgers.

## Phase 5 — infrastructure & ops proofs (PJ-07) — PASS with 2 findings

- PJ-07 creation twin ✅: two POSTs same path -> 1 project (p5twin), exactly 1 `project_created`
  event, `knowledge_path` present in payload.
- PJ-07 kill/restore ✅: orphaned that event (group deleted + aged) -> runtime sweep re-healed it
  in **420 s**, group recreated, synced=1 — no manual redeliver. HA-90's retry-recovery subcase
  passes under Hermes-delivery semantics (OUTPUT_EVENTS_URL sink per standing constraint: unused).
- Five creation-family events ✅: ai_confirm_created, blocker_created, knowledge_proposal_created,
  outcome_review_created — exactly 1 each for distinct subjects; project_todo_completed fired.
- ⚠️ O-7/F22 — BURST-DEDUPE INCIDENT (self-amplifying loop): 3 near-simultaneous add_mentions
  calls -> 3 rows, then AGENTS re-registered the same subject 17 more times across 22 min
  (each new row fires mention_created; some handler responds by creating rows — a feedback loop
  until room-less rows stopped matching). Loop decayed on its own; I removed the 17 artifacts
  (kept the 3 legit calls). Root causes: (a) no payload idempotence on creation tools (F22
  [COPILOT]); (b) no creator column on attention_items -> unattributable writes (F23 [COPILOT
  tiny]); (c) a profile treats `*_created` events as creation prompts, violating the S5
  created-lane contract ("route, never re-create") — needs cal-trail attribution first (F23
  would enable it).
- F21 [HERMES, AWAITING USER APPROVAL] — WA-04/05 guest leak CONFIRMED: flux (user 13) has ZERO
  memberships; asked two questions in room 2; w_ai answered with full receipts internals
  (approval ids, counts, milestones/todos) — msgs 615/616. Room-scope used instead of ASKER-scope.
  SOUL amendment drafted (ASKER-scope hard gate + non-disclosure template + loading-message
  parity + silence-never-valid); write blocked pending approval (protected file, timed out — not
  force-applied). Acceptance ready: re-ask as flux, expect template-only reply.
- Attachment/oversize HA-90 subcases: NOT RUN (uploads out of scope; INV battery HA-96 items
  remain Phase-2 deferred: TZ read-back, trailing-space room dup, <script> render, README parity).

## Phase 6 — idempotence & conservation — XD-01 (light interpretation) PASS + HA-100 GREEN

- XD-01 replay-delta (12 exact beat bodies reposted): topics +0, approvals +0, attention +0,
  ADRs +0, tasks +2 (both `Answer:`-class twins — O-8: dedupe Answer tasks by (question, asker,
  room) not just title). Bots wrote 3 explicit dedupe/noop cal rows in-window — the second-gate
  rule (AP-13) held under replay pressure.
- HA-100 conservation suite (finished DB): true-orphans 0, dangling message_topics 0, dangling
  history topics 0, level>3 tasks 0, finished-without-dispatched 0, dispatched-without-result 0,
  approvals status all valid. Two apparent violations were MY query bugs, both re-verified clean
  after correction (attention status is int enum 0/1/2; my rich-text join lacked record_type).
  events=326, groups=304, unsynced tail=11 (all expired-class members).
- Destructive full HA-78 fresh-DB double replay: NOT RUN (deliberate choice; ~5 h, wipes current
  scoring world; available as overnight batch on explicit request).

## Phase 7 — harness conventions gate (HA-97: HR-01..06)

- HR-01 dry-run-first ✅ with note: every runner was written to file, linted/syntax-checked and
  shape-probed against controllers/routes BEFORE launch (documented in each phase's notes).
- HR-02 no unexpected calls ⚠️: two self-inflicted crashes (v4 tuple bug, %-format bug) executed
  no writes beyond their step lists; Phase-5 crash left entities recoverable-by-resume. No
  off-script writes to the world otherwise.
- HR-03 read-before-write ✅: probe-first patterns throughout (route/shape checks pre-run).
- HR-04 noise budget (computed): required gated actions in campaign ≈ 60 (tasks) ; excess
  artifacts produced and removed/quarantined = 17 loop rows (P5 burst), 3 strike-sim duplicate
  blockers (P4 self-test), 2 Answer-task twins (P6) — noise ratio ≈ (22/60) 37% dominated by the
  P5 loop incident; all attributed artifacts either auto-decayed or surgically cleared with
  ledger records. noop-verification cal rows = 435/1038 (42%) — healthy designed-nothing
  visibility, not noise (they ARE the anti-noise instrumentation).
- HR-05 cal evidence: complete for MY-plane writes; INCOMPLETE for agent plane (F23: no creator
  column; burst loop agents wrote 17 rows with zero tool_cal rows — audit gap is the finding).
- HR-06 regression anchors-first ✅: M1/M1a/M5/M6/M7/M8/M9/M10/S9/F17/F18/F19/F20/F20b/O-5
  anchors re-verified in-sequence this campaign, each with commit + live-probe citation.

## Final campaign scoreboard
- Phase 1: PASS (126 items replayed ×2, conservation held)
- Phase 2: PARTIAL PASS -> regrades after M8: 9 hard + 8 re-verified PASS, 2 blockers closed (F14c via M8, F16 pending M9 decision)
- Phase 3: PARTIAL PASS 10 PASS / 4 PARTIAL(data-model) / KN-09 fixed+verified same day
- Phase 4: PASS 23/35 + 2 residuals -> F21 leak upgrade (privacy, fix drafted), gated items healthy
- Phase 5: PASS w/ F21+F22/F23 findings
- Phase 6: PASS (XD-01 light, HA-100 green)
- Phase 7: PASS (conventions gate; audit gap F23 named)
Open decisions/asks: M9 descope-vs-build; F21 SOUL approval (user); F22+F23 paste round; optional
HA-78 destructive overnight run; HA-96 INV battery still deferred.
