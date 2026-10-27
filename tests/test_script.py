from btm_pipeline.script import validate_script_package


def long_narration():
    return " ".join(["Robots are changing factory work in complex ways."] * 300)


def valid_package():
    return {
        "title": "How Humanoid Robots Are Learning Factory Work",
        "audience": "US English-speaking general audience",
        "editorial_angle": "What works today, what still fails, and what changes next",
        "language": "en-US",
        "target_runtime_minutes": 10,
        "minimum_word_count": 1200,
        "maximum_word_count": 1800,
        "editorial_status": "needs_review",
        "sections": [
            {"heading": "Hook", "narration": long_narration(), "claim_ids": ["robot-001"], "visual_notes": "Use cleared factory footage"},
            {"heading": "Current capability", "narration": long_narration(), "claim_ids": ["robot-001"]},
            {"heading": "Limits and future", "narration": long_narration(), "claim_ids": [], "visual_notes": "Use original diagrams"},
        ],
    }


def verified_research():
    return {"claims": [{"claim_id": "robot-001", "status": "human_verified"}]}


def test_valid_script_is_structurally_reviewable_not_auto_approved():
    report = validate_script_package(valid_package(), verified_research())
    assert report["structurally_valid"] is True
    assert report["ready_for_human_review"] is True
    assert report["editorially_approved"] is False
    assert report["word_count"] >= 1200


def test_unknown_research_claim_blocks():
    packet = valid_package()
    packet["sections"][0]["claim_ids"] = ["missing-claim"]
    report = validate_script_package(packet, verified_research())
    assert report["structurally_valid"] is False
    assert any("unknown research claim_id" in item for item in report["blockers"])


def test_unverified_research_claim_blocks():
    report = validate_script_package(valid_package(), {"claims": [{"claim_id": "robot-001", "status": "unverified"}]})
    assert report["structurally_valid"] is False
    assert any("not marked human_verified" in item for item in report["blockers"])


def test_short_script_blocks():
    packet = valid_package()
    packet["sections"][0]["narration"] = "Too short."
    packet["sections"][1]["narration"] = "Too short."
    packet["sections"][2]["narration"] = "Too short."
    report = validate_script_package(packet, verified_research())
    assert report["structurally_valid"] is False
    assert any("outside the configured range" in item for item in report["blockers"])


def test_missing_sections_and_invalid_runtime_block():
    report = validate_script_package({"title": "x", "target_runtime_minutes": 20, "sections": []})
    assert report["structurally_valid"] is False


def test_approved_status_requires_valid_package():
    packet = valid_package()
    packet["editorial_status"] = "approved"
    report = validate_script_package(packet, verified_research())
    assert report["editorially_approved"] is True
