"""Debug 4: SSE streaming with Accept: text/event-stream + first-chunk timing."""
import asyncio
import json
import pathlib
import time

import httpx

key = json.loads((pathlib.Path.home() / ".local" / "share" / "opencode" / "auth.json").read_text())["nvidia"]["key"]
base = "https://integrate.api.nvidia.com/v1"


async def test(model):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "max_tokens": 2000,
        "stream": True,
    }
    t0 = time.time()
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10, read=240, write=30, pool=10), trust_env=False
        ) as c:
            async with c.stream("POST", f"{base}/chat/completions", headers=headers, json=payload) as r:
                print(f"[{model}] HTTP {r.status_code} @ {time.time()-t0:.1f}s", flush=True)
                if r.status_code != 200:
                    body = (await r.aread()).decode("utf-8", "replace")[:300]
                    print(f"[{model}] error body: {body}", flush=True)
                    return
                n_lines, content, reasoning = 0, [], 0
                first = None
                async for line in r.aiter_lines():
                    n_lines += 1
                    if first is None:
                        first = time.time() - t0
                        print(f"[{model}] first chunk at {first:.1f}s", flush=True)
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    for ch in obj.get("choices") or []:
                        d = ch.get("delta") or {}
                        if d.get("content"):
                            content.append(d["content"])
                        if d.get("reasoning_content"):
                            reasoning += len(d["reasoning_content"])
                print(f"[{model}] DONE {time.time()-t0:.1f}s lines={n_lines} "
                      f"content={''.join(content)!r} reasoning_chars={reasoning}", flush=True)
    except Exception as e:
        print(f"[{model}] FAILED {time.time()-t0:.1f}s {type(e).__name__}: {str(e)[:150]}", flush=True)


async def main():
    for m in ["z-ai/glm-5.3-flash", "deepseek-ai/deepseek-v4.1-flash",
              "minimaxai/minimax-m3.1-flash", "z-ai/glm-5.3"]:
        await test(m)


asyncio.run(main())
