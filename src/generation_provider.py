"""Provider-neutral backend generation contract.

The Flask route continues to use the existing NVIDIA path until a provider has
produced a verified response. This module is deliberately independent of Flask,
retrieval, persistence, and frontend contracts so another provider can be
added without changing those layers.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol


@dataclass(frozen=True)
class GenerationRequest:
    messages: list[dict[str, str]]
    model: str
    max_tokens: int
    temperature: float = 0.0
    streaming: bool = True


@dataclass(frozen=True)
class GenerationResult:
    content: str | None
    completed: bool
    provider: str
    model: str
    latency_ms: int
    status_code: int | None
    error_code: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    reasoning_chars: int = 0


class GenerationProvider(Protocol):
    """A provider must return only completed text as a successful result."""

    async def generate(self, request: GenerationRequest) -> GenerationResult: ...
    async def aclose(self) -> None: ...


def _normalize_error(error: str | None, status: int | None) -> str:
    if error == "timeout":
        return "provider_timeout"
    if error == "transport error":
        return "provider_transport_error"
    if error == "stream ended without completion marker":
        return "provider_incomplete_stream"
    if status:
        return f"provider_http_{status}"
    return "provider_error"


class NvidiaGenerationProvider:
    """Adapter for the existing completion-verified NVIDIA streaming client."""

    provider_name = "nvidia"

    def __init__(
        self,
        model: str,
        client_factory: Callable[[str], Any] | None = None,
    ):
        if client_factory is None:
            from src.nim import NimClient
            client_factory = NimClient
        self.model = model
        self._client = client_factory(model)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if request.model != self.model:
            raise ValueError("request model does not match provider model")
        if not request.streaming:
            raise ValueError("NVIDIA adapter currently verifies streamed completions only")
        started = time.monotonic()
        response = await self._client.chat(
            request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        content = response.get("content")
        status = response.get("status")
        completed = bool(content) and status == 200
        return GenerationResult(
            content=content if completed else None,
            completed=completed,
            provider=self.provider_name,
            model=self.model,
            latency_ms=round((time.monotonic() - started) * 1000),
            status_code=status,
            error_code=None if completed else _normalize_error(response.get("error"), status),
            usage=response.get("usage") or {},
            reasoning_chars=response.get("reasoning_chars") or 0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()
