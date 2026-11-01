"""Smoke test: verify NVIDIA NIM connectivity, list usable models, test a chat call."""
import asyncio

from src.nim import NimClient

KEYWORDS = ("glm", "deepseek", "qwen", "gpt-oss", "nemotron", "minimax", "gemma", "llama")


async def main():
    c = NimClient("z-ai/glm-5.3")
    try:
        try:
            models = await c.list_models()
            print(f"[models] {len(models)} available at {c.base_url}")
            for m in models:
                if any(k in m.lower() for k in KEYWORDS):
                    print("  -", m)
        except Exception as e:
            print(f"[models] listing failed: {e}")

        r = await c.chat([{"role": "user", "content": "Reply with exactly: OK"}], max_tokens=10)
        if r.get("content"):
            print(f"[chat] OK -> {r['content']!r} usage={r.get('usage')}")
        else:
            print(f"[chat] FAILED -> {r}")
    finally:
        await c.aclose()


if __name__ == "__main__":
    asyncio.run(main())
