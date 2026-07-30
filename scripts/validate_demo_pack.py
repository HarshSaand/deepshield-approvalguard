#!/usr/bin/env python3
"""Measure completeness and decodability of the generated demo pack."""
from __future__ import annotations
import csv, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/"dataset/manifest.csv").open(encoding="utf-8")))
checks=[]
for row in rows:
    path=ROOT/"dataset"/row["filename"]
    command=["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name","-of","json",str(path)]
    proc=subprocess.run(command,capture_output=True,text=True)
    payload=json.loads(proc.stdout) if proc.returncode==0 else {}
    streams=payload.get("streams",[])
    checks.append({"sample_id":row["sample_id"],"exists":path.exists(),"decodable":proc.returncode==0,
                   "has_video":any(s.get("codec_type")=="video" for s in streams),
                   "has_audio":any(s.get("codec_type")=="audio" for s in streams),
                   "duration_s":round(float(payload.get("format",{}).get("duration",0)),3)})
summary={"scope":"local functional-pack media QA; not AI accuracy", "manifest_rows":len(rows),
         "files_present":sum(c["exists"] for c in checks),"files_decodable":sum(c["decodable"] for c in checks),
         "files_with_video":sum(c["has_video"] for c in checks),"files_with_audio":sum(c["has_audio"] for c in checks),
         "duration_min_s":min(c["duration_s"] for c in checks),"duration_max_s":max(c["duration_s"] for c in checks),
         "conditions":{k:sum(r["manipulation_type"]==k for r in rows) for k in sorted({r["manipulation_type"] for r in rows})},
         "checks":checks}
(ROOT/"evaluation/demo_pack_validation.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in summary.items() if k!="checks"},indent=2))

