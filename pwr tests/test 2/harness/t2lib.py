#!/usr/bin/env python3
"""t2lib — Test-2 harness core. Ledger-first, walk_pages, freeze guard, circuit breaker."""
import subprocess, json, re, time, sqlite3, os
REPO="/home/siavash/Documents/codes/Pavel/W/pwr"
T2DIR="/home/siavash/Documents/codes/Pavel/W/W-ai/pwr tests/test 2"
LEDGER=os.path.expanduser("~/.hermes/cache/scratch/t2_ledger.jsonl")
SEED_IDS=os.path.join(T2DIR,"seed-ids.json")
FREEZE=os.path.join(T2DIR,"FREEZE")
def env():
    e=open(REPO+"/.env").read()
    return dict(tok=re.search(r'OUTPUT_EVENTS_TOKEN=(\S+)',e).group(1).strip('"'),
                key=re.search(r'^MCP_AUTH_TOKEN=(\S+)',e,re.M).group(1).strip('"'))
def api(method,path,body=None):
    cmd=["curl","-s","-m","30","-w","\n|%{http_code}","-X",method,"http://localhost:3000/api"+path,
         "-H","Content-Type: application/json","-H","Authorization: Bearer "+env()["tok"]]
    if body is not None: cmd+=["-d",json.dumps(body)]
    out=subprocess.run(cmd,capture_output=True,text=True).stdout
    body_s,code=out.rsplit("\n|",1)
    try: return int(code), json.loads(body_s)
    except Exception: return int(code), body_s[:200]
def mcp(tool,args,scope="action-mcp",mid=1):
    out=subprocess.run(["curl","-s","-m","45","-X","POST","http://localhost:3000/"+scope,
        "-H","Content-Type: application/json","-H","Accept: application/json, text/event-stream",
        "-H","Authorization: Bearer "+env()["key"],"-d",json.dumps({"jsonrpc":"2.0","id":mid,
        "method":"tools/call","params":{"name":tool,"arguments":args}})],capture_output=True,text=True).stdout
    m=re.search(r'\{"jsonrpc.*',out,re.S)
    try: return json.loads(m.group(0)) if m else {"raw":out[:200]}
    except Exception: return {"raw":out[:200]}
def walk(path,key,params="",cap=40):
    rows=[]; pg=1
    while pg<=cap:
        c,d=api("GET",f"{path}{('?' in path and '&') or '?'}page={pg}&per_page=200{params}")
        chunk=(d or {}).get(key) if isinstance(d,dict) else None
        if not chunk: break
        rows+=chunk
        if len(chunk)<200: break
        pg+=1
    return rows
def sql_ro(q):
    c=sqlite3.connect("file:"+REPO+"/storage/db/development.sqlite3?mode=ro",uri=True)
    r=list(c.execute(q)); c.close(); return r
def log(step,status,detail=""):
    open(LEDGER,"a").write(json.dumps({"ts":time.strftime("%Y-%m-%d %H:%M:%S"),
        "step":step,"status":status,"detail":str(detail)[:400]})+"\n")
def freeze_guard(grading=True):
    if os.path.exists(FREEZE):
        if time.time()-os.path.getmtime(FREEZE) < 600:
            raise SystemExit("FREEZE active (<10min old) — no graded writes")
def repo_mtime_guard():
    r=subprocess.run(["git","-C",REPO,"log","-1","--format=%ct"],capture_output=True,text=True).stdout.strip()
    if r and time.time()-int(r) < 900 and os.path.exists(FREEZE):
        raise SystemExit("repo changed <15min ago inside freeze window")
def breaker_count(table,where,params,cap):
    c=sqlite3.connect("file:"+REPO+"/storage/db/development.sqlite3?mode=ro",uri=True)
    n=c.execute("select count(*) from %s where %s"%(table,where),params).fetchone()[0]; c.close()
    return n<=cap
def seed_ids():
    try: return json.load(open(SEED_IDS))
    except Exception: return {}
