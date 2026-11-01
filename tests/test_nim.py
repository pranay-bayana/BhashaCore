import asyncio
import json

import httpx

from src.nim import NimClient


class StreamResponse:
    status_code = 200
    async def __aenter__(self): return self
    async def __aexit__(self, *args): return False
    async def aiter_lines(self):
        for value in self.lines:
            yield value


class FakeClient:
    def __init__(self, lines): self.response = StreamResponse(); self.response.lines = lines
    def stream(self, *args, **kwargs): return self.response
    async def aclose(self): pass


def test_stream_requires_done_marker(monkeypatch):
    monkeypatch.setattr('src.nim.get_api_key', lambda: 'test')
    monkeypatch.setattr('src.nim.MAX_RETRIES', 1)
    client = NimClient('test-model')
    client.client = FakeClient(['data: ' + json.dumps({'choices': [{'delta': {'content': 'partial'}}]})])
    client.pace = 0
    result = asyncio.run(client.chat([{'role': 'user', 'content': 'x'}], max_tokens=8))
    assert result['content'] is None
    assert result['error'] == 'stream ended without completion marker'


def test_stream_completion_returns_content(monkeypatch):
    monkeypatch.setattr('src.nim.get_api_key', lambda: 'test')
    client = NimClient('test-model')
    client.client = FakeClient([
        'data: ' + json.dumps({'choices': [{'delta': {'content': 'OK'}}]}),
        'data: [DONE]',
    ])
    client.pace = 0
    result = asyncio.run(client.chat([{'role': 'user', 'content': 'x'}], max_tokens=8))
    assert result['content'] == 'OK'
    assert result['status'] == 200


def test_timeout_does_not_retry_generation(monkeypatch):
    class TimeoutClient:
        def __init__(self): self.calls = 0
        def stream(self, *args, **kwargs):
            self.calls += 1
            raise httpx.ReadTimeout('provider stalled')
        async def aclose(self): pass

    monkeypatch.setattr('src.nim.get_api_key', lambda: 'test')
    client = NimClient('test-model')
    fake = TimeoutClient()
    client.client = fake
    client.pace = 0
    result = asyncio.run(client.chat([{'role': 'user', 'content': 'x'}], max_tokens=8))
    assert result['content'] is None
    assert result['error'] == 'timeout'
    assert fake.calls == 1
