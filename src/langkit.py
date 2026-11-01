"""Language and script toolkit for the BhashaCore chat pipeline.

Three DISTINCT operations (never conflated):

* Detection      — decide which language/script the input is written in.
* Transliteration— convert a language between scripts, preserving the same
                   words (native -> Latin or Latin -> native). Deterministic,
                   provided by `indic_transliteration` via `src.translit`.
* Translation    — convert MEANING between languages. Only the configured
                   LLM can do this (system prompt); there is deliberately no
                   deterministic "translation" here, so nothing can silently
                   pretend to have translated.

Casual-romanization limits (documented, tested): human "Hinglish"-style input
("mera naam", "em chestunnav") is lossier than the project's ITRANS-lowercase
romanization ("bhagavana jagannatha"); the bridge is approximate and the
retrieval experiment in `scripts/eval_romanized_bridge.py` measures exactly
how much it helps on the same evaluation questions.
"""

import re

from src.config import LANGS
from src.metrics import script_purity
from src.translit import romanize as _romanize_native

_SCRIPT_TO_LANG = {
    "Devanagari": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Latin": "en",
}

# Indic scripts that can arrive romanized (Latin letters, Indic language).
_INDIC_LANGS = {"hi", "ta", "te", "kn", "ml"}


def _letters(text: str) -> str:
    return "".join(ch for ch in (text or "") if ch.isalpha())


def detect_script_and_language(text: str) -> dict:
    """Detect the dominant script and, when unambiguous, its language.

    Returns {"script", "lang" (or None), "ambiguous" (bool), "purity"}.
    Latin-script text is inherently ambiguous between English and any
    romanized Indic language — `ambiguous` is True and `lang` is None;
    callers must not assume Latin means English.
    """
    letters = _letters(text)
    if not letters:
        return {"script": None, "lang": None, "ambiguous": True, "purity": 0.0}
    best_script, best_purity = "Latin", 0.0
    for script in ("Latin", "Devanagari", "Tamil", "Telugu", "Kannada", "Malayalam"):
        p = script_purity(letters, script)
        if p > best_purity:
            best_script, best_purity = script, p
    if best_script == "Latin":
        return {"script": "Latin", "lang": None, "ambiguous": True, "purity": best_purity}
    lang = _SCRIPT_TO_LANG[best_script]
    # Mixed-script input: dominant script wins only if it is clearly dominant.
    ambiguous = best_purity < 0.6
    return {"script": best_script, "lang": None if ambiguous else lang, "ambiguous": ambiguous, "purity": best_purity}


def is_native_script(text: str, lang: str) -> bool:
    """True when the text is written in the language's native script."""
    expected = LANGS.get(lang, {}).get("script")
    if not expected:
        return False
    return script_purity(_letters(text), expected) >= 0.6


def effective_input_style(text: str, input_lang: str, requested_style: str) -> str:
    """Resolve the effective input style.

    'auto'  -> native script when the text matches the selected language's
               script; romanized when the language is Indic and the text is
               Latin; native for English.
    explicit -> used as given (the UI offers native/romanized).
    """
    if requested_style in ("native", "romanized"):
        return requested_style
    if input_lang in _INDIC_LANGS and not is_native_script(text, input_lang):
        return "romanized"
    return "native"


def bridge_to_native(latin_text: str, lang: str) -> str:
    """Transliterate Latin-script text to the language's native script.

    Approximate by design: casual romanization is lossy (no case marks for
    long vowels, no explicit schwa). Good enough to create lexical overlap
    for retrieval — measured in scripts/eval_romanized_bridge.py.
    """
    from indic_transliteration import sanscript

    scheme_by_lang = {
        "hi": sanscript.DEVANAGARI,
        "ta": sanscript.TAMIL,
        "te": sanscript.TELUGU,
        "kn": sanscript.KANNADA,
        "ml": sanscript.MALAYALAM,
    }
    target = scheme_by_lang.get(lang)
    if target is None:
        return latin_text
    text = re.sub(r"[^\w\s]", " ", latin_text or "")
    try:
        return sanscript.transliterate(text, _from=sanscript.ITRANS, _to=target)
    except Exception:
        return latin_text


# The project's ITRANS-lowercase romanization carries a few accent artifacts
# (e.g. Telugu "vèmta") that break strict ITRANS parsing; humans instead type
# digraphs ("th", "aa", "oo"). Normalize both so the bridge gets a fair input.
_ACCENT_FIXES = [
    ("è", "e"), ("ò", "o"), ("à", "a"), ("ì", "i"), ("ù", "u"),
]
_CASUAL_DIGRAPHS = [
    (r"th", "t"), (r"dh", "d"), (r"kh", "k"), (r"gh", "g"), (r"chh", "ch"),
    (r"aa", "A"), (r"ee", "I"), (r"oo", "U"), (r"ai", "ai"), (r"au", "au"),
]


def _normalize_accents(text: str) -> str:
    for src, dst in _ACCENT_FIXES:
        text = text.replace(src, dst)
    return text


def _casual_to_itrans(text: str) -> str:
    """Rewrite common casual-romanization digraphs to ITRANS long vowels."""
    for src, dst in _CASUAL_DIGRAPHS:
        text = re.sub(src, dst, text)
    return text


def bridge_variants(latin_text: str, lang: str) -> list:
    """Bridge variants for dual retrieval: strict ITRANS plus a
    casual-digraph normalization. Max-merge retrieval means extra variants
    can only surface more candidates, never remove any."""
    text = _normalize_accents(latin_text or "")
    if not text.strip():
        return []
    variants = []
    strict = bridge_to_native(text, lang)
    if strict.strip():
        variants.append(strict)
    casual = bridge_to_native(_casual_to_itrans(text), lang)
    if casual.strip() and casual != strict:
        variants.append(casual)
    return variants


def romanize_output(text: str, lang: str) -> str:
    """Render an answer in romanized (Latin) script for an Indic language.

    Deterministic transliteration of the SAME words — not a translation.
    English text is returned unchanged (it is already Latin script).
    """
    if lang not in _INDIC_LANGS or not text:
        return text
    return _romanize_native(text, LANGS[lang]["script"])
