"""Browser-level DOM harness for the MV3 content script.

Chrome does not load unpacked extensions in this environment's headless mode,
so this test runs the actual content script in Chromium with the Chrome APIs
and backend response boundary simulated.  It verifies safe node replacement,
dynamic DOM handling, and restore behavior without sending webpage content to
an external service.
"""
import asyncio
from pathlib import Path

import pytest
from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "browser-extension"


@pytest.mark.playwright
def test_content_script_translate_dynamic_content_and_restore():
    async def scenario():
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.evaluate("""
                window.__listener = null;
                window.chrome = {
                  storage: { local: { get: async () => ({apiBaseUrl: 'https://bhashacore.onrender.com'}) } },
                  runtime: {
                    onMessage: { addListener: (listener) => { window.__listener = listener; } },
                    sendMessage: async () => undefined
                  }
                };
            """)
            async def translate_route(route):
                request = route.request.post_data_json
                await route.fulfill(json={"translations": [
                    {"id": segment["id"], "text": f"T:{segment['text']}"}
                    for segment in request["segments"]
                ]})
            await page.route("**/api/translate", translate_route)
            await page.set_content("""
                <h1>Welcome</h1><p id='copy'>Visible content</p><pre id='code'>const x = 1;</pre>
                <input id='plain' placeholder='Your name'><input id='password' type='password' placeholder='Secret'>
                <div id='dynamic'></div>
            """)
            await page.add_script_tag(path=str(EXTENSION / "core.js"))
            await page.add_script_tag(path=str(EXTENSION / "content.js"))

            async def command(payload):
                return await page.evaluate("""async (payload) => new Promise((resolve) => window.__listener(payload, null, resolve))""", payload)

            result = await command({"type": "translate", "targetLang": "hi"})
            assert result["status"] == "translated"
            assert await page.locator("#copy").text_content() == "T:Visible content"
            assert await page.locator("#code").text_content() == "const x = 1;"
            assert await page.locator("#plain").get_attribute("placeholder") == "T:Your name"
            assert await page.locator("#password").get_attribute("placeholder") == "Secret"

            await page.locator("#dynamic").evaluate("""element => element.innerHTML = `
                <p id=late>Added later</p><button id=one title='First action'>One</button>
                <button id=two title='Second action'>Two</button>`""")
            await page.wait_for_function("document.querySelector('#late')?.textContent === 'T:Added later'")
            assert await page.locator("#one").get_attribute("title") == "T:First action"
            assert await page.locator("#two").get_attribute("title") == "T:Second action"

            restored = await command({"type": "restore"})
            assert restored["status"] == "original"
            assert await page.locator("#copy").text_content() == "Visible content"
            assert await page.locator("#plain").get_attribute("placeholder") == "Your name"
            await browser.close()

    asyncio.run(scenario())
