#!/usr/bin/env python3
"""anchor_map — build anchors-map.json from checklist-v2 §R (expands TP-06/07 style ids)."""
import sys, os, re, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from t2lib import T2DIR
sec=open(os.path.join(T2DIR,"pwr-semantic-checklist-v2.md"),encoding="utf-8").read()
sec=sec.split("## R — Regression anchors")[1].split("## F —")[0]
ids=set()
for fam,tail in re.findall(r"([A-Z]{2,3})-((?:\d{2}(?:/\d{2})*)+)",sec):
    for part in re.findall(r"\d{2}",tail):
        ids.add(f"{fam}-{part}")
anchors=[{"id":i,"family":i.split("-")[0],"grade_via":"Arc C"} for i in sorted(ids)]
extras=["M1","M1a","M5","M6","M7","M8","M10","F17","F18","F19","F20b","S8","S9","O-5","AP-11","KN-09","F21","F22"]
out={"anchors":anchors,"guards":extras}
json.dump(out,open(os.path.join(T2DIR,"anchors-map.json"),"w"),indent=1)
print("anchors:",len(anchors),"| families:",sorted({a["family"] for a in anchors}),"| guards:",len(extras))
