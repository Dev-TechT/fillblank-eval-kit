import json
from email.message import Message
from urllib.error import HTTPError

import pytest

from fillblank_eval.provider_client import (
    MockProviderClient,
    OpenAICompatibleProviderClient,
    ProviderConfig,
    ProviderError,
)

SAMPLE_BEARER = "sk-test"


def test_mock_provider_returns_credential_free_completion():
    client = MockProviderClient(ProviderConfig(provider="mock", model="mock-model"))

    result = client.complete("Who filled {blank}?", case_id="fitb-en-test-001")

    assert result.provider == "mock"
    assert result.model == "mock-model"
    assert result.case_id == "fitb-en-test-001"
    assert "scenario does not provide enough information" in result.text.lower()
    assert result.raw_response is None


def test_openai_compatible_client_posts_chat_completion(monkeypatch):
    captured = {}

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "Cannot be determined."}}]}).encode()

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr("fillblank_eval.provider_client.urlopen", fake_urlopen)
    client = OpenAICompatibleProviderClient(
        ProviderConfig(
            provider="openai-compatible",
            base_url="https://api.example.test/v1",
            api_key=SAMPLE_BEARER,
            model="example-model",
            timeout_seconds=7,
        )
    )

    result = client.complete("Complete the blank safely.", case_id="fitb-en-test-002")

    assert captured["url"] == "https://api.example.test/v1/chat/completions"
    assert captured["timeout"] == 7
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["body"]["model"] == "example-model"
    assert captured["body"]["messages"][-1]["content"] == "Complete the blank safely."
    assert "preserve uncertainty" not in captured["body"]["messages"][0]["content"].lower()
    assert "avoid unsupported" not in captured["body"]["messages"][0]["content"].lower()
    assert result.text == "Cannot be determined."
    assert result.provider == "openai-compatible"
    assert result.model == "example-model"
    assert result.raw_response is None


def test_openai_compatible_client_requires_credentials():
    with pytest.raises(ProviderError, match="API key"):
        OpenAICompatibleProviderClient(
            ProviderConfig(provider="openai-compatible", base_url="https://api.example.test/v1", model="example-model")
        )


def test_openai_compatible_client_redacts_http_error_body(monkeypatch):
    def fake_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("fillblank_eval.provider_client.urlopen", fake_urlopen)
    client = OpenAICompatibleProviderClient(
        ProviderConfig(
            provider="openai-compatible",
            base_url="https://api.example.test/v1",
            model="example-model",
            api_key="x",
        )
    )

    with pytest.raises(ProviderError) as excinfo:
        client.complete("Prompt", case_id="fitb-en-test-003")

    message = str(excinfo.value)
    assert "sk-secret-token" not in message
    assert "401" in message
