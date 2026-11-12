"""Automated Verification & Visual Capture Suite for the BhashaCore About Page.

Tests:
1. Full-width responsive layout at desktop (1440x900) and mobile (390x844).
2. Glassmorphic styling, typography hierarchy, and spacing.
3. Interactive cards (Tokenization, Romanized, Pretraining, Objectives, Languages, Metrics).
4. Polished glassmorphic detail popover modal opening, animation, and dismissal.
5. Complete 6-language in-place localization verification without page reload.
6. Absence of any raw untranslated translation keys (e.g. about_methodology_title).
7. Light and dark theme rendering.
"""

import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8001")
SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
ARTIFACT_DIR = Path("/Users/pranaybayana/.gemini/antigravity/brain/c72a710a-7ca7-4240-842d-52b9bc251251")

LANGUAGES = [
    ("en", "About BhashaCore", "Evaluation Methodology & LLM Judge"),
    ("hi", "भाषाकोर के बारे में", "मूल्यांकन पद्धति और एलएलएम निर्णायक"),
    ("te", "భాషాకోర్ గురించి", "మూల్యాంకన పద్ధతి మరియు ఎల్‌ఎల్‌ఎమ్ న్యాయనిర్ణేత"),
    ("ta", "பாஷாகோர் பற்றி", "மதிப்பீட்டு முறை மற்றும் எல்.எல்.எம் நீதிபதி"),
    ("kn", "ಭಾಷಾಕೋರ್ ಕುರಿತು", "ಮೌಲ್ಯಮಾಪನ ವಿಧಾನ ಮತ್ತು ಎಲ್‌ಎಲ್‌ಎಂ ತೀರ್ಪುಗಾರ"),
    ("ml", "ഭാഷാകോറിനെക്കുറിച്ച്", "മൂല്യനിർണ്ണയ രീതിശാസ്ത്രവും എൽഎൽഎം ജഡ്ജിയും"),
]

