"""Transparent, evidence-aware candidate ranking for the next episode.

Scores prioritize editorial review; they are not predictions of views or virality.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

WEIGHTS = {
    "audience_fit": 0.20,
    "demand_evidence": 0.20,
    "novelty_timing": 0.15,
    "story_strength": 0.15,
    "evidence_quality": 0.15,
    "visual_potential": 0.10,
    "production_feasibility": 0.05,
}
SCORE_FIELDS = tuple(WEIGHTS)


class TopicQueueError(ValueError):
    """Raised for incomplete or misleading topic-scoring inputs."""


def _validate_completed_topics(value: Any) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise TopicQueueError("completed topics must be a JSON list of strings")
    if any(not item.strip() for item in value):
        raise TopicQueueError("completed topics must not contain empty strings")
    return value


def rank_candidates(candidates: Any, *, completed_topics: list[str] | None = None) -> dict[str, Any]:
    if not isinstance(candidates, list):
        raise TopicQueueError("candidates must be a JSON list")
    validated_completed = _validate_completed_topics([] if completed_topics is None else completed_topics)
    completed = {x.strip().casefold() for x in validated_completed}
    ranked = []
    seen = set()
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise TopicQueueError(f"candidate {index} must be an object")
        title = candidate.get("title")
        if not isinstance(title, str) or not title.strip():
            raise TopicQueueError(f"candidate {index} needs a non-empty title")
        normalized = title.strip().casefold()
        if normalized in seen:
            raise TopicQueueError(f"duplicate candidate title: {title}")
        seen.add(normalized)
        scores = candidate.get("scores")
        if not isinstance(scores, dict):
            raise TopicQueueError(f"{title}: scores object is required")
        missing = [field for field in SCORE_FIELDS if field not in scores]
        if missing:
            raise TopicQueueError(f"{title}: missing scores: {', '.join(missing)}")
        for field in SCORE_FIELDS:
            value = scores[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 5:
                raise TopicQueueError(f"{title}: {field} must be a number from 0 to 5")
        sources = candidate.get("evidence_sources", [])
        if not isinstance(sources, list) or any(not isinstance(x, str) or not x.strip() for x in sources):
            raise TopicQueueError(f"{title}: evidence_sources must be a list of non-empty strings")
        blockers = candidate.get("blockers", [])
        if not isinstance(blockers, list) or any(not isinstance(x, str) for x in blockers):
            raise TopicQueueError(f"{title}: blockers must be a list of strings")
        raw = sum((scores[field] / 5) * weight * 100 for field, weight in WEIGHTS.items())
        penalties = []
        if not sources:
            raw -= 15
            penalties.append("no_traceable_sources:-15")
        if blockers:
            raw -= min(30, len(blockers) * 10)
            penalties.append(f"unresolved_blockers:-{min(30, len(blockers) * 10)}")
        repeated = normalized in completed
        if repeated:
            raw -= 25
            penalties.append("already_completed_topic:-25")
        ranked.append({
            "title": title.strip(),
            "score": round(max(0, min(100, raw)), 2),
            "component_scores": {field: scores[field] for field in SCORE_FIELDS},
            "evidence_sources": sources,
            "blockers": blockers,
            "penalties": penalties,
            "eligible_for_research": not blockers and bool(sources) and not repeated,
            "analytics_evidence": candidate.get("analytics_evidence", []),
            "decision_note": "Priority estimate for human/editorial review only; not a view forecast or virality prediction.",
        })
    ranked.sort(key=lambda x: (-x["score"], x["title"].casefold()))
    return {
        "schema_version": 1,
        "score_weights": WEIGHTS,
        "candidate_count": len(ranked),
        "ranked_candidates": ranked,
        "next_topic": next((x["title"] for x in ranked if x["eligible_for_research"]), None),
        "automatic_publish_authorized": False,
        "notes": [
            "Analytics evidence is only used when explicitly included with provenance by the caller.",
            "This module does not collect analytics, invent demand signals, or claim causation.",
            "A ranked topic still needs research, factual review, and rights feasibility checks.",
        ],
    }


def rank_file(input_path: str | Path, output_path: str | Path, *,
              completed_topics_path: str | Path | None = None) -> dict[str, Any]:
    source = Path(input_path)
    output = Path(output_path)
    if output.exists():
        raise TopicQueueError("output already exists; use a new versioned path")
    try:
        candidates = json.loads(source.read_text(encoding="utf-8"))
        completed: Any = []
        if completed_topics_path:
            completed = json.loads(Path(completed_topics_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise TopicQueueError("input or completed-topic file could not be read as JSON") from None
    completed = _validate_completed_topics(completed)
    result = rank_candidates(candidates, completed_topics=completed)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return result
