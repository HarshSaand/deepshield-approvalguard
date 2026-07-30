# ASVspoof 2021 DF direct-upload examples

This folder contains 24 labelled FLAC recordings selected deterministically from the ASVspoof 2021 Deepfake material already obtained locally:

- 12 `bonafide` recordings;
- 12 `spoof` recordings.

Use them through **Test a file** in ApprovalGuard. Audio-only uploads run the AASIST branch; the visual and audio–visual branches correctly report that no video is available.

`manifest.csv` preserves the official-style utterance identifier, class label, attack identifier, codec, source, speaker identifier and vocoder family available in the prepared source manifest.

These 24 files are convenient examples, not a statistically independent benchmark. The 570-file local measurement remains in `evaluation/asvspoof2021_df_aasist_results.json`.

Official source and licence information: https://www.asvspoof.org/index2021.html. The challenge page describes the released databases as Open Data Commons Attribution licensed. Retain attribution and this README when sharing the files.
