# Third-party model provenance

## AASIST

- Architecture and checkpoint source: `clovaai/aasist`
- Architecture: Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks
- Training domain: ASVspoof 2019 Logical Access
- Upstream code licence: MIT
- Bundled checkpoint SHA-256: `51d2d9cf0738172f61e2a384ec50a54a55363240f67c971ed55a92435bc1a1c0`
- Local adapter output: synthetic-voice evidence, not a calibrated probability.

## ResNet-18

- Source: torchvision official model weights
- Pretraining: ImageNet-1K V1
- Purpose here: learned frame embeddings for within-clip continuity anomaly evidence.
- It is **not** represented as a deepfake-specific classifier.
- Weights are downloaded to the local PyTorch cache on first use.

## Meso4

- Source: DeepfakeBench release v1.0.1 `meso4_best.pth`.
- Training configuration: FaceForensics++ c23, Meso4 compact CNN, 256 px inputs.
- Purpose: primary frame-level face-manipulation evidence.
- Checkpoint SHA-256: `a362ebbef2658daa551d808fbfccd57f0b5fd34fda46a05996e807cccddff4e0`.
- Boundary: the portable MVP uses a centre face-region crop. Detected and aligned
  faces are required before treating this as a production-style detector.

The audio/visual activity correlation is a transparent signal-processing module,
not a trained lip-reading model. Each modality remains separate in the API.
