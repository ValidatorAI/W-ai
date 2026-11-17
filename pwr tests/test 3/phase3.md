# Test 3 Phase 3 — Execution Verification: Can coder execute a workspace-delegated task?

Driver: Create task targeting coder profile directly (via phase 2 method), then verify coder actually executes and reports results.
Goal: Close the delegation loop — does coder receive, process, and report back?

### Steps

| # | Action | Method | Notes |
|---|--------|--------|-------|
| 1 | Defer to Phase 2 setup (session initialization + create_ai_task call to coder) | Same as P2 | Reuse existing session, skip re-init |
| 2 | Wait for dispatcher to deliver task to coder | Sleep 90s | Allow dispatch_attempts to complete |
| 3 | Query task state | SQLite: SELECT ... WHERE assigneee_profile='coder' AND finished=False ORDER BY id DESC LIMIT 1 | Get current dispatch_attempts and dispatch_error |
| 4 | Check for coder's output | SQLite JOIN: SELECT m.id, m.room_id, substr((select r.body from action_text_rich_texts r where r.record_id=m.id),1,150) FROM messages m JOIN output_events oe ON oe.event_data LIKE '%task%coder%' WHERE oe.created_at > datetime('now','-90 seconds') | Look for coder posting completion message |
| 5 | Check tool_cal_logs | SELECT used_tool_name, change_log FROM tool_cal_logs WHERE creator_id IN (coder profile IDs) AND created_at > datetime('now','-90 seconds') | Look for add_message, update_ai_task, etc. |

### Pass criteria

| ID | Criteria | Condition |
|----|----------|-----------|
| P3-01 | Task reaches coder (not stuck at dispatch_failure) | dispatch_attempts ≥ 2 OR successful delivery |
| P3-02 | Coder creates output content | Message posted by coder profile |
| P3-03 | Content matches expected scope | Body references task description topic |
