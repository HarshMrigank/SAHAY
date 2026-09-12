"""Minimal Grok OpenAI-compatible client with strict response validation."""

from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from ..config import settings
from .schemas import GrokAssessment


class GrokClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.grok_api_key
        self.model = model or settings.grok_model
        self.base_url = base_url or settings.grok_base_url
        self.timeout = timeout or settings.grok_timeout_seconds

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def assess(self, text: str) -> GrokAssessment | None:
        if not self.configured:
            return None
        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only JSON with summary, risk_flags, recommendations, evidence, "
                        "and uncertainty. Do not diagnose or provide numeric scores. "
                        "A local deterministic rules engine handles safety."
                    ),
                },
                {"role": "user", "content": text[:12000]},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                body: dict[str, Any] = response.json()
            content = body["choices"][0]["message"]["content"]
            if isinstance(content, str):
                content = json.loads(content)
            return GrokAssessment.model_validate(content)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, ValidationError):
            # An unavailable or malformed model response must never block the
            # auditable local safety result.
            return None