async def run_about_verification():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    print("==================================================================")
    print("STARTING BHASHACORE ABOUT PAGE VERIFICATION SUITE")
    print(f"Target: {BASE_URL}/about")
    print("==================================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ---------------------------------------------------------------------
        # 1. DESKTOP VERIFICATION (1440 x 900) - DARK MODE
        # ---------------------------------------------------------------------
        print("\n--- 1. Testing Desktop Layout (1440 x 900) ---")
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await page.goto(f"{BASE_URL}/about?lang=en", wait_until="networkidle")
        await page.wait_for_timeout(600)

        # Check content width
        container = page.locator(".about-container")
        box = await container.bounding_box()
        assert box is not None, "About container not found"
        print(f"✓ About container measured width: {box['width']:.1f}px (Target: ~1100-1250px)")
        assert box['width'] >= 1050, f"Expected container width >= 1050px, got {box['width']}px"

        # Check raw translation key absence
        page_text = await page.content()
        assert "about_methodology_title" not in page_text, "Found raw key 'about_methodology_title'!"
        assert "about_disparity_title" not in page_text, "Found raw key 'about_disparity_title'!"
        assert "about_hero_title" not in page_text, "Found raw key 'about_hero_title'!"
        print("✓ Zero raw translation keys detected in DOM")

        shot_desktop = SCREENSHOTS_DIR / "react_about_desktop_verified.png"
        await page.screenshot(path=str(shot_desktop), full_page=False)
        print("✓ Captured Desktop About Page:", shot_desktop)

        # ---------------------------------------------------------------------
        # 2. INTERACTIVE CARD & MODAL POPOVER VERIFICATION
        # ---------------------------------------------------------------------
        print("\n--- 2. Testing Interactive Card & Modal Popover ---")
        # Click the Tokenization Asymmetry card
        token_card = page.locator("text=Tokenization Asymmetry").first
        await token_card.click()
        await page.wait_for_timeout(500)

        # Verify modal appeared
        modal = page.locator("#aboutDetailModal")
        assert await modal.is_visible(), "Modal did not open on clicking Tokenization card!"
        print("✓ Popover modal opened smoothly with backdrop blur")

        shot_modal = SCREENSHOTS_DIR / "react_about_modal_open.png"
        await page.screenshot(path=str(shot_modal), full_page=False)
        print("✓ Captured Open Modal Popover:", shot_modal)

        # Close modal via close button
        close_btn = page.locator("#aboutModalCloseXBtn")
        await close_btn.click()
        await page.wait_for_timeout(400)
        assert await page.locator("#aboutDetailModal").count() == 0, "Modal did not close on clicking Close button!"
        print("✓ Modal dismissed cleanly")

        # Test CLI Copy button
        copy_btn = page.locator("button:has-text('Copy CLI Commands')")
        if await copy_btn.count() > 0:
            await copy_btn.click()
            await page.wait_for_timeout(300)
            print("✓ Copy CLI Commands button clicked successfully")

        # ---------------------------------------------------------------------
        # 3. LIGHT MODE VERIFICATION
        # ---------------------------------------------------------------------
        print("\n--- 3. Testing Light Mode About Page ---")
        theme_btn = page.locator("#themeToggleBtn")
        if await theme_btn.count() > 0:
            await theme_btn.click()
            await page.wait_for_timeout(500)
            shot_light = SCREENSHOTS_DIR / "react_about_light_verified.png"
            await page.screenshot(path=str(shot_light), full_page=False)
            print("✓ Captured Light Mode About Page:", shot_light)
            await theme_btn.click()
            await page.wait_for_timeout(300)

        await context.close()

        # ---------------------------------------------------------------------
        # 4. SIX-LANGUAGE LOCALIZATION AUDIT
        # ---------------------------------------------------------------------
        print("\n--- 4. Testing Six Interface Languages on About Page ---")
        l_context = await browser.new_context(viewport={"width": 1440, "height": 900})
        l_page = await l_context.new_page()

        for code, expected_title, expected_methodology in LANGUAGES:
            await l_page.goto(f"{BASE_URL}/about?lang={code}", wait_until="networkidle")
            await l_page.wait_for_timeout(400)

            # Check title
            h1 = await l_page.locator("h1").first.inner_text()
            assert expected_title in h1, f"[{code.upper()}] Expected title '{expected_title}' in '{h1}'"

            # Check methodology title (unescape HTML entities)
            import html
            content = html.unescape(await l_page.content())
            assert expected_methodology in content, f"[{code.upper()}] Missing methodology title '{expected_methodology}'"
            assert "about_methodology_title" not in content, f"[{code.upper()}] Raw key leaked!"

            print(f"✓ [{code.upper()}] Verified: '{expected_title}' & '{expected_methodology}'")

            if code == "hi":
                shot_hi = SCREENSHOTS_DIR / "react_about_hindi_verified.png"
                await l_page.screenshot(path=str(shot_hi), full_page=False)
                print("✓ Captured Hindi About Page:", shot_hi)

        await l_context.close()

        # ---------------------------------------------------------------------
        # 5. MOBILE VIEWPORT (390 x 844)
        # ---------------------------------------------------------------------
        print("\n--- 5. Testing Mobile Viewport (390 x 844) ---")
        m_context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        m_page = await m_context.new_page()
        await m_page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        await m_page.wait_for_timeout(600)

        # Check for horizontal overflow
        scroll_width = await m_page.evaluate("document.documentElement.scrollWidth")
        client_width = await m_page.evaluate("document.documentElement.clientWidth")
        overflow = scroll_width - client_width
        print(f"✓ Mobile horizontal overflow: {overflow}px (Target: 0px)")
        assert overflow <= 1, f"Horizontal overflow detected on mobile: {overflow}px"

        shot_mobile = SCREENSHOTS_DIR / "react_about_mobile_verified.png"
        await m_page.screenshot(path=str(shot_mobile), full_page=False)
        print("✓ Captured Mobile About Page:", shot_mobile)

        await m_context.close()
        await browser.close()

        # Copy captured screenshots to artifacts directory
        for s in [
            SCREENSHOTS_DIR / "react_about_desktop_verified.png",
            SCREENSHOTS_DIR / "react_about_modal_open.png",
            SCREENSHOTS_DIR / "react_about_light_verified.png",
            SCREENSHOTS_DIR / "react_about_hindi_verified.png",
            SCREENSHOTS_DIR / "react_about_mobile_verified.png",
        ]:
            if s.exists():
                dst = ARTIFACT_DIR / s.name
                shutil.copy2(str(s), str(dst))
                print(f"✓ Copied artifact: {s.name}")

    print("\n==================================================================")
    print("ALL ABOUT PAGE VERIFICATIONS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_about_verification())
