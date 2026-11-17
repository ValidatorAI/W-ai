# Test 3 Phase 5 — Concurrent Delegation Race

Driver: Simultaneously post delegations to two different profiles from the same source, verify each gets its own isolated task.
Goal: Confirm no task collision when multiple profiles are delegated simultaneously.

### Steps

| # | Action | Timing |
|---|--------|--------|
| 1 | POST message to room 6 asking coder AND business_analyst to do different things | T+0 |
| 2 | Wait 5 seconds | T+5 |
| 3 | Check tasks list for both profiles | T+10 |
| 4 | Verify separate task records for each profile | sqlite3: SELECT count(*) GROUP BY assigneee_profile |
| 5 | Wait 60 seconds | T+70 |
| 6 | Verify each profile posted independent responses | sqlite3 JOIN messages with creator_id filter per profile |

### Pass criteria

| ID | Criteria |
|----|----------|
| P5-01 | Two distinct tasks created, one for each assignee_profile |
| P5-02 | Both tasks have independent dispatch_attempts |
| P5-03 | Each profile posts its own response (no merged/duplicated messages) |
