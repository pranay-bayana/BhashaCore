"""Bounded backend-only NVIDIA NIM diagnostic. Never prints credentials."""
import asyncio
import argparse
import json
import socket
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PRIMARY_GENERATOR
from src.nim import get_api_key, get_base_url


async def request(client, payload, streaming: bool):
    started = time.monotonic()
    if not streaming:
        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        body = response.json()
        content = (body.get("choices") or [{}])[0].get("message", {}).get("content", "")
        return {"completed": bool(content), "content_chars": len(content), "first_token_s": None,
                "total_s": round(time.monotonic() - started, 3), "status": response.status_code}

    first_token = None
    content, completed = [], False
    async with client.stream("POST", "/chat/completions", json={**payload, "stream": True},
                             headers={"Accept": "text/event-stream"}) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.startswith("data:"):
                continue
            payload_line = line[5:].strip()
            if payload_line == "[DONE]":
                completed = True
                break
            try:
                data = json.loads(payload_line)
            except json.JSONDecodeError:
                continue
            delta = ((data.get("choices") or [{}])[0].get("delta") or {}).get("content")
            if delta:
                if first_token is None:
                    first_token = time.monotonic() - started
                content.append(delta)
    return {"completed": completed and bool(content), "content_chars": len("".join(content)),
            "first_token_s": round(first_token, 3) if first_token is not None else None,
            "total_s": round(time.monotonic() - started, 3), "status": 200}


async def main(mode: str = "both"):
    base = get_base_url()
    host = httpx.URL(base).host
    socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    print("DNS: PASS")
    headers = {"Authorization": f"Bearer {get_api_key()}", "Content-Type": "application/json"}
    timeout = httpx.Timeout(connect=10, read=25, write=10, pool=10)
    payload = {"model": PRIMARY_GENERATOR, "messages": [{"role": "user", "content": "Reply with exactly OK."}],
               "max_tokens": 8, "temperature": 0}
    async with httpx.AsyncClient(base_url=base, headers=headers, timeout=timeout, trust_env=False) as client:
        models = await asyncio.wait_for(client.get("/models"), timeout=15)
        models.raise_for_status()
        assert PRIMARY_GENERATOR in {m.get("id") for m in models.json().get("data", [])}
        print("authentication and configured model availability: PASS")
        probes = (("non-streaming", False), ("streaming", True))
        for name, streaming in probes:
            if mode != "both" and mode != name:
                continue
            try:
                result = await asyncio.wait_for(request(client, payload, streaming), timeout=30)
                print(f"{name}: {'PASS' if result['completed'] else 'FAIL'} "
                      f"status={result['status']} first_token_s={result['first_token_s']} "
                      f"total_s={result['total_s']} content_chars={result['content_chars']}")
            except (httpx.HTTPError, httpx.TimeoutException, httpx.TransportError) as exc:
                print(f"{name}: FAIL error={type(exc).__name__}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("both", "non-streaming", "streaming"), default="both")
    asyncio.run(main(parser.parse_args().mode))
