"""Debug NIM connectivity with per-step timing."""
import json
import pathlib
import time

import httpx

key = json.loads((pathlib.Path.home() / ".local" / "share" / "opencode" / "auth.json").read_text())["nvidia"]["key"]
base = "https://integrate.api.nvidia.com/v1"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

t0 = time.time()
try:
    r = httpx.get(f"{base}/models", headers=headers, timeout=30, trust_env=False)
    print(f"[models] status={r.status_code} bytes={len(r.content)} time={time.time()-t0:.1f}s")
except Exception as e:
    print(f"[models] FAILED after {time.time()-t0:.1f}s: {type(e).__name__}: {e}")

t0 = time.time()
try:
    r = httpx.post(
        f"{base}/chat/completions",
        headers=headers,
        json={"model": "z-ai/glm-5.3", "messages": [{"role": "user", "content": "Reply with exactly: OK"}], "max_tokens": 10},
        timeout=90,
        trust_env=False,
    )
    print(f"[chat glm-5.3] status={r.status_code} time={time.time()-t0:.1f}s")
    print(r.text[:400])
except Exception as e:
    print(f"[chat] FAILED after {time.time()-t0:.1f}s: {type(e).__name__}: {e}")
