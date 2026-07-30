# DeepShield ApprovalGuard

DeepShield ApprovalGuard is a local multimodal AI prototype for reviewing voice and video instructions associated with sensitive financial actions. It is designed around a practical question: before a payment, account recovery, limit change, or treasury instruction moves forward, can AI surface media-integrity signals that deserve a closer look?

The system does not make a fraud decision. It analyses each modality separately, shows where suspicious evidence appears, and produces a review suggestion that can sit alongside an institution's existing controls.

**Repository:** [github.com/HarshSaand/deepshield-approvalguard](https://github.com/HarshSaand/deepshield-approvalguard)

## What the project demonstrates

- real local inference with pretrained deepfake-detection models;
- separate voice, face, recording-continuity, and audio-video timing evidence;
- temporal analysis rather than a single unexplained file-level label;
- quality-aware abstention when a required media stream is missing or unusable;
- a clear review output for a financial-operations workflow;
- reproducible sample data, evaluation results, and automated tests.

## How it works

```text
Audio or video instruction
          |
          v
  Media and quality checks
          |
          +----------------+----------------+----------------+
          |                |                |                |
       AASIST           Meso4          ResNet-18       A/V activity
     voice spoof     face tampering     continuity       alignment
          |                |                |                |
          +----------------+----------------+----------------+
                                   |
                                   v
                    Timestamped evidence timeline
                                   |
                                   v
                  STANDARD / REVIEW / ESCALATE /
                        INSUFFICIENT EVIDENCE
```

### AI components

| Evidence branch | Implementation | What it contributes |
|---|---|---|
| Synthetic voice | AASIST spectro-temporal graph-attention network | Spoof evidence for the complete clip and temporal windows |
| Face manipulation | DeepfakeBench Meso4 compact CNN | Frame-level face-region manipulation evidence |
| Recording continuity | ImageNet-pretrained ResNet-18 embeddings | Learned visual discontinuity between neighbouring segments |
| Audio-video timing | Mouth-motion and audio-activity correlation | Interpretable synchronisation evidence; this branch is signal processing rather than a trained lip-reading model |

The decision layer deliberately keeps these signals separate. Its priority index is a routing aid, not a fraud probability. Two high signals suggest escalation; one high signal or two elevated signals suggest independent review. Poor-quality or missing inputs can produce an insufficient-evidence result.

## Output

For each uploaded recording, the interface returns:

- media duration and stream availability;
- audio and video quality checks;
- a synthetic-voice evidence score and temporal segments;
- face-manipulation and continuity evidence for video;
- audio-video synchronisation evidence when both streams exist;
- an interactive evidence timeline;
- a review level, supporting reasons, and suggested control action;
- a downloadable JSON record with model names, timestamps, quality fields, and a SHA-256 file hash.

## Data included with the project

The repository is immediately testable with 48 labelled files:

- **24 five-second MP4 workflow fixtures:** six controls, six audio replacements, six visible identity-region edits, and six audio-video desynchronisation cases;
- **24 ASVspoof 2021 DF audio examples:** 12 bona-fide and 12 spoof clips for direct voice-model testing.

Labels, transformations, affected intervals, and provenance are documented in `dataset/manifest.csv` and `dataset/asvspoof_examples/manifest.csv`. The MP4 files are functional fixtures, not a scientific accuracy benchmark. `DATASET_CARD.md` explains the evaluation boundaries, while `DATASET_OPTIONS.md` identifies larger datasets for broader testing.

## Locally measured voice-model result

AASIST was evaluated locally on a balanced 570-file subset of ASVspoof 2021 DF:

| Metric | Result |
|---|---:|
| ROC-AUC | 0.9078 |
| Equal error rate | 18.60% |
| Accuracy at the subset-selected EER threshold | 81.40% |
| Spoof precision | 81.40% |
| Spoof recall | 81.40% |
| Mean model inference time on Apple MPS | 17.44 ms/file |

The threshold was selected and measured on the same showcase subset, so these numbers describe the prototype experiment rather than an independent production estimate. The exact summary and all 570 per-file scores are available in `evaluation/`.

## Requirements

- Windows or macOS with at least 8 GB RAM
- Python 3.11 or 3.12
- FFmpeg
- Internet access during first-time installation; torchvision may download official ResNet-18 weights once

Python 3.13 or later is not recommended for the pinned package set.

### Install FFmpeg

macOS:

```bash
brew install ffmpeg
```

Windows PowerShell:

```powershell
winget install --id Gyan.FFmpeg --source winget
```

Close and reopen the terminal, then verify:

```bash
ffmpeg -version
```

## Run on macOS

```bash
git clone https://github.com/HarshSaand/deepshield-approvalguard.git
cd deepshield-approvalguard
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python api.py
```

Open [http://127.0.0.1:8091](http://127.0.0.1:8091) in a browser. Keep the terminal open while using the application and press `Control + C` to stop it.

## Run on Windows

```powershell
git clone https://github.com/HarshSaand/deepshield-approvalguard.git
cd deepshield-approvalguard
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python api.py
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Then open [http://127.0.0.1:8091](http://127.0.0.1:8091).

## Test the application

### Guided cases

Use the guided demonstration to compare a supplier-payment face edit, treasury audio replacement, limit-increase timing mismatch, and a control recording. Select timeline sections to jump to the corresponding evidence and download the JSON record for technical inspection.

### Upload a file

Select **Test a file**, choose an MP4, MOV, WebM, MKV, AVI, WAV, FLAC, MP3, or M4A file, and click **Analyse locally**. Audio-only files correctly omit the visual and lip-sync branches. Uploaded media is processed through a temporary local copy that is deleted after analysis.

Two useful ASVspoof examples are:

```text
dataset/asvspoof_examples/audio/DF_E_2000053.flac  bona-fide
dataset/asvspoof_examples/audio/DF_E_2000011.flac  spoof
```

## Validate the project

Run the automated tests:

```bash
python -m pytest -q
```

Validate that all demonstration videos exist, decode, and contain both audio and video:

```bash
python scripts/validate_demo_pack.py
```

Recreate the project-owned demonstration pack if required:

```bash
python scripts/generate_demo_pack.py
```

## Repository structure

```text
approvalguard/         model adapters and evidence pipeline
dataset/               labelled MP4 and ASVspoof example packs
evaluation/            local metrics and 570 per-file AASIST scores
models/                AASIST/Meso4 code and bundled checkpoints
scripts/               data preparation, evaluation, and validation
static/                browser interface
tests/                 API and pipeline tests
api.py                 local Flask application
API.md                 request schema and response example
DATASET_CARD.md        provenance, scope, and evaluation limitations
DATASET_OPTIONS.md     ranked datasets for broader evaluation
THIRD_PARTY_MODELS.md  model sources, hashes, and usage boundaries
```

## Technical boundaries

- The prototype detects media-integrity evidence; it does not establish identity or intent.
- AASIST was trained in an audio anti-spoofing domain and can shift under unseen speakers, codecs, noise, and generators.
- Meso4 uses a portable centre-region crop here; a production pipeline would require robust face detection and alignment.
- The demonstration videos are workflow fixtures outside the training domains of AASIST and Meso4.
- Scores are evidence scales, not calibrated probabilities.
- Deployment would require representative institutional data, independent validation, threshold calibration, monitoring, access controls, and human review.

See `THIRD_PARTY_MODELS.md` for model provenance and checkpoint hashes, and `API.md` for programmatic use.
