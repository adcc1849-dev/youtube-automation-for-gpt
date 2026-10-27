from unittest.mock import patch

from btm_pipeline.review import review_bundle


def test_empty_bundle_fails_closed_and_never_allows_public_publish():
    report = review_bundle({})
    assert report["overall_ready_for_private_review"] is False
    assert report["public_publish_allowed"] is False
    assert set(report["checks"]) == {"research", "script", "rights", "media", "release_gates"}


def test_orchestrator_reports_each_stage_and_never_authorizes_public_publish():
    bundle = {
        "research_packet": {"topic": "Robots", "sources": [], "claims": []},
        "script_package": {"title": "x", "sections": []},
        "claim_review_packet": {"claims": []},
        "rights_ledger": {"assets": []},
        "media_path": "/not/a/real/file.mp4",
        "release_manifest": {},
    }
    report = review_bundle(bundle)
    assert report["overall_ready_for_private_review"] is False
    assert report["public_publish_allowed"] is False
    assert "research" in report["reports"]
    assert "release" in report["reports"]


def test_orchestrator_does_not_override_failed_gate_or_media_result():
    bundle = {
        "research_packet": {"topic": "Robots", "sources": [], "claims": []},
        "script_package": {"title": "x", "sections": []},
        "claim_review_packet": {"claims": []},
        "rights_ledger": {"assets": []},
        "media_path": "/tmp/mock.mp4",
        "release_manifest": {},
    }
    with patch("btm_pipeline.review.inspect_media", return_value={"passed": True, "blockers": []}):
        report = review_bundle(bundle)
    assert report["checks"]["media"] is True
    assert report["checks"]["release_gates"] is False
    assert report["overall_ready_for_private_review"] is False
    assert report["public_publish_allowed"] is False
