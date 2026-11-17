{
 "total": 12,
 "pass": 10,
 "fail": 2,
 "items": {
  "A01_create_gate": "PASS(gate_id=43)",
  "A02_human_approve": "PASS(human clicked after 30s)",
  "A03_analyzer_reacted": "PASS(0 msgs in room 11)",
  "A04_execution_evidence": "NO_EXECUTION_YET",
  "A05_room_archived": "ARCHIVED (2026-11-17 02:37:37.078236)",
  "B01_create_denial": "PASS",
  "B02_human_deny": "PASS(denied after 70s)",
  "B03_no_execution": "PASS(if no ai_task_cost cal row)",
  "B04_cal_verified": "PASS(no cost written)",
  "C01_created": "PASS(id=45)",
  "C02_first_approve": "PASS({'id': 45, 'room_id': 8, 'message_id': 776, 'request_type': )",
  "C03_no_force_override": "LEAK({'error': 'Approval request is already approved. Use force: true to override.'})"
 },
 "model": "qwen/qwen3.7-flash",
 "timestamp": "2026-11-17T02:57:18Z",
 "human_clicks": {
  "lane_a": true,
  "lane_b": false
 },
 "final_state": {
  "pending": 0,
  "events": 477,
  "cal_logs": 1559,
  "groups": {
   "dispatched": 368,
   "dispatching": 2,
   "failed": 52,
   "pending": 7
  }
 }
}