"""Debug 3: streaming chat test across candidate models (unbuffered prints)."""
import asyncio
import sys
import time

from src.nim import NimClient

MODELS = [
    "z-ai/glm-5.3-flash",
    "deepseek-ai/deepseek-v4.1-flash",
    "z-ai/glm-5.3",
    "openai/gpt-oss-20b",
]


async def test(model):
    c = NimClient(model, concurrency=1)
    t0 = time.time()
    r = await c.chat([{"role": "user", "content": "Reply with exactly: OK"}], max_tokens=2000)
    dt = time.time() - t0
    print(f"[{model}] status={r.get('status')} {dt:.1f}s content={r.get('content')!r} "
          f"reasoning_chars={r.get('reasoning_chars')} usage={r.get('usage')}", flush=True)
    if r.get("error"):
        print(f"    error: {str(r['error'])[:200]}", flush=True)
    await c.aclose()


async def main():
    for m in MODELS:
        try:
            await test(m)
        except Exception as e:
            print(f"[{m}] EXC {type(e).__name__}: {e}", flush=True)


asyncio.run(main())
