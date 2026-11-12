"""Capture visual evidence of notification popover, 3-question guest limit, and AuthModal."""

import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8001")
SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path("/Users/pranaybayana/.gemini/antigravity/brain/c72a710a-7ca7-4240-842d-52b9bc251251")

async def run_verification():
    print(f"Connecting to {BASE_URL} to verify notifications and guest quota...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2
        )
        page = await context.new_page()

        # -------------------------------------------------------------
        # 1. NOTIFICATION POPOVER CAPTURE
        # -------------------------------------------------------------
        print("\n--- 1. Testing Notification Bell & Popover ---")
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Click notification bell button
        bell_btn = page.locator("#notificationBellBtn")
        await bell_btn.click()
        await page.wait_for_timeout(500)

        # Capture with popover open
        shot_notif = SCREENSHOTS_DIR / "react_chat_notification_popover.png"
        await page.screenshot(path=str(shot_notif), full_page=False)
        print("✓ Captured notification popover open:", shot_notif)

        # Close popover by clicking outside or pressing Escape
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(400)

        # -------------------------------------------------------------
        # 2. THREE-MESSAGE GUEST LIMIT FLOW
        # -------------------------------------------------------------
        print("\n--- 2. Testing 3-Message Guest Limit ---")
        questions = [
            "What is photosynthesis?",
            "List major government schemes in India",
            "Explain climate change in simple terms"
        ]

        for i, q in enumerate(questions, 1):
            print(f"Submitting guest question {i}/3: {q}")
            input_el = page.locator("#questionInput")
            await input_el.fill(q)
            await page.click("#sendBtn")

            # Wait for answer streaming to finish (wait for sources button or bot message status)
            print(f"Waiting for response {i} to complete...")
            await page.wait_for_selector(f".msg.bot >> nth={i-1}", timeout=35000)

            # Wait until streaming completes (stopBtn disappears, sendBtn returns or input updates)
            await page.wait_for_function(
                "() => !document.querySelector('#stopBtn')",
                timeout=35000
            )
            await page.wait_for_timeout(1200)

        # Expand citations on the 3rd response
        sources_btn = page.locator(".sources-btn")
        if await sources_btn.count() >= 3:
            await sources_btn.nth(2).click()
            await page.wait_for_timeout(600)

        # Wait for guest limit card to be visible and scroll it into view
        card = page.locator("#guestLimitCard")
        await card.wait_for(state="visible", timeout=10000)
        await card.scroll_into_view_if_needed()
        await page.wait_for_timeout(800)
        print("✓ Guest limit card is visible and scrolled into view!")

        # Capture guest limit reached screenshot
        shot_guest_limit = SCREENSHOTS_DIR / "react_chat_guest_trial_reached.png"
        await page.screenshot(path=str(shot_guest_limit), full_page=False)
        print("✓ Captured 3-message guest trial reached:", shot_guest_limit)

        # -------------------------------------------------------------
        # 3. AUTH MODAL INVITATION
        # -------------------------------------------------------------
        print("\n--- 3. Testing Auth Modal from Guest Limit Card ---")
        sign_in_btn = page.locator("#guestLimitSignInBtn")
        await sign_in_btn.click()
        await page.wait_for_timeout(600)

        # Wait for modal
        await page.wait_for_selector("#authModal", timeout=5000)
        print("✓ Auth modal opened successfully!")

        shot_auth_modal = SCREENSHOTS_DIR / "react_chat_auth_modal.png"
        await page.screenshot(path=str(shot_auth_modal), full_page=False)
        print("✓ Captured AuthModal overlay:", shot_auth_modal)

        # Close auth modal
        close_btn = page.locator("#authModal button >> nth=0")
        if await close_btn.count() > 0:
            await close_btn.click()
            await page.wait_for_timeout(400)

        # -------------------------------------------------------------
        # 4. LIGHT MODE CHAT VERIFICATION
        # -------------------------------------------------------------
        print("\n--- 4. Testing Light Mode Chat ---")
        theme_btn = page.locator("#themeToggleBtn")
        await theme_btn.click()
        await page.wait_for_timeout(600)
        shot_light = SCREENSHOTS_DIR / "react_chat_light_verified.png"
        await page.screenshot(path=str(shot_light), full_page=False)
        print("✓ Captured Light Mode Chat:", shot_light)

        # Switch back to dark mode
        await theme_btn.click()
        await page.wait_for_timeout(400)
        await context.close()

        # -------------------------------------------------------------
        # 5. MOBILE VIEWPORT (390 x 844)
        # -------------------------------------------------------------
        print("\n--- 5. Testing Mobile Viewport ---")
        m_context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        m_page = await m_context.new_page()
        await m_page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await m_page.wait_for_timeout(1000)
        shot_mobile = SCREENSHOTS_DIR / "react_chat_mobile_verified.png"
        await m_page.screenshot(path=str(shot_mobile), full_page=False)
        print("✓ Captured Mobile Viewport:", shot_mobile)

        await m_context.close()
        await browser.close()

        # Copy captured screenshots to artifacts directory
        for s in [shot_notif, shot_guest_limit, shot_auth_modal, shot_light, shot_mobile]:
            if s.exists():
                dst = ARTIFACT_DIR / s.name
                shutil.copy2(str(s), str(dst))
                print(f"✓ Copied artifact: {s.name}")

    print("\nAll verification captures completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_verification())
