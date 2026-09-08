"""Small optional OpenAI-compatible HTTP client with no hard SDK dependency."""

from __future__ import annotations

import json
from collections.abc import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import ConfigurationError, validate_ai_base_url


class AIProviderError(RuntimeError):
    """Raised when an optional provider cannot return a response."""


class OpenAICompatibleClient:
    """Call a chat-completions-compatible endpoint using standard-library HTTP."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: int = 30,
    ) -> None:
        if not api_key.strip():
            raise AIProviderError("An API key is required for the AI provider.")
        if not model.strip():
            raise AIProviderError("An AI model is required for the AI provider.")
        try:
            validated_base_url = validate_ai_base_url(base_url)
        except ConfigurationError as exc:
            raise AIProviderError(str(exc)) from exc
        self.api_key = api_key
        self.model = model
        self.endpoint = validated_base_url + "/chat/completions"
        self.timeout_seconds = timeout_seconds

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload: Mapping[str, object] = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            # The URL was constrained to HTTPS or loopback by validate_ai_base_url.
            with urlopen(request, timeout=self.timeout_seconds) as response:  # nosec B310
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise AIProviderError(
                "The configured AI provider did not return a usable response."
            ) from exc
        try:
            return str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(
                "The AI provider response did not contain message content."
            ) from exc
