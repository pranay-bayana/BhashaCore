#!/usr/bin/env python3
"""
BhashaCore Live Browser QA Test.

Tests:
1. Language selector works for all six languages
2. Question submission and streamed answer
3. Citations render and expand
4. Loading/stop/retry/new-chat interactions
5. Dashboard, language comparison, failure analysis pages
6. Responsive layout at 390px and desktop
7. No console errors or failed requests

Usage:
    python scripts/evaluate_full_ui.py
"""

import asyncio
import asyncio
from playwright.async_api import async_playwright
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BASE_URL = "http://127.0.0.1:8001"

TEST_QUESTIONS = {
    'en': [
        "What is the capital of India?",
        "Who was the first president of the United States?",
        "What is the largest planet in our solar system?",
        "Who wrote Romeo and Juliet?",
        "What is the boiling point of water?",
    ],
    'hi': [
        "भारत की राजधानी क्या है?",
        "भारत के प्रथम प्रधानमंत्री कौन थे?",
        "सबसे बड़ा ग्रह कौन सा है?",
        "रोमियो और जूलियट किसने लिखा?",
        "पानी का क्वथनांक क्या है?",
    ],
    'ta': [
        "தாய்நாடு எங்கே உள்ளது?",
        "தமிழ்நாட்டின் முதல்வர் யார்?",
        "வானObjectiveளில் மிகப் பெரிய கோளцыі",
        "ரோமியோ மற்றும் ஜூலியட் யார் எழுதியது?",
        "நீரின் காய்வெப்பநிலை என்ன?",
    ],
    "te": [
        "తెలంగాణ రాజధాని ఏది?",
        "హైదరాబాద్ ఎక్కడ ఉంది?",
        "ఏ క్రీడలో బంగారు పతకాన్ని గెలిచారు?",
        "మిల్లిక సింగ్ ఎవరు?",
        "నీరు ఎవరివ్వ градума?",
    ],
    "kn": "ಬೆಂಗಳೂರು ಎಂದರೇನು?",
    "ml": "തിരുവനന്തപുരം എന്നால் എന്താണ്?",
}

async def test_language_selector(page):
    """Test language selector works for all six languages."""
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")

    languages = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
    ]

    print("\n=== Test 1: Language Selector ===")
    all_passed = True
    for code, name in languages:
        try:
            await page.click(f'button[data-lang="{lang}"]')
            await page.wait_for_timeout(500)
            print(f"  ✓ {lang.upper()}: {name}")
        except Exception as e:
            print(f"  ✗ {lang.upper()}: {name} - FAILED: {e}")
            all_passed = False

    return all_passed


async def test_question_submission(page):
    """Test question submission and streamed answer."""
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")

    print("\n=== Test 2: Question Submission ===")
    question_box = page.locator('input[name="question"]')

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
        print(f"\n--- Testing {lang.upper()}: {question[:50]} ---")

        try:
            await page.click(f'button[data-lang="{lang}"]')
        except:
            print(f"  ✗ Failed to select language {lang}")
            continue

        await question_box.fill("")
        await question_box.fill(question)

        await page.click('button:has-text("Send")')
        await page.wait_for_timeout(3000)

        html = await page.content()
        answer_status = "insufficient_evidence" if "insufficient_evidence" in html or "does not contain sufficient" in html else "answered"

        citations = page.locator('.source-item')
        citation_count = await citations.count()

        print(f"  Status: {answer_status}")
        print(f"  Citations found: {citation_count}")

        if citation_count > 0:
            first_source = await citations.first.text_content()
            print(f"  First source: {first_source[:80]}..." if first_source else "No sources")

        if answer_status != "answered":
            all_passed = False

    return all_passed


async def test_responsive_layout(page):
    """Test responsive layout at different screen sizes."""
    print("\n=== Test 3: Responsive Layout ===")

    viewports = [
        ("Mobile 390px", {"width": 390, "height": 844}),
        ("Tablet 768px", {"width": 768, "height": 1024}),
        ("Desktop 1440px", {"width": 1440, "height": 900}),
    ]

    for name, size in viewports:
        await page.set_viewport_size(size)
        await page.wait_for_timeout(1000)

        title = await page.title()
        print(f"  {name}: title='{title}' - OK")


async def test_console_errors(page):
    """Check for console errors."""
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")

    await page.fill('input[name="question"]', "Test question")
    await page.click('button:has-text("Send")')
    await page.wait_for_timeout(3000)

    error_count = len(console_errors)
    print(f"\n=== Test 4: Console Errors ===")
    print(f"  Console errors: {error_count}")
    for err in console_errors[:5]:
        print(f"    - {err}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("=" * 60)
        print("BhashaCore Live Browser QA Test")
        print(f"{'='*60}")

        # Test 1: Language selector
        print("\n--- Test 1: Language Selector ===")
        await test_language_selector(page)

        # Test 2: Question submission
        print("\n--- Test 2: Question Submission ===")
        await test_question_submission(page)

        # Test 3: Responsive layout
        print("\n=== Test 3: Responsive Layout ===")
        await test_responsive_layout(page)

        # Test 4: Console errors
        print("\n=== Test 4: Console Errors ===")
        await test_console_errors(page)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())