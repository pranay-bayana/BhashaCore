"""BM25 retrieval over per-language pools + retrieval metrics (Recall@k, MRR@10).

Tokenization is script-aware: NFC-normalized word tokens augmented with 5-char
prefixes, which partially bridges agglutinative morphology in Dravidian
languages (Tamil/Telugu/Kannada/Malayalam) and schwa-variant spellings.
"""
import json

from rank_bm25 import BM25Okapi

from src.config import TOP_K, proc_path
from src.metrics import _normalize


def tokenize(text: str) -> list:
    """Tokenize text for BM25 indexing and querying.

    Strategy:
    - NFC-normalized word tokens (whitespace split)
    - 5-char prefixes for words >= 6 chars (bridges schwa-variant spellings)
    """
    toks = _normalize(text).split()
    prefixes = [t[:5] for t in toks if len(t) >= 6]
    return toks + prefixes


class PoolIndex:
    def __init__(self, pool_records: list):
        self.records = pool_records
        self.by_pid = {r["pid"]: r for r in pool_records}
        corpus = [tokenize(r["text"]) for r in pool_records]
        # rank_bm25 cannot index an empty corpus
        self.bm25 = BM25Okapi(corpus) if corpus and any(corpus) else None

    def search(self, query: str, top_k: int = TOP_K) -> list:
        if self.bm25 is None:
            return []
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]
        return [(self.records[i]["pid"], float(scores[i])) for i in order if scores[i] > 0]


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_retrieval(lang: str) -> str:
    """Rank pool passages for every eval question; save hits/ranks + metrics."""
    evals = load_jsonl(proc_path(f"eval_{lang}"))
    pool = load_jsonl(proc_path(f"pool_{lang}"))
    index = PoolIndex(pool)

    out_path = proc_path(f"retrieval_{lang}")
    n_hit, rr_sum, n = 0, 0.0, 0
    with open(out_path, "w", encoding="utf-8") as f:
        for q in evals:
            hits = index.search(q["question"], TOP_K)
            pids = [p for p, _ in hits]
            rank = pids.index(q["gold_pid"]) + 1 if q["gold_pid"] in pids else None
            hit = rank is not None
            mrr = 1.0 / rank if rank and rank <= 10 else 0.0
            n_hit += hit
            rr_sum += mrr
            n += 1
            f.write(json.dumps({
                "qid": q["qid"],
                "lang": lang,
                "retrieved_pids": pids,
                "rank": rank,
                "hit": hit,
                "mrr10": mrr,
            }, ensure_ascii=False) + "\n")
    summary = {"lang": lang, "recall_at_k": n_hit / max(n, 1), "mrr10": rr_sum / max(n, 1), "n": n}
    print(f"[retrieval:{lang}] Recall@{TOP_K}={summary['recall_at_k']:.3f} MRR@10={summary['mrr10']:.3f} (n={n})")
    return out_path


def run_translit_retrieval(lang: str) -> str:
    """Stress retrieval: romanized queries against the native-script pool."""
    evals = load_jsonl(proc_path(f"eval_{lang}"))
    pool = load_jsonl(proc_path(f"pool_{lang}"))
    index = PoolIndex(pool)

    out_path = proc_path(f"retrieval_translit_{lang}")
    n_hit, rr_sum, n = 0, 0.0, 0
    with open(out_path, "w", encoding="utf-8") as f:
        for q in evals:
            hits = index.search(q["romanized_question"], TOP_K)
            pids = [p for p, _ in hits]
            rank = pids.index(q["gold_pid"]) + 1 if q["gold_pid"] in pids else None
            hit = rank is not None
            mrr = 1.0 / rank if rank and rank <= 10 else 0.0
            n_hit += hit
            rr_sum += mrr
            n += 1
            f.write(json.dumps({
                "qid": q["qid"],
                "lang": lang,
                "retrieved_pids": pids,
                "rank": rank,
                "hit": hit,
                "mrr10": mrr,
            }, ensure_ascii=False) + "\n")
    summary = {"lang": lang, "recall_at_k": n_hit / max(n, 1), "mrr10": rr_sum / max(n, 1), "n": n}
    print(f"[retrieval-translit:{lang}] Recall@{TOP_K}={summary['recall_at_k']:.3f} MRR@10={summary['mrr10']:.3f} (n={n})")
    return out_path


if __name__ == "__main__":
    import sys
    from src.config import ALL_LANGS

    for lang in (sys.argv[1:] or ALL_LANGS):
        run_retrieval(lang)
        if lang != "en":
            run_translit_retrieval(lang)
