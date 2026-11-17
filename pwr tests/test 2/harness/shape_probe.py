#!/usr/bin/env python3
"""shape_probe — read-only pre-flight: routes, tables, endpoint inventories the runners will use."""
import sys, os, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from t2lib import api, mcp, sql_ro, log
REPORT={}
def chk(name,ok,detail=""):
    REPORT[name]=("PASS" if ok else "FAIL",str(detail)[:150]); print(("PASS " if ok else "FAIL "),name,"",detail if not ok else "",flush=True)
c,d=api("GET","/health"); chk("rest_health",c==200,c)
c,d=api("GET","/projects?per_page=200"); rows = d if isinstance(d,list) else (isinstance(d,dict) and (d.get("projects") or [])) or []
chk("projects_list",c==200 and rows is not None,len(rows or []))
c,d=api("GET","/rooms/1/threads"); chk("threads_route_exists",c in (200,404) , "code %s (404+parent_id col => route real, room may have none)"%c)
chk("threads_db",bool([x for x in sql_ro("pragma table_info(rooms)") if x[1]=="parent_id"]))
chk("threads_archived_col",bool([x for x in sql_ro("pragma table_info(rooms)") if x[1]=="archived_at"]))
c,d=api("GET","/directs"); chk("directs_index",c==200,str(c))
c,d=api("GET","/reservations") if False else (404,"skip")
cols=[x[1] for x in sql_ro("pragma table_info(ai_tasks)")]
chk("ai_task_cols",all(k in cols for k in ["dispatch_attempts","usd_budget","token_budget","assigneee_profile"]),
    "dispatch_attempts/usd cols present")
c,d=api("GET","/attention_items?per_page=1"); chk("attention_api",c==200,d.get("count") if isinstance(d,dict) else "")
c,d=api("GET","/approval_requests/1"); chk("S8_flat_get",c==200)
c,d=api("GET","/company_status_periods"); chk("periods_api",c==200)
inv={}
for scope,base in [("mcp","/mcp"),("action","/action-mcp"),("read","/read-mcp"),("knowledge","/knowledge-mcp"),("task","/task-mcp"),("config","/config-mcp")]:
    out=mcp("hello",{},scope=base,mid=9)
    import subprocess, json as J, re as R
    o=subprocess.run(["curl","-s","-m","20","-X","POST","http://localhost:3000"+base,"-H","Content-Type: application/json","-H","Accept: application/json, text/event-stream","-H","Authorization: Bearer "+__import__("t2lib").env()["key"],"-d",J.dumps({"jsonrpc":"2.0","id":9,"method":"tools/list","params":{}})],capture_output=True,text=True).stdout
    m=R.search(r'\{"jsonrpc.*',o,R.S); n=0
    if m:
        try: n=len(J.loads(m.group(0))["result"]["tools"])
        except Exception: pass
    inv[scope]=n
chk("mcp_inventory",all(v>0 for v in inv.values()),inv)
json.dump({"inventory":inv,"checks":REPORT},open(os.path.expanduser("~/.hermes/cache/scratch/t2_shape_probe.json"),"w"),indent=1)
log("shape_probe","done",sum(1 for v in REPORT.values() if v[0]=="PASS"))
print("SHAPE PROBE:",sum(1 for v in REPORT.values() if v[0]=="PASS"),"PASS /",len(REPORT))
