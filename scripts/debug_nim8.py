"""Debug 8: watch the minimax quota window - one tiny call every 45s."""
import asyncio
import json
import pathlib
import time

import httpx

key = json.loads((pathlib.Path.home() / ".local" / "share" / "opencode" / "auth.json").read_text())["nvidia"]["key"]
BASE = "https://integrate.api.nvidia.com/v1"


async def check():
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
               "Accept": "text/event-stream"}
    payload = {"model": "minimaxai/minimax-m3.1-flash",
               "messages": [{"role": "user", "content": "hi"}],
               "max_tokens": 512, "stream": True}
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=10), trust_env=False) as c:
            async with c.stream("POST", f"{BASE}/chat/completions", headers=headers, json=payload) as r:
                if r.status_code != 200:
                    print(f"{time.strftime('%H:%M:%S')} HTTP {r.status_code} ({time.time()-t0:.1f}s)", flush=True)
                    return False
                n = 0
                async for line in r.aiter_lines():
                    if line.startswith("data:"):
                        n += 1
                        if line[5:].strip() == "[DONE]":
                            break
                print(f"{time.strftime('%H:%M:%S')} OK 200 ({time.time()-t0:.1f}s, {n} chunks) - QUOTA AVAILABLE", flush=True)
                return True
    except Exception as e:
        print(f"{time.strftime('%H:%M:%S')} EXC {type(e).__name__} ({time.time()-t0:.1f}s)", flush=True)
        return False


async def main():
    for i in range(40):
        await check()
        await asyncio.sleep(45)


asyncio.run(main())
