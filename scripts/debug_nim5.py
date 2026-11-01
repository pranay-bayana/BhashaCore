"""Debug 5: warm-up behaviour + concurrency probe for candidate generator models."""
import asyncio
import time

from src.nim import NimClient


async def seq_test(model, n=3):
    c = NimClient(model, concurrency=1)
    for i in range(n):
        t0 = time.time()
        r = await c.chat([{"role": "user", "content": "Reply with exactly: OK"}], max_tokens=2000)
        print(f"[{model} seq#{i}] {time.time()-t0:.1f}s status={r.get('status')} "
              f"content={r.get('content')!r} err={str(r.get('error'))[:80]}", flush=True)
    await c.aclose()


async def conc_test(model, n=8):
    c = NimClient(model, concurrency=n)

    async def one(i):
        t0 = time.time()
        r = await c.chat([{"role": "user", "content": f"Say the number {i} and nothing else"}], max_tokens=2000)
        return (f"[{model} conc#{i}] {time.time()-t0:.1f}s status={r.get('status')} "
                f"content={(r.get('content') or '')[:30]!r}")

    for fut in asyncio.as_completed([one(i) for i in range(n)]):
        print(await fut, flush=True)
    await c.aclose()


async def main():
    await seq_test("z-ai/glm-5.3-flash", 3)
    await conc_test("z-ai/glm-5.3-flash", 8)
    await conc_test("minimaxai/minimax-m3.1-flash", 8)
    t0 = time.time()
    c = NimClient("deepseek-ai/deepseek-v4.1-flash", concurrency=1)
    r = await c.chat([{"role": "user", "content": "Reply with exactly: OK"}], max_tokens=2000)
    print(f"[deepseek retest] {time.time()-t0:.1f}s status={r.get('status')} "
          f"content={r.get('content')!r} err={str(r.get('error'))[:80]}", flush=True)
    await c.aclose()


asyncio.run(main())
