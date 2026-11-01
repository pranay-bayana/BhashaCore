#!/usr/bin/env python3
"""
BhashaCore - Complete Browser QA Test

Tests:
1. Language selector works for all six languages
2. Question submission and streamed answer
3. Citations render and expand
4. Loading/stop/retry/new-chat interactions
5. Dashboard, language comparison, failure analysis pages
6. Responsive layout at 390px and desktop
7. No console errors or failed requests
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
    'en': ['What is the capital of India?', 'Who was the first president of the United States?', 'What is the largest planet?'],
    'hi': ['भारत की राजधानी क्या है?', 'भारत के प्रथम प्रधानमंत्री कौन थे?'],
    'ta': 'தாய்நாடு எங்கே உள்ளது?',
    'te': 'హైదరాబాద్ ఎక్కడ ఉంది?',
    'kn': 'ಬೆಂಗಳೂರು ಎಂದರೇನು?',
    'ml': 'തിരുവനന്തപുരം എന്നால் എന്താണ്?',
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

    print("=== Test 1: Language Selector ===")
    all_passed = True
    for code, name in languages:
        try:
            await page.click(f'button[data-lang="{lang}"]')
            await page.wait_for_timeout(500)
            print(f"  ✓ {lang.upper()}: {name}")
        except Exception as e:
            print(f"  ✗ {lang.upper()}: {name} - FAILED")
            all_passed = False

    return all_passed


async def test_question_submission(page):
    """Test question submission and streaming answer."""
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
        ('ml', 'തിരുവനന്തപുരം എന്നാൽ എന്താണ്?'),
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

        # Check citations
        citations = page.locator('.source-item')
        citation_count = await citations.count()

        print(f"  Status: {result['status']}")
        print(f"  Answer: {result['answer'][:80]}")
        print(f"  Citations used: {result.get('citations_used', 0)}/{len(result['citations'])}")
    print()

    return results


async def test_insufficient_evidence(lang: str, n_questions: int = 10) -> dict:
    """Test that questions NOT in corpus are refused honestly."""
    evals = load_jsonl(PROC_DIR / f'eval_{lang}.jsonl')

    other_langs = [l for l in ['en', 'hi', 'ta', 'te', 'kn', 'ml'] if l != lang]
    other_evals = []
    for ol in other_langs:
        other_evals.extend(load_jsonl(PROC_DIR / f'eval_{ol}.jsonl'))

    import random
    random.shuffle(other_evals)
    test_questions = other_evals[:n_questions]

    refused = 0
    total = len(test_questions)

    for e in test_questions:
        result = answer_question(lang, question=e['question'], input_style='native')
        if result['status'] == 'insufficient_evidence':
            refused += 1

    return {
        'total': total,
        'refused': refused,
        'refusal_rate': refused / total if total > 0 else 0.0
    }


def run_evaluation(langs: list[str], n_questions: int = 20):
    """Run retrieval evaluation for all languages."""
    results = {}

    for lang in langs:
        print(f"\n{'='*60}")
        print(f"Evaluating {lang.upper()}")
        print(f"{'='*60}")

        ret = test_retrieval_quality(lang, n_questions)
        print(f"Retrieval Recall@5: {ret['recall_at_5']:.2%} ({ret['correct']}/{ret['total']})")

        results[lang] = ret

    return results


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Evaluate BhashaCore retrieval")
    ap.add_argument("--langs", nargs="+", default=["en", "hi", "ta", "te", "kn", "ml"])
    ap.add_argument("--n-questions", type=int, default=20)
    args = ap.parse_args()

    results = run_evaluation(args.langs, args.n_questions)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for lang, r in results.items():
        print(f"{lang.upper():4s} | Retrieval@5: {r['recall_at_5']:.2%} ({ret['correct']}/{ret['total']})")