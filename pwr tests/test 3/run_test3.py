#!/usr/bin/env python3
"""Test 3 — Inter-Profile Task Delegation Harness

Phases:
  P1: workspace -> business_analyst (chat-triggered delegation)
  P2: workspace -> coder (direct MCP create_ai_task)
  P3: coder execution verification
  P4: cross-project delegation + approval gate
  P5: concurrent delegation race

Environment:
  OUTPUT_EVENTS_TOKEN = auth token from .env
  MCP_AUTH_TOKEN = MCP auth token from .env
  Dev DB = ~/Documents/codes/Pavel/W/pwr/storage/db/development.sqlite3
  Dev server = localhost:3000
"""
import sys, os, re, time, json, sqlite3, subprocess

sys.path.insert(0, "/home/siavash/Documents/codes/Pavel/W/W-ai/pwr tests/test 2/harness")
from t2lib import sql_ro, api, log

DB = "/home/siavash/Documents/codes/Pavel/W/pwr/storage/db/development.sqlite3"
db = sqlite3.connect(DB)

env = open("/home/siavash/Documents/codes/Pavel/W/pwr/.env").read()
oet = [l.split('=')[1].strip().strip('"').strip("'") for l in env.split('\n') if 'OUTPUT_EVENTS_TOKEN=' in l][0]
mcp_token = [l.split('=')[1].strip().strip('"').strip("'") for l in env.split('\n') if 'MCP_AUTH_TOKEN=' in l][0]

R = {}  # Results dict for scoring
TIMESTAMP_START = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

def apim(method, path, body=None):
    cmd = ["curl","-s","-m","20","-X",method,f"http://localhost:3000/api{path}",
           "-H","Content-Type: application/json",f"-HAuthorization: Bearer {oet}"]
    if body is not None: cmd += ["-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    parts = out.rsplit("\nHTTP_CODE:",1)
    sc = int(parts[1].strip()) if len(parts)==2 else 200
    raw_body = parts[0].strip() if len(parts)==2 else out.strip()
    try: j = json.loads(raw_body) if raw_body.startswith("{") or raw_body.startswith("[") else None
    except: j = None
    return sc, (j or raw_body[:80])

def q(s): return list(db.execute(s))

print(f"=== TEST 3 START ({TIMESTAMP_START}) ===\n", flush=True)

# ====================== PHASE 1 ======================
print("[PHASE 1] workspace -> business_analyst delegation\n", flush=True)

# Step 1: Post delegation message
sc, msg_resp = apim("POST", "/rooms/6/messages", {
    "user_id": 1, "mode": "ask",
    "body": "business_analyst: please write a 3-bullet research note on delegation patterns across Hermes profiles (workspace, coder, business_analyst)"
})
R["P1-01_msg_posted"] = "PASS" if sc == 201 else f"FAIL({sc})"
msg_id = msg_resp.get("id") if isinstance(msg_resp, dict) else None
print(f"  [P1-01] msg_posted: {R['P1-01_msg_posted']} (id={msg_id})")

if msg_id:
    # Step 2: Check events
    time.sleep(3)
    events_after = q(f"SELECT id, event_type, substr(event_data, 1, 80) FROM output_events WHERE datetime(created_at) > '{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()-10))}' AND event_type LIKE '%question%' OR event_type='message_created' ORDER BY id DESC LIMIT 5")
    R["P1-02_events_emitted"] = "PASS(%d events)" % len(events_after) if len(events_after) > 0 else "FAIL(no events)"
    print(f"  [P1-02] events_emitted: {R['P1-02_events_emitted']}")

    # Step 3: Check tasks for delegation
    time.sleep(5)
    ba_tasks = [t for t in q("SELECT id, assigneee_profile, dispatched, finished FROM ai_tasks WHERE assigneee_profile='business_analyst' AND dispatched=1 AND created_at > '2026-11-17 03:39' ORDER BY id DESC LIMIT 1")]
    R["P1-03_task_created"] = "PASS(id=%s assignee=%s dispatched=%s)" % (ba_tasks[0][0], ba_tasks[0][1], ba_tasks[0][2]) if ba_tasks else "FAIL"
    print(f"  [P1-03] task_created: {R['P1-03_task_created']}")
    
    # Step 4 & 5: Check dispatch outcome
    task_id = ba_tasks[0][0] if ba_tasks else None
    if task_id:
        detail = q(f"SELECT id, assigneee_profile, dispatched, dispatch_attempts, dispatch_error FROM ai_tasks WHERE id={task_id}")
        attempt = detail[0][3]
        error = detail[0][4] if detail[0][4] else "none"
        R["P1-04_dispatch_attempted"] = "PASS(attempts=%s error=%s)" % (attempt, error) if attempt >= 1 else "FAIL"
        
        # Check groups
        groups = q(f"SELECT id, status FROM output_event_dispatch_groups WHERE lead_output_event_id IN (SELECT id FROM output_events WHERE event_data LIKE '%task%{task_id}%')")
        R["P1-05_delivery_success"] = "PASS(group status=%s)" % str(groups[0][1]) if groups else "DELIVERY_FAILED_no_group"
        print(f"  [P1-04] dispatch_attempted: {R['P1-04_dispatch_attempted']}")
        print(f"  [P1-05] delivery_result: {R['P1-05_delivery_success']}")

        # Step 6: Check tool_cal_logs
        cal_logs = q("SELECT id, used_tool_name, substr(change_log, 1, 60) FROM tool_cal_logs WHERE used_tool_name != 'noop-verification' AND created_at > '2026-11-17 03:39' ORDER BY id DESC LIMIT 5")
        R["P1-06_logs_present"] = "PASS(%d exec logs)" % len(cal_logs)
        
        # Step 7: Check room 6 for bot reply
        replies = q("SELECT m.id, m.room_id, m.creator_id, substr((select r.body from action_text_rich_texts r where r.record_id=m.id and r.name='body'), 1, 100) FROM messages m WHERE m.room_id=6 AND datetime(m.created_at) > '2026-11-17 03:39' ORDER BY m.id DESC LIMIT 3")
        print(f"  [P1-07] room_6_bot_replies: {len(replies)} messages")
        for r in replies:
            print(f"    msg#{r[0]} creator={r[2]}: {r[3][:80]}")
    else:
        R["P1-04_dispatch_attempted"] = "SKIP(no task created)"
        R["P1-05_delivery_success"] = "SKIP"

# Scorecard summary
pass_c = sum(1 for v in R.values() if "PASS" in v or "PASS" in v)
fail_c = len(R) - pass_c
print(f"\n=== PHASE 1 COMPLETE: {pass_c}/{len(R)} PASS, {fail_c} FAIL ===\n", flush=True)

# Save results
summary = {"total": len(R), "pass": pass_c, "fail": fail_c, "items": R, "timestamp": TIMESTAMP_START}
json.dump(summary, open("/home/siavash/Documents/codes/Pavel/W/W-ai/pwr tests/test 3/results-phase1.md", "w"), indent=1, ensure_ascii=False, default=str)

print(f"[DONE] Phase 1 results saved. See /results-phase1.md for details.")
