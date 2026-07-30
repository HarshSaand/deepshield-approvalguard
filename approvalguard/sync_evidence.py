from __future__ import annotations

import numpy as np
from PIL import Image


def _resample(values: np.ndarray, size: int) -> np.ndarray:
    if len(values) == size:
        return values
    if len(values) < 2:
        return np.zeros(size, dtype=np.float32)
    return np.interp(np.linspace(0, len(values)-1, size), np.arange(len(values)), values)


def lip_sync_evidence(frames: list[np.ndarray], audio: np.ndarray, rate: int, fps: float = 2.0) -> dict:
    """Transparent audio/visual activity correlation, not a trained lip-reading model."""
    if len(frames) < 5 or len(audio) < rate:
        return {"available": False, "reason": "Need at least 5 frames and 1 second of audio"}
    mouth = []
    for frame in frames:
        h, w = frame.shape[:2]
        roi = frame[int(h*.55):int(h*.90), int(w*.25):int(w*.75)].astype(np.float32).mean(axis=2)
        roi = np.asarray(Image.fromarray(roi.astype(np.uint8)).resize((64, 32)), dtype=np.float32)
        mouth.append(roi)
    visual = np.array([np.mean(np.abs(mouth[i]-mouth[i-1])) for i in range(1, len(mouth))])
    hop = max(1, int(rate/fps))
    energy = np.array([np.sqrt(np.mean(audio[i:i+hop]**2)+1e-9) for i in range(0, len(audio)-hop+1, hop)])
    energy = _resample(energy, len(visual))
    if np.std(visual) < 1e-5 or np.std(energy) < 1e-6:
        return {"available": False, "reason": "Insufficient visual or audio activity"}
    correlations = []
    for lag in range(-2, 3):
        if lag < 0:
            a, v = energy[-lag:], visual[:lag]
        elif lag > 0:
            a, v = energy[:-lag], visual[lag:]
        else:
            a, v = energy, visual
        correlations.append((lag, float(np.corrcoef(a, v)[0, 1])))
    lag, corr = max(correlations, key=lambda x: x[1])
    # Evidence score rises for negative correlation and for a large optimal lag.
    score = np.clip((0.45-corr)*75 + abs(lag)*10, 0, 100)
    return {
        "available": True, "score": round(float(score), 2),
        "signal": "audio/visual activity mismatch", "best_correlation": round(corr, 3),
        "best_lag_s": round(lag/fps, 2), "method": "mouth-region motion vs audio RMS correlation",
        "trained_model": False,
        "interpretation": "Supportive continuity evidence only; not identity or phoneme-level lip reading.",
    }
