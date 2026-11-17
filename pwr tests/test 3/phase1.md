# Test 3 Phase 1 — Inter-Profile Delegation: workspace → business_analyst

Driver: REST API (OUTPUT_EVENTS_TOKEN) to post messages as siavash (user_id=1).
Goal: Verify the delegation chain fires, and measure where it breaks.

### Step-by-step

| # | Action | Tool | Expected |
|---|--------|------|----------|
| 1 | Send ask to business_analyst in cobalt-main (room 6) | POST /api/rooms/6/messages | msg_created, ai_question_asked events fired |
| 2 | Poll output_events for ai_question_asked | sqlite3 query | event with room_id=6, actor.user_id=1, mode='ask' |
| 3 | Poll api/tasks?per_page=20&order=desc | curl GET | new task with assigneee_profile='business_analyst', status=newly-dispatched |
| 4 | Wait 30 seconds | sleep | dispatch attempt completes |
| 5 | Query output_event_dispatch_groups for task group | sqlite3 query | group exists, check status (dispatched vs failed) |
| 6 | Check tool_cal_logs for add_ai_task + noop-verification | sqlite3 query | workspace logged the task creation; if bus_analyst responded, logged its actions too |
| 7 | Read room 6 messages for bot reply | sqlite3 query | expect message from business_analyst profile (creator matching BA profile id), OR explicit failure reason |

### Scoring rubric

| Lane | Criteria | PASS condition |
|------|----------|----------------|
| P1-01 Message posted | msg.id exists and room_id=6 | ✅ HTTP 201, body matches input |
| P1-02 Events emitted | ai_question_asked in output_events | ✅ event_type present within 5s |
| P1-03 Task created | assigneee_profile='business_analyst' in tasks list | ✅ new row appears with correct profile |
| P1-04 Dispatch attempted | output_event_dispatch_groups has entry | ✅ group_id linked to task/event |
| P1-05 Delivery success | business_analyst posts message back to room 6 | ❌ CURRENTLY FAILS: Net::ReadTimeout in dispatch_error |

### Acceptance verdict

PASS if P1-01 through P1-04 pass, P1-05 documented as known gap.  
FAIL if P1-03 (task creation) does not produce a task with correct assignee.
