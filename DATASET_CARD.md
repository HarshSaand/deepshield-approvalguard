# Dataset card

## Included functional pack

The included `dataset/samples` pack is generated from a project-owned AI-created fictional portrait and local transformations. It contains no customer, celebrity, or real-person source recording. It exists so a reviewer can immediately upload media and see every product state. The controls are synthetic controls, not bona-fide recordings of people.

The pack must not be used to claim model accuracy. The transformations are deliberately visible and share a common generator, so results on it can overstate generalisation.

## Included ASVspoof example pack

`dataset/asvspoof_examples` contains 24 labelled FLAC clips curated from the locally obtained ASVspoof 2021 DF material: 12 bona-fide and 12 spoof. These are direct-upload examples for the AASIST branch, not the complete evaluation subset. The manifest preserves attack, codec, source, speaker and vocoder fields. The official ASVspoof page states that the released databases use the Open Data Commons Attribution licence.

The packaged example count is intentionally small. The locally measured result in `evaluation/` uses 570 balanced files and remains separate from the convenience examples.

## Recommended public evaluation sources

### FakeAVCeleb

Primary multimodal research source. It includes real/fake audio and real/fake video combinations, which is useful for testing face, voice, and cross-modal signals independently. Obtain it only through the official project instructions and retain its licence/readme alongside local data.

- Project: https://github.com/DASH-Lab/FakeAVCeleb
- Paper: https://arxiv.org/abs/2108.05080

### ASVspoof 2021 Deepfake

Useful for evaluating the audio-spoof component outside the small multimodal pack.

- Database: https://www.asvspoof.org/index2021.html
- Evaluation plan: https://www.asvspoof.org/asvspoof2021/asvspoof2021_evaluation_plan.pdf

### FaceForensics++

Useful for face-manipulation robustness. Access requires accepting the maintainers' terms; the project should not automate around that requirement.

- Project: https://github.com/ondyari/FaceForensics
- Paper: https://arxiv.org/abs/1901.08971

### Celeb-DF v2

Useful as a cross-dataset video test. Follow the official access and usage terms rather than redistributing files.

- Project: https://github.com/yuezunli/celeb-deepfakeforensics
- Paper: https://arxiv.org/abs/1909.12962

## Required experimental split

Use identity-disjoint train, validation, and test partitions. Fit thresholds and calibration only on validation data. Report per-source and cross-source results because a single pooled score can conceal generator-specific failure. Preserve the original dataset label, identity/group key, manipulation family, and licence provenance in the combined manifest.

## Suggested minimum reporting

- ROC-AUC, precision, recall, F1, balanced accuracy, and false-positive rate
- Equal error rate for the audio subsystem
- Results by manipulation family, compression, duration, and media quality
- Face-only, audio-only, sync-only, and multimodal ablation
- Calibration error and abstention coverage
- Latency on the actual deployment hardware
