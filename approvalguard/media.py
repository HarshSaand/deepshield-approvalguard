from __future__ import annotations

import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image


class MediaError(RuntimeError):
    pass


def _run(args: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise MediaError(detail.strip()) from exc


def require_ffmpeg() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise MediaError("FFmpeg and ffprobe are required and were not found on PATH")


def probe(path: Path) -> dict:
    require_ffmpeg()
    out = _run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ])
    raw = json.loads(out.stdout)
    streams = raw.get("streams", [])
    duration = float(raw.get("format", {}).get("duration") or 0.0)
    return {
        "duration_s": round(duration, 3),
        "has_audio": any(s.get("codec_type") == "audio" for s in streams),
        "has_video": any(s.get("codec_type") == "video" for s in streams),
        "streams": streams,
    }


def extract_audio(path: Path, target: Path) -> tuple[np.ndarray, int]:
    _run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", str(target)])
    with wave.open(str(target), "rb") as wav:
        rate = wav.getframerate()
        width = wav.getsampwidth()
        data = wav.readframes(wav.getnframes())
    if width != 2:
        raise MediaError("Expected 16-bit PCM after audio normalization")
    samples = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0
    return samples, rate


def extract_frames(path: Path, directory: Path, fps: float = 2.0, limit: int = 32) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    pattern = directory / "frame_%04d.jpg"
    _run([
        "ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf",
        f"fps={fps},scale='min(640,iw)':-2", "-frames:v", str(limit),
        "-q:v", "3", str(pattern),
    ])
    return sorted(directory.glob("frame_*.jpg"))


def load_rgb(paths: list[Path]) -> list[np.ndarray]:
    return [np.asarray(Image.open(p).convert("RGB"), dtype=np.uint8) for p in paths]
