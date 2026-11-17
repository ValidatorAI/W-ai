# Test 3 Phase 4 — Cross-Project Delegation with Approval Gate

Driver: Post a cross-scope delegation request in receipts-founders (room 3) that asks workspace to delegate to w_ai, then requires human approval before execution.
Goal: Verify delegation across project boundaries respects project-scoping rules, and approval gates prevent unauthorized cross-project writes.

### Setup

User (siavash, user_id=1) is member of all three projects: receipts (proj 2), cobalt (proj 8), relay (proj 9).

### Steps

| # | Action | Scope | Details |
|---|--------|-------|---------|
| 1 | Ask workspace in receipts-founders (room 3): "w_ai, draft a risk assessment for cobalt project" | Room 3 (receipts project) | Cross-project scope question |
| 2 | Verify delegation triggers task for w_ai | sqlite3 tasks | task with assigneee_profile=w_ai, project_id=cobalt (or null if cross-scope rejected) |
| 3 | Check if approval required | sqlite3 approval_requests | gateway raises gate if writing across project boundary |
| 4 | Approve via API (PATCH /approval_requests/:id/approve) | REST API | Simulate human click |
| 5 | Wait for w_ai execution | Sleep 60s | w_ai drafts the risk assessment |
| 6 | Verify w_ai's output | sqlite3 messages w_ai replies | Check body for cobalt-relevant content |

### Pass criteria

| ID | Criteria |
|----|----------|
| P4-01 | Cross-scope task creation (workspace recognizes out-of-project target) |
| P4-02 | Approval gate raised automatically for cross-scope write |
| P4-03 | Human approval clears the gate |
| P4-04 | Target profile (w_ai) receives and executes within gate window |
