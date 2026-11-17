# Phase 4 — Required Changes (from results-scoreboard-phase4.md)

Repo state: `W/pwr` @ `7a06e94` (+local probes) · 2026-11-15
Owner tags: `[COPILOT]` = PWR code (paste-ready) · `[HERMES]` = W-ai souls/skills + mirror deploy · `[PRODUCT]` = decision.

---

## MUST

### F19 [COPILOT] ✅ FIXED + VERIFIED (e8235db, 2026-11-15) — action_label defaults on API/MCP

Model-level default (after_initialize + before_validation from CATEGORY_CONFIG, fallback "Resolve") —
no parallel paths. Live: MCP add_blockers -> item #31 with action_label 'Assign & Unblock' (exact
config string). AT-05 flips to PASS.

Evidence: MCP `add_blockers` / `add_mentions` / `add_outcomes_review` created items with
`action_label: null` for all three categories. The web plane applies CATEGORY_CONFIG defaults
("Approve", "Assign & Unblock", "Record Result"). Parity gap, same family as M8/F17/F18.

Paste for Copilot:

"Attention items created through the API/MCP path (add_blockers, add_mentions, add_outcomes_review,
and any other category) come back with action_label = null. The web plane assigns defaults from the
category config. Find the canonical CATEGORY_CONFIG/label defaults used by the web creation path and
apply them in the model (after_initialize or a before_validation default) so both planes produce
identical labels — no parallel paths. Add request specs: creating each category via API yields the
exact default label strings; explicitly-provided labels are preserved; unknown categories get the
documented fallback."

### F20 [COPILOT] — dispatch groups stuck pending for an hour (M7 family, unclaimed-pending trigger)

Evidence: groups 511-513, 517-518 created 2026-11-15 08:58 stayed `pending` for ~60 minutes; their
`message_created`/`ai_question_asked` events never dispatched (beats 546, 549, 551, 557 undelivered
for an hour; 517 flipped to dispatched only after manual redelivery of its lead event; 4 groups
still pending at cutoff). `ReconcileDispatchesJob` does not re-drive pending groups that were never
claimed; M7's recovery covers duplicate claims only.

Paste for Copilot:

"Dispatch groups created with status pending are never picked up if the initial claim job dies or
never runs: five groups from 08:58 sat pending for an hour (ids 511-513, 517-518) while their events
stayed unsynced; manual redelivery of the lead event moved one group (517) to dispatched, proving the
group data is fine and the claim/execute step is what stalls. Extend the recovery: a scheduled sweep
(the existing ReconcileDispatchesJob or a sibling) must find groups whose status is pending and whose
created_at is older than the settle window, and either claim them directly (same code path as the
normal claim — no parallel implementation) or re-enqueue their lead event through the existing
dispatch job. Add freshness/idempotence guards identical to M7's duplicate-claim recovery. Tests:
(a) create a group, never run the claim job, run the sweep -> group reaches dispatched and events
sync; (b) sweep is a no-op for pending groups inside the settle window and for dispatched groups;
(c) two sweeps in a row do not double-dispatch (single-flight)."

### AP-11 [HERMES] ✅ FIXED + VERIFIED LIVE (2026-11-15) — over-cautious approval raising

Verified chain (msg 592 replay of the exact failure): analyzer routed `Direct action: rename the
welcome checklist… — no approval needed; if the artifact does not exist on record, report that once
in the room and offer to register the intent as a todo` (task 63, coder) -> coder reply 594:
"artifact not on record, rename not applied. Direct action, no approval" -> approval table frozen
at #22 across the whole test. Zero approvals for a non-destructive rename with missing target =
mapping behavior restored. Deployed: message_analyzer SOUL routing rule (action-class gate +
Direct-action lane) + bot-approvals AP-11 pre-flight + Direct-action handling, mirrored 5/5
profiles, byte-verified, .bak-ap11 kept.

Evidence: beat 320 (rename a draft title — non-destructive) produced approval request #22, while the
mapping demands zero approvals for non-destructive renames. Nuance: the target artifact did not
exist yet.

Fix (SOUL/skill wording, w_ai + workspace approval skill): raise an approval only when the action is
destructive/irreversible OR spends money OR sends externally. For a non-destructive edit whose
target is missing, do NOT raise an approval: report the missing target in-channel and register the
intent as a todo/task (or ask a single clarifying question). Add the contrast example:
Right: "No FAQ draft is filed yet — nothing to rename. Want me to note it as a todo for when it
lands?" Wrong: approval request for a title rename.


### F20b [COPILOT or DEPLOY] ✅ SOLVED + VERIFIED LIVE (777e48f, 2026-11-15) — hands-off self-heal proven

