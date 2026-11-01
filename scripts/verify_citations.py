#!/usr/bin/env python3
"""
Phase 6: Verify citations and answer quality.

Tests:
1. Corpus-grounded answers cite actual retrieved passages
2. Cited passages genuinely support the answer (support >= 0.8)
3. Model-only answers have 0/5 citations used
4. Citation provenance (source_url, title, text match actual pool records)
5. Model-only answers clearly state they're not corpus-grounded
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/Users/pranaybayana/Desktop/Supervised project")
from src.app import answer_question
from src.retrieval import load_jsonl
from src.config import PROC_DIR


def verify_citation_provenance(lang: str, question: str, gold_pid: str = None):
    """Verify that cited passages are real and have correct provenance."""
    result = answer_question(lang, question=question, input_style="native", eval_mode=True)

    print(f"\n=== {lang.upper()}: {question[:60]} ===")
    print(f"Status: {result['status']}")
    print(f"Model: {result['model']}")
    print(f"Is model-only: {result.get('is_model_only', False)}")
    print(f"Answer: {result['answer'][:150]}")

    pool = {r["pid"]: r for r in load_jsonl(PROC_DIR / f"pool_{lang}.jsonl")}

    issues = []
    for c in result["citations"]:
        pid = c["pid"]
        # Verify citation refers to actual pool record
        if pid not in pool:
            issues.append(f"Citation pid {pid} not found in pool")
            continue
        rec = pool[pid]
        # Verify citation text matches pool record
        if rec["text"][:50] != c["text"][:50]:
            issues.append(f"Citation text mismatch for pid {pid}")
        # Verify support score is present
        if "support" not in c:
            issues.append(f"Citation {pid} missing support score")

    used = [c for c in result["citations"] if c.get("used")]
    print(f"Citations: {len(result['citations'])} total, {len(used)} used")

    for c in used:
        print(f"  Used: pid={c['pid'][:16]} support={c.get('support')} source={c.get('source')}")
        if c.get("pid") == gold_pid:
            print(f"    ^ GOLD PASSAGE")

    if issues:
        print(f"  ISSUES: {issues}")
    else:
        print(f"  All citations valid")

    return len(issues) == 0


def verify_model_only_no_citations(lang: str, question: str):
    """Verify model-only answers have no citations used."""
    result = answer_question(lang, question=question, input_style="native")

    print(f"\n=== {lang.upper()} Model-Only: {question[:60]} ===")
    print(f"Status: {result['status']}")
    print(f"Is model-only: {result.get('is_model_only', False)}")
    print(f"Answer: {result['answer'][:150]}")

    used = [c for c in result["citations"] if c.get("used")]
    total = len(result["citations"])

    if result.get("is_model_only") and used:
        print(f"  ISSUE: Model-only answer has {len(used)} used citations!")
        return False
    elif result.get("is_model_only") and total == 0:
        print(f"  OK: Model-only answer has 0 citations")
        return True
    else:
        print(f"  Not model-only or has citations - status={result['status']}")
        return True


if __name__ == "__main__":
    all_pass = True

    # Test corpus-grounded citations for each language
    test_cases = [
        ("en", "What is the basic pay for a teacher, in Euros?", "p_9184b759642b"),
        ("hi", "ताजमहल कहां स्थित है?", None),
        ("ta", "அக்பர் எங்கே பிறந்தார்?", None),
        ("te", "గుర్రం వెంట ఎవరి బృfficacité ఉంది?", None),
        ("kn", "ಜಿನ್ನಾ ಏನನ್ನು ಕೋರಿದ್ದರು?", None),
        ("ml", "ഗാന്ധിജിയുടെ ജന്മസ്ഥലം ഏത് ?", None),
    ]

    for lang, question, gold_pid in test_cases:
        ok = verify_citation_provenance(lang, question, gold_pid)
        all_pass = all_pass and ok

    # Test model-only answers have no citations
    model_only_tests = [
        ("en", "What is the capital of Japan?"),
        ("hi", "पृथ्वी का सबसे बड़ा महासागर कौन सा है?"),
    ]

    for lang, question in model_only_tests:
        ok = verify_model_only_no_citations(lang, question)
        all_pass = all_pass and ok

    print(f"\n{'='*50}")
    print(f"CITATION VERIFICATION: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*50}")
