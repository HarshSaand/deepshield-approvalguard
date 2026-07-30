#!/usr/bin/env python3
"""Create a small, balanced ASVspoof 2021 DF example pack from local data.

The source dataset must already have been obtained under its official terms.
This script never downloads or relabels audio.
"""
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="ASVspoof showcase folder containing manifest.csv and audio/")
    parser.add_argument("--output", type=Path, default=Path("dataset/asvspoof_examples"))
    parser.add_argument("--per-class", type=int, default=12)
    args = parser.parse_args()

    rows = list(csv.DictReader((args.source / "manifest.csv").open(encoding="utf-8")))
    selected = []
    for label in ("bonafide", "spoof"):
        available = [row for row in rows if row["label"] == label and (args.source / "audio" / label / row["filename"]).exists()]
        selected.extend(sorted(available, key=lambda row: row["utterance_id"])[: args.per_class])
    if len(selected) != args.per_class * 2:
        raise SystemExit(f"Not enough source files: selected {len(selected)}")

    audio_dir = args.output / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for row in selected:
        source = args.source / "audio" / row["label"] / row["filename"]
        shutil.copy2(source, audio_dir / row["filename"])
        row["local_path"] = f"audio/{row['filename']}"
        row["example_pack_role"] = "direct upload example; not a standalone benchmark"

    fields = list(selected[0])
    with (args.output / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(selected)
    print(f"Created {len(selected)} labelled examples in {args.output}")


if __name__ == "__main__":
    main()
