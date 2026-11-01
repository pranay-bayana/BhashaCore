"""Provider-neutral backend generation contract.

The Flask route continues to use the existing NVIDIA path until a provider has
produced a verified response. This module is deliberately independent of Flask,
retrieval, persistence, and frontend contracts so another provider can be
added without changing those layers.
"""
from __future__ import annotations

import time
import json
import os
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol

import httpx


SARVAM_DEFAULT_BASE_URL = "https://api.sarvam.ai/v1"
SARVAM_DEFAULT_MODEL = "sarvam-105b-conversations"


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


def get_sarvam_api_key() -> str:
    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        raise RuntimeError("SARVAM_API_KEY is required for the Sarvam provider")
    return key


class SarvamGenerationProvider:
    """OpenAI-compatible Sarvam streaming adapter with completion verification."""

    provider_name = "sarvam"

    def __init__(
        self,
        model: str | None = None,
        *,
        client: Any | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | None = None,
    ):
        self.model = model or os.environ.get("SARVAM_MODEL", SARVAM_DEFAULT_MODEL)
        if client is None:
            client = httpx.AsyncClient(
                base_url=(base_url or os.environ.get("SARVAM_BASE_URL", SARVAM_DEFAULT_BASE_URL)).rstrip("/"),
                headers={
                    "Authorization": f"Bearer {api_key or get_sarvam_api_key()}",
                    "Content-Type": "application/json",
                },
                timeout=timeout or httpx.Timeout(connect=10, read=30, write=10, pool=10),
                trust_env=False,
            )
        self._client = client

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if request.model != self.model:
            raise ValueError("request model does not match provider model")
        if not request.streaming:
            raise ValueError("Sarvam adapter currently verifies streamed completions only")
        started = time.monotonic()
        payload = {
            "model": self.model,
            "messages": request.messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": True,
        }
        content: list[str] = []
        usage: dict[str, Any] = {}
        reasoning_chars = 0
        completed = False
        status: int | None = None
        try:
            async with self._client.stream(
                "POST", "/chat/completions", json=payload,
                headers={"Accept": "text/event-stream"},
            ) as response:
                status = response.status_code
                if status != 200:
                    return GenerationResult(
                        content=None, completed=False, provider=self.provider_name, model=self.model,
                        latency_ms=round((time.monotonic() - started) * 1000), status_code=status,
                        error_code=f"provider_http_{status}",
                    )
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        completed = True
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    usage = event.get("usage") or usage
                    for choice in event.get("choices") or []:
                        delta = choice.get("delta") or {}
                        if delta.get("content"):
                            content.append(delta["content"])
                        reasoning = delta.get("reasoning_content")
                        if reasoning:
                            reasoning_chars += len(reasoning)
        except httpx.TimeoutException:
            return GenerationResult(None, False, self.provider_name, self.model,
                                    round((time.monotonic() - started) * 1000), status, "provider_timeout")
        except httpx.TransportError:
            return GenerationResult(None, False, self.provider_name, self.model,
                                    round((time.monotonic() - started) * 1000), status, "provider_transport_error")
        answer = "".join(content).strip()
        if not completed:
            return GenerationResult(None, False, self.provider_name, self.model,
                                    round((time.monotonic() - started) * 1000), status,
                                    "provider_incomplete_stream", usage, reasoning_chars)
        if not answer:
            return GenerationResult(None, False, self.provider_name, self.model,
                                    round((time.monotonic() - started) * 1000), status,
                                    "provider_empty_completion", usage, reasoning_chars)
        return GenerationResult(answer, True, self.provider_name, self.model,
                                round((time.monotonic() - started) * 1000), status,
                                usage=usage, reasoning_chars=reasoning_chars)

    async def aclose(self) -> None:
        await self._client.aclose()


def create_generation_provider(
    provider_name: str | None = None,
    model: str | None = None,
) -> GenerationProvider:
    """Build a configured provider without coupling selection to Flask.

    `GENERATION_PROVIDER=sarvam` selects the verified Sarvam adapter; the
    default keeps the existing NVIDIA implementation available.
    """
    selected = (provider_name or os.environ.get("GENERATION_PROVIDER", "nvidia")).lower()
    if selected == "sarvam":
        return SarvamGenerationProvider(model=model)
    if selected == "nvidia":
        from src.config import PRIMARY_GENERATOR
        return NvidiaGenerationProvider(model=model or os.environ.get("NVIDIA_MODEL", PRIMARY_GENERATOR))
    raise ValueError(f"unsupported generation provider: {selected}")
