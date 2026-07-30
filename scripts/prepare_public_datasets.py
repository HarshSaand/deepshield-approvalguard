#!/usr/bin/env python3
"""Validate user-supplied public datasets and create a neutral inventory.

This script intentionally does not bypass access forms or redistribute datasets.
"""
from __future__ import annotations
import argparse, csv
from pathlib import Path

EXTS={".mp4",".mov",".mkv",".avi",".wav",".flac",".mp3",".m4a"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source", required=True, help="Dataset directory obtained under its official terms")
    ap.add_argument("--dataset-name", required=True, choices=["fakeavceleb","asvspoof2021_df","faceforensicspp","celebdf_v2"])
    ap.add_argument("--output", required=True); args=ap.parse_args()
    source=Path(args.source).expanduser().resolve()
    if not source.is_dir(): raise SystemExit(f"Not a directory: {source}")
    files=sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in EXTS)
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=["dataset","relative_path","suffix","label","identity_group","split"]); w.writeheader()
        for p in files: w.writerow({"dataset":args.dataset_name,"relative_path":str(p.relative_to(source)),"suffix":p.suffix.lower(),"label":"REQUIRED","identity_group":"REQUIRED","split":"REQUIRED"})
    print(f"Inventoried {len(files)} media files. Fill verified labels/groups before evaluation: {out}")

if __name__ == "__main__": main()

