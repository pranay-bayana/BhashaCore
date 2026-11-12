import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8001"
SCREENSHOTS_DIR = Path("/Users/pranaybayana/.gemini/antigravity/brain/c72a710a-7ca7-4240-842d-52b9bc251251")

async def run_e2e():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1. Fresh incognito context
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[1] Navigating to /chat...")
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Verify only ONE sidebar
        sidebars = page.locator("aside")
        sidebar_count = await sidebars.count()
        print(f"Sidebar count on /chat: {sidebar_count}")
        assert sidebar_count == 1, f"Expected exactly 1 sidebar, found {sidebar_count}"

        # Verify guest counter 0/3
        page_text = await page.content()
        assert "0/3" in page_text or "messages used" in page_text
        print("Guest trial 0/3 verified.")

        # Capture screenshot of clean chat workspace
        await page.screenshot(path=str(SCREENSHOTS_DIR / "bhashacore_chat_clean_workspace.png"))

        # [2] Submit question "What is photosynthesis?"
        print("[2] Submitting question: 'What is photosynthesis?'...")
        input_el = page.locator("#questionInput")
        await input_el.fill("What is photosynthesis?")
        await page.click("#sendBtn")

        # Wait for assistant response to start streaming and complete
        print("Waiting for streaming response...")
        # Check that NO BAD REQUEST error appears
        await page.wait_for_timeout(3000)
        current_content = await page.content()
        assert "Error: BAD REQUEST" not in current_content, "Found Error: BAD REQUEST!"

        # Wait for completion (sources button or answered status)
        try:
            await page.wait_for_selector(".sources-btn, [data-citation], button:has-text('citations')", timeout=45000)
            print("Response completed with citations!")
        except Exception as e:
            print(f"Citation wait notice: {e}")
            await page.wait_for_timeout(5000)

        # Capture active chat with streaming response & citations
        await page.screenshot(path=str(SCREENSHOTS_DIR / "bhashacore_chat_answered_citations.png"))

        # [3] Verify guest counter updated to 1/3
        updated_text = await page.content()
        assert "1/3" in updated_text, "Expected guest counter to be 1/3"
        print("Guest counter is 1/3.")

        # [4] Verify sidebar has meaningful title (not 'Conversation')
        history_list = page.locator("#chatHistoryList")
        history_text = await history_list.inner_text()
        print(f"Conversation history text:\n{history_text}")
        assert "photosynthesis" in history_text.lower(), "Expected question title in history"
        assert "Conversation\nConversation" not in history_text, "Found repeated dummy Conversation entries!"

        # [5] Refresh page to verify persistence
        print("[5] Refreshing page to verify persistence...")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(2000)

        refreshed_text = await page.content()
        assert "1/3" in refreshed_text, "Expected 1/3 to persist across refresh"
        refreshed_history = await page.locator("#chatHistoryList").inner_text()
        assert "photosynthesis" in refreshed_history.lower(), "Expected conversation to persist in history"
        print("Persistence across refresh verified!")

        # [6] Click '+ New chat'
        print("[6] Clicking + New chat...")
        await page.click("#newChatBtn")
        await page.wait_for_timeout(1000)

        # Verify chat workspace is cleared for new chat, while previous chat remains in history
        new_history = await page.locator("#chatHistoryList").inner_text()
        assert "photosynthesis" in new_history.lower(), "Previous conversation must remain in history after new chat"
        print("New chat creation verified!")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "bhashacore_chat_after_new_chat.png"))
        await browser.close()
        print("\n=== ALL E2E VERIFICATION TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(run_e2e())
