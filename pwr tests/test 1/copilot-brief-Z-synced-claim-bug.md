# Copilot brief Z — claim-before-200: `synced=true` flips even when delivery fails

Repo: /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD a970f2d+)
Date found: 2026-11-11, during Phase-1 replay (naive run, ledger
~/.hermes/cache/scratch/phase1_ledger.jsonl).

## Symptom (live-verified, three independent observations)
1. Events 1,2,3 (message_created, dispatched while the gateway 401'd) ended with
   `synced=true` — yet development.log shows the HTTP attempt failed with 401.
2. Redeliver of event 4: log recorded `Net::ReadTimeout` — event 4 still flipped
   to `synced=true` within the same job run.
3. Current run: message_created rows keep arriving with `synced=false` while the
   analyzer demonstrably executed the turns (message_analysis rows written), and
   `grep 'Successfully dispatched' log/development.log` returns ZERO hits since
   boot. Net effect: `synced` is disconnected from delivery reality in BOTH
   directions (true-on-failure, false-on-effectively-processed).

## Where (code trace)
app/jobs/output_events/process_and_dispatch_job.rb:
  - the group/event rows are created or claimed as pending BEFORE the HTTP POST
    to Hermes (~line 70-100: DispatchGroup upsert + event association);
  - `synced` on OutputEvent is set during that claim/merge step (or by the
    group-status transition), not in the success branch after
    `hermes_client.chat_completions` returns (~line 104-124);
  - the rescue path (~line 111) writes `result:{error...}` on the GROUP and
    reschedules, but the events already flagged `synced=true` are never rolled
    back — hence the 401-era true-flags.
ReadTimeout is ALSO swallowed as "transient" while the agent actually continues
running gateway-side, so the event is marked processed for an attempt whose
HTTP outcome is unknowable — the flag must reflect a confirmed 2xx response.

## Fix required
1. `synced` (and any consumed/processed group state) may flip to true ONLY after
   a confirmed successful HTTP response from Hermes (2xx parsed OK). Claiming a
   group for dispatch must use an intermediate state (group `status:"dispatching"`
   or a `claimed_at` column), NOT the event's `synced` flag.
2. On TransientDeliveryError/timeout/401: keep `synced=false`, group stays
   pending/failed per existing reschedule logic (hermes_busy path unchanged), and
   any partially-flagged events from that attempt are reset to false in the same
   transaction as the group error write (line ~111).
3. Permanent errors: synced stays false + group failed (already asserted by
   earlier tests — keep).
4. Keep the ReadTimeout case working: the agent may legitimately complete
   gateway-side after a client timeout. A timeout must NOT mark synced (attempt
   outcome unknown); reconcile will redrive; dedup at the agent/MCP layer is what
   keeps duplicates harmless — do not paper over it by trusting the claim.

## Tests (must fail before the fix, pass after)
- stub Hermes::Client.chat_completions raising HttpError(401): enqueue
  ProcessAndDispatchJob for an event → assert event.synced == false and group
  result records the 401 (reproduces ledger observation 1).
- stub raising Net::ReadTimeout → assert event.synced == false, group rescheduled.
- stub returning 200 → assert synced true, group dispatched (success path keeps
  working).
- redeliver of a 401-failed event: enqueues a fresh attempt; still false until a
  real 2xx (no inherited true from the first claim).
- conservation: after N failed attempts + 1 success, event row is still ONE row
  synced exactly once true (no duplicate dispatch groups re-marking others).
- `grep -c Successfully dispatched` parity: every synced=true flip must have a
  matching success log line (assert via capture in the controller-integration
  test — the ledger-vs-log audit this brief came from must become impossible).

## Acceptance = replay semantics restored
XD-01/XD-04 idempotence and OUT-02/04 delivery assertions read `synced` as a
delivery fact, and the /api/output_events?synced=false queue becomes trustworthy
as the "needs attention" view. The Phase-1 final re-audit will re-run this
observation set; the fix must not change dispatch success behavior itself, only
WHEN the true-flag is allowed.

NON-GOALS: do not change merge/dedupe keys, hermes_busy throttling,
ReconcileDispatchesJob cadence, or FILTERED_EVENT_TYPES. Do not add a new HTTP
endpoint; this is state-transition ordering inside the job (+ maybe one
intermediate group status string).
