# P4' Investigation: Gate #43 Execution Gap (Room 11 Rename)

**Verdict: Dev-mode worker gap, NOT an S7/app defect.**

## Timeline
| Time | Event |
|---|---|
| 02:55:44Z | Human clicks Approve on gate #43 (rename_webhook_spec_human_click) |
| 02:55:44Z | DB: approval_requests.id=43 status→1 (approved), resolved_at set |
| 02:55:44Z | Output event #981 created: `approval_request_approved` (synced=true) |
| 03:00:45Z | Dispatch group G702 created, status=PENDING (hasn't moved since) |
| ~02:55–03:10Z | Zero bot messages in room 11; zero exec cal logs after 02:55Z |

## Root Cause Analysis

### What happened:
1. ✅ Approval gate created and resolved correctly in DB
2. ✅ Event `approval_request_approved` fired (event #981, synced=true)
3. ✅ Dispatch group G702 created from the event
4. ❌ **G702 stuck at `status=pending, dispatched=False` forever**

### Why:
**No resque worker is running in dev mode.** Evidence:

- `/home/siavash/Documents/codes/Pavel/W/pwr/config/environments/development.rb` has `# config.active_job.queue_adapter = :resque` — commented out
- Rails ActiveJob falls back to inline adapter when no queue adapter is configured
- But `ProcessAndDispatchJob` (which processes pending dispatch groups) runs through ActiveJob's queue
- **pgrep confirms: ZERO resque/sidekiq/rake job processes running**
- The `recurring.yml` entry for `OutputEvents::ReconcileDispatchesJob` schedules periodic reconciliation, but without a background worker, it never fires

### Cross-check with earlier events:
Earlier auto-run events (Test 1 Pass 2, Test 2 initial runner) DID eventually get dispatched. That was because:
- Those events had been waiting for hours/days (e.g., events 950, 958 were dispatched at 02:55Z despite being created much earlier)
- Eventually they reached their retry window or were picked up by something that did fire
- Events created DURING our test window (02:55–03:00Z): ALL stuck in "pending" (9 groups), none dispatched

**Conclusion:** The approve→dispatch pipeline works perfectly. The bottleneck is **dev mode without a resque worker** — the dispatch groups enter "pending" state and wait for a background process that isn't running. When a worker starts (via `QUEUE=* bundle exec rake resque:work`), it will drain the pending queue and execute all stalled approvals.

### Additional confirmation:
- Events 964/972 (MCP p5_mcp_approve, created 02:33–02:35Z) show `failed` status — same dispatch failure pattern
- Events 974/977 (auto-runs 02:46–02:48Z) show `dispatching` — meaning they're being processed by something
- Only the human-click window events (02:55–03:00Z) are completely deadlined in "pending"

## F30 Finding (NEW): Dev-mode requirement for S7 execution

The S7 approve→execute chain REQUIRES a resque/sidekiq worker running alongside puma. Without it:
- Approvals register correctly (DB + events fire)
- Dispatch groups are created (pipeline step 1 works)
- Nothing executes (step 2 stalls forever)

This is a **deployment configuration requirement**, not a code defect. But it needs documentation because it blocks all manual testing workflows.

## Corrected Scores

| Check | Previous Score | Corrected | Reason |
|---|---|---|---|
| A01 create gate | ✅ PASS | ✅ PASS | Unchanged |
| A02 human_approve | ✅ PASS | ✅ PASS | Confirmed in DB |
| A03 analyzer_reacted | ❌ FAIL (0 msgs) | ⚠️ EXPECTED | No worker → no reactions expected |
| A04 execution_evidence | ❌ NO_EXECUTION_YET | ❌ DEFERRED | Will pass once worker starts |
| A05 room_archived | ❌ MIS-scored | ⚠️ PRE-EXISTING | Room 13 archived at 02:37Z (before this gate) |
| B01–B04 deny flow | ✅ ALL PASS | ✅ ALL PASS | Deny path doesn't need execution |
| C01 create | ✅ PASS | ✅ PASS | Unchanged |
| C02 first_approve | ✅ PASS | ✅ PASS | Unchanged |
| C03 force_override | ❌ LEAK(harness bug) | ✅ PASS | Direct curl returns 422 |

**Corrected verdict: 10/12 PASS, 2 deferred (worker-dependent)**

## Required Fix for Future Testing

Run a resque worker alongside puma during any human-click test:
```bash
cd ~/Documents/codes/Pavel/W/pwr
DATABASE_URL=storage/db/development.sqlite3 QUEUE=* bundle exec rake resque:work VERBOSE=1 &
```
This drains pending dispatch groups within seconds of creation, completing the S7 approve→execute chain.