Acceptance run: manually set live group 523 to `pending` (simulating dead claim), posted one normal
message through the API; the fresh claim self-enqueued the sweep and `ReconcileDispatchesJob` RAN IN
APP RUNTIME (no rails runner) within ~2 min — group 523 re-driven to dispatched, gateway busy at
8/8 so it parked as `hermes_busy` with `scheduled_at + retry_token` (F13 semantics) for retry —
which the now-live sweep will execute. Expiry works at scale: 12 ancient Nov-13 groups flipped to
failed in the same runtime sweeps. Busy-guard preserved (skips at 8>=8, proceeds at 16).
Sub-caveats: (1) the recurring.yml 2-min schedule is dormant in this dev box because dev runs the
async in-process adapter (no bin/jobs) — self-enqueue-per-claim covers it; in resque deployments the
scheduler entry needs bin/jobs running. (2) Gap-2 (resque-pool) was fixed by DOCUMENTATION in README,
not by running a worker — acceptable for dev (async), verify in prod compose.
SECURITY: commit 777e48f accidentally tracked `.env.bak-f20` (contains real token values).
Remove now: `git rm --cached .env.bak-f20 && git commit -m "remove accidentally committed env backup"
&& rm .env.bak-f20` — and purge from history (git filter-repo / BFG) before any push; file came from
MY pre-F20 test backup, not Copilot's idea.

### O-5 [COPILOT] ✅ SOLVED + VERIFIED LIVE (bbdcb73, 2026-11-16) — group-less orphan events self-heal
Orphan pass in ReconcileDispatchesJob after the busy-guard: unsynced events older than MIN_STALE
with NO group reference -> re-enqueued through the standard ProcessAndDispatchJob claim (cap 50/run,
`touch(:updated_at)` throttle prevents double-enqueue, telemetry now reports `orphaned N`).
Verified live by late-orphan design (event 786): group deleted AFTER delivery settled + 5min age
stamp -> next runtime sweep logged `orphaned 1 event(s)` and the event was synced with a NEW group
within 75s — no redeliver. Idempotence proven by an adjacent sweep logging `orphaned 0`.
Scan of the remaining unsynced tail: 13/13 all belong to EXPIRED (failed) groups — by-design tail,
revivable via redeliver (proven on 507) — zero true orphans remain.
Housekeeping confirmed: `.env.bak-f20` removed from tracking AND worktree (user commits 46495e4/
89f7c4f). History still contains the blob locally — purge (filter-repo/BFG) or rotate tokens
before pushing the branch anywhere.

### (superseded plan) F20b — the recovery sweep is never actually scheduled (paste prompt as delivered)

Evidence: the ONLY reference to running ReconcileDispatchesJob outside the job file and tests is a
COMMENTED cron instruction in `config/initializers/scheduled_jobs.rb` (line 15). Nothing in the app
enqueues it: no recurring.yml entry, no self-enqueue from ProcessAndDispatchJob, no resque-scheduler
job. So even with correct recovery logic, stale pending groups still never self-heal in practice.

Paste for Copilot:

"Wire the dispatch-group recovery sweep so it actually runs: (1) add an entry to config/recurring.yml
(or the resque-scheduler mechanism this app uses for file_reservation_cleanup — mirror that pattern
exactly) scheduling OutputEvents::ReconcileDispatchesJob every 2-3 minutes; (2) additionally
self-enqueue it from OutputEvents::ProcessAndDispatchJob after a group is created (perform_later(…
wait: 90.seconds)) so a group whose first claim never arrives gets swept without depending on the
cron; (3) keep the busy-guard/throttle behavior; (4) spec: fake the scheduler, create a group whose
claim job never runs, assert within the scheduled cadence the group reaches dispatched and its lead
event synced. Note the current dev box has no resque worker process running even though
Procfile declares resque-pool — if the app's intended consumer is resque-pool, document the exact
command to start it in README/ENVIRONMENT docs."

### Phase-4 status after re-checks (2026-11-15)
F19 ✅ | F20 code ✅ / end-to-end ⚠ (F20b scheduling + worker gap) | AP-11 ✅ | M10 ✅ closed.
Unsolved ledger tail: 20 unsynced events incl. the expired-272 members (507/508) — will clear once
F20b lands or by manual redrive (which works: 47->20 during these tests).

---

## SHOULD

### R2 [TEST-OWNER] ✅ DONE (2026-11-16) — see results-scoreboard-phase4.md R2 section (23/35 PASS, residuals: WA-04/05 guest replay -> Phase 5; O-6 ADR structured body -> product)
1. Re-run beats 546 (AP-13 filing), 549 (WA-06 variant), 551 (MS-11 explicit refusal), 557 (guest
   WA-04/05 wording diff) and grade the deferred rows.
2. Grade DS-04/XD-07 after the gated approvals (#19 dissent ADR, #21 slip decision) are executed by
   a human; check ADR body fields + linked todo/task in period.
3. PJ-10 hallucination detector on p4rich/p4vague/p4empty once their creation events deliver:
   rich -> plan citing description substrings; vague/empty -> question or minimal plan, never invented
   specifics.
4. ST-04 with a real milestone row (post beat 326 as a human ask after creating a milestone).

---

## Order & dependencies
1. F19 + F20 in one PR (both small, both API-plane).
2. AP-11 wording (HERMES lane, my deploy) — independent.
3. R2 re-tests after 1-2 merge.
Phase 5 (infrastructure/ops proofs: log ordering, TZ, README route parity, HA-96 INV battery) is NOT
gated by these — the only shared prerequisite is the F20 fix for reliable dispatch timing.
