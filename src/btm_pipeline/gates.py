"""Fail-closed release gates. This module never uploads or publishes content."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    mandatory: bool
    details: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "mandatory": self.mandatory,
            "details": list(self.details),
        }


def _is_http_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _items(manifest: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = manifest.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def check_metadata(manifest: dict[str, Any]) -> GateResult:
    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict):
        return GateResult("metadata", False, True, ("metadata object is missing",))
    missing = [
        key for key in ("title", "description", "language")
        if not isinstance(metadata.get(key), str) or not metadata[key].strip()
    ]
    details = tuple(f"missing required metadata: {key}" for key in missing)
    return GateResult("metadata", not missing, True, details or ("required metadata fields present",))


def check_claim_evidence(manifest: dict[str, Any]) -> GateResult:
    claims = _items(manifest, "claims")
    if not claims:
        return GateResult("factual_evidence", False, True, ("no claims/evidence ledger supplied",))
    problems: list[str] = []
    for index, claim in enumerate(claims):
        label = str(claim.get("claim", "")).strip() or f"claim #{index + 1}"
        if claim.get("status") != "verified":
            problems.append(f"{label}: status is not verified")
        sources = claim.get("sources")
        valid_sources = [
            source for source in sources
            if isinstance(source, dict) and _is_http_url(source.get("url"))
            and isinstance(source.get("supports"), str) and source["supports"].strip()
        ] if isinstance(sources, list) else []
        if not valid_sources:
            problems.append(f"{label}: no usable source URL with a description of what it supports")
    return GateResult(
        "factual_evidence", not problems, True,
        tuple(problems) or (f"{len(claims)} claim(s) have recorded evidence; human/source verification is still required",),
    )


def check_asset_rights(manifest: dict[str, Any]) -> GateResult:
    assets = _items(manifest, "assets")
    if not assets:
        return GateResult("asset_rights", False, True, ("no asset rights ledger supplied",))
    problems: list[str] = []
    for index, asset in enumerate(assets):
        asset_id = str(asset.get("asset_id", "")).strip() or f"asset #{index + 1}"
        for field in ("source_url", "license_url", "proof_url"):
            if not _is_http_url(asset.get(field)):
                problems.append(f"{asset_id}: missing or invalid {field}")
        license_name = asset.get("license_name")
        if not isinstance(license_name, str) or not license_name.strip():
            problems.append(f"{asset_id}: license_name is unresolved")
        if asset.get("rights_reviewed") is not True:
            problems.append(f"{asset_id}: rights_reviewed must be true")
        if asset.get("attribution_required") is True and not str(asset.get("attribution_text", "")).strip():
            problems.append(f"{asset_id}: required attribution text is missing")
    return GateResult(
        "asset_rights", not problems, True,
        tuple(problems) or (f"{len(assets)} asset(s) have documented rights fields; documentation is not a legal guarantee",),
    )


def check_technical(manifest: dict[str, Any]) -> GateResult:
    technical = manifest.get("technical")
    if not isinstance(technical, dict):
        return GateResult("technical", False, True, ("technical validation results are missing",))
    required = ("render_exists", "duration_valid", "audio_valid", "video_stream_valid")
    problems = [f"{key} is not true" for key in required if technical.get(key) is not True]
    return GateResult("technical", not problems, True, tuple(problems) or ("declared technical checks passed; actual media inspection must be implemented by a renderer adapter",))


def check_security(manifest: dict[str, Any]) -> GateResult:
    security = manifest.get("security")
    if not isinstance(security, dict):
        return GateResult("security", False, True, ("security validation results are missing",))
    required = ("secret_scan_passed", "no_unapproved_paid_services", "no_public_upload_attempt")
    problems = [f"{key} is not true" for key in required if security.get(key) is not True]
    return GateResult("security", not problems, True, tuple(problems) or ("declared security checks passed",))


def evaluate_release(manifest: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a manifest; never publish. Missing gates always block release."""
    gates = [
        check_metadata(manifest),
        check_claim_evidence(manifest),
        check_asset_rights(manifest),
        check_technical(manifest),
        check_security(manifest),
    ]
    policy = manifest.get("policy")
    policy = policy if isinstance(policy, dict) else {}
    private_tests_passed = policy.get("staged_private_tests_passed") is True
    activation_authorized = policy.get("owner_public_activation_authorized") is True
    public_enabled = policy.get("public_publishing_enabled") is True

    mandatory_pass = all(gate.passed for gate in gates if gate.mandatory)
    release_ready = mandatory_pass and private_tests_passed
    public_publish_allowed = release_ready and activation_authorized and public_enabled
    blockers = [f"{gate.name}: {'; '.join(gate.details)}" for gate in gates if gate.mandatory and not gate.passed]
    if not private_tests_passed:
        blockers.append("staged private end-to-end tests have not passed")
    if not activation_authorized:
        blockers.append("explicit owner authorization for public publishing is absent")
    if not public_enabled:
        blockers.append("public publishing is disabled by policy")

    return {
        "release_ready_for_private_review": release_ready,
        "public_publish_allowed": public_publish_allowed,
        "gates": [gate.as_dict() for gate in gates],
        "blockers": blockers,
    }
