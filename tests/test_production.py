from __future__ import annotations

import json
from pathlib import Path

import pytest

from btm_pipeline import production


def test_missing_required_fields_blocks_before_external_tools():
    with pytest.raises(production.ProductionError, match="missing required config fields"):
        production.run_production({})


def test_requires_explicit_narration_rights_before_synthesis(tmp_path, monkeypatch):
    script = tmp_path / "script.txt"
    script.write_text("Narration text", encoding="utf-8")
    voice = tmp_path / "voice.json"
    voice.write_text(json.dumps({"assets": []}), encoding="utf-8")
    ledger = tmp_path / "production.json"
    ledger.write_text(json.dumps({"assets": []}), encoding="utf-8")
    called = False

    def fake_tts(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("TTS must not run before narration rights are recorded")

    monkeypatch.setattr(production, "synthesize_with_piper", fake_tts)
    config = {
        "script_path": str(script),
        "piper_model_path": str(tmp_path / "voice.onnx"),
        "voice_asset_id": "voice",
        "voice_rights_ledger_path": str(voice),
        "production_rights_ledger_path": str(ledger),
        "narration_asset_id": "narration",
        "segments": [{"image_path": "unused", "asset_id": "image", "duration_seconds": 10}],
        "output_path": str(tmp_path / "out.mp4"),
        "report_path": str(tmp_path / "report.json"),
    }
    with pytest.raises(production.ProductionError, match="must explicitly document"):
        production.run_production(config)
    assert called is False


def test_failed_media_qc_means_pipeline_not_complete(tmp_path, monkeypatch):
    script = tmp_path / "script.txt"
    script.write_text("Narration text", encoding="utf-8")
    voice = tmp_path / "voice.json"
    voice.write_text(json.dumps({"assets": [{"asset_id": "voice"}]}), encoding="utf-8")
    ledger = tmp_path / "production.json"
    ledger.write_text(json.dumps({"assets": [
        {"asset_id": "voice", "kind": "original"},
        {"asset_id": "narration", "kind": "generated"},
    ]}), encoding="utf-8")
    output = tmp_path / "out.mp4"
    narration = tmp_path / "out.narration.wav"

    def fake_tts(*args, **kwargs):
        narration.write_bytes(b"wav")
        return {"synthesized": True}

    def fake_render(*args, **kwargs):
        output.write_bytes(b"video")
        return {"rendered": True}

    monkeypatch.setattr(production, "synthesize_with_piper", fake_tts)
    monkeypatch.setattr(production, "render_documentary", fake_render)
    monkeypatch.setattr(production, "inspect_media", lambda *a, **k: {
        "passed": False, "blockers": ["video stream is missing"]
    })
    report_path = tmp_path / "report.json"
    report = production.run_production({
        "script_path": str(script),
        "piper_model_path": str(tmp_path / "voice.onnx"),
        "voice_asset_id": "voice",
        "voice_rights_ledger_path": str(voice),
        "production_rights_ledger_path": str(ledger),
        "narration_asset_id": "narration",
        "segments": [{"image_path": "image.png", "asset_id": "image", "duration_seconds": 10}],
        "output_path": str(output),
        "report_path": str(report_path),
    })
    assert report["production_completed"] is False
    assert report["public_publish_allowed"] is False
    assert "video stream is missing" in report["blockers"]
    assert json.loads(report_path.read_text())["production_completed"] is False
