"""Fail-closed asset provenance and rights-ledger validation.

This module validates completeness of recorded evidence only. It cannot determine
whether a license is authentic, legally applicable, or sufficient for a use.
"""
from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urlparse

ASSET_KINDS = {"original", "generated", "third_party"}
RIGHTS_STATUSES = {"pending", "reviewed", "rejected"}
LICENSE_FAMILIES = {
    "public_domain", "cc0", "cc_by", "cc_by_sa", "cc_by_nc",
    "cc_by_nc_sa", "cc_by_nd", "cc_by_nc_nd", "mit", "apache-2.0",
    "custom_permission", "platform_terms", "original", "unknown",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _https_url(value: Any) -> bool:
    if not _nonempty(value):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password


def _iso_date(value: Any) -> bool:
    if not _nonempty(value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except (TypeError, ValueError):
        return False


def validate_asset_rights_ledger(ledger: Any) -> dict[str, Any]:
    """Return a structured report; incomplete/ambiguous records fail closed."""
    if not isinstance(ledger, dict):
        return {"passed": False, "asset_count": 0, "blockers": ["ledger root must be an object"]}
    assets = ledger.get("assets")
    if not isinstance(assets, list) or not assets:
        return {"passed": False, "asset_count": 0, "blockers": ["assets must be a non-empty list"]}

    blockers: list[str] = []
    seen: set[str] = set()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            blockers.append(f"asset #{index + 1}: record must be an object")
            continue
        asset_id = asset.get("asset_id")
        label = asset_id.strip() if _nonempty(asset_id) else f"asset #{index + 1}"
        if not _nonempty(asset_id):
            blockers.append(f"{label}: asset_id is required")
        elif asset_id in seen:
            blockers.append(f"{label}: duplicate asset_id")
        else:
            seen.add(asset_id)

        kind = asset.get("kind")
        if kind not in ASSET_KINDS:
            blockers.append(f"{label}: kind must be one of {', '.join(sorted(ASSET_KINDS))}")

        for field in ("description", "source_url", "captured_at", "rights_status",
                      "license_family", "license_name", "license_url", "proof_url",
                      "intended_use", "reviewed_by", "reviewed_at"):
            if not _nonempty(asset.get(field)):
                blockers.append(f"{label}: {field} is required")

        for field in ("source_url", "license_url", "proof_url"):
            if _nonempty(asset.get(field)) and not _https_url(asset[field]):
                blockers.append(f"{label}: {field} must be an HTTPS URL without embedded credentials")

        for field in ("captured_at", "reviewed_at"):
            if _nonempty(asset.get(field)) and not _iso_date(asset[field]):
                blockers.append(f"{label}: {field} must use YYYY-MM-DD")

        status = asset.get("rights_status")
        if status != "reviewed":
            blockers.append(f"{label}: rights_status must be reviewed")
        family = asset.get("license_family")
        if family not in LICENSE_FAMILIES or family in {"unknown"}:
            blockers.append(f"{label}: license_family is unknown or unsupported")
        # Reject license families whose standard terms conflict with monetized,
        # edited documentary use even if contradictory booleans were supplied.
        if family in {"cc_by_nc", "cc_by_nc_sa", "cc_by_nc_nd"}:
            blockers.append(f"{label}: non-commercial Creative Commons license is incompatible with this channel's commercial-use requirement")
        if family in {"cc_by_nd", "cc_by_nc_nd"}:
            blockers.append(f"{label}: no-derivatives Creative Commons license is incompatible with an edited video workflow")
        if asset.get("commercial_use_allowed") is not True:
            blockers.append(f"{label}: commercial_use_allowed must be explicitly true for this channel")
        if asset.get("modification_allowed") is not True:
            blockers.append(f"{label}: modification_allowed must be explicitly true for editing")
        if asset.get("attribution_required") not in (True, False):
            blockers.append(f"{label}: attribution_required must be explicitly true or false")
        elif asset.get("attribution_required") is True and not _nonempty(asset.get("attribution_text")):
            blockers.append(f"{label}: attribution_text is required by the recorded license")
        if kind == "original" and not _nonempty(asset.get("creator")):
            blockers.append(f"{label}: creator is required for original assets")
        if kind == "generated":
            if not _nonempty(asset.get("generator")):
                blockers.append(f"{label}: generator/model provenance is required")
            if not _nonempty(asset.get("terms_checked_at")) or not _iso_date(asset.get("terms_checked_at")):
                blockers.append(f"{label}: terms_checked_at must be a date for generated assets")
        if kind == "third_party" and not _nonempty(asset.get("rights_holder")):
            blockers.append(f"{label}: rights_holder is required for third-party assets")
        if asset.get("rights_reviewed") is not True:
            blockers.append(f"{label}: rights_reviewed must be explicitly true")
        if asset.get("restricted_or_unclear") is not False:
            blockers.append(f"{label}: restricted_or_unclear must be explicitly false")

    return {
        "passed": not blockers,
        "asset_count": len(assets),
        "blockers": blockers,
        "notice": "A structurally complete ledger is not legal advice and does not prove the evidence or license is authentic, applicable, or sufficient. Human review remains mandatory.",
    }
