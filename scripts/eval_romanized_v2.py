#!/usr/bin/env python3
"""Measure romanized retrieval quality."""
import sys
from pathlib import Path

sys.path.insert(0, "/Users/pranaybayana/Desktop/Supervised project")
from src.retrieval import PoolIndex, load_jsonl
from src.config import PROC_DIR, TOP_K, INDIC_LANGS

def evaluate_romanized_recall(lang: str, n_questions: int = 100):
    """Measure Recall@5 for romanized queries against native-script pool."""
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
        rq = e.get("romanized_question", "")
        if not rq:
            continue
        hits = index.search(rq, 10)
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
        "recall_at_1": results[1] / total if total > 0 else 0,
        "recall_at_5": results[5] / total if total > 0 else 0,
        "recall_at_10": results[10] / total if total > 0 else 0,
        "avg_rank": sum(ranks) / len(ranks) if ranks else 0,
    }


if __name__ == "__main__":
    print("=== Romanized Retrieval Quality ===")
    print(f"{'Lang':6s} {'R@1':>6s} {'R@5':>6s} {'R@10':>7s} {'AvgRank':>8s} {'N':>4s}")
    for lang in INDIC_LANGS:
        r = evaluate_romanized_recall(lang)
        print(f"{lang.upper():6s} {r['recall_at_1']:>6.1%} {r['recall_at_5']:>6.1%} "
              f"{r['recall_at_10']:>7.1%} {r['avg_rank']:>8.1f} {r['total']:>4d}")
