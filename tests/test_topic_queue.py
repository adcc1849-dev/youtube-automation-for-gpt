from __future__ import annotations
import json
import pytest
from btm_pipeline.topic_queue import TopicQueueError, rank_candidates, rank_file

SCORES = {
    "audience_fit": 5, "demand_evidence": 4, "novelty_timing": 4,
    "story_strength": 5, "evidence_quality": 5, "visual_potential": 4,
    "production_feasibility": 5,
}


def candidate(title="Factory robots", **kwargs):
    value = {"title": title, "scores": dict(SCORES),
             "evidence_sources": ["https://example.org/source"], "blockers": []}
    value.update(kwargs)
    return value


def test_rank_is_deterministic_and_not_a_virality_claim():
    result = rank_candidates([candidate()])
    assert result["next_topic"] == "Factory robots"
    assert result["ranked_candidates"][0]["score"] > 0
    assert result["ranked_candidates"][0]["decision_note"].find("not a view forecast") >= 0
    assert result["automatic_publish_authorized"] is False


def test_missing_sources_penalize_and_make_candidate_ineligible():
    result = rank_candidates([candidate(evidence_sources=[])])
    row = result["ranked_candidates"][0]
    assert row["eligible_for_research"] is False
    assert "no_traceable_sources:-15" in row["penalties"]


def test_blockers_and_completed_topics_prevent_selection():
    result = rank_candidates([
        candidate("Blocked", blockers=["unverified claim"]),
        candidate("Already done"),
    ], completed_topics=["Already done"])
    assert result["next_topic"] is None


def test_invalid_score_is_rejected():
    bad = candidate()
    bad["scores"]["demand_evidence"] = 6
    with pytest.raises(TopicQueueError, match="0 to 5"):
        rank_candidates([bad])


def test_duplicate_titles_rejected():
    with pytest.raises(TopicQueueError, match="duplicate"):
        rank_candidates([candidate(), candidate()])


def test_rank_file_preserves_output_history(tmp_path):
    source = tmp_path / "candidates.json"
    output = tmp_path / "ranked.json"
    source.write_text(json.dumps([candidate()]), encoding="utf-8")
    rank_file(source, output)
    assert json.loads(output.read_text())["next_topic"] == "Factory robots"
    with pytest.raises(TopicQueueError, match="already exists"):
        rank_file(source, output)
