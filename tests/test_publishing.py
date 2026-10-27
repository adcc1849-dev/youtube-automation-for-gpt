from __future__ import annotations

import json
from pathlib import Path

import pytest

from btm_pipeline.publishing import PublishingError, validate_release


def valid_manifest():
    return {
        "release_gates": {
            "factual_evidence": True, "asset_rights": True, "technical": True,
            "metadata": True, "security": True,
        },
        "human_review_complete": True,
        "metadata": {"title": "A verified episode", "description": "Sources and context.", "tags": ["AI"]},
    }


def test_private_release_passes_local_preflight(tmp_path):
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"video")
    result = validate_release(valid_manifest(), video)
    assert result["visibility"] == "private"
    assert result["title"] == "A verified episode"


@pytest.mark.parametrize("gate", [
    "factual_evidence", "asset_rights", "technical", "metadata", "security",
])
def test_any_failed_mandatory_gate_blocks(tmp_path, gate):
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"video")
    manifest = valid_manifest()
    manifest["release_gates"][gate] = False
    with pytest.raises(PublishingError, match="mandatory release gates"):
        validate_release(manifest, video)


def test_human_review_is_mandatory(tmp_path):
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"video")
    manifest = valid_manifest()
    manifest["human_review_complete"] = False
    with pytest.raises(PublishingError, match="human review"):
        validate_release(manifest, video)


def test_public_upload_blocked_by_default_policy(tmp_path):
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"video")
    manifest = valid_manifest()
    with pytest.raises(PublishingError, match="public publishing is disabled"):
        validate_release(manifest, video, visibility="public", policy={
            "public_publishing_enabled": False,
            "owner_public_activation_authorized": False,
            "staged_private_end_to_end_tests_required": True,
        })


def test_existing_receipt_blocks_duplicate(tmp_path):
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"video")
    receipt = tmp_path / "receipt.json"
    receipt.write_text("{}", encoding="utf-8")
    with pytest.raises(PublishingError, match="possible duplicate"):
        validate_release(valid_manifest(), video, receipt_path=receipt)


def test_invalid_video_path_blocks(tmp_path):
    with pytest.raises(PublishingError, match="non-empty video"):
        validate_release(valid_manifest(), tmp_path / "missing.mp4")
