#!/usr/bin/env python3
"""Generate a deterministic, legally safe functional AV demo pack.

The media is intentionally procedural. It is not a deepfake benchmark.
"""
from __future__ import annotations

import csv
import math
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "samples"
MANIFEST = ROOT / "dataset" / "manifest.csv"
FPS, DURATION, WIDTH, HEIGHT, RATE = 15, 5.0, 480, 270, 16000
GENERATOR = "approvalguard-synthetic-identity-v2"
PORTRAIT = ROOT / "dataset" / "assets" / "synthetic_identity.png"


def envelope(t: float, seed: int) -> float:
    syllable = max(0.0, math.sin((2.3 + seed * 0.07) * math.pi * t + seed))
    phrase = 0.35 + 0.65 * max(0.0, math.sin(math.pi * (t + 0.15) / DURATION))
    return syllable * phrase


def write_audio(path: Path, seed: int, shift: float = 0.0, replacement: bool = False) -> None:
    frames = bytearray()
    for n in range(int(RATE * DURATION)):
        t = n / RATE
        source_t = (t - shift) % DURATION
        env_seed = seed + 31 if replacement else seed
        amp = envelope(source_t, env_seed)
        f = 145 + seed * 7
        signal = amp * (0.70 * math.sin(2 * math.pi * f * t) + 0.22 * math.sin(4 * math.pi * f * t))
        frames.extend(struct.pack("<h", int(max(-1, min(1, signal)) * 18000)))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(RATE); wav.writeframes(frames)


def frame_bytes(frame: int, seed: int, condition: str) -> bytes:
    t = frame / FPS
    if not PORTRAIT.exists():
        raise FileNotFoundError(f"Missing generated synthetic identity asset: {PORTRAIT}")
    base = Image.open(PORTRAIT).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    # Small deterministic capture variations create six sessions without claiming
    # six identities. The source portrait is fully synthetic and project-owned.
    base = ImageEnhance.Brightness(base).enhance(0.94 + seed * 0.015)
    base = ImageEnhance.Color(base).enhance(0.92 + seed * 0.025)
    draw = ImageDraw.Draw(base, "RGBA")
    mouth_open = 1 + int(3 * envelope(t, seed))
    draw.ellipse((234, 153-mouth_open, 253, 155+mouth_open), fill=(68, 30, 32, 95))
    draw.line((235, 153, 252, 154), fill=(177, 104, 105, 105), width=1)
    if condition == "video_tampered" and 1.6 <= t <= 3.1:
        patch = base.crop((180, 55, 300, 190)).filter(ImageFilter.GaussianBlur(3))
        shifted = ImageEnhance.Color(patch).enhance(2.4)
        base.paste(shifted, (190 + (frame % 4), 58))
        tamper = ImageDraw.Draw(base, "RGBA")
        tamper.rectangle((188, 56, 312, 194), outline=(188, 55, 220, 145), width=3)
    return base.tobytes()


def make_video(sample_id: str, seed: int, condition: str, shift: float) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="approvalguard_") as tmp_name:
        tmp = Path(tmp_name); raw = tmp / "frames.rgb"; wav = tmp / "audio.wav"
        with raw.open("wb") as fh:
            for frame in range(int(FPS * DURATION)):
                fh.write(frame_bytes(frame, seed, condition))
        write_audio(wav, seed, shift=shift, replacement=condition == "audio_replaced")
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", str(raw),
               "-i", str(wav), "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", str(OUT / f"{sample_id}.mp4")]
        subprocess.run(cmd, check=True)


def main() -> None:
    if not shutil.which("ffmpeg"):
        raise SystemExit("FFmpeg is required. Install it and rerun this script.")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    conditions = ["clean_sync", "audio_replaced", "video_tampered", "av_desync"]
    for condition in conditions:
        for idx in range(1, 7):
            sample_id = f"{condition}_{idx:02d}"
            shift = round(0.55 + idx * 0.11, 2) if condition == "av_desync" else 0.0
            make_video(sample_id, idx, condition, shift)
            rows.append({
                "sample_id": sample_id, "filename": f"samples/{sample_id}.mp4",
                "integrity_label": "control" if condition == "clean_sync" else "manipulated",
                "target": 0 if condition == "clean_sync" else 1,
                "manipulation_type": condition, "affected_interval_s": "none" if condition == "clean_sync" else ("1.6-3.1" if condition == "video_tampered" else "0.0-5.0"),
                "av_shift_s": shift, "duration_s": DURATION, "provenance": "project-owned AI-generated fictional identity; locally animated and transformed; no real source person or recording",
                "generator": GENERATOR, "benchmark_eligible": "no"
            })
    fields = list(rows[0])
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    print(f"Generated {len(rows)} samples in {OUT}")


if __name__ == "__main__":
    main()
