"""Debug 2: list model ids; test chat on candidate models with timing."""
import json
import pathlib
import time

import httpx

key = json.loads((pathlib.Path.home() / ".local" / "share" / "opencode" / "auth.json").read_text())["nvidia"]["key"]
base = "https://integrate.api.nvidia.com/v1"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

r = httpx.get(f"{base}/models", headers=headers, timeout=30, trust_env=False)
ids = [m["id"] for m in r.json().get("data", [])]
print(f"[models] {len(ids)} ids:")
for m in ids:
    print("  -", m)


def chat(model, timeout=240):
    t0 = time.time()
    try:
        r = httpx.post(
            f"{base}/chat/completions",
            headers=headers,
            json={"model": model, "messages": [{"role": "user", "content": "Reply with exactly: OK"}], "max_tokens": 8},
            timeout=timeout,
            trust_env=False,
        )
        dt = time.time() - t0
        print(f"[chat {model}] {r.status_code} {dt:.1f}s :: {r.text[:200]}")
    except Exception as e:
        print(f"[chat {model}] FAILED after {time.time()-t0:.1f}s: {type(e).__name__}: {str(e)[:120]}")


for m in ["z-ai/glm-5.3-flash", "deepseek-ai/deepseek-v4.1-flash", "z-ai/glm-5.3"]:
    chat(m)
