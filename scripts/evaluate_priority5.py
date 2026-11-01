#!/usr/bin/env python3
"""
BhashaCore - Priority 5 Comprehensive Evaluation.

Measures:
- Recall@1, Recall@5, Recall@10
- End-to-end answer correctness
- Citation support and groundedness
- Appropriate refusal on unsupported questions
- Native-script and Romanized input performance
- Cross-language answer behavior
- Latency

Usage:
    python scripts/evaluate_priority5.py --langs en hi ta te kn ml --n-questions 50
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import answer_question
from src.retrieval import load_jsonl, PoolIndex
from src.config import PROC_DIR


def eval_recall(lang: str, n_questions: int) -> dict:
    """Recall@1, @5, @10 for gold passages."""
    evals = load_jsonl(PROC_DIR / f"eval_{lang}.jsonl")
    pool_records = load_jsonl(PROC_DIR / f"pool_{lang}.jsonl")
    kno_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
    kno_records = load_jsonl(kno_file) if kno_file.exists() else []
    all_records = pool_records + kno_records

    index = PoolIndex(all_records)

    results = {k: 0 for k in (1, 5, 10)}
    total = min(len(evals), n_questions)
    ranks = []

    for e in evals[:total]:
        hits = index.search(e["question"], 10)
        pids = [p for p, _ in hits]
        gold_pid = e.get("gold_pid")
        if gold_pid and gold_pid in pids:
            rank = pids.index(gold_pid) + 1
            ranks.append(rank)
            for k in (1, 5, 10):
                if rank <= k:
                    results[k] += 1

    return {
        "total": total,
        "recall_at_1": results[1] / total,
        "recall_at_5": results[5] / total,
        "recall_at_10": results[10] / total,
        "avg_rank": sum(ranks) / len(ranks) if ranks else 0,
    }


def eval_answer_correctness(lang: str, n_questions: int) -> dict:
    """End-to-end answer correctness for known eval questions."""
    evals = load_jsonl(PROC_DIR / f"eval_{lang}.jsonl")
    total = min(len(evals), n_questions)

    correct = 0
    answered = 0
    insufficient = 0
    latencies = []
    citation_support_scores = []

    for e in evals[:total]:
        t0 = time.time()
        result = answer_question(lang, question=e["question"], input_style="native")
        latencies.append(time.time() - t0)

        if result["status"] == "answered":
            answered += 1
            # Check if answer contains any of the gold answers
            gold_answers = e.get("answers", [])
            answer_text = result["answer"].lower()
            matched = any(ga.lower() in answer_text for ga in gold_answers if ga)
            if matched:
                correct += 1

            # Citation support
            used_citations = [c for c in result["citations"] if c.get("used")]
            if used_citations:
                support_scores = [c.get("support", 0) for c in used_citations]
                citation_support_scores.append(sum(support_scores) / len(support_scores))

        elif result["status"] == "insufficient_evidence":
            insufficient += 1

    return {
        "total": total,
        "answered": answered,
        "insufficient": insufficient,
        "answer_rate": answered / total if total > 0 else 0,
        "correctness": correct / answered if answered > 0 else 0,
        "correct_over_total": correct / total if total > 0 else 0,
        "avg_latency_ms": (sum(latencies) / len(latencies) * 1000) if latencies else 0,
        "avg_citation_support": (sum(citation_support_scores) / len(citation_support_scores)) if citation_support_scores else 0,
    }


def eval_refusal(lang: str, n_questions: int) -> dict:
    """Appropriate refusal on questions NOT in this language's corpus."""
    evals = load_jsonl(PROC_DIR / f"eval_{lang}.jsonl")
    other_langs = [l for l in ["en", "hi", "ta", "te", "kn", "ml"] if l != lang]
    other_evals = []
    for ol in other_langs:
        other_evals.extend(load_jsonl(PROC_DIR / f"eval_{ol}.jsonl"))

    import random
    random.shuffle(other_evals)
    test_questions = other_evals[:n_questions]

    refused = 0
    answered = 0
    total = len(test_questions)

    for e in test_questions:
        result = answer_question(lang, question=e["question"], input_style="native")
        if result["status"] == "insufficient_evidence":
            refused += 1
        elif result["status"] == "answered":
            answered += 1

    return {
        "total": total,
        "refused": refused,
        "answered_incorrectly": answered,
        "refusal_rate": refused / total if total > 0 else 0,
        "false_answer_rate": answered / total if total > 0 else 0,
    }


