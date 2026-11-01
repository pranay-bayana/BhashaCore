import asyncio

import pytest

from src.generation_provider import (
    GenerationRequest,
    NvidiaGenerationProvider,
)


class FakeNvidiaClient:
    def __init__(self, response):
        self.response = response
        self.closed = False

    async def chat(self, messages, temperature, max_tokens):
        return self.response

    async def aclose(self):
        self.closed = True


def request():
    return GenerationRequest(
        messages=[{"role": "user", "content": "hello"}],
        model="model-a",
        max_tokens=8,
    )


def test_nvidia_adapter_returns_completed_result_and_metrics():
    client = FakeNvidiaClient({"content": "OK", "status": 200, "usage": {"total_tokens": 2}})
    provider = NvidiaGenerationProvider("model-a", client_factory=lambda _: client)
    result = asyncio.run(provider.generate(request()))
    assert result.completed is True
    assert result.content == "OK"
    assert result.provider == "nvidia"
    assert result.latency_ms >= 0
    assert result.usage == {"total_tokens": 2}
    asyncio.run(provider.aclose())
    assert client.closed is True


@pytest.mark.parametrize(
    ("response", "expected_error"),
    [
        ({"content": None, "status": 0, "error": "timeout"}, "provider_timeout"),
        ({"content": None, "status": 0, "error": "stream ended without completion marker"}, "provider_incomplete_stream"),
        ({"content": None, "status": 404, "error": "HTTP 404"}, "provider_http_404"),
    ],
)
def test_nvidia_adapter_normalizes_failures(response, expected_error):
    provider = NvidiaGenerationProvider("model-a", client_factory=lambda _: FakeNvidiaClient(response))
    result = asyncio.run(provider.generate(request()))
    assert result.completed is False
    assert result.content is None
    assert result.error_code == expected_error


def test_nvidia_adapter_rejects_unverified_nonstreaming_path():
    provider = NvidiaGenerationProvider("model-a", client_factory=lambda _: FakeNvidiaClient({}))
    with pytest.raises(ValueError, match="streamed completions"):
        asyncio.run(provider.generate(GenerationRequest(
            messages=[{"role": "user", "content": "hello"}], model="model-a", max_tokens=8, streaming=False,
        )))
