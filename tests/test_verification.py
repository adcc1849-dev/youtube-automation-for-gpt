from __future__ import annotations
import pytest
from btm_pipeline.verification import VerificationError, verify_video


class Request:
    def __init__(self, value): self.value = value
    def execute(self): return self.value


class Videos:
    def __init__(self, value): self.value = value
    def list(self, **kwargs): return Request(self.value)


class Service:
    def __init__(self, value): self.value = value
    def videos(self): return Videos(self.value)


def payload(title="Episode", visibility="private", processing="succeeded"):
    return {"items": [{
        "id": "abc123",
        "snippet": {"title": title},
        "status": {"privacyStatus": visibility, "uploadStatus": "processed"},
        "processingDetails": {"processingStatus": processing},
        "contentDetails": {"duration": "PT8M"},
    }]}


def test_verifies_expected_title_visibility_and_processing():
    result = verify_video("abc123", youtube=Service(payload()),
                          expected_title="Episode", expected_visibility="private")
    assert result["verified"] is True
    assert result["processing_status"] == "succeeded"
    assert "caption_track_content_and_timing" in result["not_verified"]


def test_title_mismatch_fails_closed():
    with pytest.raises(VerificationError, match="title_mismatch"):
        verify_video("abc123", youtube=Service(payload(title="Wrong")), expected_title="Episode")


def test_visibility_mismatch_fails_closed():
    with pytest.raises(VerificationError, match="visibility_mismatch"):
        verify_video("abc123", youtube=Service(payload(visibility="public")), expected_visibility="private")


def test_processing_failure_fails_closed():
    with pytest.raises(VerificationError, match="processing_failed"):
        verify_video("abc123", youtube=Service(payload(processing="failed")))


def test_missing_video_fails_closed():
    with pytest.raises(VerificationError, match="exactly one"):
        verify_video("missing", youtube=Service({"items": []}))
