from btm_pipeline.gates import evaluate_release


def valid_manifest():
    return {
        "metadata": {"title": "Factory Robots", "description": "A test brief.", "language": "en-US"},
        "claims": [{
            "claim": "Example claim",
            "status": "verified",
            "sources": [{"url": "https://example.org/report", "supports": "The report documents the claim."}],
        }],
        "assets": [{
            "asset_id": "asset-001",
            "kind": "third_party",
            "description": "Example factory video",
            "source_url": "https://example.org/video",
            "captured_at": "2026-10-27",
            "rights_status": "reviewed",
            "license_family": "cc_by",
            "license_name": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "proof_url": "https://example.org/rights-proof",
            "intended_use": "Edited documentary video",
            "reviewed_by": "human-reviewer",
            "reviewed_at": "2026-10-27",
            "commercial_use_allowed": True,
            "modification_allowed": True,
            "rights_holder": "Example source",
            "rights_reviewed": True,
            "restricted_or_unclear": False,
            "attribution_required": True,
            "attribution_text": "Example source — CC BY 4.0",
        }],
        "technical": {
            "render_exists": True,
            "duration_valid": True,
            "audio_valid": True,
            "video_stream_valid": True,
        },
        "security": {
            "secret_scan_passed": True,
            "no_unapproved_paid_services": True,
            "no_public_upload_attempt": True,
        },
        "policy": {
            "staged_private_tests_passed": False,
            "owner_public_activation_authorized": False,
            "public_publishing_enabled": False,
        },
    }


def test_complete_manifest_is_only_ready_for_private_review():
    report = evaluate_release(valid_manifest())
    assert report["release_ready_for_private_review"] is True
    assert report["public_publish_allowed"] is False


def test_missing_claim_evidence_blocks_release():
    manifest = valid_manifest()
    manifest["claims"][0]["sources"] = []
    report = evaluate_release(manifest)
    assert report["release_ready_for_private_review"] is False
    assert any("factual_evidence" in item for item in report["blockers"])


def test_unreviewed_asset_blocks_release():
    manifest = valid_manifest()
    manifest["assets"][0]["rights_reviewed"] = False
    report = evaluate_release(manifest)
    assert report["release_ready_for_private_review"] is False


def test_missing_technical_results_blocks_release():
    manifest = valid_manifest()
    manifest.pop("technical")
    report = evaluate_release(manifest)
    assert report["release_ready_for_private_review"] is False


def test_manifest_flags_can_never_enable_public_publishing_without_an_uploader():
    manifest = valid_manifest()
    manifest["policy"].update({
        "staged_private_tests_passed": True,
        "owner_public_activation_authorized": True,
        "public_publishing_enabled": True,
    })
    report = evaluate_release(manifest)
    assert report["release_ready_for_private_review"] is True
    assert report["public_publish_allowed"] is False


def test_owner_authorization_alone_cannot_bypass_failed_gate():
    manifest = valid_manifest()
    manifest["policy"].update({
        "staged_private_tests_passed": True,
        "owner_public_activation_authorized": True,
        "public_publishing_enabled": True,
    })
    manifest["assets"][0]["proof_url"] = ""
    report = evaluate_release(manifest)
    assert report["public_publish_allowed"] is False
    assert report["release_ready_for_private_review"] is False


def test_missing_policy_fails_closed():
    manifest = valid_manifest()
    manifest.pop("policy")
    report = evaluate_release(manifest)
    assert report["release_ready_for_private_review"] is False
    assert report["public_publish_allowed"] is False
