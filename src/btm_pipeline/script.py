"""Editorial script-package validation; no AI provider is called here."""
from __future__ import annotations

import re
from typing import Any

_WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_script_package(package: Any, research_packet: Any = None) -> dict[str, Any]:
    """Check structure, duration, and evidence references without asserting truth."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not isinstance(package, dict):
        return {"structurally_valid": False, "ready_for_human_review": False,
                "word_count": 0, "estimated_minutes": 0.0,
                "blockers": ["script package root must be an object"], "warnings": []}

    for field in ("title", "audience", "editorial_angle", "language"):
        if not _text(package.get(field)):
            blockers.append(f"{field} must be a non-empty string")

    target = package.get("target_runtime_minutes")
    if not isinstance(target, (int, float)) or isinstance(target, bool) or not 8 <= target <= 12:
        blockers.append("target_runtime_minutes must be between 8 and 12 for this channel format")

    sections = package.get("sections")
    if not isinstance(sections, list) or len(sections) < 3:
        blockers.append("at least three script sections are required")
        sections = []

    word_count = 0
    used_claim_ids: set[str] = set()
    for index, section in enumerate(sections):
        label = f"section #{index + 1}"
        if not isinstance(section, dict):
            blockers.append(f"{label} must be an object")
            continue
        if not _text(section.get("heading")):
            blockers.append(f"{label} heading is required")
        narration = section.get("narration")
        if not _text(narration):
            blockers.append(f"{label} narration is required")
        else:
            word_count += len(_WORD_RE.findall(narration))
        claims = section.get("claim_ids", [])
        if not isinstance(claims, list) or any(not _text(item) for item in claims):
            blockers.append(f"{label} claim_ids must be a list of non-empty IDs")
        else:
            used_claim_ids.update(claims)
        if "visual_notes" in section and not _text(section.get("visual_notes")):
            warnings.append(f"{label} has empty visual_notes")

    target_min = package.get("minimum_word_count", 1200)
    target_max = package.get("maximum_word_count", 1800)
    if (not isinstance(target_min, int) or isinstance(target_min, bool) or
            not isinstance(target_max, int) or isinstance(target_max, bool) or
            target_min < 1 or target_max < target_min):
        blockers.append("minimum_word_count and maximum_word_count must be valid positive bounds")
    elif not target_min <= word_count <= target_max:
        blockers.append(f"script word count {word_count} is outside the configured range {target_min}–{target_max}")

    research_claim_ids: set[str] = set()
    verified_claim_ids: set[str] = set()
    if research_packet is not None:
        if not isinstance(research_packet, dict):
            blockers.append("research_packet must be an object when supplied")
        else:
            claims = research_packet.get("claims", [])
            if not isinstance(claims, list):
                blockers.append("research_packet claims must be a list")
            else:
                for claim in claims:
                    if not isinstance(claim, dict) or not _text(claim.get("claim_id")):
                        continue
                    claim_id = claim["claim_id"]
                    research_claim_ids.add(claim_id)
                    if claim.get("status") == "human_verified":
                        verified_claim_ids.add(claim_id)
            for claim_id in sorted(used_claim_ids - research_claim_ids):
                blockers.append(f"script references unknown research claim_id: {claim_id}")
            for claim_id in sorted(used_claim_ids & research_claim_ids - verified_claim_ids):
                blockers.append(f"claim {claim_id} is not marked human_verified in the review packet")
    elif used_claim_ids:
        warnings.append("claim IDs are recorded but no research packet was supplied to resolve them")

    status = package.get("editorial_status", "draft")
    if status not in {"draft", "needs_review", "approved"}:
        blockers.append("editorial_status must be draft, needs_review, or approved")
    if status != "approved":
        warnings.append("editorial approval is absent; this package is not cleared for production")

    estimated_minutes = round(word_count / 150, 2)
    structurally_valid = not blockers
    return {
        "structurally_valid": structurally_valid,
        "ready_for_human_review": structurally_valid,
        "editorially_approved": structurally_valid and status == "approved",
        "word_count": word_count,
        "estimated_minutes_at_150_wpm": estimated_minutes,
        "used_claim_ids": sorted(used_claim_ids),
        "blockers": blockers,
        "warnings": warnings,
        "important_limit": "This validator checks structure, length, and declared references only. It does not verify facts, originality, copyright, quality, or suitability; a human editor must review the script and evidence.",
    }
