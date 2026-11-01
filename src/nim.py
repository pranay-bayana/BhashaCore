"""Minimal async client for the NVIDIA NIM OpenAI-compatible endpoint.

Key resolution order:
  1. env NVIDIA_API_KEY
  2. ~/.local/share/opencode/auth.json  (the local OpenCode "nvidia" provider entry)
Base URL: env NVIDIA_BASE_URL, default https://integrate.nvidia.com/v1
"""
import asyncio
import json
import logging
import os
import random
import time
from pathlib import Path

import httpx

from src.config import (
    COOLDOWN_ON_429,
    CONCURRENCY,
    LAUNCH_PACE,
    MAX_OUT_TOKENS,
    MAX_RETRIES,
    RATE_LIMIT_SLEEP,
    TIMEOUT_CONNECT,
    TIMEOUT_READ,
)

DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
AUTH_FILE = Path.home() / ".local" / "share" / "opencode" / "auth.json"
logger = logging.getLogger(__name__)


def get_api_key() -> str:
    key = os.environ.get("NVIDIA_API_KEY")
    if key:
        return key
    try:
        data = json.loads(AUTH_FILE.read_text())
        k = data.get("nvidia", {}).get("key")
        if k:
            return k
    except Exception:
        pass
    raise RuntimeError(
        "NVIDIA API key not found. Export NVIDIA_API_KEY or configure the "
        "OpenCode nvidia provider in ~/.local/share/opencode/auth.json"
    )


def get_base_url() -> str:
    return os.environ.get("NVIDIA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


class NimClient:
    def __init__(self, model: str, concurrency: int = CONCURRENCY, pace: float = LAUNCH_PACE):
        self.model = model
        self.base_url = get_base_url()
        self.key = get_api_key()
        self.sem = asyncio.Semaphore(concurrency)
        self.pace = pace
        self._last_launch = 0.0
        self._cooldown_until = 0.0
        self._pace_lock = asyncio.Lock()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(TIMEOUT_READ, connect=TIMEOUT_CONNECT),
            trust_env=False,  # ignore proxy env vars - they hang on this network
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    async def _pace_launch(self):
        """Rate-limit launches: one per `self.pace` seconds, plus a shared 429 cooldown."""
        async with self._pace_lock:
            now = time.monotonic()
            if now < self._cooldown_until:
                await asyncio.sleep(self._cooldown_until - now)
                now = time.monotonic()
            wait = self._last_launch + self.pace - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_launch = time.monotonic()

    async def aclose(self):
        await self.client.aclose()

    async def list_models(self) -> list:
        r = await self.client.get(f"{self.base_url}/models")
        r.raise_for_status()
        return sorted(m.get("id", "") for m in r.json().get("data", []))

    async def chat(
        self,
        messages: list,
        temperature: float = 0.0,
        max_tokens: int = MAX_OUT_TOKENS,
    ) -> dict:
        started = time.monotonic()
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        url = f"{self.base_url}/chat/completions"
        last_err = "no attempts made"
        async with self.sem:
            await self._pace_launch()
            for attempt in range(MAX_RETRIES):
                content, reasoning_chars, usage = [], 0, {}
                completed = False
                try:
                    async with self.client.stream(
                        "POST", url, json=payload,
                        headers={"Accept": "text/event-stream"},
                    ) as r:
                        if r.status_code != 200:
                            body = (await r.aread()).decode("utf-8", "replace")
                            last_err = f"HTTP {r.status_code}: {body[:150]}"
                            if r.status_code == 429:
                                # pause every launch of this client for a shared cooldown
                                self._cooldown_until = max(
                                    self._cooldown_until,
                                    time.monotonic() + COOLDOWN_ON_429,
                                )
                                await asyncio.sleep(RATE_LIMIT_SLEEP + random.uniform(0, 5))
                                continue
                            if r.status_code in (500, 502, 503, 504):
                                await asyncio.sleep(min(2 ** attempt * 2, 30))
                                continue
                            if r.status_code == 400 and "temperature" in body:
                                payload.pop("temperature", None)
                                continue
                            return {"content": None, "error": last_err, "status": r.status_code}
                        async for line in r.aiter_lines():
                            if not line or not line.startswith("data:"):
                                continue
                            data = line[5:].strip()
                            if data == "[DONE]":
                                completed = True
                                break
                            try:
                                obj = json.loads(data)
                            except json.JSONDecodeError:
                                continue
                            if obj.get("usage"):
                                usage = obj["usage"]
                            for choice in obj.get("choices") or []:
                                delta = choice.get("delta") or {}
                                if delta.get("content"):
                                    content.append(delta["content"])
                                rc = delta.get("reasoning_content")
                                if rc:
                                    reasoning_chars += len(rc)
                    if not completed:
                        # A clean TCP EOF is not an OpenAI-compatible stream
                        # completion. Returning partial text as an answer would
                        # misrepresent a provider interruption as success.
                        last_err = "stream ended without completion marker"
                        # The provider may already have performed inference
                        # before a proxy terminates the stream. Retrying here
                        # risks duplicate generated answers and duplicate cost.
                        return {"content": None, "error": last_err, "status": 0}
                    result = {
                        "content": "".join(content).strip(),
                        "usage": usage,
                        "reasoning_chars": reasoning_chars,
                        "status": 200,
                    }
                    logger.info("nim_chat status=%s latency_ms=%d content_chars=%d", 200,
                                (time.monotonic() - started) * 1000, len(result["content"]))
                    return result
                except httpx.TimeoutException:
                    last_err = "timeout"
                    # A timeout is ambiguous: do not submit the user's prompt
                    # a second time when the provider may still be processing it.
                    return {"content": None, "error": last_err, "status": 0}
                except httpx.TransportError:
                    last_err = "transport error"
                    return {"content": None, "error": last_err, "status": 0}
            logger.warning("nim_chat status=%s latency_ms=%d error=%s", 0,
                           (time.monotonic() - started) * 1000, last_err)
            return {"content": None, "error": f"exhausted retries (last: {last_err})", "status": 0}
