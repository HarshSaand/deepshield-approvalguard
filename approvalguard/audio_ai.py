from __future__ import annotations

import hashlib
import importlib.util
import math
from pathlib import Path
from threading import Lock

import numpy as np
import torch

CONFIG = {
    "architecture": "AASIST", "nb_samp": 64600, "first_conv": 128,
    "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
    "gat_dims": [64, 32], "pool_ratios": [0.5, 0.7, 0.5, 0.5],
    "temperatures": [2.0, 2.0, 100.0, 100.0],
}
EXPECTED_SHA256 = "51d2d9cf0738172f61e2a384ec50a54a55363240f67c971ed55a92435bc1a1c0"


class AASISTVoiceEvidence:
    def __init__(self, root: Path):
        weights = root / "models" / "weights" / "AASIST.pth"
        source = root / "models" / "aasist_official.py"
        digest = hashlib.sha256(weights.read_bytes()).hexdigest()
        if digest != EXPECTED_SHA256:
            raise RuntimeError(f"AASIST checkpoint checksum mismatch: {digest}")
        spec = importlib.util.spec_from_file_location("approvalguard_aasist", source)
        if not spec or not spec.loader:
            raise RuntimeError("Could not load AASIST architecture")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model = module.Model(CONFIG).to(self.device)
        self.model.load_state_dict(torch.load(weights, map_location=self.device, weights_only=True))
        self.model.eval()

    @staticmethod
    def _windows(samples: np.ndarray) -> tuple[torch.Tensor, list[int]]:
        waveform = torch.as_tensor(samples, dtype=torch.float32)
        size = CONFIG["nb_samp"]
        if waveform.numel() < size:
            repeats = size // max(1, waveform.numel()) + 1
            return waveform.repeat(repeats)[:size].unsqueeze(0), [0]
        count = min(9, max(1, math.ceil(waveform.numel() / size)))
        last = waveform.numel() - size
        starts = [0] if count == 1 else sorted({round(i * last / (count - 1)) for i in range(count)})
        return torch.stack([waveform[s:s + size] for s in starts]), starts

    def analyze(self, samples: np.ndarray, rate: int = 16000) -> dict:
        if rate != 16000:
            raise ValueError("AASIST adapter expects normalized 16 kHz audio")
        windows, starts = self._windows(samples)
        with torch.inference_mode():
            _, logits = self.model(windows.to(self.device), Freq_aug=False)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
        spoof = probs[:, 0]
        top_n = max(1, math.ceil(len(spoof) / 3))
        score = float(np.sort(spoof)[-top_n:].mean() * 100)
        duration = len(samples) / rate
        segments = []
        for i, (start, p) in enumerate(zip(starts, spoof)):
            p = float(np.clip(p, 1e-7, 1 - 1e-7))
            entropy = -(p * math.log2(p) + (1-p) * math.log2(1-p)) * 100
            segments.append({
                "index": i + 1, "start_s": round(start/rate, 2),
                "end_s": round(min(duration, start/rate + CONFIG["nb_samp"]/rate), 2),
                "spoof_score": round(p*100, 2), "uncertainty_entropy": round(entropy, 2),
            })
        return {
            "available": True, "score": round(score, 2), "signal": "synthetic-voice evidence",
            "model": "AASIST", "training_domain": "ASVspoof 2019 Logical Access",
            "device": str(self.device), "calibrated_probability": False,
            "aggregation": "mean of highest-scoring third of temporal windows",
            "segments": segments,
        }


_lock = Lock()
_instance = None


def get_voice_model(root: Path):
    global _instance
    with _lock:
        if _instance is None:
            _instance = AASISTVoiceEvidence(root)
    return _instance
