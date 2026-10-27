import json
from unittest.mock import patch

import pytest

from btm_pipeline.providers.gemini import (
    GeminiConfigurationError,
    GeminiRequestError,
    draft_script,
)


def packet():
    return {
        "topic": "Factory robotics",
        "sources": [],
        "claims": [{"claim_id": "claim-1", "text": "Example", "status": "unverified"}],
    }


def test_adapter_disabled_by_default(monkeypatch):
    monkeypatch.delenv("BTM_ENABLE_CLOUD_AI", raising=False)
    monkeypatch.delenv("BTM_GEMINI_FREE_TIER_CONFIRMED", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "not-a-real-key")
    with pytest.raises(GeminiConfigurationError, match="Cloud AI is disabled"):
        draft_script("Factory robotics", packet())


def test_requires_separate_free_tier_confirmation(monkeypatch):
    monkeypatch.setenv("BTM_ENABLE_CLOUD_AI", "1")
    monkeypatch.delenv("BTM_GEMINI_FREE_TIER_CONFIRMED", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "not-a-real-key")
    with pytest.raises(GeminiConfigurationError, match="unconfirmed"):
        draft_script("Factory robotics", packet())


def test_requires_key(monkeypatch):
    monkeypatch.setenv("BTM_ENABLE_CLOUD_AI", "1")
    monkeypatch.setenv("BTM_GEMINI_FREE_TIER_CONFIRMED", "1")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(GeminiConfigurationError, match="GEMINI_API_KEY is missing"):
        draft_script("Factory robotics", packet())


def test_success_returns_draft_and_never_authorizes_production(monkeypatch):
    monkeypatch.setenv("BTM_ENABLE_CLOUD_AI", "1")
    monkeypatch.setenv("BTM_GEMINI_FREE_TIER_CONFIRMED", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")
    model_output = {
        "title": "Factory Robotics",
        "audience": "General audience",
        "editorial_angle": "Capabilities and limits",
        "language": "en-US",
        "target_runtime_minutes": 10,
        "minimum_word_count": 1,
        "maximum_word_count": 5000,
        "editorial_status": "draft",
        "sections": [
            {"heading": "Opening", "narration": "A short draft.", "claim_ids": ["claim-1"]},
            {"heading": "Capabilities", "narration": "Another short draft.", "claim_ids": []},
            {"heading": "Limits", "narration": "Final short draft.", "claim_ids": []},
        ],
    }
    response = {"candidates": [{"content": {"parts": [{"text": json.dumps(model_output)}]}}]}

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return json.dumps(response).encode("utf-8")

    with patch("btm_pipeline.providers.gemini.urlopen", return_value=FakeResponse()) as mocked:
        result = draft_script("Factory robotics", packet())
    request = mocked.call_args.args[0]
    assert request.full_url.endswith(":generateContent")
    assert request.get_header("X-goog-api-key") == "fake-test-key"
    assert result["production_authorized"] is False
    assert result["script_package"]["editorial_status"] == "draft"
    assert any("not marked human_verified" in x for x in result["validation_report"]["blockers"])


def test_provider_error_does_not_echo_credentials(monkeypatch):
    monkeypatch.setenv("BTM_ENABLE_CLOUD_AI", "1")
    monkeypatch.setenv("BTM_GEMINI_FREE_TIER_CONFIRMED", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "secret-test-value")
    from urllib.error import HTTPError
    with patch("btm_pipeline.providers.gemini.urlopen", side_effect=HTTPError("https://example.invalid", 429, "quota", {}, None)):
        with pytest.raises(GeminiRequestError) as exc:
            draft_script("Factory robotics", packet())
    assert "secret-test-value" not in str(exc.value)
