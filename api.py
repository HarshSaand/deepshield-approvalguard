from __future__ import annotations

import json
import os
import tempfile
import csv
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from approvalguard import ApprovalGuardPipeline

ROOT = Path(__file__).resolve().parent
ALLOWED = {".wav", ".flac", ".mp3", ".m4a", ".mp4", ".mov", ".webm", ".mkv", ".avi"}
MAX_BYTES = 250 * 1024 * 1024

DEMO_CASES = {
    "video_tampered_01": {"title": "Supplier payment approval", "subtitle": "Synthetic face-region splice", "workflow": "Supplier payment", "amount": "SGD 184,000"},
    "audio_replaced_01": {"title": "Treasury release", "subtitle": "Audio track replaced", "workflow": "Treasury release", "amount": "SGD 420,000"},
    "av_desync_01": {"title": "Limit increase", "subtitle": "Audio and video shifted", "workflow": "Limit increase", "amount": "SGD 75,000"},
    "clean_sync_01": {"title": "Account recovery approval", "subtitle": "Synthetic control recording", "workflow": "Account recovery", "amount": "Not applicable"},
}


def demo_rows() -> list[dict]:
    with (ROOT / "dataset" / "manifest.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["sample_id"]: row for row in csv.DictReader(handle)}
    result = []
    for sample_id, context in DEMO_CASES.items():
        row = rows[sample_id]
        result.append({**context, **row, "media_url": f"/data/{row['filename']}"})
    return result


def create_app(pipeline=None) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES
    engine = pipeline or ApprovalGuardPipeline(ROOT)

    @app.get("/")
    def home():
        return send_from_directory(ROOT / "static", "index.html")

    @app.get("/<path:asset>")
    def static_asset(asset):
        if asset not in {"app.js", "style.css"}:
            return jsonify({"error": "Not found"}), 404
        return send_from_directory(ROOT / "static", asset)

    @app.get("/data/<path:filename>")
    def demo_media(filename):
        return send_from_directory(ROOT / "dataset", filename)

    @app.get("/api/scenarios")
    def scenarios():
        return jsonify(demo_rows())

    @app.post("/api/scenarios/<sample_id>/analyze")
    def analyze_scenario(sample_id):
        match = next((item for item in demo_rows() if item["sample_id"] == sample_id), None)
        if not match:
            return jsonify({"error": "Unknown demo scenario"}), 404
        media_path = ROOT / "dataset" / match["filename"]
        context = {key: match[key] for key in ("workflow", "amount", "title")}
        result = engine.analyze(media_path, context)
        result["scenario"] = match
        return jsonify(result)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "DeepShield ApprovalGuard", "schema_version": "1.0"})

    @app.post("/api/analyze")
    def analyze():
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            return jsonify({"error": "multipart field 'file' is required"}), 400
        suffix = Path(uploaded.filename).suffix.lower()
        if suffix not in ALLOWED:
            return jsonify({"error": f"Unsupported extension. Allowed: {sorted(ALLOWED)}"}), 415
        context_raw = request.form.get("context", "{}")
        try:
            context = json.loads(context_raw)
            if not isinstance(context, dict):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            return jsonify({"error": "context must be a JSON object"}), 400
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(prefix="approvalguard_upload_", suffix=suffix, delete=False) as tmp:
                uploaded.save(tmp)
                temp_name = tmp.name
            result = engine.analyze(Path(temp_name), context)
            result["original_filename"] = Path(uploaded.filename).name
            return jsonify(result)
        except (ValueError, RuntimeError) as exc:
            return jsonify({"error": str(exc)}), 422
        finally:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)

    @app.errorhandler(413)
    def too_large(_):
        return jsonify({"error": "File exceeds 250 MB limit"}), 413

    return app


if __name__ == "__main__":
    port = int(os.environ.get("APPROVALGUARD_PORT", "8091"))
    create_app().run(host="127.0.0.1", port=port, debug=False)
