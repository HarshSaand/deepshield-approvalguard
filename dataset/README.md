# ApprovalGuard demo media pack

This folder contains 24 small MP4 files for exercising the ApprovalGuard upload, analysis, timeline, and reporting flow without using customer data.

## Important boundary

This is a **functional demo pack**, not a deepfake benchmark and not evidence of production accuracy. Its fictional professional is a project-owned AI-generated image, animated locally; its audio is a generated speech-like signal; and its labels describe transformations applied by the generator. Do not describe `clean_sync` as a real human or `manipulated` as proven fraud.

The pack is balanced across four conditions:

| Condition | Count | Intended check |
|---|---:|---|
| `clean_sync` | 6 | Control media with matched mouth and audio envelopes |
| `audio_replaced` | 6 | Audio envelope is replaced while video is retained |
| `video_tampered` | 6 | A blurred, colour-shifted identity-region splice appears from 1.6–3.1 s |
| `av_desync` | 6 | Audio is shifted relative to mouth movement |

`manifest.csv` records each sample, transformation, intended label, affected interval, generator version, and provenance. The generator is deterministic; rerunning it recreates the pack.

## Recreate it

Requirements: Python 3.10+, Pillow, and FFmpeg. The source portrait is at `dataset/assets/synthetic_identity.png`.

```bash
python3 scripts/generate_demo_pack.py
```

## Evaluate a detector

Create a CSV with `sample_id` and `score` where larger scores mean more likely manipulated. Then run:

```bash
python3 scripts/evaluate_predictions.py \
  --manifest dataset/manifest.csv \
  --predictions evaluation/predictions.csv \
  --output evaluation/metrics.json
```

The evaluator reports confusion-matrix counts, accuracy, balanced accuracy, precision, recall, F1, false-positive rate, and ROC-AUC. Choose a threshold on a validation set; the default `0.5` is only for exercising the tool.

## Public benchmarks

See `DATASET_CARD.md` and `scripts/prepare_public_datasets.py`. Public datasets are not redistributed here because their licences, access forms, and size make silent bundling inappropriate.
