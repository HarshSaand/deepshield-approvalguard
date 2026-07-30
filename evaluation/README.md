# Evaluation outputs

`demo_pack_validation.json` checks that the 24 functional MP4 files exist, decode, contain audio and video, and have the expected duration. It is media QA, not detector evaluation.

`asvspoof2021_df_aasist_results.json` and its 570-row score CSV contain the actual local AASIST measurement used in the report. The balanced subset uses seed 6127 with 285 bona-fide and 285 spoof files. Its operating threshold was selected and measured on the same showcase subset, so the result is reproducible prototype evidence rather than an independent production estimate.

For a visual or full multimodal accuracy study, prepare a licence-compliant held-out dataset through `scripts/prepare_public_datasets.py`, select thresholds on validation identities, and keep test identities separate.
