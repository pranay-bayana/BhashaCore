"""Credential-safe bounded Sarvam completion and language diagnostic."""
import asyncio
import json
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=False)

from src.generation_provider import (  # noqa: E402
    GenerationRequest,
    SARVAM_DEFAULT_MODEL,
    SarvamGenerationProvider,
)


QUESTIONS = {
    "en": "Reply with exactly OK.",
    "hi": "केवल ठीक लिखें।",
    "te": "సరే అని మాత్రమే రాయండి.",
    "ta": "சரி என்று மட்டும் எழுதுங்கள்.",
    "kn": "ಸರಿ ಎಂದು ಮಾತ್ರ ಬರೆಯಿರಿ.",
    "ml": "ശരി എന്ന് മാത്രം എഴുതുക.",
    "hi_romanized": "Keval theek likhen.",
}


def script_summary(value: str) -> str:
    names = {unicodedata.name(char, "").split(" ", 1)[0] for char in value if char.isalpha()}
    return ",".join(sorted(name for name in names if name)) or "LATIN/OTHER"


async def main():
    provider = SarvamGenerationProvider()
    try:
        for language, question in QUESTIONS.items():
            started = time.monotonic()
            result = await provider.generate(GenerationRequest(
                messages=[{"role": "user", "content": question}],
                model=provider.model,
                max_tokens=64,
                temperature=0,
            ))
            print(
                f"{language}: {'PASS' if result.completed else 'FAIL'} "
                f"status={result.status_code} latency_s={round((time.monotonic() - started), 3)} "
                f"content_chars={len(result.content or '')} script={script_summary(result.content or '')} "
                f"error={result.error_code or '-'}"
            )
    finally:
        await provider.aclose()


if __name__ == "__main__":
    asyncio.run(main())
