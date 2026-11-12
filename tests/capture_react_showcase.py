"""Script to capture full high-fidelity screenshots of BhashaCore React SPA for visual verification."""

import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8001")
SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path("/Users/pranaybayana/.gemini/antigravity/brain/c72a710a-7ca7-4240-842d-52b9bc251251")

async def capture_all():
    print(f"Connecting to {BASE_URL} to capture React showcase...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. DESKTOP DARK THEME
        # -------------------------------------------------------------
        print("\n--- 1. Desktop Dark Theme ---")
        context = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = await context.new_page()

        # Set theme to dark
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.evaluate("localStorage.setItem('bhashacore_theme', 'dark'); localStorage.setItem('bhashacore_ui_lang', 'en');")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1.1 Home Page
        print("Capturing 1.1 Home Page (Dark)...")
        shot_home = SCREENSHOTS_DIR / "react_home_desktop.png"
        await page.screenshot(path=str(shot_home), full_page=False)

        # 1.2 Chat Empty
        print("Capturing 1.2 Chat Empty (Dark)...")
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        shot_chat_empty = SCREENSHOTS_DIR / "react_chat_empty.png"
        await page.screenshot(path=str(shot_chat_empty), full_page=False)

        # 1.3 Chat Active (Ask a question & stream real Sarvam AI response)
        print("Capturing 1.3 Chat Active with real citations (Dark)...")
        input_el = page.locator("#questionInput")
        await input_el.fill("What is photosynthesis?")
        await page.click("#sendBtn")

        # Wait for answer streaming to finish and citations button to appear
        try:
            await page.wait_for_selector(".sources-btn", timeout=30000)
            await page.wait_for_timeout(1500)
            # Expand citations
            sources_btn = page.locator(".sources-btn")
            if await sources_btn.count() > 0:
                await sources_btn.first.click()
                await page.wait_for_timeout(800)
        except Exception as e:
            print(f"Notice on chat stream wait: {e}")
            await page.wait_for_timeout(3000)

        shot_chat_active = SCREENSHOTS_DIR / "react_chat_active.png"
        await page.screenshot(path=str(shot_chat_active), full_page=False)

        # 1.4 Research Dashboard
        print("Capturing 1.4 Research Dashboard (Dark)...")
        await page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        shot_dashboard = SCREENSHOTS_DIR / "react_dashboard_desktop.png"
        await page.screenshot(path=str(shot_dashboard), full_page=False)

        # 1.5 Language Comparison
        print("Capturing 1.5 Language Comparison (Dark)...")
        await page.goto(f"{BASE_URL}/language-comparison", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        shot_comparison = SCREENSHOTS_DIR / "react_comparison_desktop.png"
        await page.screenshot(path=str(shot_comparison), full_page=False)

        # 1.6 Failure Analysis
        print("Capturing 1.6 Failure Analysis (Dark)...")
        await page.goto(f"{BASE_URL}/failure-analysis", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        shot_failures = SCREENSHOTS_DIR / "react_failures_desktop.png"
        await page.screenshot(path=str(shot_failures), full_page=False)

        # 1.7 About Page
        print("Capturing 1.7 About Page (Dark)...")
        await page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        shot_about = SCREENSHOTS_DIR / "react_about_desktop.png"
        await page.screenshot(path=str(shot_about), full_page=False)

        # -------------------------------------------------------------
        # 2. DESKTOP LIGHT THEME
        # -------------------------------------------------------------
        print("\n--- 2. Desktop Light Theme ---")
        await page.evaluate("localStorage.setItem('bhashacore_theme', 'light');")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        shot_home_light = SCREENSHOTS_DIR / "react_home_light.png"
        await page.screenshot(path=str(shot_home_light), full_page=False)
        print("Capturing 2.1 Home (Light)...")

        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        shot_chat_light = SCREENSHOTS_DIR / "react_chat_light.png"
        await page.screenshot(path=str(shot_chat_light), full_page=False)
        print("Capturing 2.2 Chat (Light)...")

        await page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        shot_dashboard_light = SCREENSHOTS_DIR / "react_dashboard_light.png"
        await page.screenshot(path=str(shot_dashboard_light), full_page=False)
        print("Capturing 2.3 Dashboard (Light)...")

        await page.goto(f"{BASE_URL}/language-comparison", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        shot_comparison_light = SCREENSHOTS_DIR / "react_comparison_light.png"
        await page.screenshot(path=str(shot_comparison_light), full_page=False)
        print("Capturing 2.4 Comparison (Light)...")

        await page.goto(f"{BASE_URL}/failure-analysis", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        shot_failures_light = SCREENSHOTS_DIR / "react_failures_light.png"
        await page.screenshot(path=str(shot_failures_light), full_page=False)
        print("Capturing 2.5 Failures (Light)...")

        # -------------------------------------------------------------
        # 3. LOCALIZED VIEWS (HINDI & TELUGU)
        # -------------------------------------------------------------
        print("\n--- 3. Localized Views ---")
        # Hindi Home
        await page.evaluate("localStorage.setItem('bhashacore_theme', 'dark'); localStorage.setItem('bhashacore_ui_lang', 'hi');")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        shot_home_hindi = SCREENSHOTS_DIR / "react_home_hindi.png"
        await page.screenshot(path=str(shot_home_hindi), full_page=False)
        print("Capturing 3.1 Home in Hindi...")

        # Hindi Chat
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        shot_chat_hindi = SCREENSHOTS_DIR / "react_chat_hindi.png"
        await page.screenshot(path=str(shot_chat_hindi), full_page=False)
        print("Capturing 3.2 Chat in Hindi...")

        # Telugu Home
        await page.evaluate("localStorage.setItem('bhashacore_ui_lang', 'te');")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        shot_home_telugu = SCREENSHOTS_DIR / "react_home_telugu.png"
        await page.screenshot(path=str(shot_home_telugu), full_page=False)
        print("Capturing 3.3 Home in Telugu...")

        await context.close()

        # -------------------------------------------------------------
        # 4. MOBILE VIEWPORT (390 x 844)
        # -------------------------------------------------------------
        print("\n--- 4. Mobile Responsiveness ---")
        m_context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        m_page = await m_context.new_page()
        await m_page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await m_page.evaluate("localStorage.setItem('bhashacore_theme', 'dark'); localStorage.setItem('bhashacore_ui_lang', 'en');")
        await m_page.reload(wait_until="networkidle")
        await m_page.wait_for_timeout(1000)
        shot_home_mob = SCREENSHOTS_DIR / "react_home_mobile.png"
        await m_page.screenshot(path=str(shot_home_mob), full_page=False)
        print("Capturing 4.1 Home Mobile...")

        await m_page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await m_page.wait_for_timeout(1000)
        shot_chat_mob = SCREENSHOTS_DIR / "react_chat_mobile.png"
        await m_page.screenshot(path=str(shot_chat_mob), full_page=False)
        print("Capturing 4.2 Chat Mobile...")

        await m_context.close()
        await browser.close()

        # -------------------------------------------------------------
        # 5. COPY ALL SCREENSHOTS TO ARTIFACTS DIRECTORY
        # -------------------------------------------------------------
        all_shots = [
            shot_home, shot_chat_empty, shot_chat_active, shot_dashboard,
            shot_comparison, shot_failures, shot_about,
            shot_home_light, shot_chat_light, shot_dashboard_light,
            shot_comparison_light, shot_failures_light,
            shot_home_hindi, shot_chat_hindi, shot_home_telugu,
            shot_home_mob, shot_chat_mob
        ]

        for s in all_shots:
            if s.exists():
                dst = ARTIFACT_DIR / s.name
                shutil.copy2(str(s), str(dst))
                print(f"✓ Copied artifact: {s.name}")

        print("\nAll showcase captures successfully written to artifacts directory!")

if __name__ == "__main__":
    asyncio.run(capture_all())
