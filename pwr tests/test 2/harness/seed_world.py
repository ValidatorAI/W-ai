#!/usr/bin/env python3
"""seed_world — P0' seeding via product API only; SEED-OPS log for membership grants if no API."""
import sys, os, json, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from t2lib import api, walk, seed_ids, log, T2DIR, SEED_IDS
WANT=[("cobalt","Analytics for founder ops","/company/1/projects/cobalt",
       [("cobalt-main","general"),("cobalt-data","threads home")],30000),
      ("relay","Integrations and webhooks","/company/1/projects/relay",
       [("relay-main","general"),("relay-security","restricted")],10000)]
ids=seed_ids() or {"projects":{},"rooms":{},"threads":{},"dms":{},"seed_ops":[]}
for name,desc,path,rooms,budget in WANT:
    if name in ids["projects"]: continue
    c,d=api("POST","/projects",{"name":name,"path":path,"description":desc})
    pid=d.get("id") if isinstance(d,dict) else None
    ids["projects"][name]=pid; log("seed.project.%s"%name,c,d)
    for rn,purpose in rooms:
        c2,d2=api("POST","/rooms",{"name":rn,"project_id":pid,"purpose":purpose})
        if c2 in (404,405):  # fallback lane: ensure_room
            c2,d2=api("POST",f"/projects/{pid}/ensure_room",{"name":rn,"kind":purpose})
        ids["rooms"][rn]=d2.get("id") if isinstance(d2,dict) else None
        log("seed.room.%s"%rn,c2,d2)
# membership grants: try API lanes; if none, record SEED-OPS pending (direct SQL needs USER OK, per rules)
GRANTS=[("cobalt",{"human":[1,9],"bot":[2,3],"guest":[11]}),("relay",{"human":[1,8],"bot":[2],"guest":[10,14]})]
c,d=api("GET","/projects/2/members") # probe grant/read surface shape
for proj,who in GRANTS:
    ids.setdefault("grants_needed",[]).append({"project":proj,"users":who})
log("seed.grants","needs-api-or-approved-sql",len(ids.get("grants_needed",[])))
json.dump(ids,open(SEED_IDS,"w"),indent=1)
print("seed-ids.json written:",{k:len(v) for k,v in ids.items() if isinstance(v,dict)})
