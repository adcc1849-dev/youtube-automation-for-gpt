"""Safe loader and input-readiness checks for the vendored 11 YouTube agent skills."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


SKILLS = {
    "yt-script": {"purpose": "Draft a source-aware long-form script", "required_inputs": {"topic", "research_packet"}},
    "yt-package": {"purpose": "Create titles and packaging for a finished script/video", "required_inputs": {"script"}},
    "yt-edit": {"purpose": "Review an edit plan and pacing", "required_inputs": {"script", "asset_inventory"}},
    "yt-comment": {"purpose": "Analyze audience comments", "required_inputs": {"comments"}},
    "yt-plan": {"purpose": "Plan a channel/video schedule", "required_inputs": {"channel_context"}},
    "yt-viral": {"purpose": "Analyze hook/shareability patterns", "required_inputs": {"topic"}},
    "yt-retention": {"purpose": "Analyze retention from transcript or timestamped data", "required_inputs": {"transcript_or_retention_data"}},
    "yt-shorts": {"purpose": "Adapt source material into short-form concepts", "required_inputs": {"source_script_or_video_transcript"}},
    "yt-seo": {"purpose": "Prepare search-oriented metadata", "required_inputs": {"script", "topic"}},
    "yt-chapters": {"purpose": "Create chapters from a transcript", "required_inputs": {"transcript"}},
    "yt-audit": {"purpose": "Audit a published video/channel", "required_inputs": {"video_or_channel_data"}},
}


class SkillInputError(ValueError):
    """Raised when a skill name is unknown or its required input is unavailable."""


def available_skills() -> list[dict[str, object]]:
    return [
        {"name": name, "purpose": metadata["purpose"], "required_inputs": sorted(metadata["required_inputs"])}
        for name, metadata in SKILLS.items()
    ]


def load_skill(skill_name: str, available_inputs: Iterable[str] | None = None) -> dict[str, object]:
    """Load a skill prompt only when its required inputs are explicitly available."""
    if skill_name not in SKILLS:
        raise SkillInputError(f"unknown skill: {skill_name}")
    provided = set(available_inputs or ())
    required = SKILLS[skill_name]["required_inputs"]
    missing = sorted(required - provided)
    if missing:
        return {"name": skill_name, "ready": False, "missing_inputs": missing, "prompt": None}
    path = Path(__file__).parent / "skill_assets" / "skills" / skill_name / "SKILL.md"
    try:
        prompt = path.read_text(encoding="utf-8")
    except OSError:
        return {"name": skill_name, "ready": False, "missing_inputs": [], "prompt": None,
                "error": "vendored skill prompt is missing from this installation"}
    return {
        "name": skill_name,
        "ready": True,
        "missing_inputs": [],
        "prompt": prompt,
        "source": "Jakeschincariol/youtube-agent-skill",
        "source_commit": "a2feb2104981a375ffd4f87ee04f4f5344ac43c6",
        "notice": "Skill instructions are guidance, not evidence. Do not fabricate missing inputs. Upstream helper utilities are not automatically executed by this loader.",
    }
