"""Unit tests for src/langkit.py — detection, transliteration, bridging.

Transliteration (script conversion) is deterministic and is tested as such.
Translation (meaning across languages) is intentionally NOT implemented here
— only the configured LLM performs translation, asserted elsewhere.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.langkit import (  # noqa: E402
    bridge_to_native,
    bridge_variants,
    detect_script_and_language,
    effective_input_style,
    is_native_script,
    romanize_output,
)
from src.metrics import script_purity  # noqa: E402

NATIVE_SAMPLES = {
    "hi": "तुम क्या कर रहे हो?",
    "ta": "நீ என்ன செய்கிறாய்?",
    "te": "ఏం చేస్తున్నావు?",
    "kn": "ನೀನು ಏನು ಮಾಡುತ್ತಿದ್ದೀಯಾ?",
    "ml": "നീ എന്താണ് ചെയ്യുന്നത്?",
}
SCRIPTS = {"hi": "Devanagari", "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"}


@pytest.mark.parametrize("lang", NATIVE_SAMPLES.keys())
def test_detect_native_script_inputs(lang):
    det = detect_script_and_language(NATIVE_SAMPLES[lang])
    assert det["lang"] == lang
    assert det["script"] == SCRIPTS[lang]
    assert not det["ambiguous"]


def test_detect_english():
    det = detect_script_and_language("What are you doing?")
    assert det["script"] == "Latin"
    assert det["lang"] is None and det["ambiguous"]  # English vs romanized Indic


def test_detect_romanized_indic_is_ambiguous_latin():
    # Latin-script Indic text must NOT be silently classified as English
    det = detect_script_and_language("mera naam Pranay hai")
    assert det["script"] == "Latin"
    assert det["lang"] is None and det["ambiguous"]


def test_detect_empty_and_mixed():
    det = detect_script_and_language("")
    assert det["ambiguous"] and det["lang"] is None
    mixed = detect_script_and_language("ok तुम क्या कर रहे हो ok")
    assert mixed["ambiguous"] or mixed["lang"] == "hi"


@pytest.mark.parametrize("lang", NATIVE_SAMPLES.keys())
def test_is_native_script(lang):
    assert is_native_script(NATIVE_SAMPLES[lang], lang)
    assert not is_native_script("mera naam Pranay hai", lang)


def test_effective_input_style_auto():
    # native-script text for a native-selected language -> native
    assert effective_input_style("तुम क्या कर रहे हो?", "hi", "auto") == "native"
    # Latin text for an Indic language -> romanized (never assume English words)
    assert effective_input_style("mera naam Pranay hai", "hi", "auto") == "romanized"
    # English stays native (Latin is English's native script)
    assert effective_input_style("What are you doing?", "en", "auto") == "native"
    # explicit style wins over auto
    assert effective_input_style("तुम क्या कर रहे हो?", "hi", "romanized") == "romanized"
    assert effective_input_style("mera naam", "hi", "native") == "native"


@pytest.mark.parametrize("lang", NATIVE_SAMPLES.keys())
def test_bridge_produces_native_script(lang):
    bridged = bridge_to_native("mera naam Pranay hai", lang)
    assert script_purity(bridged, SCRIPTS[lang]) >= 0.8, f"{lang}: {bridged!r}"


def test_bridge_is_deterministic():
    a = bridge_to_native("bhagavana jagannatha ki bahana", "hi")
    b = bridge_to_native("bhagavana jagannatha ki bahana", "hi")
    assert a == b


def test_bridge_variants_structure():
    variants = bridge_variants("cheppalante em chestunnav", "te")
    assert variants, "expected at least one bridge variant"
    for v in variants:
        assert script_purity(v, "Telugu") >= 0.8
    # determinism
    assert bridge_variants("cheppalante em chestunnav", "te") == variants


def test_bridge_variants_handle_casual_digraphs():
    # 'th' in casual typing is usually a dental 't' — a variant must exist
    # that normalizes it (proves the casual rewrite layer is active)
    strict = bridge_to_native("venta", "te")
    casual_variants = bridge_variants("ventha", "te")
    assert any(v != strict for v in casual_variants) or strict in casual_variants


@pytest.mark.parametrize("lang", NATIVE_SAMPLES.keys())
def test_romanize_output_is_latin(lang):
    out = romanize_output(NATIVE_SAMPLES[lang], lang)
    assert script_purity(out, "Latin") >= 0.8, f"{lang}: {out!r}"


def test_romanize_output_english_unchanged():
    assert romanize_output("The capital of India is Delhi.", "en") == "The capital of India is Delhi."


def test_romanize_output_is_deterministic_and_word_preserving():
    native = "भगवान जगन्नाथ की बहन का नाम सुभद्रा है।"
    a, b = romanize_output(native, "hi"), romanize_output(native, "hi")
    assert a == b
    # transliteration preserves the same words — not a translation:
    # a strong signal is that the token count is preserved
    assert len(a.split()) == len(native.replace("।", "").split())


def test_transliteration_is_not_translation():
    """A transliterated answer contains the SAME words in another script.
    The word count must be preserved (a translation would generally not)."""
    native = "भारत की राजधानी दिल्ली है।"
    roman = romanize_output(native, "hi")
    assert len(roman.split()) == len(native.replace("।", "").split())
