import json
from unittest.mock import patch

import pytest

from btm_pipeline.providers.gemini import GeminiConfigurationError, run_skill


def test_runner_blocks_skill_when_required_input_is_missing(monkeypatch):
    monkeypatch.setenv("BTM_ENABLE_CLOUD_AI", "1")
    monkeypatch.setenv("BTM_GEMINI_FREE_TIER_CONFIRMED", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    with pytest.raises(GeminiConfigurationError, match="missing required inputs: comments"):
        run_skill("yt-comment", {"topic": "robots"})


def test_runner_uses_only_supplied_input_keys_and_never_authorizes_publish(monkeypatch):
    monkeypatch.setenv("BTM_ENABLE_CLOUD_AI", "1")
    monkeypatch.setenv("BTM_GEMINI_FREE_TIER_CONFIRMED", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    response = {"candidates": [{"content": {"parts": [{"text": "{\"result\": \"reviewed provided comments\"}"}]}}]}

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return json.dumps(response).encode("utf-8")

    with patch("btm_pipeline.providers.gemini.urlopen", return_value=FakeResponse()) as mocked:
        result = run_skill("yt-comment", {"comments": [{"text": "Great video"}]})
    request_body = json.loads(mocked.call_args.args[0].data.decode("utf-8"))
    prompt = request_body["contents"][0]["parts"][0]["text"]
    assert "yt-comment" in prompt
    assert "Great video" in prompt
    assert result["inputs_used"] == ["comments"]
    assert result["public_publish_allowed"] is False
    assert result["human_review_required"] is True
