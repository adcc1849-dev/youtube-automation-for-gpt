from copy import deepcopy

from btm_pipeline.rights import validate_asset_rights_ledger


def valid_asset():
    return {
        "asset_id": "shot-001",
        "kind": "third_party",
        "description": "Factory robot establishing shot",
        "source_url": "https://media.example.org/asset",
        "captured_at": "2026-10-27",
        "rights_status": "reviewed",
        "license_family": "cc_by",
        "license_name": "Creative Commons Attribution 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "proof_url": "https://media.example.org/asset/license-proof",
        "intended_use": "Edited documentary video on YouTube",
        "reviewed_by": "human-reviewer",
        "reviewed_at": "2026-10-27",
        "commercial_use_allowed": True,
        "modification_allowed": True,
        "attribution_required": True,
        "attribution_text": "Creator Name / source / license",
        "rights_holder": "Creator Name",
        "rights_reviewed": True,
        "restricted_or_unclear": False,
    }


def test_complete_record_passes_structural_review():
    report = validate_asset_rights_ledger({"assets": [valid_asset()]})
    assert report["passed"] is True
    assert report["asset_count"] == 1
    assert "not legal advice" in report["notice"]


def test_missing_proof_fails_closed():
    asset = valid_asset()
    asset["proof_url"] = ""
    report = validate_asset_rights_ledger({"assets": [asset]})
    assert report["passed"] is False
    assert any("proof_url is required" in item for item in report["blockers"])


def test_unknown_license_fails_closed():
    asset = valid_asset()
    asset["license_family"] = "unknown"
    report = validate_asset_rights_ledger({"assets": [asset]})
    assert report["passed"] is False


def test_attribution_required_without_text_fails():
    asset = valid_asset()
    asset["attribution_text"] = ""
    report = validate_asset_rights_ledger({"assets": [asset]})
    assert report["passed"] is False
    assert any("attribution_text is required" in item for item in report["blockers"])


def test_duplicate_asset_ids_fail():
    asset = valid_asset()
    report = validate_asset_rights_ledger({"assets": [asset, deepcopy(asset)]})
    assert report["passed"] is False
    assert any("duplicate asset_id" in item for item in report["blockers"])


def test_http_and_credential_urls_fail():
    asset = valid_asset()
    asset["source_url"] = "http://media.example.org/asset"
    asset["proof_url"] = "https://user:password@media.example.org/proof"
    report = validate_asset_rights_ledger({"assets": [asset]})
    assert report["passed"] is False
    assert any("source_url must be an HTTPS URL" in item for item in report["blockers"])
    assert any("proof_url must be an HTTPS URL" in item for item in report["blockers"])


def test_generated_asset_requires_model_and_terms_review_date():
    asset = valid_asset()
    asset.update(kind="generated", generator="Example image model", terms_checked_at="not-a-date")
    asset.pop("rights_holder")
    report = validate_asset_rights_ledger({"assets": [asset]})
    assert report["passed"] is False
    assert any("terms_checked_at must be a date" in item for item in report["blockers"])


def test_non_object_and_empty_ledger_fail():
    assert not validate_asset_rights_ledger(None)["passed"]
    assert not validate_asset_rights_ledger({"assets": []})["passed"]
