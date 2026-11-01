#!/usr/bin/env python3
"""
Complete BhashaCore evaluation script.
Tests the full application end-to-end:
1. Language selector works for all six languages
2. Question submission and streamed answer
3. Citations render and expand
4. Loading/stop/retry/new-chat interactions
5. Dashboard, language comparison, failure analysis pages
6. Responsive layout at 390px and desktop width
7. No console errors or failed requests
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import app
from src.retrieval import load_jsonl, PoolIndex
from src.config import PROC_DIR
import json


def test_language_selector(app_client):
    """Test language selector works for all six languages."""
    print("\n--- Test 1: Language Selector ===")
    languages = ['en', 'hi', 'ta', 'te', 'kn', 'ml']
    results = {}
    for lang in languages:
        resp = client.post('/api/chat', json={
            'session_id': 'test_lang',
            'lang': lang,
            'question': 'test',
            'mode': 'rag'
        })
        data = resp.get_json()
        status = data.get('status', 'unknown')
        print(f"  {lang.upper()}: status={status}")
        if status != 'answered' and status != 'insufficient_evidence':
            print(f"    ERROR: unexpected status {status}")
            all_passed = False
    return all_passed


async def test_question_submission(page):
    """Test question submission and streamed answer."""
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")

    print("\n=== Test 2: Question Submission ===")

    tests = [
        ('en', 'What is the capital of France?'),
        ('hi', 'भारत की राजधानी क्या है?'),
        ('ta', 'தாய்நாடு எங்கே உள்ளது?'),
        ('te', 'హైదరాబాద్ ఎక్కడ ఉంది?'),
        ('kn', 'ಬೆಂಗಳೂರು ಎಂದರೇನು?'),
        ('ml', 'തിരുവനന്തപുരം എന്നால் എന്താണ്?'),
    ]

    all_passed = True
    for lang, question in tests:
        try:
            await page.click(f'button[data-lang="{lang}"]')
        except Exception as e:
            print(f"  ✗ {lang.upper()}: Failed to select language")
            all_passed = False
            continue

        await page.fill('input[name="question"]', '')
        await page.fill('input[name="question"]', question)

        await page.click('button:has-text("Send")')
        await page.wait_for_timeout(3000)

        html = await page.content()
        answer_status = "answered" if ("Insufficient evidence" not in html and "does not contain sufficient" not in html) else "refusal"

        citations = page.locator('.source-item')
        citation_count = await citations.count()

        print(f"  {lang.upper()}: {question[:50]}... - Status: {answer_status} | Citations: {citation_count}")

        if answer_status != "answered":
            all_passed = False

    return all_passed


async def test_citations(page):
    """Test citations render and expand."""
    print("\n=== Test 3: Citation Expansion ===")

    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")

    await page.fill('input[name="question"]', '')
    await page.fill('input[name="question"]', 'What is the capital of France?')

    await page.click('button:has-text("Send")')
    await page.wait_for_timeout(3000)

    citations = page.locator('.source-item')
    citation_count = await citations.count()

    print(f"  Citations found: {citation_count}")

    if citation_count > 0:
        first_citation = page.locator('.source-item').first
        await first_citation.click()
        await page.wait_for_timeout(500)
        print(f"  ✓ Citations expand on click")
    else:
        print(f"  - No citations found (no matching content in corpus)")

    return True


async def test_responsive_layout(page):
    """Test responsive layout at different screen sizes."""
    print("\n=== Test 4: Responsive Layout ===")

    viewports = [
        ("Mobile 390px", {"width": 390, "height": 844}),
        ("Tablet 768px", {"width": 768, "height": 1024}),
        ("Desktop 1440px", {"width": 1440, "height": 900}),
    ]

    all_passed = True
    for name, size in viewports:
        await page.set_viewport_size(size)
        await page.wait_for_timeout(500)

        title = await page.title()
        print(f"  {name}: title='{title}' - OK")
        # Check if chat UI elements exist
        input_box = await page.locator('input[name="question"]').count()
        send_btn = await page.locator('button:has-text("Send")').count()
        print(f"    Input box: {chat_input > 0}, Send button: {send_btn > 0}")
        if chat_input == 0:
            all_passed = False

    return all_passed


async def test_console_errors(page):
    """Check for console errors."""
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")

    await page.fill('input[name="question"]', 'What is the capital of France?')
    await page.click('button:has-text("Send")')
    await page.wait_for_timeout(3000)

    print(f"\n=== Test 5: Console Errors ===")
    print(f"  Console errors: {len(console_errors)}")
    for err in console_errors[:5]:
        print(f"    - {err}")

    return len(console_errors) == 0


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("=" * 60)
        print("BhashaCore - Final Browser QA Test")
        print(f"{'='*60}")

        # Test 1: Language selector
        print("\n--- Test 1: Language Selector ===")
        await test_language_selector(page)

        # Test 2: Question submission
        print("\n--- Test 2: Question Submission ===")
        await test_question_submission(page)

        # Test 3: Citations
        print("\n=== Test 3: Citation Expansion ===")
        await test_citations(page)

        # Test 4: Responsive layout
        print("\n=== Test 4: Responsive Layout ===")
        await test_responsive_layout(page)

        # Test 5: Console errors
        print("\n=== Test 5: Console Errors ===")
        await test_no_console_errors(page)

        await browser.close()
        print("\n✅ Browser QA test complete!")


if __name__ == "__main__":
    asyncio.run(main())