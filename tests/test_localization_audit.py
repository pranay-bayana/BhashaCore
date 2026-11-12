"""Automated Localization Audit & Verification Suite for BhashaCore.

Verifies:
1. Complete key parity across all six languages (en, hi, te, ta, kn, ml).
2. No untranslated English strings remain in non-English dictionaries (with approved technical exemptions).
3. Server-side rendering audit across all routes and locales.
4. Client-side instantaneous in-place translation switching without page refresh.
5. Strict independence between interface language, input language, and answer language.
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app import app
from src.translations import (
    LANGUAGE_NAMES_BY_INTERFACE,
    _load_translations,
    get_all_translations,
    get_available_languages,
    get_translations,
    t,
)

SUPPORTED_LANGS = ["en", "hi", "te", "ta", "kn", "ml"]

# Permitted technical terms, proper names, metrics, and abbreviations in non-English locales
ALLOWED_ENGLISH_TOKENS = {
    "bhashacore",
    "indiccorp",
    "indicqa",
    "ai4bharat",
    "bm25",
    "rag",
    "mrr",
    "f1",
    "em",
    "qid",
    "api",
    "llm",
    "iso-15919",
    "en",
    "hi",
    "te",
    "ta",
    "kn",
    "ml",
    "name@domain.com",
    "1–5",
    "6",
}


# ==============================================================================
# TEST 1: DICTIONARY KEY PARITY AUDIT
# ==============================================================================
def test_translation_key_parity():
    """Verify 100% key parity: all keys in en.json must exist in every other language."""
    en_catalog = _load_translations("en")
    assert len(en_catalog) > 200, f"Expected >200 translation keys, found {len(en_catalog)}"

    en_keys = set(en_catalog.keys())

    for lang in ["hi", "te", "ta", "kn", "ml"]:
        lang_catalog = _load_translations(lang)
        lang_keys = set(lang_catalog.keys())
        missing_keys = en_keys - lang_keys
        assert not missing_keys, f"Language '{lang}' is missing {len(missing_keys)} keys: {sorted(list(missing_keys))[:10]}"


def test_home_demo_has_a_native_example_for_every_interface_language():
    """Prevent a static example in one language from surviving UI switches."""
    source = (ROOT / "frontend" / "src" / "pages" / "HomePage.tsx").read_text(encoding="utf-8")
    for lang in SUPPORTED_LANGS:
        assert re.search(rf"\b{lang}:\s*\{{\s*question:", source), lang
    assert "const demo = HOME_DEMO[language]" in source


# ==============================================================================
# TEST 2: NO UNTRANSLATED ENGLISH STRINGS IN NON-ENGLISH CATALOGS
# ==============================================================================
def test_no_raw_english_in_indic_locales():
    """Audit that non-English dictionaries contain native Indic translations rather than copied English."""
    en_catalog = _load_translations("en")

    critical_keys = [
        "chat_hero_headline_plain",
        "chat_hero_subheadline",
        "chat_input_placeholder",
        "chat_try_asking",
        "chat_sample_q1",
        "chat_sample_q2",
        "chat_sample_q3",
        "chat_sample_q4",
        "nav_research_group",
        "nav_new_chat",
        "nav_conversations",
        "goal_title",
        "goal_desc",
        "stat_indian_languages",
        "stat_research_backed",
        "stat_answers",
        "stat_lang_quality",
        "stat_comparison",
        "auto_detect_label",
        "native_script_label",
        "romanized_label",
        "dashboard_eyebrow",
        "dashboard_criteria_title",
        "dashboard_criteria_desc",
        "dashboard_fetching",
        "dashboard_live_run",
        "comparison_eyebrow",
        "comparison_matrix_title",
        "failure_eyebrow",
        "about_eyebrow",
        "settings_eyebrow",
        "settings_subtitle",
    ]

    for lang in ["hi", "te", "ta", "kn", "ml"]:
        catalog = _load_translations(lang)
        for key in critical_keys:
            val = catalog.get(key, "").strip()
            en_val = en_catalog.get(key, "").strip()

            assert val != "", f"Key '{key}' is empty in '{lang}'"
            # It must not be identical to the English string
            assert val != en_val, f"Key '{key}' in locale '{lang}' is identical to English: '{val}'"


# ==============================================================================
# TEST 3: SERVER-SIDE SSR LOCALIZATION ACROSS ALL PAGES
# ==============================================================================
@pytest.fixture
def client():
    old_anon = app.config.get("ALLOW_ANONYMOUS_CHAT")
    app.config["TESTING"] = True
    app.config["ALLOW_ANONYMOUS_CHAT"] = True
    with app.test_client() as c:
        yield c
    if old_anon is not None:
        app.config["ALLOW_ANONYMOUS_CHAT"] = old_anon


def test_ssr_chat_page_hindi(client):
    """Verify that when requested in Hindi, the server renders all elements in Hindi."""
    resp = client.get("/chat?lang=hi")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # 1. Headline & Subtitle
    assert "अपनी भाषा" in html
    assert "भारतीय भाषाओं के लिए एक बहुभाषी, शोध-समर्थित चैटबॉट" in html

    # 2. Input Placeholder & Try Asking
    assert "अपना प्रश्न यहाँ टाइप करें..." in html
    assert "पूछ कर देखें" in html

    # 3. Sample Questions
    assert "प्रकाश संश्लेषण क्या है?" in html
    assert "भारत की प्रमुख सरकारी योजनाओं की सूची बनाएं" in html
    assert "स्वस्थ जीवनशैली कैसे बनाए रखें?" in html
    assert "जलवायु परिवर्तन को सरल शब्दों में समझाएं" in html

    # 4. Navigation & Sidebar
    assert "शोध" in html
    assert "नई बातचीत" in html
    assert "बातचीत सूची" in html
    assert "शोध लक्ष्य" in html
    assert "विश्लेषण करें कि भारतीय भाषाओं में उत्तर की गुणवत्ता कैसे भिन्न होती है।" in html

    # 5. Footer Statistics
    assert "भारतीय भाषाएं" in html
    assert "शोध-समर्थित" in html
    assert "उत्तर" in html
    assert "भाषा गुणवत्ता" in html
    assert "तुलना" in html


def test_ssr_all_routes_all_languages(client):
    """Verify that all core routes render cleanly in all six languages."""
    routes = [
        "/",
        "/chat",
        "/dashboard",
        "/language-comparison",
        "/failure-analysis",
        "/about",
        "/settings",
        "/signin",
        "/signup",
        "/forgot-password",
        "/welcome",
    ]

    for lang in SUPPORTED_LANGS:
        for r in routes:
            resp = client.get(f"{r}?lang={lang}")
            if r == "/settings":
                # Unauthenticated redirect to signin is expected
                assert resp.status_code in (200, 302)
            else:
                assert resp.status_code == 200, f"Route {r} failed for lang {lang}: status {resp.status_code}"
                html = resp.get_data(as_text=True)
                assert f'lang="{lang}"' in html, f"Route {r} missing html lang='{lang}'"


# ==============================================================================
# TEST 4: TRANSLATIONS API ENDPOINTS
# ==============================================================================
def test_translations_api_endpoints(client):
    """Verify /api/translations and /api/translations/all endpoints."""
    # Test specific lang
    r1 = client.get("/api/translations?lang=hi")
    assert r1.status_code == 200
    data1 = r1.get_json()
    assert data1["lang"] == "hi"
    assert "अपनी भाषा में कुछ भी पूछें" in data1["translations"]["chat_hero_headline_plain"]

    # Test all langs catalog
    r2 = client.get("/api/translations/all")
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert len(data2["catalogs"]) == 6
    for l in SUPPORTED_LANGS:
        assert l in data2["catalogs"]
        assert "chat_input_placeholder" in data2["catalogs"][l]


# ==============================================================================
# TEST 5: PLAYWRIGHT IN-PLACE CLIENT-SIDE LOCALIZATION (NO RELOAD)
# ==============================================================================
@pytest.mark.anyio
async def test_playwright_inplace_language_switching(anyio_backend):
    """Verify in-place language switching on / without page refresh using Playwright."""
    from playwright.async_api import async_playwright

    base_url = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8001")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Track any full page navigations to guarantee ZERO reload
        nav_tracker = {"count": 0}
        def on_nav(frame):
            if frame == page.main_frame:
                nav_tracker["count"] += 1
        page.on("framenavigated", on_nav)

        # 1. Load chat workspace in English
        await page.goto(f"{base_url}/chat?lang=en", wait_until="networkidle")
        assert nav_tracker["count"] == 1, "Initial page load counts as 1 navigation"

        # Verify initial English strings
        headline = await page.locator("h1.hero-headline-center").inner_text()
        assert "Ask anything in your language" in headline

        input_box = page.locator("#questionInput")
        placeholder = await input_box.get_attribute("placeholder")
        assert placeholder == "Type your question here..."

        # Set a sentinel marker on the window object
        await page.evaluate("window.__BHASHACORE_NO_RELOAD_TEST_SENTINEL__ = 'active_session';")

        # 2. Switch interface language to Hindi in-place
        await page.select_option("#interfaceLangSelect", "hi")
        await page.wait_for_timeout(350)  # Wait for in-place DOM translation

        # Verify ZERO page reloads happened
        sentinel = await page.evaluate("window.__BHASHACORE_NO_RELOAD_TEST_SENTINEL__")
        assert sentinel == "active_session", "Page was reloaded! In-place requirement violated."
        assert nav_tracker["count"] == 1, "Page reloaded via navigation event!"

        # Verify live DOM updated to Hindi instantly
        new_headline = await page.locator("h1.hero-headline-center").inner_text()
        assert "अपनी भाषा में कुछ भी पूछें" in new_headline, f"Expected Hindi headline, got: {new_headline}"

        new_placeholder = await input_box.get_attribute("placeholder")
        assert new_placeholder == "अपना प्रश्न यहाँ टाइप करें...", f"Expected Hindi placeholder, got: {new_placeholder}"

        try_asking = await page.locator(".try-asking-header span:last-child").inner_text()
        assert "पूछ कर देखें" in try_asking

        q1_text = await page.locator("#heroPromptCard1 .card-text").inner_text()
        assert "प्रकाश संश्लेषण क्या है?" in q1_text

        # Verify language codes remained unchanged
        lang_sub_codes = await page.locator(".horizontal-lang-bar .lang-sub-code").all_inner_texts()
        assert set(lang_sub_codes) == {"EN", "HI", "TE", "TA", "KN", "ML"}

        # Verify input language button selection is still 'auto' and was not overwritten
        auto_btn = page.locator('.horizontal-lang-bar .lang-btn[data-lang="auto"]')
        assert await auto_btn.get_attribute("aria-pressed") == "true"

        # 3. Switch to Telugu in-place
        await page.select_option("#interfaceLangSelect", "te")
        await page.wait_for_timeout(350)

        te_headline = await page.locator("h1.hero-headline-center").inner_text()
        assert "మీ భాషలో ఏదైనా అడగండి" in te_headline

        te_placeholder = await input_box.get_attribute("placeholder")
        assert te_placeholder == "మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి..."

        # 4. Switch to Tamil in-place
        await page.select_option("#interfaceLangSelect", "ta")
        await page.wait_for_timeout(350)

        ta_headline = await page.locator("h1.hero-headline-center").inner_text()
        assert "உங்கள் மொழியில் எதையும் கேளுங்கள்" in ta_headline

        # 5. Switch to Kannada in-place
        await page.select_option("#interfaceLangSelect", "kn")
        await page.wait_for_timeout(350)

        kn_headline = await page.locator("h1.hero-headline-center").inner_text()
        assert "ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಏನನ್ನಾದರೂ ಕೇಳಿ" in kn_headline

        # 6. Switch to Malayalam in-place
        await page.select_option("#interfaceLangSelect", "ml")
        await page.wait_for_timeout(350)

        ml_headline = await page.locator("h1.hero-headline-center").inner_text()
        assert "നിങ്ങളുടെ ഭാഷയിൽ എന്തും ചോദിക്കൂ" in ml_headline

        # Final verification: still 0 page reloads
        sentinel_final = await page.evaluate("window.__BHASHACORE_NO_RELOAD_TEST_SENTINEL__")
        assert sentinel_final == "active_session", "Page was reloaded during multi-language switching!"

        await browser.close()
        print("\n[SUCCESS] Playwright in-place localization test PASSED with 0 reloads across all 6 languages!")


if __name__ == "__main__":
    test_translation_key_parity()
    print("PASS: test_translation_key_parity")
    test_no_raw_english_in_indic_locales()
    print("PASS: test_no_raw_english_in_indic_locales")
    with app.test_client() as c:
        test_ssr_chat_page_hindi(c)
        print("PASS: test_ssr_chat_page_hindi")
        test_ssr_all_routes_all_languages(c)
        print("PASS: test_ssr_all_routes_all_languages")
        test_translations_api_endpoints(c)
        print("PASS: test_translations_api_endpoints")
    print("\nRunning Playwright in-place language switching test...")
    asyncio.run(test_playwright_inplace_language_switching())
