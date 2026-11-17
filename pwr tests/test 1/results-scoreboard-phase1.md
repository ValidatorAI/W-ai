# Phase 1 results scoreboard — v1 core replay (naive sequential)

Run: 2026-11-11 23:33 → 2026-11-12 04:35 UTC (+0330 06:36→11:38), 5 h 03 m.
Code state: W/pwr @ a970f2d throughout (Option A honored — no app edits during run).
Harness fixes made pre/at start (data/env only): HERMES_HTTP_TIMEOUT=60→900 in .env +
server restart; profile .env API_SERVER_KEY re-seeded with the correct 64-char value
(the 401s were my earlier masking slip, not PWR); runner bugfixes (message_analysis
response key, MCP session shortcut, probe readback).
Ledger: ~/.hermes/cache/scratch/phase1_ledger.jsonl (161 beat rows + SNAPSHOT).
Sweep: ~/.hermes/cache/scratch/phase1_sweep.json.

## 1. Beat-level rollup

| metric | value |
|---|---|
| beats replayed (v1 101–261) | 161 (115 human posts → msg ids 5–122, 46 bot-asserts, 1 probe) |
| human beats reacted in-window (≤240 s) | 70 (61%) |
| upgraded LATE-PASS at sweep | 4 → coverage 74/115 (64%); 41 NO-REACT |
| analyzer message_analysis rows | 77 (analyzed ids incl. late backlog; queue still draining post-redrive) |
| probe #103 token_budget | **lock holds** — create succeeded, value silently nil (TK-05/119 semantics PASS) |
| bot-authored room messages | **1** (msg #35, coder completion report to receipts-build) |
| approvals raised anywhere | 0 (all rooms) — click path never exercised by replay |
| todos persisted | 0 (but see F1 — one was CLAIMED in a tool log) |
| topics / message_links / history snapshots | 35 / 73 / 43 |
| tool_cal_log rows | 10 (sparse vs ~20+ agent writes) |
| redrive experiment (OUT-02/04 + XD conservation) | 100 unsynced events → POST redeliver → **row count 236→236**, no dup event rows; all flipped synced (flag not trustworthy pre-Z) |

## 2. Family verdicts (Phase-1 items only; full re-audit after queue drain)

| prefix | verdict | evidence / gap |
|---|---|---|
| AN (analysis) | PASS-partial | 77 rows, importance+tags present; 41 beats unre-analyzed (merge windows + 2-slot throttle; re-check post-backlog) |
| TP (topics) | PASS | 35 topics, 73 links, 43 room_history rows from replay chatter — nurturing alive |
| TK (tasks) | PASS-core | 2 tasks dispatched+finished with cost-before-close ($0.03/14k, $0.08/58k); #103 lock PASS; dedupe/child/rollup rows UNTESTED (no agent-created tasks beyond probes) |
| RH | PASS | 43 snapshots |
| WA (w_ai answering) | GAP | no in-room answers to any question beat, incl. guest #147-class |
| MS (messaging norms) | PARTIAL-GAP | 1 bot message (MS-01 PASS on room/identity), absence-heavy rows vacuous-pass, #131 @zzz stored raw ✓ (MS-12 partial) |
| AP / DS / HI / AT | GAP (not raised) | agents never call add_action_message from gated-intent beats → click/echo/ledger families unexercised by replay (machinery already proven out-of-band) |
| EV (handlers) | PARTIAL | coder task-execution + directory writes = handler-acts observed (EV-26/27-class); EV-00c post-write logging PARTIAL (10 logs); EV-00b dedupe held (no dup rows) ✓ |
| XD | PASS-conservation / FLAG-bug | redrive conserved; synced-claim bug confirmed (brief Z) — OUT/XD full pass must wait for Z |
| OR | PARTIAL | read-before-write visible in coder logs (tool_cal read before close); analyzer batch-order unverified |
| ST / IA / KN / PJ(seed) / HR | UNTESTED in Pass 1 (Phase 2/3 drivers) |
| F (ghost write) | **NEW finding F1** — see §3 |

## 3. Findings (severity-ordered)

F1 HIGH, semantic: analyzer logged `add_project_todo` (cal_log #1: "todo 'OSS README rewrite'
created (owner=roya, due Friday); new topic 7 opened", target_entity_id=15, project 2) —
topics row EXISTS, `project_todos` count = 0. **Logged-a-write-that-didn't-happen**
(hallucinated write + EV-00c violation twin). Needs: analyzer SOUL/prompt check AND a PWR
question — should add_project_todo via MCP have failed loudly instead? Repro: msg 101 arc.
F2 HIGH, platform: synced=true flips on claim, not on 2xx (three independent proofs;
brief Z drafted, ready to paste now the repo is unfrozen).
F3 HIGH, product-semantics: no agent raises approval requests from chat intent → AP/DS/HI
families need either SOUL tuning (bot-approvals skill not firing in message_analyzer/w_ai
context) or these flows are UI/event-only by design — needs owner decision, card for
message_analyzer SOUL author.
F4 MED: bot chat-plane nearly silent (1/115 arcs produced a reply) — w_ai answering +
mention-routed answers did not emerge from REST-replayed messages; likely tied to
plain-text-mention non-attachability + analyzer routing choices (mode:"ask" DID reach the
analyzer — it analyzed but chose not to answer in-room).
F5 MED: create_ai_task schema trap — unknown args (incl. `profile_name` vs triple-e
`assigneee_profile`) silently dropped; unassigned tasks never dispatch (correct routing,
but silent data loss on typo). Recommend schema strictness (reject unknown keys) — small
brief candidate.
F6 POSITIVE: AGT-02 wake model verified live end-to-end (assign → poller wakes coder →
pull via get_ai_task/tool reads → act → cost → close → report msg #35 → cal logs).
F7 POSITIVE: topic-nurturing plane is strong (35/73/43 rows) — analyzer does maintain
topics from pure chat, including creating new ones mid-replay.
F8 LOW: analyzer coverage 63% under 2-slot throttle; queue drained post-redrive — expect
late coverage climb; re-audit T+2 h.
F9 LOW: merge windows collapse rapid replay beats (by design); naive-sequential pacing
still merges trio events — fine for conservation, noted for per-message analysis claims.
F10 LOW: 12 events analyzed-but-flagged late; ghost #104-#111 TIMEOUTs were mostly
window artifacts, not infra.

## 4b. Post-script — Brief Z verified LIVE (2026-11-12, bf0d2c9)

Z merged during review; two-stage claim/dispatch job confirmed in code and behavior:
probe event #237 recorded `synced=false` at claim, flipped true ONLY after confirmed
2xx; `Successfully dispatched` log 0→17; regression tests for 401/timeout present.
F2 CLOSED (pre-Z true-flags on old rows remain historical artifacts; conservation
re-measured clean at Pass 2 sweep). Analysis coverage stayed 77 after backlog —
the 41 NO-REACTs are confirmed as legitimate EV-41 'nothing/verification-only'
outcomes, upgrading F8 to informational.

Pass 2 (full replay, XD-01 idempotence + dedupe gate: same 161 beat bodies incl.
#103 probe re-fire) running as of this addendum; ledger phase1_pass2_ledger.jsonl.

## 5. Pass 2 results (2026-11-13, resumed after kill, complete 101–261)

Run split note: gateway restart killed pass-2 at beat 146 (old SOULs, 12.5 h stall);
resumed 147–261 under the deployed M2/M3/M4 SOULs + post-Z code — the before/after
contrast is itself evidence.

| metric | pass 1 | pass 2 |
|---|---|---|
| human beats in-window reacted | 70/115 | 67/115 (+late-pass upgrades via analysis rows) |
| analyzer routing tasks created | 0 | ≥5 organic (14,15,16,17,18: coder/w_ai/pm, incl. child BLOCKED-PENDING) |
| approvals raised by agents | 0 | 6 (rooms 1–4; incl. expense, content-freeze, ADR-006, case-study, recap) — AP/DS/HI LIVE |
| decisions executed | 0 | 6 approve clicks incl. double-click no-op (6 action rows exactly) + echoes 284–288 |
| bot-authored room messages | 1 | 20+ (coder blockers, PM raises, w-ai answers, system echoes) |
| tool_cal_log rows | 10 | 159 — post-write logging now flowing (EV-00c) |
| F1 ghost write recurrence | 1 | none observed (M2 holding; final census pending) |
| XD-01 artifact growth on identical replay | — | topics 35→~40 w/ MERGE not linear dup; messages/todos: todo-plane still 0 rows → TK-17/person-todo routing = open gap |
| output events | 236 | 474; conservation 474→474 across 201 redrive ✓ ZERO dup rows |

F13 (new, ops/platform): hermes_busy reschedules write group pending/dispatching with
scheduled_at but dev :async never re-drives (ReconcileDispatchesJob needs solid_queue)
→ dispatches stall at exactly MAX_ACTIVE_AGENTS occupancy; redeliver-of-member hits
dedupe (duplicate member of stalled group). Mitigation applied: HERMES_MAX_ACTIVE_AGENTS
2→4 + Rails restart (backlog started flowing: cal logs 11→159). Required: busy path
self-reschedule (perform_later(wait:)) or run a queue worker in dev.

Pass-2 family delta vs Pass-1 (verdict upgrades): AP-01..07 GAP→LIVE-verified (raise,
4-tuple body, one-call w/ msg link (message_id 242/207), pending state, resolved
transitions, action ledger, no dupes); DS-01..03/06 LIVE (echoes + actor names);
HI-06 double-click PASS (idempotent, no new action row); WA-01..05 partially live
(w-ai answered task-routed questions in-room; attribution closed via user rename M5);
MS-01/02/13 live-positive (bot identity except the closed M5 case; cites what was read);
TK-14 STILL HOLDS: no delete_ai_task observed (task 13 "missing" was my probe cleanup,
agent rows intact); TK-17/person-todo STILL GAP: project_todos remains 0 despite
todo-log beats.

## 6. Gates & next steps (updated 2026-11-13)

Phase 1 = COMPLETE with verdict: PASS with findings (Z, M1a, M5 closed; M6 pending paste;
F13 filed; F1 not reproduced post-M2).
1. PASTE M6 (UserAdminService partial-update bug) + F13 block when convenient:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD 341192b+).
F13: OutputEvents::ProcessAndDispatchJob hermes_busy path updates the dispatch group to
pending/dispatching with result.scheduled_at but nothing re-drives it without
solid_queue (dev :async never runs ReconcileDispatchesJob) — dispatches stall
permanently once MAX_ACTIVE_AGENTS occupancy is reached. Fix: on busy reschedule,
self-enqueue OutputEvents::ProcessAndDispatchJob.perform_later(event_id, stage: :dispatch,
dispatch_group_id: group.id, wait: <retry delay seconds>); also add a stale-dispatching
sweep (groups stuck in dispatching > N minutes get re-driven by the reconcile job when
it does run). Tests: busy path enqueues a delayed follow-up; stale group recovered;
no duplicate groups created (dedupe key intact).
```
2. Phase 2 (event-injection battery HA-24…62, 59 items) — GO once M6+F13 land; needs
   gateway + server stable overnight window (same naive runner approach, event side).
3. Post-Phase-2: Pass-3 differential for HI click matrix (deny/cancel paths still
   un-clicked live; only approves exercised so far).
4. Product backlog raised by Phase 1: TK-17 person-todo never persists (analyzer routes
   but no todo rows), w_ai answer quality digests, ai_profiles seeding decision (F12).
