#!/usr/bin/env python3
"""seed2 — complete P0' world: projects/rooms/threads + grants via API; SQL only if no lane."""
import sys, os, json, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from t2lib import api, sql_ro, log, SEED_IDS
ids={"projects":{},"rooms":{},"threads":{},"dms":{},"seed_ops":[]}
# projects (idempotent)
for name,path,desc in [("cobalt","/company/1/projects/cobalt","Analytics for founder ops"),
                       ("relay","/company/1/projects/relay","Integrations and webhooks")]:
    c,d=api("POST","/projects",{"name":name,"path":path,"description":desc})
    pid=d.get("id") if isinstance(d,dict) else None
    if c in (422,) or pid is None:
        rows=sql_ro(f"select id from projects where name='{name}'")
        pid=rows[0][0] if rows else None
    ids["projects"][name]=pid
# rooms via POST /rooms (creator user_id=1)
for rn,pid in [("cobalt-main",None),("cobalt-data",None),("relay-main",None),("relay-security",None)]:
    proj = "cobalt" if rn.startswith("cobalt") else "relay"
    pid = ids["projects"][proj]
    c,d=api("POST","/rooms",{"name":rn,"project_id":pid,"user_id":1})
    if c==422 and "exists" in str(d).lower():
        rows=sql_ro(f"select id from rooms where name='{rn}'"); rid=rows[0][0] if rows else None
    else:
        rid=d.get("id") if isinstance(d,dict) else None
    ids["rooms"][rn]=rid; log("seed.room."+rn,c,rid)
# thread lane probe: rooms.parent_id
c,d=api("POST","/rooms",{"name":"attribution-jobs","project_id":ids["projects"]["cobalt"],"user_id":1,"parent_id":ids["rooms"].get("cobalt-data")})
print("thread-create probe:",c,str(d)[:120])
if c in (200,201) and isinstance(d,dict):
    ids["threads"]["attribution-jobs"]=d.get("id")
    for tn,tp in [("pii-scan",("relay","relay-security")),("pricing-followup",("receipts","receipts-founders"))]:
        pid=ids["projects"].get(tp[0]) or 2
        parent=ids["rooms"].get(tp[1]) or {"receipts-founders":3}.get(tp[1])
        c2,d2=api("POST","/rooms",{"name":tn,"project_id":pid,"user_id":1,"parent_id":parent})
        ids["threads"][tn]=d2.get("id") if isinstance(d2,dict) else None
        log("seed.thread."+tn,c2,ids["threads"][tn])
# grants: API lane probe then SEED-OPS SQL (user authorized)
c,d=api("GET","/projects/%s/members"%ids["projects"]["cobalt"]); print("members read:",c,str(d)[:100])
GRANTS=[("cobalt",[1,9,2,3,11]),("relay",[1,8,2,10,14])]
for proj,users in GRANTS:
    pid=ids["projects"][proj]
    # project rooms = which room ids
    room_ids=[rid for rn,rid in ids["rooms"].items() if ids["projects"].get(rn.split("-")[0])==pid]
    for uid in users:
        c2,d2=api("POST",f"/projects/{pid}/members",{"user_id":uid})
        if c2 not in (200,201):
            ids["seed_ops"].append({"op":"sql_grant","project":pid,"user":uid,"api_code":c2})
print("api grant worked? last:",c2,str(d2)[:80])
json.dump(ids,open(SEED_IDS,"w"),indent=1)
print(json.dumps(ids,indent=1)[:900])
