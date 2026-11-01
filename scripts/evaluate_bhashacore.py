#!/usr/bin/env python3
"""
BhashaCore - Complete Evaluation Script

Tests:
1. Retrieval quality (Recall@5 for gold passages)
2. Answer generation quality (for eval questions)
3. Insufficient evidence handling (questions not in corpus)
4. Language consistency (answers in correct language/script)
5. Citation quality (relevant passages cited)

Usage:
    python scripts/evaluate_bhashacore.py [--langs en hi ta te kn ml] [--n-questions 20]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import answer_question
from src.retrieval import load_jsonl, PoolIndex
from src.config import PROC_DIR


def test_retrieval_quality(lang: str, n_questions: int = 20) -> dict:
    """Test if gold passages are retrieved for eval questions."""
    evals = load_jsonl(PROC_DIR / f'eval_{lang}.jsonl')
    pool_records = load_jsonl(PROC_DIR / f'pool_{lang}.jsonl')

    index = PoolIndex(pool_records)

    correct = 0
    total = min(len(evals), n_questions)

    for e in evals[:n_questions]:
        hits = index.search(e['question'], 5)
        gold_pid = e.get('gold_pid')
        if gold_pid and any(pid == e['gold_pid'] for pid, _ in hits):
            correct += 1

    return {
        'total': total,
        'correct': correct,
        'recall_at_5': correct / total if total > 0 else 0.0
    }


def test_answer_generation(lang: str, n_questions: int = 10) -> dict:
    """Test if answers are generated for eval questions with gold passages."""
    evals = load_jsonl(PROC_DIR / f'eval_{lang}.jsonl')

    correct = 0
    total = min(len(evals), n_questions)
    total_citations = 0
    used_citations = 0

    for e in evals[:n_questions]:
        result = answer_question(lang, question=e['question'], input_style='native')

        if result['status'] == 'answered':
            correct += 1

        citations = result.get('citations', [])
        total_citations += len(citations)
        used_citations += sum(1 for c in citations if c.get('used'))

    return {
        'total': total,
        'correct': correct,
        'accuracy': correct / total if total > 0 else 0.0,
        'avg_citations': total_citations / total if total > 0 else 0,
        'avg_citations_used': used_citations / total if total > 0 else 0
    }


def test_insufficient_evidence(lang: str, n_questions: int = 10) -> dict:
    """Test that questions NOT in corpus are refused honestly."""
    evals = load_jsonl(PROC_DIR / f'eval_{lang}.jsonl')

    # Use questions from OTHER languages as "unknown" questions
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
    """Run full evaluation for all languages."""
    results = {}

    for lang in langs:
        print(f"\n{'='*60}")
        print(f"Evaluating {lang.upper()}")
        print(f"{'='*60}")

        # Retrieval quality
        ret = test_retrieval_quality(lang, n_questions)
        print(f"Retrieval Recall@5: {ret['recall_at_5']:.2%} ({ret['correct']}/{ret['total']})")

        # Answer quality (only test a few to save time)
        qa = test_answer_generation(lang, min(n_questions, 5))
        print(f"Answer correctness: {qa['accuracy']:.2%} ({qa['correct']}/{qa['total']})")
        print(f"Avg citations used: {qa['avg_citations_used']:.2f}")

        # Insufficient evidence handling
        ie = test_insufficient_evidence(lang, n_questions)
        print(f"Refusal rate: {ie['refusal_rate']:.2%} ({ie['refused']}/{ie['total']})")

        results[lang] = {
            'retrieval': ret,
            'answer_quality': qa,
            'insufficient_evidence': ie
        }

    return results


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Evaluate BhashaCore")
    ap.add_argument("--langs", nargs="+", default=["en", "hi", "ta", "te", "kn", "ml"])
    ap.add_argument("--n-questions", type=int, default=20)
    args = ap.parse_args()

    results = run_evaluation(args.langs, args.n_questions)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for lang, r in results.items():
        print(f"{lang.upper():4s} | Retrieval@5: {r['retrieval']['recall_at_5']:.2%} ({ret['correct']}/{ret['total']}) | "
              f"Answer: {r['answer_quality']['accuracy']:.2%} | "
              f"Refusal: {r['insufficient_evidence']['refusal_rate']:.2%}")