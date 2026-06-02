from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    """Raised when a provider cannot be configured or called safely."""


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    temperature: float = 0.0
    max_tokens: int = 256
    timeout_seconds: int = 60
    include_raw_response: bool = False


@dataclass(frozen=True)
class CompletionResult:
    provider: str
    model: str
    case_id: str
    text: str
    raw_response: dict[str, Any] | None = None


class ProviderClient:
    def complete(self, prompt: str, *, case_id: str) -> CompletionResult:
        raise NotImplementedError


class MockProviderClient(ProviderClient):
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    def complete(self, prompt: str, *, case_id: str) -> CompletionResult:
        text = "The scenario does not provide enough information to determine the blank."
        return CompletionResult(provider="mock", model=self.config.model, case_id=case_id, text=text)


class OpenAICompatibleProviderClient(ProviderClient):
    def __init__(self, config: ProviderConfig) -> None:
        if not config.base_url:
            raise ProviderError("OpenAI-compatible provider requires a base URL")
        if not config.api_key:
            raise ProviderError("OpenAI-compatible provider requires an API key")
        if not config.model:
            raise ProviderError("OpenAI-compatible provider requires a model name")
        self.config = config
        self.base_url = config.base_url

    def complete(self, prompt: str, *, case_id: str) -> CompletionResult:
        endpoint = self.base_url.rstrip("/") + "/chat/completions"
        body = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer the user's prompt concisely.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        request = Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ProviderError(f"Provider HTTP error {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise ProviderError(f"Provider connection error: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise ProviderError("Provider returned invalid JSON") from exc

        text = _extract_openai_text(payload)
        if not text.strip():
            raise ProviderError("Provider returned an empty completion")
        return CompletionResult(
            provider="openai-compatible",
            model=self.config.model,
            case_id=case_id,
            text=text,
            raw_response=payload if self.config.include_raw_response else None,
        )


def _extract_openai_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderError("Provider response missing choices")
    first = choices[0]
    if not isinstance(first, dict):
        raise ProviderError("Provider response choice is not an object")
    message = first.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return message["content"]
    if isinstance(first.get("text"), str):
        return first["text"]
    raise ProviderError("Provider response missing message content")


def build_provider_client(config: ProviderConfig) -> ProviderClient:
    provider = config.provider.lower().strip()
    if provider in {"mock", "dry-run", "dry_run"}:
        return MockProviderClient(config)
    if provider in {"openai-compatible", "openai", "compatible"}:
        return OpenAICompatibleProviderClient(config)
    raise ProviderError(f"Unsupported provider: {config.provider}")
