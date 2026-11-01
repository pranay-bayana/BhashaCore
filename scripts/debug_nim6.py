"""Debug 6: probe remaining catalog models for speed + basic Indic capability."""
import asyncio
import json
import pathlib
import time

import httpx

key = json.loads((pathlib.Path.home() / ".local" / "share" / "opencode" / "auth.json").read_text())["nvidia"]["key"]
BASE = "https://integrate.api.nvidia.com/v1"

HINDI_Q = "भगवान जगन्नाथ की बहन का नाम क्या है?"          # expected: सुभद्रा
TAMIL_Q = "இந்தியாவின் தேசியக் கொடியை வடிவமைத்தவர் யார்?"  # expected: பிங்கலி வெங்கையா

MODELS = [
    "openai/gpt-oss-20b",
    "nvidia/nemotron-3.5-super-vl-120b-a12b",
    "meta/muse-glimmer-30b",
    "stepfun-ai/step-5-preview",
    "google/diffusiongemma-26b-a4b-it",
    "poolside/laguna-xs-2.1",
]


async def probe(model, prompt, timeout=150, max_tokens=1500):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "stream": True,
    }
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=10), trust_env=False) as c:
            async with c.stream("POST", f"{BASE}/chat/completions", headers=headers, json=payload) as r:
                if r.status_code != 200:
                    body = (await r.aread()).decode("utf-8", "replace")[:200]
                    return f"HTTP{r.status_code} {time.time()-t0:.1f}s :: {body[:120]}"
                content = []
                async for line in r.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    d = line[5:].strip()
                    if d == "[DONE]":
                        break
                    try:
                        o = json.loads(d)
                    except json.JSONDecodeError:
                        continue
                    for ch in o.get("choices") or []:
                        if (ch.get("delta") or {}).get("content"):
                            content.append(ch["delta"]["content"])
                return f"OK {time.time()-t0:.1f}s :: {''.join(content)[:120]!r}"
    except Exception as e:
        return f"FAIL {time.time()-t0:.1f}s {type(e).__name__}"


async def main():
    for m in MODELS:
        r = await probe(m, "Reply with exactly: OK")
        print(f"[{m}] ok-test: {r}", flush=True)
        if r.startswith("OK") and float(r.split()[1].rstrip("s")) < 30:
            h = await probe(m, HINDI_Q)
            print(f"[{m}] hindi: {h}", flush=True)
            t = await probe(m, TAMIL_Q)
            print(f"[{m}] tamil: {t}", flush=True)


asyncio.run(main())
