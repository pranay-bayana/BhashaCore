import asyncio
import os
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://127.0.0.1:8001"
SCREENSHOTS_DIR = Path("/Users/pranaybayana/.gemini/antigravity/brain/c72a710a-7ca7-4240-842d-52b9bc251251")

async def wait_for_response(page, timeout=45000):
    """Wait for bot response to finish streaming and answer text to be populated."""
    await page.wait_for_selector(".msg.bot .answer-text", timeout=timeout)
    await page.wait_for_function(
        "() => { const els = document.querySelectorAll('.msg.bot .answer-text'); if (!els.length) return false; const last = els[els.length - 1]; return (last.innerText || '').trim().length > 10; }",
        timeout=timeout
    )
    await page.wait_for_selector("#sendBtn:not([style*='display: none'])", timeout=timeout)
    await page.wait_for_timeout(1000)

async def run_guest_session_comprehensive():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("\n================== 1. FRESH GUEST INITIALIZATION ==================")
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Verify clean URL (no stale query parameters)
        current_url = page.url
        print(f"Initial URL: {current_url}")
        assert current_url.rstrip("/") == f"{BASE_URL}/chat", f"Fresh chat URL must be clean without stale ID, got {current_url}"

        # 2. Verify welcome hero
        welcome_hero = page.locator(".hero-headline-center")
        assert await welcome_hero.is_visible(), "Welcome hero must be visible on clean workspace"

        # 3. Verify guest trial starts at 0/3
        content = await page.content()
        assert "0/3" in content, "Guest trial must start at 0/3"
        print("Guest trial starts at 0/3.")

        # 4. Verify temporary memory notice in sidebar
        assert "kept in memory" in content.lower(), "Sidebar must indicate conversations are kept in memory and not saved"
        print("Sidebar memory indicator confirmed.")

        print("\n================== 2. SUBMIT QUESTION 1 (0/3 -> 1/3) ==================")
        input_el = page.locator("#questionInput")
        await input_el.fill("What is photosynthesis?")
        await page.click("#sendBtn")
        await wait_for_response(page)

        # Verify quota incremented to 1/3
        content = await page.content()
        assert "1/3" in content, "Guest quota must increment to 1/3 after successful answer"
        print("Guest quota incremented to 1/3.")

        # Verify URL now has conversation ID
        conv1_url = page.url
        print(f"URL after question 1: {conv1_url}")
        assert "?id=" in conv1_url, "URL must update with conversation ID after sending message"
        conv1_id = re.search(r"id=([^&]+)", conv1_url).group(1)

        # Verify sidebar shows Conversation 1
        sidebar_history = page.locator("#chatHistoryList")
        history_text = await sidebar_history.inner_text()
        assert "photosynthesis" in history_text.lower(), "Conversation 1 title missing from sidebar"
        print("Conversation 1 appears in sidebar history.")

        print("\n================== 3. REFRESH ON ACTIVE CONVERSATION ==================")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # URL preserved
        assert conv1_id in page.url, "Active conversation ID must persist across refresh"
        # Quota preserved
        content = await page.content()
        assert "1/3" in content, "Quota must remain 1/3 across refresh"
        # Messages preserved
        assert "photosynthesis" in content.lower(), "Conversation 1 messages must survive reload"
        print("Active conversation and 1/3 quota survived page reload.")

        print("\n================== 4. CROSS-PAGE NAVIGATION ==================")
        # Navigate to About
        await page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        await page.wait_for_timeout(500)
        # Navigate back to Chat on conv1
        await page.goto(f"{BASE_URL}/chat?id={conv1_id}", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        content = await page.content()
        assert "1/3" in content, "Guest quota must persist across full navigation to About and back"
        assert "photosynthesis" in content.lower(), "Conversation 1 content must persist after returning from About"
        print("Guest quota 1/3 and Conversation 1 persisted across multi-page navigation.")

        print("\n================== 5. CLICKING NEW CHAT ==================")
        new_chat_btn = page.locator("#newChatBtn")
        await new_chat_btn.click()
        await page.wait_for_timeout(1000)

        # URL changed to genuinely new ID
        conv2_url = page.url
        print(f"URL after New Chat: {conv2_url}")
        assert "?id=" in conv2_url, "New Chat must update URL with new ID"
        conv2_id = re.search(r"id=([^&]+)", conv2_url).group(1)
        assert conv2_id != conv1_id, "New Chat must generate a genuinely new session ID"

        # Canvas cleared immediately to welcome screen
        assert await welcome_hero.is_visible(), "Welcome screen must be displayed on New Chat"
        # Input cleared and focused
        input_val = await input_el.input_value()
        assert input_val == "", "Input must be cleared"
        # Quota NOT reset (must still be 1/3)
        content = await page.content()
        assert "1/3" in content, "New Chat must NOT reset guest quota!"
        # Previous conversation 1 still in sidebar
        hist_text = await sidebar_history.inner_text()
        assert "photosynthesis" in hist_text.lower(), "Previous conversation must remain in sidebar"
        print("New Chat successfully updated URL, cleared canvas, preserved previous chat, and maintained 1/3 quota.")

        print("\n================== 6. SUBMIT QUESTION 2 (1/3 -> 2/3) ==================")
        await input_el.fill("Explain climate change in simple terms")
        await page.click("#sendBtn")
        await wait_for_response(page)

        # Quota must be 2/3
        content = await page.content()
        assert "2/3" in content, "Guest quota must increment to 2/3"
        # Both conversations in sidebar
        hist_text = await sidebar_history.inner_text()
        assert "photosynthesis" in hist_text.lower(), "Conv 1 must be in sidebar"
        assert "climate" in hist_text.lower(), "Conv 2 must be in sidebar"
        print("Question 2 completed: quota is 2/3, both conversations in sidebar.")

        print("\n================== 7. BROWSER BACK & FORWARD NAVIGATION ==================")
        # Browser Back -> Conversation 1
        print("Navigating browser back...")
        await page.go_back(wait_until="networkidle")
        await page.wait_for_timeout(1500)
        assert conv1_id in page.url, f"Browser back must return to conv1 URL {conv1_id}, got {page.url}"
        content_back = await page.content()
        assert "photosynthesis" in content_back.lower(), "Conversation 1 content must be restored on browser back"
        print("Browser back navigation restored Conversation 1.")

        # Browser Forward -> Conversation 2
        print("Navigating browser forward...")
        await page.go_forward(wait_until="networkidle")
        await page.wait_for_timeout(1500)
        assert conv2_id in page.url, f"Browser forward must return to conv2 URL {conv2_id}, got {page.url}"
        content_fwd = await page.content()
        assert "climate" in content_fwd.lower(), "Conversation 2 content must be restored on browser forward"
        print("Browser forward navigation restored Conversation 2.")

        print("\n================== 8. STALE ID CLEARANCE (SCREENSHOT DEFECT FIX) ==================")
        # Navigate to a stale / non-existent conversation ID
        stale_id = "640bae2a-405b-402e-8c00-1758db46670d"
        print(f"Navigating to stale conversation URL: /chat?id={stale_id}...")
        await page.goto(f"{BASE_URL}/chat?id={stale_id}", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # The stale ID MUST BE CLEARED from the URL!
        cleared_url = page.url
        print(f"URL after stale ID cleanup: {cleared_url}")
        assert stale_id not in cleared_url, f"Stale conversation ID {stale_id} must be purged from URL!"
        assert cleared_url.rstrip("/") == f"{BASE_URL}/chat", f"URL must become clean /chat, got {cleared_url}"

        # Clean new-chat workspace shown
        assert await welcome_hero.is_visible(), "Clean new-chat workspace must be shown when conversation is unavailable"
        # Quota remains intact (2/3)
        content_stale = await page.content()
        assert "2/3" in content_stale, "Quota must remain 2/3 after stale ID clearance"
        print("Stale ID purged from URL! Clean new-chat workspace rendered with intact quota.")

        print("\n================== 9. SUBMIT QUESTION 3 (2/3 -> 3/3 TRIAL LIMIT) ==================")
        input_el = page.locator("#questionInput")
        await input_el.fill("How does rain form in nature?")
        await page.click("#sendBtn")
        await wait_for_response(page)

        # Quota must be 3/3
        content = await page.content()
        assert "3/3" in content, "Guest quota must reach 3/3"
        print("Guest trial limit (3/3) reached.")

        # Locked limit banner should be visible
        locked_banner = page.locator("#composerGuestSignInBtn")
        assert await locked_banner.is_visible(), "Trial limit locked banner must be visible"

        # Input should be disabled
        is_disabled = await input_el.is_disabled()
        assert is_disabled, "Question input must be disabled after 3/3 trial limit"
        print("Trial limit enforcement confirmed (input disabled, banner visible).")

        # Refresh page: quota and lock must persist
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1000)
        content_reload = await page.content()
        assert "3/3" in content_reload, "3/3 quota must persist across refresh"
        assert await page.locator("#questionInput").is_disabled(), "Input must remain disabled after refresh"
        print("3/3 locked quota persisted across refresh.")

        # Take verification screenshot
        screenshot_path = SCREENSHOTS_DIR / "bhashacore_guest_session_consistency_verified.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"Captured verification screenshot: {screenshot_path}")

        print("\n================== 10. DATABASE GUEST ISOLATION CHECK ==================")
        from src.app import app
        from src.auth import db, Conversation
        with app.app_context():
            guest_convs = db.session.scalars(db.select(Conversation).where(Conversation.user_id.is_(None))).all()
            assert len(guest_convs) == 0, "Guest conversations must never be in permanent Conversation table"
        print("Database verification: 0 guest conversations in permanent table (temporary memory confirmed).")

        await context.close()
        await browser.close()
        print("\n=== ALL GUEST SESSION INCONSISTENCY TESTS PASSED 100%! ===")

if __name__ == "__main__":
    asyncio.run(run_guest_session_comprehensive())
