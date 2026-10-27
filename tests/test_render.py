from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from btm_pipeline.render import RenderError, render_documentary


def rights_ledger():
    base = {
        "kind": "original",
        "description": "Example production asset",
        "source_url": "https://example.org/asset",
        "captured_at": "2026-10-27",
        "rights_status": "reviewed",
        "license_family": "original",
        "license_name": "Original asset, contributor terms reviewed",
        "license_url": "https://example.org/rights",
        "proof_url": "https://example.org/proof",
        "intended_use": "Documentary video",
        "reviewed_by": "human-reviewer",
        "reviewed_at": "2026-10-27",
        "commercial_use_allowed": True,
        "modification_allowed": True,
        "attribution_required": False,
        "attribution_text": "",
        "creator": "Production team",
        "rights_reviewed": True,
        "restricted_or_unclear": False,
    }
    return {"assets": [{**base, "asset_id": "image-1"}, {**base, "asset_id": "voice-1"}]}


def test_render_blocks_missing_rights_evidence(tmp_path):
    image = tmp_path / "image.png"
    audio = tmp_path / "voice.wav"
    image.write_bytes(b"x")
    audio.write_bytes(b"x")
    ledger = rights_ledger()
    ledger["assets"][0]["proof_url"] = ""
    with pytest.raises(RenderError, match="rights ledger failed"):
        render_documentary({
            "segments": [{"image_path": str(image), "asset_id": "image-1", "duration_seconds": 10}],
            "narration_path": str(audio), "narration_asset_id": "voice-1",
        }, ledger, tmp_path / "out.mp4")


def test_render_blocks_untracked_asset(tmp_path):
    image = tmp_path / "image.png"
    audio = tmp_path / "voice.wav"
    image.write_bytes(b"x")
    audio.write_bytes(b"x")
    with pytest.raises(RenderError, match="not in the cleared rights ledger"):
        render_documentary({
            "segments": [{"image_path": str(image), "asset_id": "unknown", "duration_seconds": 10}],
            "narration_path": str(audio), "narration_asset_id": "voice-1",
        }, rights_ledger(), tmp_path / "out.mp4")


def test_render_blocks_existing_output_without_overwrite(tmp_path):
    image = tmp_path / "image.png"
    audio = tmp_path / "voice.wav"
    output = tmp_path / "out.mp4"
    image.write_bytes(b"x")
    audio.write_bytes(b"x")
    output.write_bytes(b"x")
    with pytest.raises(RenderError, match="output already exists"):
        render_documentary({
            "segments": [{"image_path": str(image), "asset_id": "image-1", "duration_seconds": 10}],
            "narration_path": str(audio), "narration_asset_id": "voice-1",
        }, rights_ledger(), output)


def test_render_command_is_local_and_qc_required(tmp_path):
    image = tmp_path / "image.png"
    audio = tmp_path / "voice.wav"
    image.write_bytes(b"x")
    audio.write_bytes(b"x")
    qc = {"passed": True, "duration_seconds": 600, "stream_types": ["audio", "video"], "blockers": []}
    with patch("btm_pipeline.render.shutil.which", return_value="/usr/bin/ffmpeg"), patch(
        "btm_pipeline.render.subprocess.run", return_value=CompletedProcess([], 0, "", "")
    ) as run, patch("btm_pipeline.render.inspect_media", return_value=qc):
        report = render_documentary({
            "segments": [{"image_path": str(image), "asset_id": "image-1", "duration_seconds": 10}],
            "narration_path": str(audio), "narration_asset_id": "voice-1",
        }, rights_ledger(), tmp_path / "out.mp4")
    assert report["rendered"] is True
    assert report["public_publish_allowed"] is False
    command = run.call_args.args[0]
    assert command[0] == "/usr/bin/ffmpeg"
    assert "https://" not in " ".join(command)
    assert "-filter_complex" in command


def test_render_requires_local_ffmpeg(tmp_path):
    image = tmp_path / "image.png"
    audio = tmp_path / "voice.wav"
    image.write_bytes(b"x")
    audio.write_bytes(b"x")
    with patch("btm_pipeline.render.shutil.which", return_value=None):
        with pytest.raises(RenderError, match="not found"):
            render_documentary({
                "segments": [{"image_path": str(image), "asset_id": "image-1", "duration_seconds": 10}],
                "narration_path": str(audio), "narration_asset_id": "voice-1",
            }, rights_ledger(), tmp_path / "out.mp4")
