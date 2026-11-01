#!/usr/bin/env python3
"""
Phase 5: Evaluate held-out questions against the live BhashaCore app.

Sends each held-out question to /api/chat and records:
- Actual model output (not hardcoded expected answers)
- Correctness separately for corpus-grounded vs model-only answers
- Refusal behavior for unsupported questions
- Citation support and provenance
- Per-language and per-category metrics

Usage:
    BHASHACORE_LLM_TIMEOUT=300 .venv/bin/python3 scripts/evaluate_heldout.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/Users/pranaybayana/Desktop/Supervised project")

import requests

BASE_URL = "http://127.0.0.1:8001"
HELDOUT_PATH = Path("/Users/pranaybayana/Desktop/Supervised project/data/heldout/heldout_questions.jsonl")
RESULTS_DIR = Path("/Users/pranaybayana/Desktop/Supervised project/run_20261029")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_heldout_questions() -> list:
    """Load held-out questions."""
    questions = []
    with open(HELDOUT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions


def ask_question(question: str, lang: str, timeout: int = 300) -> dict:
    """Send a question to the live chat API and return the result."""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "session_id": f"heldout-{int(time.time())}",
                "lang": lang,
                "question": question,
                "mode": "rag",
                "input_style": "auto",
                "answer_script": "native",
            },
            timeout=timeout,
        )
        if resp.status_code != 200:
            return {"status": "error", "error": f"HTTP {resp.status_code}", "answer": ""}

        # Parse NDJSON response
        events = []
        for line in resp.text.splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        done = next((e for e in events if e.get("type") == "done"), None)
        if done:
            return {
                "status": done.get("status", "unknown"),
                "answer": done.get("answer", ""),
                "model": done.get("model", ""),
                "citations": done.get("citations", []),
                "citations_used": sum(1 for c in done.get("citations", []) if c.get("used")),
                "is_model_only": done.get("is_model_only", False),
                "latency_ms": done.get("latency_ms", 0),
                "gold_rank": done.get("gold_rank"),
            }
        else:
            return {"status": "no_done", "answer": "", "error": "No done event"}

    except requests.exceptions.Timeout:
        return {"status": "timeout", "answer": "", "error": "Request timed out"}
    except Exception as e:
        return {"status": "error", "answer": "", "error": str(e)[:200]}


def check_correctness(answer: str, expected_answers: list) -> bool:
    """Check if the answer contains any of the expected answers (case-insensitive)."""
    if not expected_answers:
        return None  # No expected answer to check against
    answer_lower = answer.lower()
    for ea in expected_answers:
        if ea.lower() in answer_lower:
            return True
    return False


def main():
    questions = load_heldout_questions()
    print(f"Loaded {len(questions)} held-out questions")

    results = []
    for i, q in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {q['lang'].upper():4s} | {q['category']:18s} | {q['question'][:60]}")

        result = ask_question(q["question"], q["lang"])
        print(f"  Status: {result['status']} | Model-only: {result.get('is_model_only', False)} | "
              f"Citations used: {result.get('citations_used', 0)}/{len(result.get('citations', []))} | "
              f"Latency: {result.get('latency_ms', 0)}ms")

        # Check correctness if there are expected answers
        expected = q.get("expected_answers", [])
        if expected:
            correct = check_correctness(result.get("answer", ""), expected)
            print(f"  Correctness: {correct} | Expected answers: {expected}")
        else:
            correct = None
            print(f"  Correctness: N/A (refusal question)")

        result_record = {
            "qid": q["qid"],
            "lang": q["lang"],
            "category": q["category"],
            "question": q["question"],
            "expected_answers": expected,
            "status": result["status"],
            "answer": result.get("answer", ""),
            "model": result.get("model", ""),
            "is_model_only": result.get("is_model_only", False),
            "citations_used": result.get("citations_used", 0),
            "total_citations": len(result.get("citations", [])),
            "latency_ms": result.get("latency_ms", 0),
            "correctness": correct,
            "error": result.get("error"),
        }
        results.append(result_record)

        # Be polite - small delay between requests
        time.sleep(1)

    # Save results
    output_path = RESULTS_DIR / "heldout_evaluation_results.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Summary
    print(f"\n{'='*70}")
    print("HELD-OUT EVALUATION SUMMARY")
    print(f"{'='*70}")

    # By category
    for category in ["corpus_grounded", "model_only", "refusal"]:
        cat_results = [r for r in results if r["category"] == category]
        if not cat_results:
            continue
        answered = sum(1 for r in cat_results if r["status"] == "answered")
        total = len(cat_results)
        correct = sum(1 for r in cat_results if r["correctness"] is True)
        correct_with_expected = sum(1 for r in cat_results if r["correctness"] is not None)
        print(f"\n{category}:")
        print(f"  Total: {total}, Answered: {answered}/{total} ({answered/total:.0%})")
        if correct_with_expected > 0:
            print(f"  Correct: {correct}/{correct_with_expected} ({correct/correct_with_expected:.0%})")

    # By language
    print(f"\nBy Language:")
    for lang in ["en", "hi", "ta", "te", "kn", "ml"]:
        lang_results = [r for r in results if r["lang"] == lang]
        if not lang_results:
            continue
        answered = sum(1 for r in lang_results if r["status"] == "answered")
        total = len(lang_results)
        model_only = sum(1 for r in lang_results if r.get("is_model_only"))
        print(f"  {lang.upper():4s}: {answered}/{total} answered, {model_only} model-only")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
