from btm_pipeline.skills import SkillInputError, available_skills, load_skill


def test_all_eleven_skills_are_registered():
    skills = available_skills()
    assert len(skills) == 11
    assert {item["name"] for item in skills} == {
        "yt-script", "yt-package", "yt-edit", "yt-comment", "yt-plan", "yt-viral",
        "yt-retention", "yt-shorts", "yt-seo", "yt-chapters", "yt-audit",
    }


def test_skill_does_not_run_without_required_inputs():
    result = load_skill("yt-comment", available_inputs={"topic"})
    assert result["ready"] is False
    assert result["missing_inputs"] == ["comments"]
    assert result["prompt"] is None


def test_script_skill_loads_when_research_is_available():
    result = load_skill("yt-script", available_inputs={"topic", "research_packet"})
    assert result["ready"] is True
    assert "SKILL" not in result["prompt"] or len(result["prompt"]) > 100
    assert result["source_commit"] == "a2feb2104981a375ffd4f87ee04f4f5344ac43c6"


def test_unknown_skill_fails_explicitly():
    try:
        load_skill("yt-nonexistent", available_inputs=set())
    except SkillInputError:
        pass
    else:
        raise AssertionError("unknown skill should fail")