def eval_romanized(lang: str, n_questions: int) -> dict:
    """Romanized input performance for Indic languages."""
    if lang == "en":
        return {"skipped": True, "reason": "English is already Latin script"}

    evals = load_jsonl(PROC_DIR / f"eval_{lang}.jsonl")
    total = min(len(evals), n_questions)

    correct = 0
    answered = 0
    insufficient = 0

    for e in evals[:total]:
        romanized_q = e.get("romanized_question", "")
        if not romanized_q:
            continue
        result = answer_question(lang, question=romanized_q, input_style="romanized")
        if result["status"] == "answered":
            answered += 1
            gold_answers = e.get("answers", [])
            answer_text = result["answer"].lower()
            if any(ga.lower() in answer_text for ga in gold_answers if ga):
                correct += 1
        elif result["status"] == "insufficient_evidence":
            insufficient += 1

    return {
        "total": total,
        "answered": answered,
        "insufficient": insufficient,
        "answer_rate": answered / total if total > 0 else 0,
        "correctness": correct / answered if answered > 0 else 0,
    }


def run_evaluation(langs: list[str], n_questions: int = 50):
    results = {}

    for lang in langs:
        print(f"\n{'='*70}")
        print(f"Evaluating {lang.upper()}")
        print(f"{'='*70}")

        # Recall
        r = eval_recall(lang, n_questions)
        print(f"Recall@1:  {r['recall_at_1']:.1%} ({int(r['recall_at_1']*r['total'])}/{r['total']})")
        print(f"Recall@5:  {r['recall_at_5']:.1%} ({int(r['recall_at_5']*r['total'])}/{r['total']})")
        print(f"Recall@10: {r['recall_at_10']:.1%} ({int(r['recall_at_10']*r['total'])}/{r['total']})")
        print(f"Avg rank:  {r['avg_rank']:.1f}")

        # Answer correctness
        a = eval_answer_correctness(lang, min(n_questions, 20))
        print(f"Answer rate:  {a['answer_rate']:.1%} ({a['answered']}/{a['total']})")
        print(f"Correctness:  {a['correctness']:.1%} ({a['correct_over_total']:.1%} of total)")
        print(f"Insufficient: {a['insufficient']}/{a['total']}")
        print(f"Avg latency:  {a['avg_latency_ms']:.0f}ms")
        print(f"Avg citation support: {a['avg_citation_support']:.0%}")

        # Refusal
        ref = eval_refusal(lang, min(n_questions, 20))
        print(f"Refusal rate:    {ref['refusal_rate']:.1%} ({ref['refused']}/{ref['total']})")
        print(f"False answer rate: {ref['false_answer_rate']:.1%} ({ref['answered_incorrectly']}/{ref['total']})")

        # Romanized (Indic only)
        rom = eval_romanized(lang, min(n_questions, 20))
        if not rom.get("skipped"):
            print(f"Romanized answer rate:  {rom['answer_rate']:.1%} ({rom['answered']}/{rom['total']})")
            print(f"Romanized correctness:  {rom['correctness']:.1%}")

        results[lang] = {
            "recall": r,
            "answer_correctness": a,
            "refusal": ref,
            "romanized": rom,
        }

    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Priority 5 comprehensive evaluation")
    ap.add_argument("--langs", nargs="+", default=["en", "hi", "ta", "te", "kn", "ml"])
    ap.add_argument("--n-questions", type=int, default=50)
    args = ap.parse_args()

    results = run_evaluation(args.langs, args.n_questions)

    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"{'Lang':6s} {'R@1':>6s} {'R@5':>6s} {'R@10':>7s} {'AnsRate':>8s} {'Correct':>8s} {'Refusal':>8s} {'Latency':>8s}")
    for lang, r in results.items():
        rec = r["recall"]
        ans = r["answer_correctness"]
        ref = r["refusal"]
        print(f"{lang.upper():6s} {rec['recall_at_1']:>6.1%} {rec['recall_at_5']:>6.1%} "
              f"{rec['recall_at_10']:>7.1%} {ans['answer_rate']:>8.1%} {ans['correct_over_total']:>8.1%} "
              f"{ref['refusal_rate']:>8.1%} {ans['avg_latency_ms']:>7.0f}ms")
