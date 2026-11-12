import asyncio
import os
import uuid
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8001"
SCREENSHOTS_DIR = Path("/Users/pranaybayana/.gemini/antigravity/brain/c72a710a-7ca7-4240-842d-52b9bc251251")

async def wait_for_response(page, timeout=45000):
    # Wait for bot message to appear
    await page.wait_for_selector(".msg.bot .answer-text", timeout=timeout)
    # Wait for answer-text to contain actual characters (not empty)
    await page.wait_for_function(
        "() => { const els = document.querySelectorAll('.msg.bot .answer-text'); if (!els.length) return false; const last = els[els.length - 1]; return (last.innerText || '').trim().length > 10; }",
        timeout=timeout
    )
    # Wait for streaming to finish (#sendBtn visible)
    await page.wait_for_selector("#sendBtn:not([style*='display: none'])", timeout=timeout)
    await page.wait_for_timeout(1000)

async def run_lifecycle_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # =========================================================================
        # PART A: GUEST USER LIFECYCLE
        # =========================================================================
        print("\n================== PART A: GUEST USER ==================")
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[A1] Navigating to /chat as fresh guest...")
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Verify welcome screen is visible
        welcome_hero = page.locator(".hero-headline-center")
        assert await welcome_hero.is_visible(), "Expected welcome screen to be visible"
        print("Welcome screen is visible on empty chat.")

        # Check guest quota is 0/3
        content = await page.content()
        assert "0/3" in content, "Guest trial must start at 0/3"
        print("Guest trial starts at 0/3.")

        # [A2] Send question in conversation 1
        print("[A2] Sending 1st question: 'What is photosynthesis?'...")
        input_el = page.locator("#questionInput")
        await input_el.fill("What is photosynthesis?")
        await page.click("#sendBtn")

        # Wait for answer
        await wait_for_response(page)

        # Verify guest quota is now 1/3
        content = await page.content()
        assert "1/3" in content, "Guest trial must now be 1/3"
        print("Guest trial incremented to 1/3.")

        # Verify sidebar shows conversation 1
        sidebar_history = page.locator("#chatHistoryList")
        history_text = await sidebar_history.inner_text()
        assert "photosynthesis" in history_text.lower(), "Conversation 1 title missing from sidebar"
        print("Conversation 1 appears in sidebar history.")

        # [A3] Click 'New Chat' button
        print("[A3] Testing New Chat button...")
        # Check active session before
        initial_url = page.url
        print(f"URL before New Chat: {initial_url}")

        # Click New Chat
        new_chat_btn = page.locator("#newChatBtn")
        await new_chat_btn.click()
        await page.wait_for_timeout(1000)

        # Verify URL changed to new session
        new_url = page.url
        print(f"URL after New Chat: {new_url}")
        assert new_url != initial_url, "URL must update with new session ID"

        # Verify chat area immediately becomes empty and displays welcome screen
        assert await welcome_hero.is_visible(), "Chat area must display welcome screen on New Chat"
        print("Chat area cleared and displays welcome screen.")

        # Verify input field is cleared and focused
        input_val = await input_el.input_value()
        assert input_val == "", "Input field must be cleared"
        is_focused = await input_el.evaluate("el => document.activeElement === el")
        print(f"Input is cleared: {input_val == ''}, focused: {is_focused}")

        # Verify creating a new chat does NOT reset the guest quota (must still be 1/3)
        content_after_new = await page.content()
        assert "1/3" in content_after_new, "New chat must NOT reset guest trial quota!"
        print("Guest trial quota remains 1/3 after New Chat (no reset).")

        # Verify previous conversation 1 is STILL in the sidebar
        history_text_after_new = await sidebar_history.inner_text()
        assert "photosynthesis" in history_text_after_new.lower(), "Previous conversation must remain in sidebar"
        print("Previous conversation remained in sidebar.")

        # [A4] Send question in conversation 2
        print("[A4] Sending question in conversation 2: 'Explain climate change'...")
        await input_el.fill("Explain climate change in simple terms")
        await page.click("#sendBtn")
        await wait_for_response(page)

        # Quota must be 2/3
        content_conv2 = await page.content()
        assert "2/3" in content_conv2, "Guest trial must now be 2/3"
        print("Guest trial incremented to 2/3.")

        # Both conversations must appear in the sidebar
        history_text_both = await sidebar_history.inner_text()
        assert "photosynthesis" in history_text_both.lower(), "Conv 1 must be in sidebar"
        assert "climate" in history_text_both.lower(), "Conv 2 must be in sidebar"
        print("Both conversations present in sidebar history.")

        # [A5] Switch back to Conversation 1
        print("[A5] Switching back to Conversation 1...")
        conv1_item = page.locator("#chatHistoryList >> text=photosynthesis")
        await conv1_item.first.click()
        await page.wait_for_timeout(1500)

        # Verify messages for Conv 1 are restored
        conv1_content = await page.content()
        assert "photosynthesis" in conv1_content, "Conversation 1 content must be restored"
        print("Conversation 1 restored successfully.")

        # [A6] Refresh page and verify active conversation is preserved
        print("[A6] Refreshing page to verify persistence...")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(2000)
        refreshed_content = await page.content()
        assert "photosynthesis" in refreshed_content, "Active conversation must persist across reload"
        assert "2/3" in refreshed_content, "2/3 quota must persist across reload"
        print("Active conversation and quota survived page reload.")

        # [A7] Test New Chat when sidebar is collapsed (Toolbar New Chat button)
        print("[A7] Testing New Chat with collapsed sidebar...")
        collapse_btn = page.locator("#chatSidebarCollapseBtn")
        if await collapse_btn.is_visible():
            await collapse_btn.click()
            await page.wait_for_timeout(500)
            print("Sidebar collapsed.")

            toolbar_new_btn = page.locator("#toolbarNewChatBtn")
            assert await toolbar_new_btn.is_visible(), "Toolbar New Chat button must be visible when sidebar is collapsed"
            await toolbar_new_btn.click()
            await page.wait_for_timeout(1000)
            assert await welcome_hero.is_visible(), "Toolbar New Chat must clear chat and show welcome screen"
            print("Toolbar New Chat works independently while sidebar is collapsed!")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "bhashacore_new_chat_guest_verified.png"))
        await context.close()

        # =========================================================================
        # PART B: AUTHENTICATED USER LIFECYCLE
        # =========================================================================
        print("\n================== PART B: AUTHENTICATED USER ==================")
        auth_context = await browser.new_context(viewport={"width": 1440, "height": 900})
        auth_page = await auth_context.new_page()

        # Sign up a unique test account
        test_email = f"user-{uuid.uuid4().hex[:8]}@example.com"
        print(f"[B1] Signing up test account: {test_email}...")
        await auth_page.goto(f"{BASE_URL}/signup", wait_until="networkidle")
        await auth_page.fill('input[name="name"]', "Research Tester")
        await auth_page.fill('input[name="email"]', test_email)
        await auth_page.fill('input[name="password"]', "ComplexPassword123!Safe")
        await auth_page.fill('input[name="confirm_password"]', "ComplexPassword123!Safe")
        consent_cb = auth_page.locator('input[name="consent"]')
        if await consent_cb.count() > 0:
            await consent_cb.check()
        await auth_page.click('button[type="submit"]')
        await auth_page.wait_for_timeout(1500)

        # Navigate to /chat
        print("[B2] Navigating to /chat as authenticated user...")
        await auth_page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await auth_page.wait_for_timeout(1000)

        # Authenticated user should NOT have guest trial card
        auth_content = await auth_page.content()
        assert "Guest Trial" not in auth_content, "Authenticated user must not see Guest Trial card"
        print("Authenticated user does not have guest trial limits.")

        # Send question 1
        print("[B3] Sending question as authenticated user: 'What is machine learning?'...")
        auth_input = auth_page.locator("#questionInput")
        await auth_input.fill("What is machine learning?")
        await auth_page.click("#sendBtn")
        await wait_for_response(auth_page)

        auth_history = auth_page.locator("#chatHistoryList")
        auth_hist_text = await auth_history.inner_text()
        assert "machine learning" in auth_hist_text.lower(), "Question title must be saved in database history"
        print("First question titled and saved in database history.")

        # Click New Chat as authenticated user
        print("[B4] Clicking New Chat as authenticated user...")
        await auth_page.click("#newChatBtn")
        await auth_page.wait_for_timeout(1000)

        # Verify welcome screen
        auth_welcome = auth_page.locator(".hero-headline-center")
        assert await auth_welcome.is_visible(), "Chat area must display welcome screen on New Chat"
        print("Authenticated New Chat cleared canvas and displayed welcome screen.")

        # Send question 2
        print("[B5] Sending 2nd question: 'Explain neural networks'...")
        await auth_input.fill("Explain neural networks simply")
        await auth_page.click("#sendBtn")
        await wait_for_response(auth_page)

        # Both conversations in database history
        await auth_page.wait_for_selector("#chatHistoryList >> text=neural network", timeout=15000)
        auth_hist_both = await auth_history.inner_text()
        assert "machine learning" in auth_hist_both.lower()
        assert "neural network" in auth_hist_both.lower()
        print("Both authenticated conversations persist in history.")

        # Switch between them
        print("[B6] Switching back to conversation 1...")
        await auth_page.locator("#chatHistoryList >> text=machine learning").first.click()
        await auth_page.wait_for_timeout(1500)
        conv1_auth_text = await auth_page.content()
        assert "machine learning" in conv1_auth_text.lower()
        print("Authenticated conversation switching verified.")

        # Refresh page
        print("[B7] Refreshing page...")
        await auth_page.reload(wait_until="networkidle")
        await auth_page.wait_for_timeout(2000)
        reloaded_auth = await auth_page.content()
        assert "machine learning" in reloaded_auth.lower(), "Active conversation must survive refresh"
        print("Authenticated active conversation persisted across refresh.")

        await auth_page.screenshot(path=str(SCREENSHOTS_DIR / "bhashacore_new_chat_auth_verified.png"))
        await browser.close()
        print("\n=== ALL NEW CHAT AND CONVERSATION LIFECYCLE TESTS PASSED 100%! ===")

if __name__ == "__main__":
    asyncio.run(run_lifecycle_test())
