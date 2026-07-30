# Additional dataset options for ApprovalGuard

This shortlist is organised by what each source would test in the implemented prototype. Dataset size alone is not the selection criterion; labels, access terms and relevance to temporal financial-approval media matter more.

## Recommended order

### 1. PartialSpoof v1.2 — best immediate technical extension

**Use for:** injected fake words or short synthetic sections inside otherwise bona-fide speech.

Why it fits: ApprovalGuard already returns temporal AASIST evidence. PartialSpoof provides utterance labels plus fine-grained segment/timestamp labels, so it can test whether the timeline actually localises a short attack rather than only classifying the whole file.

- Official record: https://zenodo.org/records/5766198
- Approximate full download: 10 GB
- Access: direct Zenodo download
- Practical first step: download protocols and timestamp labels before the multi-gigabyte audio archives.

### 2. In-the-Wild Audio Deepfake — best robustness check

**Use for:** realistic compression, social-platform audio and generators outside ASVspoof’s laboratory setup.

The Fraunhofer AISEC release contains roughly 20.8 hours of bona-fide and 17.2 hours of spoofed audio across 58 public figures. It is intended specifically to test detector generalisation and is documented under Apache 2.0.

- Official page: https://deepfake-demo.aisec.fraunhofer.de/in_the_wild
- Dataset link: available from the official page
- Access: Hugging Face download
- Caution: public-figure speech is not banking speech, and identity leakage must be controlled.

### 3. AV-Deepfake1M / AV-Deepfake1M++ — strongest multimodal target

**Use for:** audio-only, visual-only and combined manipulations with temporal localisation.

The official metadata distinguishes `real`, `visual_modified`, `audio_modified` and `both_modified`, and includes audio and visual fake-segment timestamps. This is the closest research match to ApprovalGuard’s multimodal evidence timeline.

- Official repository: https://github.com/ControlNet/AV-Deepfake1M
- Scale: more than one million videos; the newer 1M++ release exceeds two million
- Access: signed EULA/challenge process
- Practicality: use a documented validation subset rather than trying to package the full corpus with the prototype.

### 4. FakeAVCeleb — clearest four-way multimodal ablation

**Use for:** comparing real audio/real video, fake audio/real video, real audio/fake video and fake audio/fake video.

- Official repository: https://github.com/DASH-Lab/FakeAVCeleb
- Scale: the official repository describes 20,000 videos
- Access: request form and supplied download script
- Caution: public celebrity media is outside a banking domain.

### 5. FaceForensics++ — model-family validation

**Use for:** checking Meso4 on its relevant face-manipulation/compression family.

- Official repository: https://github.com/ondyari/FaceForensics
- Composition: 1,000 original sequences manipulated by Deepfakes, Face2Face, FaceSwap and NeuralTextures
- Access: request form and terms of use
- Value: provides the most defensible first visual benchmark for the current Meso4 branch.

### 6. Celeb-DF v2 — cross-dataset video robustness

**Use for:** measuring how a visual detector behaves on a different, higher-quality generation pipeline.

- Official repository: https://github.com/yuezunli/celeb-deepfakeforensics
- Access: follow the maintainers’ download and usage terms
- Value: should be a held-out test, not another source mixed into threshold selection.

### 7. DF40 — generator diversity

**Use for:** testing newer visual manipulation and full-image synthesis families.

- Official repository: https://github.com/YZY-stack/DF40
- Composition: 40 generation/manipulation techniques
- Value: useful after the basic FaceForensics++ evaluation is reproducible.

### 8. LlamaPartialSpoof — newer partial voice attacks

**Use for:** LLM-planned sentence manipulation and multiple TTS systems.

- Dataset card: https://huggingface.co/datasets/HaoY0001/LlamaPartialSpoof
- Licence shown by the dataset card: CC BY 4.0
- Value: useful as an external partial-spoof challenge after PartialSpoof.

## What is already packaged

ApprovalGuard includes two different example layers:

1. `dataset/samples`: 24 project-owned MP4 workflow demonstrations. These show product states and known transformations, not accuracy.
2. `dataset/asvspoof_examples`: 24 labelled FLAC clips drawn from the locally obtained ASVspoof 2021 DF material—12 bona-fide and 12 spoof—for direct upload testing. Their manifest preserves attack, codec, source and vocoder metadata.

Formal evaluation results must remain separate from example packs. Thresholds should be selected on validation identities and reported on held-out identities or datasets.
