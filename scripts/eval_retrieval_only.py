#!/usr/bin/env python3
"""Fast retrieval-only evaluation for BhashaCore."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.retrieval import load_jsonl, PoolIndex
from src.config import PROC_DIR


def test_retrieval(lang: str, n_questions: int = 20) -> dict:
    evals = load_jsonl(PROC_DIR / f"eval_{lang}.jsonl")
    pool_records = load_jsonl(PROC_DIR / f"pool_{lang}.jsonl")
    kno_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
    kno_records = load_jsonl(kno_file) if kno_file.exists() else []
    all_records = pool_records + kno_records

    index = PoolIndex(all_records)

    correct = 0
    total = min(len(evals), n_questions)
    ranks = []

    for e in evals[:n_questions]:
        hits = index.search(e["question"], 5)
        pids = [p for p, _ in hits]
        gold_pid = e.get("gold_pid")
        if gold_pid and gold_pid in pids:
            correct += 1
            ranks.append(pids.index(gold_pid) + 1)

    return {
        "total": total,
        "correct": correct,
        "recall_at_5": correct / total if total > 0 else 0.0,
        "avg_rank": sum(ranks) / len(ranks) if ranks else 0,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=["en", "hi", "ta", "te", "kn", "ml"])
    ap.add_argument("--n-questions", type=int, default=20)
    args = ap.parse_args()

    print("=" * 70)
    print("Retrieval Recall@5 Evaluation")
    print("=" * 70)
    for lang in args.langs:
        r = test_retrieval(lang, args.n_questions)
        print(
            f"{lang.upper():4s} | Recall@5: {r['recall_at_5']:.1%} "
            f"({r['correct']}/{r['total']}) | "
            f"Avg rank: {r['avg_rank']:.1f}"
        )
    print("=" * 70)
