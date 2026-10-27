from btm_pipeline.research import validate_research_packet


def packet():
    return {
        "topic": "Humanoid robots in factories",
        "sources": [{
            "source_id": "src-001",
            "url": "https://www.nist.gov/example",
            "title": "Robotics report",
            "publisher": "NIST",
            "published_at": "2026-03-10",
            "accessed_at": "2026-10-27",
            "source_type": "official_documentation",
            "relevance": "Provides context for industrial robotics standards.",
            "supports": ["claim-001"],
        }],
        "claims": [{
            "claim_id": "claim-001",
            "text": "Example claim that still needs source review.",
            "status": "unverified",
            "source_ids": ["src-001"],
        }],
    }


def test_complete_packet_is_structurally_reviewable_not_verified():
    report = validate_research_packet(packet())
    assert report["structurally_reviewable"] is True
    assert "does not verify" in report["important_limit"]


def test_http_source_is_rejected():
    data = packet()
    data["sources"][0]["url"] = "http://example.org"
    report = validate_research_packet(data)
    assert report["structurally_reviewable"] is False
    assert any("HTTPS" in issue for issue in report["blockers"])


def test_claim_cannot_self_mark_verified():
    data = packet()
    data["claims"][0]["status"] = "verified"
    report = validate_research_packet(data)
    assert any("must start as unverified" in issue for issue in report["blockers"])


def test_unknown_source_reference_blocks_packet():
    data = packet()
    data["claims"][0]["source_ids"] = ["missing"]
    report = validate_research_packet(data)
    assert any("not present" in issue for issue in report["blockers"])


def test_missing_publication_date_blocks_packet():
    data = packet()
    data["sources"][0]["published_at"] = ""
    report = validate_research_packet(data)
    assert any("published_at" in issue for issue in report["blockers"])


def test_research_source_does_not_grant_media_rights():
    data = packet()
    data["sources"][0]["rights_to_reuse_content"] = True
    report = validate_research_packet(data)
    assert any("reuse rights" in issue for issue in report["blockers"])


def test_non_object_packet_fails_closed():
    report = validate_research_packet([])
    assert report["structurally_reviewable"] is False
