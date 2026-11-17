#!/usr/bin/env python3
"""score_emit — draft phase scoreboard md + machine results-t2.jsonl from ledger."""
import sys, os, json, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from t2lib import T2DIR
LED=os.path.expanduser("~/.hermes/cache/scratch/t2_ledger.jsonl")
def emit(arc):
    rows=[json.loads(l) for l in open(LED,encoding="utf-8") if l.strip()]
    mine=[r for r in rows if r["step"].startswith(arc)]
    out=os.path.join(T2DIR,"results-scoreboard-t2-%s.md"%arc)
    with open(out,"w",encoding="utf-8") as f:
        f.write("# T2 scoreboard draft — arc %s (%s)\n\n" % (arc, time.strftime("%Y-%m-%d %H:%M")))
        f.write("| step | status | detail |\n|---|---|---|\n")
        for r in mine: f.write("| %s | %s | %s |\n"%(r["step"],r["status"],r["detail"].replace("|","/")[:100]))
    with open(os.path.join(T2DIR,"results-t2.jsonl"),"a",encoding="utf-8") as f:
        for r in mine: f.write(json.dumps(r)+"\n")
    print("drafted",out,len(mine),"rows")
if __name__=="__main__":
    emit(sys.argv[1] if len(sys.argv)>1 else "A")
