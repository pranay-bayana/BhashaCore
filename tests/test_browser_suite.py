"""Comprehensive Playwright End-to-End & Localization Test Suite for BhashaCore.

Verifies:
1. Six-Language Interface Localization across all routes and persistence.
2. Full functional flows (Landing, Auth, Chat, Dashboard, Comparison, Failures, About, Settings).
3. Responsive viewport behaviors (Desktop 1440px, Mobile 390px, Drawer).
4. Visual test screenshots capture.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.translations import get_available_languages, t

LOCALIZED_LANGUAGE_NAMES = {
    "en": {"en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"},
    "hi": {"en": "अंग्रेज़ी", "hi": "हिंदी", "ta": "तमिल", "te": "तेलुगु", "kn": "कन्नड़", "ml": "मलयालम"},
    "ta": {"en": "ஆங்கிலம்", "hi": "இந்தி", "ta": "தமிழ்", "te": "தெலுங்கு", "kn": "கன்னடம்", "ml": "மலையாளம்"},
    "te": {"en": "ఆంగ్లం", "hi": "హిందీ", "ta": "తమిళం", "te": "తెలుగు", "kn": "కన్నడ", "ml": "మలయాళం"},
    "kn": {"en": "ಇಂಗ್ಲಿಷ್", "hi": "ಹಿಂದಿ", "ta": "ತಮಿಳು", "te": "ತೆಲುಗು", "kn": "ಕನ್ನಡ", "ml": "ಮಲಯಾಳಂ"},
    "ml": {"en": "ഇംഗ്ലീഷ്", "hi": "ഹിന്ദി", "ta": "തമിഴ്", "te": "തെലുങ്ക്", "kn": "കന്നഡ", "ml": "മലയാളം"}
}

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8001")
SCREENSHOTS_DIR = ROOT / "tests" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

RESULTS = {"pass": 0, "fail": 0, "checks": []}


def record(name: str, passed: bool, detail: str = ""):
    RESULTS["pass" if passed else "fail"] += 1
    status = "PASS" if passed else "FAIL"
    msg = f"[{status}] {name}" + (f" — {detail}" if detail else "")
    RESULTS["checks"].append(msg)
    print(msg)


async def run_suite():
    print("=" * 70)
    print("STARTING BHASHACORE COMPREHENSIVE PLAYWRIGHT TEST SUITE")
    print(f"Target: {BASE_URL}")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ----------------------------------------------------------------------
        # PART 1: SIX-LANGUAGE INTERFACE LOCALIZATION REPAIR VERIFICATION
        # ----------------------------------------------------------------------
        print("\n--- PART 1: SIX-LANGUAGE INTERFACE LOCALIZATION TESTS ---")
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        langs = ["hi", "te", "ta", "kn", "ml", "en"]

        for lang in langs:
            expected_title = t("landing_title", lang=lang)
            expected_nav_dash = t("nav_dashboard", lang=lang)
            expected_nav_chat = t("nav_chat", lang=lang)
            expected_nav_about = t("nav_about", lang=lang)

            # 1. Open landing page with direct route or selector
            await page.goto(f"{BASE_URL}/welcome?lang={lang}", wait_until="networkidle")

            # Verify HTML lang attribute
            html_lang = await page.locator("html").get_attribute("lang")
            record(f"[{lang.upper()}] HTML lang attribute is set to {lang}", html_lang == lang, f"got {html_lang}")

            # Verify Page Heading
            heading = await page.locator("h1.hero-headline").text_content()
            record(
                f"[{lang.upper()}] Hero headline is rendered in {lang}",
                expected_title in heading,
                f"expected '{expected_title[:30]}...', got '{heading[:30]}...'"
            )

            # Verify Navigation items
            nav_text = await page.locator("nav.main-nav").text_content()
            record(
                f"[{lang.upper()}] Navigation includes translated Dashboard ({expected_nav_dash})",
                expected_nav_dash in nav_text,
                f"got nav text snippet: {nav_text[:40]}"
            )
            record(
                f"[{lang.upper()}] Navigation includes translated Chat ({expected_nav_chat})",
                expected_nav_chat in nav_text
            )

            # Verify Selector reflects active language
            selected_val = await page.locator("#interfaceLangSelect").input_value()
            record(
                f"[{lang.upper()}] Selector value matches active language",
                selected_val == lang,
                f"selected={selected_val}"
            )

            # 2. Navigate to Chat and verify language persists
            await page.click(f"nav.main-nav a:has-text('{expected_nav_chat}')")
            await page.wait_for_load_state("networkidle")
            chat_html_lang = await page.locator("html").get_attribute("lang")
            record(
                f"[{lang.upper()}] Language persists on navigation to Chat",
                chat_html_lang == lang,
                f"html lang is {chat_html_lang}"
            )

            # Verify all six language-selection buttons in sidebar dynamically translated for this interface language
            for c_code, c_expected in LOCALIZED_LANGUAGE_NAMES[lang].items():
                btn_text = await page.locator(f'.lang-btn[data-lang="{c_code}"]').text_content()
                record(
                    f"[{lang.upper()}] Sidebar language button for {c_code.upper()} dynamically translated ({c_expected})",
                    c_expected in btn_text,
                    f"button text: {btn_text.strip()}"
                )

            # 3. Navigate to Dashboard and verify language persists
            await page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
            dash_html_lang = await page.locator("html").get_attribute("lang")
            dash_h1 = await page.locator("h1").text_content()
            record(
                f"[{lang.upper()}] Dashboard page heading translated and persisted",
                expected_nav_dash in dash_h1 and dash_html_lang == lang,
                f"h1={dash_h1}, lang={dash_html_lang}"
            )

            # 4. Refresh page and verify persistence
            await page.reload(wait_until="networkidle")
            refreshed_lang = await page.locator("html").get_attribute("lang")
            record(
                f"[{lang.upper()}] Interface language persists after browser refresh",
                refreshed_lang == lang,
                f"refreshed_lang={refreshed_lang}"
            )

            # Capture localized full interface screenshot
            screenshot_path = SCREENSHOTS_DIR / f"interface_{lang}.png"
            await page.screenshot(path=str(screenshot_path), full_page=False)
            record(f"[{lang.upper()}] Captured screenshot interface_{lang}.png", screenshot_path.exists())

        # ----------------------------------------------------------------------
        # PART 2: FUNCTIONAL WORKSPACE & CHAT TESTS
        # ----------------------------------------------------------------------
        print("\n--- PART 2: FUNCTIONAL WORKSPACE & CHAT TESTS ---")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")

        # Verify chat workspace layout components
        record("Chat composer textarea present", await page.locator("#questionInput").is_visible())
        record("Send button present", await page.locator("#sendBtn").is_visible())
        record("Language control badges present", await page.locator("#langBadge").is_visible())
        record("7 input language buttons rendered in sidebar", await page.locator(".lang-btn").count() == 7)

        # Test selecting Hindi input language
        await page.click('.lang-btn[data-lang="hi"]')
        sidebar_badge = await page.locator("#sidebarInputBadge").text_content()
        record("Selecting Hindi updates input badge to HI", "HI" in sidebar_badge)

        # Test selecting Romanized input style
        await page.click('button[data-style="romanized"]')
        is_romanized = await page.locator('button[data-style="romanized"]').get_attribute("class")
        record("Selecting Romanized input style sets active state", "active" in is_romanized)

        # Test entering a prompt and verifying submission
        await page.click('.lang-btn[data-lang="en"]')
        await page.click('button[data-style="native"]')
        await page.locator("#questionInput").fill("What is the capital of India?")
        await page.locator("#questionInput").press("Enter")

        # Verify Stop button appears while generating
        stop_btn_visible = False
        for _ in range(15):
            if await page.locator("#stopBtn").is_visible():
                stop_btn_visible = True
                break
            await page.wait_for_timeout(100)
        record("Stop button displayed during generation", stop_btn_visible)

        # Wait for bot response to finish
        for _ in range(60):
            status_lines = await page.locator(".msg-bubble .status-line").all_text_contents()
            if status_lines and not any("Searching" in s for s in status_lines):
                break
            await page.wait_for_timeout(400)

        completed_status = await page.locator(".msg-bubble .status-line").last.text_content()
        record(
            "Chat stream produced completed status response",
            bool(completed_status),
            f"status: {completed_status}"
        )

        # Verify citation button and expansion if citations exist
        sources_btn = page.locator(".sources-btn").first
        if await sources_btn.count() > 0:
            btn_txt = await sources_btn.text_content()
            await sources_btn.click()
            await page.wait_for_timeout(300)
            list_visible = await page.locator(".sources-list.show").count() > 0
            record("Citations expandable drawer functions", list_visible, btn_txt)

        # Test New Chat reset
        await page.click("button:has-text('New chat'), button:has-text('New conversation')")
        await page.wait_for_timeout(400)
        msg_count = await page.locator(".msg-wrapper").count()
        record("New chat resets conversation messages", msg_count == 0, f"msg_count={msg_count}")

        # ----------------------------------------------------------------------
        # PART 3: RESEARCH PAGES & ANALYTICS VISUALIZATION
        # ----------------------------------------------------------------------
        print("\n--- PART 3: RESEARCH & ANALYTICS VERIFICATION ---")

        # 1. Research Dashboard
        await page.goto(f"{BASE_URL}/dashboard?lang=en", wait_until="networkidle")
        await page.wait_for_timeout(600)
        counts_txt = await page.locator("#countsCard").text_content()
        record("Dashboard displays real evaluated sample counts", "1117" in counts_txt and "530" in counts_txt)
        quality_rows = await page.locator("#qualityTable tbody tr").count()
        record("Dashboard quality table populated with 6 languages", quality_rows == 6, f"{quality_rows} rows")
        retrieval_rows = await page.locator("#retrievalTable tbody tr").count()
        record("Dashboard retrieval table populated", retrieval_rows >= 6, f"{retrieval_rows} rows")
        dash_shot = SCREENSHOTS_DIR / "dashboard_desktop.png"
        await page.screenshot(path=str(dash_shot), full_page=False)
        record("Captured dashboard_desktop.png", dash_shot.exists())

        # 2. Language Comparison
        await page.goto(f"{BASE_URL}/language-comparison?lang=en", wait_until="networkidle")
        await page.wait_for_timeout(600)
        comp_rows = await page.locator("#compTable tbody tr").count()
        record("Language comparison table populated", comp_rows == 6, f"{comp_rows} rows")
        waterfall_bars = await page.locator(".lang-waterfall-item").count()
        record("Waterfall comparative bars rendered for all languages", waterfall_bars == 6, f"{waterfall_bars} items")
        comp_shot = SCREENSHOTS_DIR / "comparison_desktop.png"
        await page.screenshot(path=str(comp_shot), full_page=False)
        record("Captured comparison_desktop.png", comp_shot.exists())

        # 3. Failure Analysis
        await page.goto(f"{BASE_URL}/failure-analysis?lang=en", wait_until="networkidle")
        await page.wait_for_timeout(800)
        fail_cards = await page.locator("#results .failure-item-card").count()
        record("Failure analysis loads real failure records", fail_cards >= 5, f"{fail_cards} cards")
        await page.select_option("#langFilter", "ta")
        await page.click("button:has-text('Apply Filters')")
        await page.wait_for_timeout(800)
        ta_count = await page.locator("#results .failure-item-card").count()
        record("Failure filter by Tamil (TA) returns filtered records", ta_count >= 1, f"{ta_count} records")
        fail_shot = SCREENSHOTS_DIR / "failures_desktop.png"
        await page.screenshot(path=str(fail_shot), full_page=False)
        record("Captured failures_desktop.png", fail_shot.exists())

        # 4. About Page
        await page.goto(f"{BASE_URL}/about?lang=en", wait_until="networkidle")
        about_text = await page.locator("main").text_content()
        record("About page documents metrics and IndicQA data", "Judge" in about_text and "IndicQA" in about_text)
        record("About page documents threshold: failure when scores <= 3", "≤ 3" in about_text or "<= 3" in about_text)

        # ----------------------------------------------------------------------
        # PART 4: AUTHENTICATION & SETTINGS FLOWS
        # ----------------------------------------------------------------------
        print("\n--- PART 4: AUTHENTICATION & SETTINGS FLOWS ---")
        # 1. Sign In Page
        await page.goto(f"{BASE_URL}/signin?lang=en", wait_until="networkidle")
        record("Sign in form renders email and password fields", await page.locator("input[name='email']").is_visible() and await page.locator("input[name='password']").is_visible())

        # 2. Sign Up Page & Consent Checkbox
        await page.goto(f"{BASE_URL}/signup?lang=en", wait_until="networkidle")
        has_consent = await page.locator("input[name='consent']").is_visible()
        record("Sign up form includes mandatory terms consent checkbox", has_consent)

        # Test registration with immediate login
        test_email = f"qa_engineer_{int(time.time())}@example.com"
        await page.fill("input[name='name']", "QA Test Engineer")
        await page.fill("input[name='email']", test_email)
        await page.fill("input[name='password']", "StrongPassword123!")
        await page.fill("input[name='confirm_password']", "StrongPassword123!")
        await page.check("input[name='consent']")
        async with page.expect_navigation():
            await page.click("button[type='submit']")
        await page.wait_for_timeout(500)

        # Verify logged in state
        auth_cookie = await context.cookies()
        session_cookie_exists = any("session" in c["name"] for c in auth_cookie)
        record("Account registration creates active authenticated session", session_cookie_exists)

        # 3. Settings Page
        await page.goto(f"{BASE_URL}/settings", wait_until="networkidle")
        settings_text = await page.locator("main").text_content()
        record("Settings page renders user profile information", test_email in settings_text)
        record("Settings page renders delete account controls", await page.locator("input[name='password']").is_visible())

        # 4. Theme switching
        theme_before = await page.evaluate("document.documentElement.getAttribute('data-theme')")
        await page.click("#themeToggleBtn")
        theme_after = await page.evaluate("document.documentElement.getAttribute('data-theme')")
        record("Theme toggle button switches theme mode", theme_before != theme_after, f"{theme_before} -> {theme_after}")
        light_shot = SCREENSHOTS_DIR / "theme_light.png"
        await page.screenshot(path=str(light_shot), full_page=False)
        record("Captured theme_light.png", light_shot.exists())

        # Revert theme
        await page.click("#themeToggleBtn")

        # ----------------------------------------------------------------------
        # PART 5: RESPONSIVE & MOBILE VERIFICATION
        # ----------------------------------------------------------------------
        print("\n--- PART 5: RESPONSIVE VIEWPORT & MOBILE TESTS ---")
        # 1. Desktop 1440x900 Landing & Chat
        await page.set_viewport_size({"width": 1440, "height": 900})
        await page.goto(f"{BASE_URL}/welcome?lang=en", wait_until="networkidle")
        landing_desktop_shot = SCREENSHOTS_DIR / "landing_desktop.png"
        await page.screenshot(path=str(landing_desktop_shot), full_page=False)
        record("Captured landing_desktop.png (1440px)", landing_desktop_shot.exists())

        await page.goto(f"{BASE_URL}/?lang=en", wait_until="networkidle")
        chat_desktop_shot = SCREENSHOTS_DIR / "chat_desktop.png"
        await page.screenshot(path=str(chat_desktop_shot), full_page=False)
        record("Captured chat_desktop.png (1440px)", chat_desktop_shot.exists())

        # 2. Mobile 390x844 Landing & Chat
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto(f"{BASE_URL}/welcome?lang=en", wait_until="networkidle")
        landing_mobile_shot = SCREENSHOTS_DIR / "landing_mobile.png"
        await page.screenshot(path=str(landing_mobile_shot), full_page=False)
        record("Captured landing_mobile.png (390px)", landing_mobile_shot.exists())

        # Verify no horizontal scroll overflow on mobile
        overflow_landing = await page.evaluate("document.body.scrollWidth - document.documentElement.clientWidth")
        record("No horizontal overflow on mobile landing (390px)", overflow_landing <= 0, f"overflow={overflow_landing}px")

        # Test mobile drawer
        await page.click(".mobile-menu-btn")
        await page.wait_for_timeout(300)
        drawer_open = await page.locator("#mobileNavDrawer").get_attribute("class")
        record("Mobile menu button opens navigation drawer", "open" in drawer_open)
        drawer_shot = SCREENSHOTS_DIR / "mobile_drawer.png"
        await page.screenshot(path=str(drawer_shot), full_page=False)
        record("Captured mobile_drawer.png", drawer_shot.exists())

        # Close mobile drawer
        await page.click("#mobileNavDrawer .btn-ghost")
        await page.wait_for_timeout(300)

        # Mobile Chat Viewport
        await page.goto(f"{BASE_URL}/?lang=en", wait_until="networkidle")
        chat_mobile_shot = SCREENSHOTS_DIR / "chat_mobile.png"
        await page.screenshot(path=str(chat_mobile_shot), full_page=False)
        record("Captured chat_mobile.png (390px)", chat_mobile_shot.exists())
        overflow_chat = await page.evaluate("document.body.scrollWidth - document.documentElement.clientWidth")
        record("No horizontal overflow on mobile chat (390px)", overflow_chat <= 0, f"overflow={overflow_chat}px")

        await browser.close()

    total = RESULTS["pass"] + RESULTS["fail"]
    print("\n" + "=" * 70)
    print(f"PLAYWRIGHT TEST SUITE SUMMARY: {RESULTS['pass']}/{total} checks PASSED")
    print("=" * 70)
    return 0 if RESULTS["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run_suite()))
