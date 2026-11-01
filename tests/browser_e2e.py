"""BhashaCore browser end-to-end verification (Playwright).

Covers: chat streaming + citations + language switching, all four research
pages, responsive layout, console errors, failed requests, keyboard nav.

Waiting contract: each submitted question adds exactly one new status line;
we wait for the message COUNT to grow (never match stale lines from earlier
messages — that was the bug in the first version of this harness).
"""

import asyncio
import sys
import time

from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8001"
RESULTS = {"pass": 0, "fail": 0, "details": []}


def check(name, ok, detail=""):
    RESULTS["pass" if ok else "fail"] += 1
    mark = "PASS" if ok else "FAIL"
    RESULTS["details"].append(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


async def status_lines(page):
    return await page.locator(".status-line").all_text_contents()


async def wait_for_new_message(page, expected_count, timeout=90):
    """Wait until at least `expected_count` completed status lines exist."""
    end = time.time() + timeout
    while time.time() < end:
        s = await status_lines(page)
        if len(s) >= expected_count and not any("Searching the corpus" in x for x in s):
            return s
        await page.wait_for_timeout(400)
    return await status_lines(page)


async def submit(page, question):
    await page.locator("#questionInput").fill(question)
    await page.locator("#questionInput").press("Enter")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()

        console_errors = []
        failed_requests = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("requestfailed", lambda r: failed_requests.append(r.url))

        # ------------------------------------------------------------------
        # 1. Chat page loads with real data
        # ------------------------------------------------------------------
        await page.goto(BASE + "/", wait_until="networkidle")
        check("chat page title", "BhashaCore" in await page.title())
        check("7 language buttons (auto + 6 languages)", await page.locator(".lang-btn").count() == 7)
        check("5 nav links", await page.locator("nav.main-nav a").count() == 5)
        example_count = await page.locator(".example-q").count()
        check("real example chips rendered", example_count >= 6, f"{example_count} chips")

        # ------------------------------------------------------------------
        # 2. Hindi question: streaming, answer, citations
        # ------------------------------------------------------------------
        await page.click('.lang-btn[data-lang="hi"]')
        await submit(page, "ताजमहल कहां स्थित है?")

        # while generating, the Stop button must be visible (loading state)
        stop_visible = False
        for _ in range(12):
            if await page.locator("#stopBtn").is_visible():
                stop_visible = True
                break
            await page.wait_for_timeout(150)
        check("stop button visible during generation", stop_visible)

        s = await wait_for_new_message(page, 1)
        latest = s[-1]
        check("hindi answer completed", "grounded in" in latest, latest)
        answer_text = await page.locator(".msg.bot .answer-text").last.text_content()
        check("hindi answer contains gold fact", "आगरा" in (answer_text or ""), repr((answer_text or "")[:60]))
        badge = await page.locator("#langBadge").text_content()
        check("language badge shows Hindi", "Hindi" in badge, badge)

        sources_btn = page.locator(".sources-btn").first
        check("sources button present", await sources_btn.count() > 0)
        btn_text = await sources_btn.text_content()
        check("sources cite real passages", "used" in btn_text, btn_text)
        await sources_btn.click()
        await page.wait_for_timeout(300)
        visible_sources = await page.locator(".sources-list.show .source-item").count()
        check("citations expand", visible_sources >= 1, f"{visible_sources} source items visible")
        first_source = await page.locator(".sources-list.show .source-item").first.text_content()
        check("citation shows pid+source", ("p_" in first_source) or ("sq_" in first_source) or ("ic_" in first_source) or ("pid" in first_source) or ("sq_" in first_source))
        check("stop button hidden after completion", not await page.locator("#stopBtn").is_visible())

        # ------------------------------------------------------------------
        # 3. Insufficient evidence path
        # ------------------------------------------------------------------
        await page.click('.lang-btn[data-lang="en"]')
        await submit(page, "What is the airspeed velocity of an unladen swallow in 1492?")
        s = await wait_for_new_message(page, 2)
        check("insufficient evidence shown in UI", "Insufficient evidence" in s[-1], s[-1])
        # Click the sources button for the LAST message (the insufficient evidence one)
        await page.locator(".sources-btn").last.click()
        await page.wait_for_timeout(2000)
        # Debug: check if sources list is visible for the LAST message
        sources_list_visible = await page.locator(".sources-list.show").last.is_visible()
        not_used = await page.locator(".sources-list.show .source-item.not-used").last.count()
        check("references marked not-used", not_used >= 1, f"{not_used} not-used refs (list visible: {sources_list_visible})")

        # ------------------------------------------------------------------
        # 4. All six languages via the real API examples
        # ------------------------------------------------------------------
        done_count = 2
        for lang in ["en", "hi", "ta", "te", "kn", "ml"]:
            await page.click(f'.lang-btn[data-lang="{lang}"]')
            question = await page.evaluate(
                "fetch('/api/examples').then(r => r.json()).then(d => d.examples['" + lang + "'][0].question)"
            )
            await submit(page, question)
            done_count += 1
            s = await wait_for_new_message(page, done_count)
            ok = "grounded in" in s[-1]
            check(f"{lang} example answered", ok, s[-1])
            # Wait for UI to be ready for next input
            await page.wait_for_timeout(1000)

        # ------------------------------------------------------------------
        # 5. New chat resets the conversation
        # ------------------------------------------------------------------
        msg_count_before = await page.locator(".msg").count()
        await page.click("text=New chat")
        await page.wait_for_timeout(600)
        msg_count_after = await page.locator(".msg").count()
        check("new chat clears messages", msg_count_after < msg_count_before, f"{msg_count_before} -> {msg_count_after}")

        # ------------------------------------------------------------------
        # 6. Research pages render real data
        # ------------------------------------------------------------------
        await page.goto(BASE + "/dashboard", wait_until="networkidle")
        await page.wait_for_timeout(900)
        counts_txt = await page.locator("#countsCard").text_content()
        check("dashboard shows judged count", "1117" in counts_txt, counts_txt[:70])
        check("dashboard shows failure count", "530" in counts_txt)
        rows = await page.locator("#qualityTable tbody tr").count()
        check("dashboard quality table filled", rows == 6, f"{rows} language rows")
        rrows = await page.locator("#retrievalTable tbody tr").count()
        check("dashboard retrieval table filled", rrows >= 6, f"{rrows} rows")

        await page.goto(BASE + "/language-comparison", wait_until="networkidle")
        await page.wait_for_timeout(900)
        comp_rows = await page.locator("#compTable tbody tr").count()
        check("comparison table filled", comp_rows == 6, f"{comp_rows} rows")
        comp_txt = await page.locator("#compTable").text_content()
        check("comparison shows headline numbers", "4.94" in comp_txt and "2.76" in comp_txt)

        await page.goto(BASE + "/failure-analysis", wait_until="networkidle")
        await page.wait_for_timeout(900)
        fail_cards = await page.locator("#results .card").count()
        check("failure analysis loads records", fail_cards >= 5, f"{fail_cards} cards")
        await page.select_option("#langFilter", "ta")
        await page.wait_for_timeout(1200)
        ta_cards = await page.locator("#results .card").count()
        # every record card (excluding the summary card) must start with the TA code
        card_texts = await page.locator("#results .card").all_text_contents()
        record_cards = [t.strip() for t in card_texts if "matching failures shown" not in t]
        all_ta = bool(record_cards) and all(t.startswith("TA ·") for t in record_cards)
        check("ta filter returns ta-only records", ta_cards >= 2 and all_ta, f"{ta_cards} cards, all_ta={all_ta}")

        await page.goto(BASE + "/about", wait_until="networkidle")
        about_txt = await page.locator("main").text_content()
        check("about shows metric definitions", "Recall@5" in about_txt and "Faithfulness" in about_txt)
        check("about shows limitations", "limitations" in about_txt.lower())
        check("about honest demo notice", "not verified government guidance" in about_txt.lower())

        # ------------------------------------------------------------------
        # 7. Responsive layout: no horizontal overflow at all breakpoints
        # ------------------------------------------------------------------
        for width in [390, 768, 1024, 1440]:
            await page.set_viewport_size({"width": width, "height": 900})
            await page.goto(BASE + "/", wait_until="networkidle")
            overflow = await page.evaluate("document.body.scrollWidth - document.documentElement.clientWidth")
            check(f"no horizontal overflow at {width}px", overflow <= 0, f"overflow={overflow}px")
            check(f"chat window visible at {width}px", await page.locator(".chat-window").is_visible())

        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto(BASE + "/dashboard", wait_until="networkidle")
        await page.wait_for_timeout(700)
        check("dashboard usable at 390px", "1117" in (await page.locator("#countsCard").text_content()))

        # ------------------------------------------------------------------
        # 8. Keyboard navigation and visible focus
        # ------------------------------------------------------------------
        await page.goto(BASE + "/", wait_until="networkidle")
        await page.keyboard.press("Tab")
        await page.keyboard.press("Tab")
        focus_tag = await page.evaluate("document.activeElement.tagName")
        focus_visible = await page.evaluate(
            "() => { const el = document.activeElement; const s = getComputedStyle(el);"
            " return s.outlineStyle !== 'none' || s.boxShadow !== 'none' || el.matches(':focus-visible'); }"
        )
        check("keyboard navigation reaches elements", focus_tag in ("A", "BUTTON", "TEXTAREA"), focus_tag)
        check("visible focus indicator", focus_visible)
        textarea_label = await page.locator("#questionInput").get_attribute("aria-label")
        check("input has accessible label", bool(textarea_label), str(textarea_label))

        # ------------------------------------------------------------------
        # 9. Console errors / failed requests across the whole session
        # ------------------------------------------------------------------
        check("zero browser console errors", len(console_errors) == 0, "; ".join(console_errors[:3]))
        check("zero failed network requests", len(failed_requests) == 0, "; ".join(failed_requests[:3]))

        await browser.close()

    total = RESULTS["pass"] + RESULTS["fail"]
    print("\n" + "=" * 60)
    print(f"BROWSER E2E: {RESULTS['pass']}/{total} checks passed")
    if RESULTS["fail"]:
        print("FAILED CHECKS:")
        for d in RESULTS["details"]:
            if d.startswith("[FAIL]"):
                print("  " + d)
    return 1 if RESULTS["fail"] else 0


sys.exit(asyncio.run(main()))
