"""Romanized-query stress set: synthetic transliteration of native-script questions.

We approximate the very common real-world behaviour of Indian users typing their
language in Latin script ("Hinglish"/"Tanglish") by transliterating the native
question text to ITRANS and lowercasing. ITRANS-lowercase is close to the
informal romanization users type (e.g. Hindi "प्रधानमंत्री" -> "pradhAnamantrI"
-> "pradhanamantri").

This is a synthetic approximation (it cannot capture the true lossiness of
casual romanization); the report states this explicitly.
"""
import re

from indic_transliteration import sanscript

_SCHEMES = {
    "Devanagari": sanscript.DEVANAGARI,
    "Tamil": sanscript.TAMIL,
    "Telugu": sanscript.TELUGU,
    "Kannada": sanscript.KANNADA,
    "Malayalam": sanscript.MALAYALAM,
}

# ITRANS artifacts that look unnatural in casual typing.
_CLEANUPS = [
    (r"\.a\b", " "),   # avagraha
    (r"\\", ""),
    (r"\^\^", ""),
    (r"\^", ""),
    (r"~", ""),
    (r"\.", ""),
]


def romanize(text: str, script: str) -> str:
    """Transliterate native-script text to lowercase Latin (ITRANS-based)."""
    scheme = _SCHEMES.get(script)
    if scheme is None:  # already Latin
        return text
    try:
        out = sanscript.transliterate(text, _from=scheme, _to=sanscript.ITRANS)
    except Exception:
        # Fallback: pivot through Devanagari (lossy for some Dravidian sounds).
        out = sanscript.transliterate(
            sanscript.transliterate(text, _from=scheme, _to=sanscript.DEVANAGARI),
            _from=sanscript.DEVANAGARI,
            _to=sanscript.ITRANS,
        )
    out = out.lower()
    for pat, rep in _CLEANUPS:
        out = re.sub(pat, rep, out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def make_stress_question(question: str, script: str) -> dict:
    return {
        "question": romanize(question, script),
        "romanized": True,
        "source_script": script,
    }
