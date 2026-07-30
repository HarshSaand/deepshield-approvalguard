from __future__ import annotations

import hashlib
import tempfile
import time
from pathlib import Path

import numpy as np

from .audio_ai import get_voice_model
from .media import extract_audio, extract_frames, load_rgb, probe
from .sync_evidence import lip_sync_evidence
from .visual_ai import VisualContinuityEncoder, frame_quality


class ApprovalGuardPipeline:
    def __init__(self, root: Path, enable_visual_ai: bool = True):
        self.root = Path(root)
        self.voice = get_voice_model(self.root)
        self.visual = VisualContinuityEncoder(self.root) if enable_visual_ai else None

    @staticmethod
    def _decision(signals: dict, quality: dict) -> dict:
        usable = {k: v["score"] for k, v in signals.items() if v.get("available")}
        if not usable:
            return {"level": "INSUFFICIENT EVIDENCE", "action": "Use another verification channel", "reasons": []}
        reasons = [f"{k.replace('_',' ')} {v:.1f}/100" for k, v in usable.items() if v >= 60]
        high = sum(v >= 65 for v in usable.values())
        elevated = sum(v >= 50 for v in usable.values())
        if not quality.get("audio_sufficient", True) and not quality.get("video", {}).get("sufficient", True):
            level, action = "INSUFFICIENT EVIDENCE", "Request a clearer approval recording"
        elif high >= 2:
            level, action = "ESCALATE", "Hold approval and verify through a trusted channel"
        elif high == 1 or elevated >= 2:
            level, action = "REVIEW", "Require independent reviewer verification"
        else:
            level, action = "STANDARD", "Continue normal approval controls"
        # Routing index is intentionally not presented as a fraud probability.
        priority = float(np.mean(sorted(usable.values(), reverse=True)[:2]))
        return {"level": level, "action": action, "priority_index": round(priority, 2),
                "priority_is_probability": False, "reasons": reasons}

    def analyze(self, path: Path, case_context: dict | None = None) -> dict:
        started = time.perf_counter()
        meta = probe(path)
        if not meta["has_audio"]:
            raise ValueError("ApprovalGuard requires an audio stream")
        signals, quality = {}, {}
        with tempfile.TemporaryDirectory(prefix="approvalguard_") as tmp:
            work = Path(tmp)
            audio, rate = extract_audio(path, work / "audio.wav")
            rms = float(np.sqrt(np.mean(audio**2)+1e-12))
            quality["audio_sufficient"] = len(audio) >= rate and rms >= 0.002
            signals["voice_ai"] = self.voice.analyze(audio, rate)
            frames = []
            if meta["has_video"]:
                sample_fps = 5.0
                frame_paths = extract_frames(path, work / "frames", fps=sample_fps)
                frames = load_rgb(frame_paths)
                quality["video"] = frame_quality(frames)
                if self.visual:
                    signals["visual_ai"] = self.visual.analyze(frames, fps=sample_fps)
                signals["lip_sync"] = lip_sync_evidence(frames, audio, rate, fps=sample_fps)
            else:
                quality["video"] = {"sufficient": False, "reason": "No video stream"}
                signals["visual_ai"] = {"available": False, "reason": "No video stream"}
                signals["lip_sync"] = {"available": False, "reason": "No video stream"}
        decision = self._decision(signals, quality)
        return {
            "schema_version": "1.0", "case_context": case_context or {},
            "media": {k: v for k, v in meta.items() if k != "streams"},
            "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "quality": quality, "signals": signals, "review": decision,
            "processing_ms": round((time.perf_counter()-started)*1000, 1),
            "disclaimer": "Evidence-support prototype. Outputs are not identity, fraud, or transaction-approval decisions.",
        }
