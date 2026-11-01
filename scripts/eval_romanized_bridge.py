"""Paired evaluation: does back-transliterating romanized queries to native
script improve BM25 retrieval over the native-script corpus?

Uses the SAME evaluation questions (the project's own romanized eval set),
the SAME pools, and the SAME metrics (Recall@5 / MRR@10) as the saved research
results, so the comparison is paired and directly comparable:

  baseline: BM25(romanized query) on the native-script pool
            (reproduces the saved rag_translit recall, ~0.0-0.09)
  bridge:   BM25(bridge(romanized) -> native script) on the same pool
  dual:     merge of baseline + bridge results by max score, top-5

Writes a NEW artifact `results/summary/retrieval_romanized_bridge.csv`.
Does not modify any existing research artifact.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import INDIC_LANGS, SUMMARY_DIR, TOP_K, proc_path  # noqa: E402
from src.langkit import bridge_to_native, bridge_variants  # noqa: E402
from src.retrieval import PoolIndex, load_jsonl  # noqa: E402


def merge_hits(hit_lists, top_k=TOP_K):
    """Merge ranked (pid, score) lists from multiple query variants by max score."""
    best = {}
    for hits in hit_lists:
        for pid, score in hits:
            if score > best.get(pid, 0.0):
                best[pid] = score
    ranked = sorted(best.items(), key=lambda kv: -kv[1])[:top_k]
    return [(pid, score) for pid, score in ranked if score > 0]


def recall_mrr(records):
    n = len(records)
    if not n:
        return 0.0, 0.0
    hits = sum(1 for r in records if r["hit"])
    mrr = sum(r["mrr10"] for r in records) / n
    return hits / n, mrr


def main():
    rows = []
    print(f"{'lang':>5} {'strategy':>9} {'recall@5':>9} {'mrr@10':>7}   (n per cell)")
    for lang in INDIC_LANGS:
        evals = load_jsonl(proc_path(f"eval_{lang}"))
        pool = load_jsonl(proc_path(f"pool_{lang}"))
        index = PoolIndex(pool)

        results = {"baseline": [], "bridge": [], "dual": [], "dual_casual": []}
        bridged_queries = {}
        for e in evals:
            rq = e["romanized_question"]
            bq = bridge_to_native(rq, lang)
            variants = bridge_variants(rq, lang)
            bridged_queries[e["qid"]] = bq

            baseline_hits = index.search(rq, TOP_K)
            bridge_hits = index.search(bq, TOP_K)
            dual_hits = merge_hits([baseline_hits, bridge_hits], TOP_K)
            casual_hit_lists = [index.search(v, TOP_K) for v in variants]
            dual_casual_hits = merge_hits([baseline_hits] + casual_hit_lists, TOP_K)

            for strategy, hits in (
                ("baseline", baseline_hits),
                ("bridge", bridge_hits),
                ("dual", dual_hits),
                ("dual_casual", dual_casual_hits),
            ):
                pids = [p for p, _ in hits]
                rank = pids.index(e["gold_pid"]) + 1 if e["gold_pid"] in pids else None
                results[strategy].append(
                    {
                        "qid": e["qid"],
                        "hit": rank is not None,
                        "mrr10": (1.0 / rank if rank and rank <= 10 else 0.0),
                    }
                )

        for strategy, recs in results.items():
            r5, mrr = recall_mrr(recs)
            rows.append(
                {
                    "lang": lang,
                    "strategy": strategy,
                    "n": len(recs),
                    "recall@5": round(r5, 4),
                    "mrr@10": round(mrr, 4),
                }
            )
            print(f"{lang:>5} {strategy:>9} {r5:>9.4f} {mrr:>7.4f}   (n={len(recs)})")

    out = SUMMARY_DIR / "retrieval_romanized_bridge.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["lang", "strategy", "n", "recall@5", "mrr@10"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {out}")
    print("Baseline values reproduce the saved rag_translit recall when correct.")


if __name__ == "__main__":
    main()
