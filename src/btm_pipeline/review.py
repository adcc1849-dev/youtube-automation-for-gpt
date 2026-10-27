"""Bundle-level preflight orchestration. This module never publishes."""
from __future__ import annotations

from typing import Any

from .gates import evaluate_release
from .media import inspect_media
from .research import validate_research_packet
from .rights import validate_asset_rights_ledger
from .script import validate_script_package


def review_bundle(bundle: Any) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        return {
            "overall_ready_for_private_review": False,
            "public_publish_allowed": False,
            "blockers": ["bundle root must be an object"],
        }

    research = validate_research_packet(bundle.get("research_packet"))
    rights = validate_asset_rights_ledger(bundle.get("rights_ledger"))
    script = validate_script_package(bundle.get("script_package"), bundle.get("claim_review_packet"))
    media_path = bundle.get("media_path")
    if isinstance(media_path, str) and media_path.strip():
        media = inspect_media(media_path)
    else:
        media = {"passed": False, "blockers": ["media_path is missing; inspect a rendered file before private review"]}

    release_manifest = bundle.get("release_manifest")
    release_manifest = release_manifest if isinstance(release_manifest, dict) else {}
    release = evaluate_release(release_manifest)
    ledger_assets = bundle.get("rights_ledger", {}).get("assets", []) if isinstance(bundle.get("rights_ledger"), dict) else []
    manifest_assets = release_manifest.get("assets", [])
    ledger_ids = {asset.get("asset_id") for asset in ledger_assets if isinstance(asset, dict) and isinstance(asset.get("asset_id"), str)}
    manifest_ids = {asset.get("asset_id") for asset in manifest_assets if isinstance(asset, dict) and isinstance(asset.get("asset_id"), str)} if isinstance(manifest_assets, list) else set()
    asset_ledger_consistent = bool(ledger_ids) and ledger_ids == manifest_ids
    checks = {
        "research": research.get("structurally_reviewable") is True,
        "script": script.get("structurally_valid") is True and script.get("editorially_approved") is True,
        "rights": rights.get("passed") is True,
        "asset_ledger_consistent": asset_ledger_consistent,
        "media": media.get("passed") is True,
        "release_gates": release.get("release_ready_for_private_review") is True,
    }
    if not asset_ledger_consistent:
        blockers_asset_consistency = ["asset IDs in release_manifest.assets must exactly match rights_ledger.assets"]
    else:
        blockers_asset_consistency = []
    blockers: list[str] = []
    for name, report in (("research", research), ("script", script), ("rights", rights), ("media", media)):
        for item in report.get("blockers", []):
            blockers.append(f"{name}: {item}")
    blockers.extend(f"asset_ledger_consistency: {item}" for item in blockers_asset_consistency)
    blockers.extend(f"release_manifest: {item}" for item in release.get("blockers", []))
    ready = all(checks.values())
    return {
        "overall_ready_for_private_review": ready,
        "public_publish_allowed": False,
        "checks": checks,
        "reports": {
            "research": research,
            "script": script,
            "rights": rights,
            "media": media,
            "release": release,
        },
        "blockers": blockers,
        "notice": "This is a local preflight report only. It cannot authorize public publishing; this orchestrator always reports public_publish_allowed=false.",
    }
