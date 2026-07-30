# DeepShield ApprovalGuard

ApprovalGuard is a local prototype that reviews video or audio instructions before a sensitive financial action. It separates four forms of evidence:

- face-manipulation evidence from DeepfakeBench Meso4;
- synthetic-voice evidence from AASIST;
- learned recording-continuity evidence from ResNet-18 embeddings;
- audio/video timing evidence from mouth-motion and audio activity.

It then suggests `STANDARD`, `REVIEW`, `ESCALATE`, or `INSUFFICIENT EVIDENCE`. This is decision support. It does not identify a person, prove fraud, or approve a transaction.

## What you can try immediately

The folder contains 24 five-second MP4 files in `dataset/samples`:

- 6 synthetic controls;
- 6 audio-replacement cases;
- 6 visible identity-region tampering cases;
- 6 audio/video desynchronisation cases.

Open `dataset/manifest.csv` to see the label, transformation, affected interval, and provenance for every file. These are functional demonstration files, not a scientific accuracy benchmark.

It also includes `dataset/asvspoof_examples`: **24 labelled ASVspoof 2021 DF audio clips**—12 bona-fide and 12 spoof—for direct upload testing. See that folder’s README and manifest for attribution and labels.

## Before you start

You need:

1. A Windows or macOS computer with at least 8 GB RAM.
2. Python 3.11 or 3.12. Python 3.13+ is not recommended for this package set.
3. FFmpeg.
4. An internet connection for the first installation. Model checkpoints used by ApprovalGuard are already included; torchvision may download its official ResNet-18 weights once.

### Install Python

Download Python 3.12 from [python.org](https://www.python.org/downloads/). On Windows, tick **Add Python to PATH** during installation.

Check the installation:

macOS:

```bash
python3.12 --version
```

Windows PowerShell:

```powershell
py -3.12 --version
```

### Install FFmpeg

macOS with Homebrew:

```bash
brew install ffmpeg
```

If `brew` is not available, install it from [brew.sh](https://brew.sh/) and rerun the command.

Windows PowerShell with Winget:

```powershell
winget install --id Gyan.FFmpeg --source winget
```

Close and reopen the terminal, then check:

```bash
ffmpeg -version
```

## Run on macOS

Open Terminal, clone the repository, and move into the project:

```bash
git clone https://github.com/HarshSaand/deepshield-approvalguard.git
cd deepshield-approvalguard
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python api.py
```

Wait until the terminal shows an address, then open:

[http://127.0.0.1:8091](http://127.0.0.1:8091)

Keep the terminal open while using the website. Stop the program with `Control + C`.

## Run on Windows

Open PowerShell in the project folder. A simple method is to open the folder in File Explorer, click the address bar, type `powershell`, and press Enter.

```powershell
git clone https://github.com/HarshSaand/deepshield-approvalguard.git
cd deepshield-approvalguard
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python api.py
```

If PowerShell blocks activation, run this once in the same window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open [http://127.0.0.1:8091](http://127.0.0.1:8091). Stop the program with `Control + C`.

## Use the website

### Guided demonstration

1. Start with **Supplier payment**.
2. Press play to see the visible identity-region splice between roughly 1.6 and 3.1 seconds.
3. Compare the four evidence cards. They are kept separate because they answer different questions.
4. Click a timeline section to jump to that point in the recording.
5. Try **Treasury release**, **Limit increase**, and the **synthetic control**.
6. Download the JSON evidence record if you want to inspect the model names, timestamps, file hash, quality fields, and review suggestion.

### Test your own file

1. Select **Test a file**.
2. Choose an MP4, MOV, WebM, MKV, AVI, WAV, FLAC, MP3, or M4A file.
3. Click **Analyse locally**.
4. Wait for the results. A short video normally takes a few seconds after the models have loaded.

The prototype processes uploads in a temporary local file and deletes that temporary copy after analysis.

## Dataset and measurements

`dataset/` contains the directly playable 24-file video pack and a 24-file ASVspoof audio example pack. `DATASET_OPTIONS.md` ranks additional sources including PartialSpoof, In-the-Wild Audio, AV-Deepfake1M, FakeAVCeleb, FaceForensics++, Celeb-DF v2, DF40 and LlamaPartialSpoof.

The included AASIST result was measured locally on a balanced 570-file ASVspoof 2021 DF subset:

- ROC-AUC: 0.9078;
- equal error rate: 18.60%;
- accuracy at the subset-selected EER threshold: 81.40%;
- spoof precision: 81.40%;
- spoof recall: 81.40%;
- 17.44 ms mean model time per audio file on Apple MPS.

That threshold was selected and measured on the same showcase subset. Treat it as a transparent prototype measurement, not an independent production estimate. The exact JSON and 570 per-file scores are in `evaluation/`.

## Recreate and validate the included media

With the virtual environment active:

```bash
python scripts/generate_demo_pack.py
python scripts/validate_demo_pack.py
```

The validation checks that all 24 files exist, decode correctly, contain audio and video, and are five seconds long.

## Run automated tests

```bash
python -m pytest -q
```

## Common problems

### `python` or `py` is not recognised

Install Python 3.12, reopen the terminal, and repeat the version check above.

### `ffmpeg` is not recognised

Install FFmpeg, close and reopen the terminal, and run `ffmpeg -version`.

### The first run appears slow

PyTorch is loading three model branches and may download the official ResNet-18 ImageNet weights once. Later analyses are faster.

### The browser says the page cannot be reached

The terminal running `python api.py` must remain open. Use port 8091, not 8080 or 8090.

### A model score looks wrong on a demo clip

The included clips are synthetic workflow fixtures and are outside the training domains of AASIST and Meso4. Inspect the known label and timeline, but do not treat fixture behaviour as model accuracy. Use the benchmark preparation guidance in `DATASET_CARD.md` for a formal study.

## Folder guide

```text
approvalguard/       AI and media-processing pipeline
dataset/             24 playable MP4s plus 24 labelled ASVspoof audio examples
evaluation/          local measurements and per-file scores
models/              AASIST and Meso4 code/checkpoints
scripts/             dataset preparation and evaluation utilities
static/              local web interface
tests/               automated checks
api.py               starts the application
API.md               API schema and request examples
DATASET_CARD.md      dataset scope, provenance and limitations
DATASET_OPTIONS.md   ranked options for broader evaluation
THIRD_PARTY_MODELS.md model sources, hashes and usage boundaries
```

For model sources, licences, checkpoint hashes, and boundaries, read `THIRD_PARTY_MODELS.md`.
