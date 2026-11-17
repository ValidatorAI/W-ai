#!/usr/bin/env python3
"""run_arc — executes transcript-t2.md beats. --dry prints ordered step list (HR-01), no writes."""
import sys, os, re, json, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from t2lib import api, mcp, walk, log, seed_ids, freeze_guard, breaker_count, T2DIR
TRANS=os.path.join(T2DIR,"transcript-t2.md")
USERS={"siavash":1,"David":8,"Jason":9,"w-ai":2,"Coder":3,"Market Research":4,"Business Analyst":5,
       "Project Manager":6,"nimbus":10,"orbit":11,"vector":12,"flux":13,"halo":14}
def beats():
    out=[]
    for l in open(TRANS,encoding="utf-8"):
        m=re.match(r"^\|([ABDEFG]-?\d*|[A-G]\d{2})\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|",l)
        if m:
            bid,room,actor,mode,body=[x.strip() for x in m.groups()]
            if mode in ("purpose","—","-"): continue
            out.append((bid,room,actor,mode,body))
    return out
def resolve_room(name,ids):
    n=name.replace("thread:","")
    return ids.get("rooms",{}).get(name) or ids.get("rooms",{}).get(n) or ids.get("threads",{}).get(n)
def run(dry=False,arc=None):
    ids=seed_ids(); plan=[]
    for bid,room,actor,mode,body in beats():
        if arc and not bid.startswith(arc): continue
        rid=resolve_room(room,ids)
        step={"beat":bid,"room":room,"room_id":rid,"actor":actor,"mode":mode,"body":body[:60]}
        plan.append(step)
        if dry: continue
        if mode in ("dm",): # DM lane posts via directs room id
            if rid: c,d=api("POST",f"/rooms/{rid}/messages",{"user_id":USERS.get(actor),"body":body}); log(bid,c,d)
        elif mode in ("ask","message"):
            if rid is None: log(bid,"SKIP-UNRESOLVED",room); continue
            c,d=api("POST",f"/rooms/{rid}/messages",{"user_id":USERS.get(actor),"mode":("ask" if mode=="ask" else "message"),"body":body})
            log(bid,c,d)
            if c==201 and "mention" in body.lower() or "proposal" in body.lower():
                if not breaker_count("attention_items","title like ?",(f"%{body[:25]}%",),8):
                    log(bid+"-breaker","TRIPPED"); break
            time.sleep(2)
        else:
            log(bid,"MANUAL-HARNESS",body[:60])
    for s in plan: print("{beat} | {mode} | {actor} -> {room}{id} | {body}".format(**s, id=("(%s)"%s["room_id"] if s["room_id"] else "(UNRESOLVED)")))
    print("STEPS:",len(plan))
if __name__=="__main__":
    dry="--dry" in sys.argv
    arc=None
    for a in sys.argv:
        if a.startswith("--arc="): arc=a.split("=")[1]
    if not dry: freeze_guard()
    run(dry, arc)
