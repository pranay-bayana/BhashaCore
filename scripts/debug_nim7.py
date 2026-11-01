"""Debug 7: what does minimax return right now? Status codes + headers."""
import asyncio
import json
import pathlib
import time

import httpx

key = json.loads((pathlib.Path.home() / ".local" / "share" / "opencode" / "auth.json").read_text())["nvidia"]["key"]
BASE = "https://integrate.api.nvidia.com/v1"


async def one(i, delay=0):
    await asyncio.sleep(delay)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    payload = {
        "model": "minimaxai/minimax-m3.1-flash",
        "messages": [{"role": "user", "content": f"Say the number {i}"}],
        "max_tokens": 100,
        "stream": True,
    }
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10), trust_env=False) as c:
            async with c.stream("POST", f"{BASE}/chat/completions", headers=headers, json=payload) as r:
                if r.status_code != 200:
                    body = (await r.aread()).decode("utf-8", "replace")[:150]
                    ra = r.headers.get("retry-after")
                    print(f"[{i}] HTTP {r.status_code} @ {time.time()-t0:.1f}s retry-after={ra} :: {body}", flush=True)
                    return
                content = []
                async for line in r.aiter_lines():
                    if line.startswith("data:"):
                        d = line[5:].strip()
                        if d == "[DONE]":
                            break
                        try:
                            o = json.loads(d)
                            for ch in o.get("choices") or []:
                                if (ch.get("delta") or {}).get("content"):
                                    content.append(ch["delta"]["content"])
                        except json.JSONDecodeError:
                            pass
                print(f"[{i}] OK {time.time()-t0:.1f}s :: {''.join(content)[:40]!r}", flush=True)
    except Exception as e:
        print(f"[{i}] EXC {time.time()-t0:.1f}s {type(e).__name__}: {str(e)[:100]}", flush=True)


async def main():
    await one(0)
    await asyncio.gather(*[one(i, delay=i * 0.5) for i in range(1, 9)])

asyncio.run(main())
