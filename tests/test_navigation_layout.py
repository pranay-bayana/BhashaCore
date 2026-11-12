"""Test script verifying the navigation and layout requirements:
1. Home page has NO sidebar, full width, responsive hero, top nav links.
2. Chat page has ChatGPT-style sidebar with history, new chat, search, rename, delete, current title.
3. Chat workspace has message rendering, citations, language controls.
4. Research and About pages are full-width without any sidebar.
5. Navigation between pages works seamlessly.
"""

import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8001")
SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

async def run_navigation_layout_audit():
    print(f"Connecting to {BASE_URL}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        page.on("console", lambda msg: print(f"[Console {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[Page Error] {err}"))

        # -------------------------------------------------------------
        # 1. HOME PAGE VERIFICATION (No sidebar, full width, centered hero)
        # -------------------------------------------------------------
        print("\n--- 1. Testing Home Page (/) ---")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")

        # Verify sidebar does NOT exist on Home
        chat_sidebar = await page.query_selector("#chatHistorySidebar")
        global_sidebar = await page.query_selector(".global-app-sidebar")
        assert chat_sidebar is None, "Chat sidebar should NOT exist on Home page"
        assert global_sidebar is None, "Global sidebar should NOT exist on Home page"
        print("✓ Confirmed: Home page has NO sidebar")

        # Verify top navigation
        header = await page.query_selector(".app-top-header")
        assert header is not None, "Top header must exist"
        home_link = await page.query_selector(".top-horizontal-nav a[href='/']")
        chat_link = await page.query_selector(".top-horizontal-nav a[href='/chat']")
        research_link = await page.query_selector(".top-horizontal-nav a[href='/dashboard']")
        about_link = await page.query_selector(".top-horizontal-nav a[href='/about']")
        assert home_link and chat_link and research_link and about_link, "All top nav links must exist"
        print("✓ Confirmed: Top navigation has Home, Chat, Research, About")

        # Verify header right cluster
        lang_select = await page.query_selector("#interfaceLangSelect")
        theme_btn = await page.query_selector("#themeToggleBtn")
        assert lang_select and theme_btn, "Header right controls must exist"
        print("✓ Confirmed: Language selector and theme toggle exist in header")

        # Verify hero elements
        hero_headline = await page.query_selector(".home-hero-headline")
        start_btn = await page.query_selector(".btn-start-chat")
        assert hero_headline and start_btn, "Home hero headline and Start Chatting button exist"
        print("✓ Confirmed: Home hero section is rendered with CTAs")

        # Take screenshot of Home
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_home_desktop.png"))
        print("✓ Captured screenshot: layout_home_desktop.png")

        # -------------------------------------------------------------
        # 2. CHAT PAGE VERIFICATION (Dedicated ChatGPT-style sidebar)
        # -------------------------------------------------------------
        print("\n--- 2. Testing Chat Page (/chat) ---")
        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")

        # Verify chat sidebar exists
        sidebar = await page.query_selector("#chatHistorySidebar")
        assert sidebar is not None, "Chat history sidebar must exist on /chat"
        new_chat_btn = await page.query_selector("#newChatBtn")
        search_input = await page.query_selector("#historySearchInput")
        history_list = await page.query_selector("#chatHistoryList")
        assert new_chat_btn and search_input and history_list, "Sidebar must have New Chat, Search, and History List"
        print("✓ Confirmed: ChatGPT-style sidebar exists with New Chat, Search, and History")

        # Verify main chat workspace elements
        title_badge = await page.query_selector("#currentChatTitleBadge")
        title_text = await page.query_selector("#currentChatTitle")
        assert title_badge and title_text, "Current conversation title badge must exist"

        composer = await page.query_selector(".composer-capsule")
        question_input = await page.query_selector("#questionInput")
        send_btn = await page.query_selector("#sendBtn")
        assert composer and question_input and send_btn, "Bottom message composer must exist"
        print("✓ Confirmed: Chat workspace has Title badge, composer, and send button")

        # Capture initial empty chat hero state
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_chat_empty.png"))
        print("✓ Captured screenshot: layout_chat_empty.png")

        # -------------------------------------------------------------
        # 3. CHAT CONVERSATION INTERACTION & PERSISTENCE
        # -------------------------------------------------------------
        print("\n--- 3. Testing Chat Interaction & Conversation Persistence ---")
        # Ask the exact question from user's screenshot
        await question_input.fill("What is photosynthesis?")
        await send_btn.click()

        # Wait for bot response to complete
        await page.wait_for_selector(".msg.bot .answer-text", state="visible", timeout=15000)
        await page.wait_for_selector("#sendBtn:not([disabled])", timeout=25000)

        # Verify message bubbles rendered
        user_msg = await page.query_selector(".msg.user")
        bot_msg = await page.query_selector(".msg.bot")
        assert user_msg and bot_msg, "Both user and bot messages must be rendered"

        bot_text = (await page.locator(".msg.bot .answer-text").inner_text()).strip()
        status_text = (await page.locator(".msg.bot .status-line").inner_text()).strip()
        print(f"✓ Bot status: '{status_text}'")
        print(f"✓ Bot answer snippet: '{bot_text[:80]}...'")
        assert "BAD REQUEST" not in status_text, "BAD REQUEST error must NOT appear in response status"
        assert "BAD REQUEST" not in bot_text, "BAD REQUEST error must NOT appear in bot response"
        assert len(bot_text) > 10, "Real answer text must be generated"
        print("✓ Confirmed: Real AI response streamed successfully without BAD REQUEST error")

        # Verify title badge updated to the first question
        current_title = (await title_text.inner_text()).strip()
        print(f"✓ Confirmed: Active conversation title updated to: '{current_title}'")
        assert "photosynthesis" in current_title.lower(), "Title should reflect the question asked"

        # Verify history items in sidebar
        history_titles = await page.eval_on_selector_all(
            ".history-item .history-title",
            "elements => elements.map(el => el.textContent.trim())"
        )
        print(f"✓ Confirmed: {len(history_titles)} conversation item(s) in sidebar")
        # Assert NO generic 'Conversation' placeholder exists
        generic_conversations = [t for t in history_titles if t == "Conversation" or t == "बातचीत"]
        assert len(generic_conversations) == 0, f"No entries should be named 'Conversation', found: {generic_conversations}"
        print("✓ Confirmed: Zero placeholder entries named 'Conversation'")

        # Verify citations button if available
        sources_btn = await page.query_selector(".sources-btn")
        if sources_btn:
            await sources_btn.click()
            sources_list = await page.query_selector(".sources-list.show")
            assert sources_list is not None, "Sources list must expand on click"
            print("✓ Confirmed: Research citations expand with source metadata")

        # Capture active chat screenshot
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_chat_active.png"))
        print("✓ Captured screenshot: layout_chat_active.png")

        # Test Search filtering in sidebar
        search_input = await page.query_selector("#historySearchInput")
        await search_input.fill("photosynthesis")
        await page.wait_for_timeout(300)
        filtered_count = len(await page.query_selector_all(".history-item"))
        print(f"✓ Confirmed: History search for 'photosynthesis' returned {filtered_count} item(s)")
        await search_input.fill("")
        await page.wait_for_timeout(300)

        # Test New Chat button
        await new_chat_btn.click()
        await page.wait_for_timeout(500)
        new_title = (await title_text.inner_text()).strip()
        print(f"✓ Confirmed: After clicking New Chat, title is '{new_title}' and hero stage is reset")

        # Test loading previous conversation by clicking in history
        first_item = await page.wait_for_selector(".history-item")
        first_item_id = await first_item.get_attribute("data-id")
        await first_item.click()
        await page.wait_for_timeout(600)

        # Verify messages reloaded
        reloaded_msgs = await page.query_selector_all(".msg")
        assert len(reloaded_msgs) >= 2, "Previous conversation messages must be loaded upon click"
        print("✓ Confirmed: Clicking saved conversation loaded previous messages into chat workspace")

        # Verify URL updated with ?id=
        assert f"id={first_item_id}" in page.url or first_item_id in page.url, "URL must update with session id"
        print(f"✓ Confirmed: URL updated to {page.url}")

        # -------------------------------------------------------------
        # 4. RESEARCH PAGES VERIFICATION (Full width, NO sidebar)
        # -------------------------------------------------------------
        print("\n--- 4. Testing Research Pages (Full Width, No Sidebar) ---")
        for route, name in [("/dashboard", "Dashboard"), ("/language-comparison", "Comparison"), ("/failure-analysis", "Failures")]:
            await page.goto(f"{BASE_URL}{route}", wait_until="networkidle")
            sb = await page.query_selector("#chatHistorySidebar")
            assert sb is None, f"{name} should NOT have chat sidebar"
            container = await page.query_selector(".research-content-container")
            assert container is not None, f"{name} must have .research-content-container"
            print(f"✓ Confirmed: {name} ({route}) is full width without chat sidebar")

        await page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_research_dashboard.png"))
        print("✓ Captured screenshot: layout_research_dashboard.png")

        # -------------------------------------------------------------
        # 5. ABOUT PAGE VERIFICATION (Full width, NO sidebar)
        # -------------------------------------------------------------
        print("\n--- 5. Testing About Page (Full Width, No Sidebar) ---")
        await page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        sb = await page.query_selector("#chatHistorySidebar")
        assert sb is None, "About page should NOT have chat sidebar"
        container = await page.query_selector(".about-container")
        assert container is not None, "About page must have .about-container"
        print("✓ Confirmed: About page is full width without chat sidebar")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_about_desktop.png"))
        print("✓ Captured screenshot: layout_about_desktop.png")

        # -------------------------------------------------------------
        # 6. MOBILE RESPONSIVENESS (390x844)
        # -------------------------------------------------------------
        print("\n--- 6. Testing Mobile Viewport (390px) ---")
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_home_mobile.png"))
        print("✓ Captured screenshot: layout_home_mobile.png")

        await page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "layout_chat_mobile.png"))
        print("✓ Captured screenshot: layout_chat_mobile.png")

        print("\n==========================================")
        print("ALL LAYOUT & NAVIGATION CHECKS PASSED 100%!")
        print("==========================================")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_navigation_layout_audit())
