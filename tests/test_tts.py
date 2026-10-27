from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from btm_pipeline.tts import TTSError, synthesize_with_piper


def ledger():
    return {"assets": [{
        "asset_id": "voice-model",
        "kind": "generated",
        "description": "Local Piper voice model",
        "source_url": "https://example.org/model",
        "captured_at": "2026-10-27",
        "rights_status": "reviewed",
        "license_family": "cc_by",
        "license_name": "Example voice model license",
        "license_url": "https://example.org/license",
        "proof_url": "https://example.org/proof",
        "intended_use": "Generate narration for an edited documentary",
        "reviewed_by": "human-reviewer",
        "reviewed_at": "2026-10-27",
        "commercial_use_allowed": True,
        "modification_allowed": True,
        "attribution_required": False,
        "attribution_text": "",
        "generator": "Piper",
        "terms_checked_at": "2026-10-27",
        "rights_reviewed": True,
        "restricted_or_unclear": False,
    }]}


def test_tts_blocks_missing_model(tmp_path):
    with pytest.raises(TTSError, match="does not exist locally"):
        synthesize_with_piper("Hello world", tmp_path / "missing.onnx", "voice-model", ledger(), tmp_path / "voice.wav")


def test_tts_blocks_uncleared_voice(tmp_path):
    model = tmp_path / "voice.onnx"
    model.write_bytes(b"model")
    with pytest.raises(TTSError, match="not in the cleared rights ledger"):
        synthesize_with_piper("Hello world", model, "unknown", ledger(), tmp_path / "voice.wav")


def test_tts_synthesizes_locally_and_requires_output(tmp_path):
    model = tmp_path / "voice.onnx"
    model.write_bytes(b"model")
    output = tmp_path / "voice.wav"

    def fake_run(command, **kwargs):
        output.write_bytes(b"fake wav")
        return CompletedProcess(command, 0, "", "")

    with patch("btm_pipeline.tts.shutil.which", return_value="/usr/bin/piper"), patch(
        "btm_pipeline.tts.subprocess.run", side_effect=fake_run
    ) as mocked:
        report = synthesize_with_piper("Hello world", model, "voice-model", ledger(), output)
    assert report["synthesized"] is True
    assert report["public_publish_allowed"] is False
    assert mocked.call_args.args[0][1:] == ["--model", str(model), "--output_file", str(output)]


def test_tts_refuses_overwrite_by_default(tmp_path):
    model = tmp_path / "voice.onnx"
    output = tmp_path / "voice.wav"
    model.write_bytes(b"model")
    output.write_bytes(b"old")
    with pytest.raises(TTSError, match="output already exists"):
        synthesize_with_piper("Hello world", model, "voice-model", ledger(), output)
