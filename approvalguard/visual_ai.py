from __future__ import annotations

import math

import numpy as np
import torch


class Meso4(torch.nn.Module):
    """Compact face-forgery CNN matching the DeepfakeBench Meso4 checkpoint."""
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(3, 8, 3, padding=1, bias=False)
        self.bn1 = torch.nn.BatchNorm2d(8)
        self.conv2 = torch.nn.Conv2d(8, 8, 5, padding=2, bias=False)
        self.bn2 = torch.nn.BatchNorm2d(16)
        self.conv3 = torch.nn.Conv2d(8, 16, 5, padding=2, bias=False)
        self.conv4 = torch.nn.Conv2d(16, 16, 5, padding=2, bias=False)
        self.pool2 = torch.nn.MaxPool2d(2)
        self.pool4 = torch.nn.MaxPool2d(4)
        self.fc1 = torch.nn.Linear(16*8*8, 16)
        self.fc2 = torch.nn.Linear(16, 2)

    def forward(self, x):
        x = self.pool2(self.bn1(torch.relu(self.conv1(x))))
        x = self.pool2(self.bn1(torch.relu(self.conv2(x))))
        x = self.pool2(self.bn2(torch.relu(self.conv3(x))))
        x = self.pool4(self.bn2(torch.relu(self.conv4(x))))
        x = x.flatten(1)
        return self.fc2(torch.nn.functional.leaky_relu(self.fc1(x), 0.1))


class VisualContinuityEncoder:
    """Pretrained ResNet embeddings used for temporal anomaly evidence.

    This is deliberately not described as a deepfake classifier: ImageNet
    pretraining provides learned visual representations, while distance from
    the clip's own embedding trajectory identifies discontinuities.
    """

    def __init__(self, root=None):
        try:
            from torchvision.models import ResNet18_Weights, resnet18
        except ImportError as exc:
            raise RuntimeError("torchvision is required for visual AI evidence") from exc
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        weights = ResNet18_Weights.DEFAULT
        model = resnet18(weights=weights)
        model.fc = torch.nn.Identity()
        self.model = model.eval().to(self.device)
        self.preprocess = weights.transforms()
        if root is None:
            raise ValueError("Project root is required for the DeepfakeBench checkpoint")
        checkpoint = root / "models" / "weights" / "meso4_best.pth"
        self.forgery_model = Meso4().eval().to(self.device)
        state = torch.load(checkpoint, map_location=self.device, weights_only=True)
        state = {k.removeprefix("backbone."): v for k, v in state.items()}
        self.forgery_model.load_state_dict(state)

    @staticmethod
    def _face_region(frame: np.ndarray):
        # Portable MVP crop. A production adapter should replace this with
        # detected/aligned face boxes and abstain when no face is present.
        from PIL import Image
        h, w = frame.shape[:2]
        size = min(h, w)
        y0, x0 = (h-size)//2, (w-size)//2
        image = Image.fromarray(frame[y0:y0+size, x0:x0+size]).resize((256, 256))
        tensor = torch.from_numpy(np.asarray(image).copy()).permute(2, 0, 1).float() / 255.0
        return (tensor - 0.5) / 0.5

    def analyze(self, frames: list[np.ndarray], fps: float = 2.0) -> dict:
        if len(frames) < 3:
            return {"available": False, "reason": "At least 3 sampled video frames are required"}
        from PIL import Image
        batch = torch.stack([self.preprocess(Image.fromarray(x)) for x in frames]).to(self.device)
        with torch.inference_mode():
            embeddings = self.model(batch)
            embeddings = torch.nn.functional.normalize(embeddings, dim=1).cpu().numpy()
            face_batch = torch.stack([self._face_region(x) for x in frames]).to(self.device)
            fake_scores = torch.softmax(self.forgery_model(face_batch), dim=1)[:, 1].cpu().numpy() * 100.0
        deltas = 1.0 - np.sum(embeddings[1:] * embeddings[:-1], axis=1)
        median = float(np.median(deltas))
        mad = float(np.median(np.abs(deltas - median))) + 1e-6
        robust_z = np.maximum(0.0, (deltas - median) / (1.4826 * mad))
        anomaly = 100.0 * (1.0 - np.exp(-robust_z / 4.0))
        timeline = [{
            "start_s": round(i/fps, 2), "end_s": round((i+1)/fps, 2),
            "embedding_shift": round(float(deltas[i]), 4),
            "anomaly_score": round(float(anomaly[i]), 2),
            "face_forgery_score": round(float(fake_scores[i+1]), 2),
        } for i in range(len(anomaly))]
        top_n = max(1, math.ceil(len(fake_scores) / 3))
        score = float(np.sort(fake_scores)[-top_n:].mean())
        return {
            "available": True, "score": round(score, 2),
            "signal": "face-manipulation evidence",
            "model": "DeepfakeBench Meso4 (FF++ c23) + ResNet-18 continuity encoder",
            "calibrated_probability": False,
            "face_preprocessing": "portable center face-region crop; detector/alignment is a production integration requirement",
            "interpretation": "Meso4 is deepfake-specific; generalisation beyond its training domain is not guaranteed.",
            "sampled_frames": len(frames), "timeline": timeline,
            "continuity_anomaly_top": round(float(np.max(anomaly)), 2),
        }


def frame_quality(frames: list[np.ndarray]) -> dict:
    if not frames:
        return {"sufficient": False, "reason": "No video frames decoded"}
    grayscale = [f.astype(np.float32).mean(axis=2) for f in frames]
    brightness = float(np.mean([g.mean() for g in grayscale]))
    sharpness = float(np.mean([
        np.var(g[:, 1:] - g[:, :-1]) + np.var(g[1:, :] - g[:-1, :]) for g in grayscale
    ]))
    sufficient = 22 <= brightness <= 235 and sharpness >= 18 and len(frames) >= 3
    return {"sufficient": sufficient, "brightness": round(brightness, 2),
            "sharpness": round(sharpness, 2), "sampled_frames": len(frames)}
