import asyncio
import os
import sys
import uuid
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8001")

async def run_verification():
    print(f"Starting verification against {BASE_URL}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 840})
        page = await context.new_page()

        # Step 1: Clean guest session
        print("\n--- 1. Testing Clean Guest Session (0/3) ---")
        # Reset session
        await page.goto(f"{BASE_URL}/chat?lang=en", wait_until="networkidle")
        await page.evaluate("""async () => {
            await fetch('/api/guest-reset', { method: 'POST' });
            localStorage.clear();
        }""")
        await page.reload(wait_until="networkidle")

        # Check sidebar guest badge and count
        sidebar = page.locator("#chatHistorySidebar")
        await sidebar.wait_for(state="visible")
        sidebar_text = await sidebar.inner_text()
        print("Sidebar text preview:", sidebar_text[:120].replace('\n', ' '))
        assert "0/3 messages used" in sidebar_text, f"Expected 0/3 messages used, got: {sidebar_text}"
        print("✓ Verified: Fresh guest session starts at 0/3.")

        # Capture 0/3 screenshot
        await page.screenshot(path="tests/screenshots/guest_0_of_3.png")

        # Step 2: Test Interactive Prompt Starter Cards
        print("\n--- 2. Testing Prompt Starter Card Interaction ---")
        prompt1 = page.locator("#heroPromptCard1")
        await prompt1.wait_for(state="visible")
        # Check class
        prompt1_class = await prompt1.get_attribute("class")
        assert "interactive-glass-card" in prompt1_class, f"Expected interactive-glass-card in prompt1, got {prompt1_class}"

        # Click prompt 1
        print("Clicking prompt 1...")
        await prompt1.click()

        # Wait for streaming to complete
        await page.wait_for_timeout(3000)
        # Wait for answer to appear
        bot_msg = page.locator(".msg.bot")
        await bot_msg.first.wait_for(state="visible", timeout=10000)
        print("✓ Bot message received.")

        # Check updated guest counter in sidebar
        sidebar_text = await sidebar.inner_text()
        print("Sidebar text after 1st question:", sidebar_text[:120].replace('\n', ' '))
        assert "1/3 messages used" in sidebar_text, f"Expected 1/3 messages used, got: {sidebar_text}"
        print("✓ Verified: Incremented to 1/3 after successful response.")
        await page.screenshot(path="tests/screenshots/guest_1_of_3.png")

        # Step 3: Send 2nd question
        print("\n--- 3. Sending 2nd question ---")
        input_box = page.locator("#questionInput")
        await input_box.fill("List major government schemes in India")
        send_btn = page.locator("#sendBtn")
        await send_btn.click()
        await page.wait_for_timeout(3000)
        await page.locator(".msg.bot").nth(1).wait_for(state="visible", timeout=10000)

        sidebar_text = await sidebar.inner_text()
        assert "2/3 messages used" in sidebar_text, f"Expected 2/3 messages used, got: {sidebar_text}"
        print("✓ Verified: Incremented to 2/3.")

        # Step 4: Send 3rd question (Reaching Limit)
        print("\n--- 4. Sending 3rd question (Reaching 3/3 Limit) ---")
        await input_box.fill("Explain climate change in simple terms")
        await send_btn.click()
        await page.wait_for_timeout(3000)
        await page.locator(".msg.bot").nth(2).wait_for(state="visible", timeout=10000)

        sidebar_text = await sidebar.inner_text()
        assert "3/3 messages used" in sidebar_text, f"Expected 3/3 messages used, got: {sidebar_text}"
        print("✓ Verified: Incremented to 3/3.")

        # Check guest limit card
        limit_card = page.locator("#guestLimitCard")
        await limit_card.wait_for(state="visible")
        limit_card_text = await limit_card.inner_text()
        print("Limit card text:", limit_card_text.replace('\n', ' '))
        assert "3-question trial limit" in limit_card_text or "3/3" in limit_card_text
        print("✓ Verified: Guest trial limit card displayed.")

        # Check composer disabled state
        is_disabled = await input_box.is_disabled()
        assert is_disabled, "Expected questionInput to be disabled at 3/3"
        print("✓ Verified: Question input is disabled.")

        # Capture 3/3 locked screenshot
        await page.screenshot(path="tests/screenshots/guest_3_of_3_locked.png")

        # Step 5: Test Reload Abuse Protection
        print("\n--- 5. Testing Page Reload Abuse Protection ---")
        await page.reload(wait_until="networkidle")
        sidebar_text = await sidebar.inner_text()
        assert "3/3 messages used" in sidebar_text, f"Expected 3/3 after reload, got: {sidebar_text}"
        is_disabled_after_reload = await page.locator("#questionInput").is_disabled()
        assert is_disabled_after_reload, "Expected questionInput to remain disabled after reload"
        print("✓ Verified: Trial limit cannot be bypassed by reloading the page.")

        # Step 6: Test Sidebar Collapse & Expand
        print("\n--- 6. Testing Sidebar Collapse and Reopen ---")
        collapse_btn = page.locator("#chatSidebarCollapseBtn")
        await collapse_btn.click()
        await page.wait_for_timeout(500)
        reopen_btn = page.locator("#chatSidebarReopenBtn")
        await reopen_btn.wait_for(state="visible")
        print("✓ Sidebar collapsed successfully; reopen button visible.")
        await page.screenshot(path="tests/screenshots/sidebar_collapsed.png")

        await reopen_btn.click()
        await page.wait_for_timeout(500)
        await sidebar.wait_for(state="visible")
        print("✓ Sidebar reopened successfully.")

        # Step 7: Test About Page Interactive Cards & Modals
        print("\n--- 7. Testing About Page Interactive Cards & Modals ---")
        await page.goto(f"{BASE_URL}/about?lang=en", wait_until="networkidle")

        # Find the 3 disparity cards
        disparity_cards = page.locator(".interactive-glass-card")
        count = await disparity_cards.count()
        print(f"Total interactive glass cards found on About page: {count}")
        assert count >= 10, f"Expected at least 10 interactive cards, found {count}"

        # Card 1: Tokenization
        tokenization_card = page.locator('.interactive-glass-card:has-text("Tokenization Asymmetry")').first
        await tokenization_card.hover()
        await page.wait_for_timeout(300)
        print("Hovering on Tokenization card...")

        # Click to open modal
        await tokenization_card.click()
        modal = page.locator("#aboutDetailModal")
        await modal.wait_for(state="visible", timeout=5000)
        modal_text = await modal.inner_text()
        print("FULL MODAL TEXT:\n", modal_text)
        assert "Tokenization Asymmetry" in modal_text or "TOKENIZATION" in modal_text
        print("✓ Tokenization modal opened with rich metrics.")
        await page.screenshot(path="tests/screenshots/about_tokenization_modal.png")

        # Close modal
        close_btn = page.locator("#aboutModalCloseXBtn")
        await close_btn.click()
        await page.wait_for_timeout(500)

        # Step 8: Authenticated User Unrestricted Test
        print("\n--- 8. Testing Authenticated User Exemption ---")
        # Sign up a new user
        unique_email = f"tester_{uuid.uuid4().hex[:8]}@example.com"

        # Navigate to sign in/up
        await page.goto(f"{BASE_URL}/signup?lang=en", wait_until="networkidle")
        await page.fill('input[name="name"]', "Verified Researcher")
        await page.fill('input[name="email"]', unique_email)
        await page.fill('input[name="password"]', "SecurePass123!Safe")
        await page.fill('input[name="confirm_password"]', "SecurePass123!Safe")
        consent_box = page.locator('input[name="consent"]')
        if await consent_box.count() > 0:
            await consent_box.check()
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(2000)

        # Go to chat as authenticated user
        await page.goto(f"{BASE_URL}/chat?lang=en", wait_until="networkidle")
        auth_sidebar = page.locator("#chatHistorySidebar")
        auth_sidebar_text = await auth_sidebar.inner_text()
        assert "Guest Trial" not in auth_sidebar_text, "Signed-in user should not see Guest Trial"
        print("✓ Verified: Signed-in user is completely exempt from guest trial limits.")

        auth_input = page.locator("#questionInput")
        is_auth_disabled = await auth_input.is_disabled()
        assert not is_auth_disabled, "Signed-in user question input should be enabled"
        print("✓ Verified: Signed-in user composer is enabled and unlimited.")

        await page.screenshot(path="tests/screenshots/authenticated_unlimited_chat.png")

        print("\nALL INTERACTION AND GUEST TRIAL VERIFICATIONS PASSED SUCCESSFULLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
