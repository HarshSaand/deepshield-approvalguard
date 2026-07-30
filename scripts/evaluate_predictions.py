#!/usr/bin/env python3
"""Evaluate binary integrity scores without third-party Python packages."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path


def safe_div(a, b): return a / b if b else 0.0


def auc(labels, scores):
    positives = [s for y, s in zip(labels, scores) if y == 1]
    negatives = [s for y, s in zip(labels, scores) if y == 0]
    if not positives or not negatives: return None
    wins = sum((p > n) + 0.5 * (p == n) for p in positives for n in negatives)
    return wins / (len(positives) * len(negatives))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--predictions", required=True)
    ap.add_argument("--output", required=True); ap.add_argument("--threshold", type=float, default=0.5); args = ap.parse_args()
    truth = {r["sample_id"]: int(r["target"]) for r in csv.DictReader(open(args.manifest, encoding="utf-8"))}
    preds = {r["sample_id"]: float(r["score"]) for r in csv.DictReader(open(args.predictions, encoding="utf-8"))}
    missing, extra = sorted(set(truth)-set(preds)), sorted(set(preds)-set(truth))
    if missing or extra: raise SystemExit(f"ID mismatch. Missing={missing}; extra={extra}")
    ids = sorted(truth); labels = [truth[i] for i in ids]; scores = [preds[i] for i in ids]
    binary = [int(s >= args.threshold) for s in scores]
    tp=sum(y==1 and p==1 for y,p in zip(labels,binary)); tn=sum(y==0 and p==0 for y,p in zip(labels,binary))
    fp=sum(y==0 and p==1 for y,p in zip(labels,binary)); fn=sum(y==1 and p==0 for y,p in zip(labels,binary))
    recall=safe_div(tp,tp+fn); specificity=safe_div(tn,tn+fp); precision=safe_div(tp,tp+fp)
    result={"scope":"functional demo pack; not a benchmark", "samples":len(ids), "threshold":args.threshold,
            "confusion":{"tp":tp,"tn":tn,"fp":fp,"fn":fn}, "accuracy":safe_div(tp+tn,len(ids)),
            "balanced_accuracy":(recall+specificity)/2, "precision":precision, "recall":recall,
            "f1":safe_div(2*precision*recall,precision+recall), "false_positive_rate":safe_div(fp,fp+tn), "roc_auc":auc(labels,scores)}
    Path(args.output).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__": main()

