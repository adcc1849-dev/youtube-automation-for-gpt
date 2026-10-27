"""Source-backed research packet validation; no claim is auto-verified by this module."""

from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urlparse


SOURCE_TYPES = {"primary", "secondary", "news", "academic", "official_documentation"}


def _valid_https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password


def validate_research_packet(packet: Any) -> dict[str, Any]:
    """Return blockers and a readiness flag. Readiness means structurally reviewable, not factually true."""
    blockers: list[str] = []
    if not isinstance(packet, dict):
        return {"structurally_reviewable": False, "blockers": ["packet root must be an object"], "source_count": 0, "claim_count": 0}

    topic = packet.get("topic")
    if not isinstance(topic, str) or not topic.strip():
        blockers.append("topic must be a non-empty string")

    sources = packet.get("sources")
    if not isinstance(sources, list) or not sources:
        blockers.append("at least one source record is required")
        sources = []
    for index, source in enumerate(sources):
        label = f"source #{index + 1}"
        if not isinstance(source, dict):
            blockers.append(f"{label} must be an object")
            continue
        if not _valid_https_url(source.get("url")):
            blockers.append(f"{label} must have a valid HTTPS URL without embedded credentials")
        for field in ("title", "publisher", "published_at", "accessed_at", "relevance"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                blockers.append(f"{label} is missing {field}")
        source_type = source.get("source_type")
        if source_type not in SOURCE_TYPES:
            blockers.append(f"{label} source_type must be one of: {', '.join(sorted(SOURCE_TYPES))}")
        for field in ("published_at", "accessed_at"):
            value = source.get(field)
            if isinstance(value, str) and value.strip():
                try:
                    date.fromisoformat(value[:10])
                except ValueError:
                    blockers.append(f"{label} {field} must begin with an ISO date (YYYY-MM-DD)")
        supports = source.get("supports")
        if not isinstance(supports, list) or not supports or not all(isinstance(x, str) and x.strip() for x in supports):
            blockers.append(f"{label} must list the claim IDs or statements it supports")
        if source.get("rights_to_reuse_content") is True:
            blockers.append(f"{label} cannot assert reuse rights merely because it is a research source; record media rights separately")

    claims = packet.get("claims")
    if not isinstance(claims, list) or not claims:
        blockers.append("at least one explicit claim record is required")
        claims = []
    source_ids = {s.get("source_id") for s in sources if isinstance(s, dict) and isinstance(s.get("source_id"), str)}
    for index, claim in enumerate(claims):
        label = f"claim #{index + 1}"
        if not isinstance(claim, dict):
            blockers.append(f"{label} must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            blockers.append(f"{label} needs a claim_id")
        if not isinstance(claim.get("text"), str) or not claim["text"].strip():
            blockers.append(f"{label} needs explicit claim text")
        if claim.get("status") != "unverified":
            blockers.append(f"{label} must start as unverified; this tool cannot verify factual truth")
        evidence = claim.get("source_ids")
        if not isinstance(evidence, list) or not evidence:
            blockers.append(f"{label} needs at least one source_id")
        elif any(source_id not in source_ids for source_id in evidence):
            blockers.append(f"{label} references a source_id not present in the packet")

    return {
        "structurally_reviewable": not blockers,
        "blockers": blockers,
        "source_count": len(sources),
        "claim_count": len(claims),
        "important_limit": "Structural validation does not verify source authenticity, claim accuracy, recency, or media reuse rights.",
    }
