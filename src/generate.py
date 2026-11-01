"""Chatbot generation across modes and languages (NVIDIA NIM, resumable).

Modes:
  closed_book   - question only (measures the model's own knowledge per language)
  gold_context  - question + gold context (measures reading comprehension)
  rag           - question + top-k retrieved passages (end-to-end pipeline)
  rag_translit  - Romanized question + top-k passages retrieved with the
                  romanized query (realistic "user types Hinglish" stress test)
"""
import asyncio
import json
import time

from src.config import (
    INDIC_LANGS,
    LANGS,
    TOP_K,
    gen_results_path,
    proc_path,
)
from src.nim import NimClient
from src.retrieval import PoolIndex, load_jsonl

SYSTEM_TMPL = (
    "You are BhashaCore, a helpful government-services assistant for Indian citizens. "
    "Answer the user's question in {name} (write in the {script} script). "
    "Be concise: at most 3 sentences. {grounding}{roman_note}"
)
GROUNDING_CTX = (
    "Use ONLY the context passages provided below. If they do not contain the answer, "
    "reply that you cannot answer from the available information. Never invent facts."
)
GROUNDING_CB = "If you are not certain of the answer, say so instead of guessing."
ROMAN_NOTE = (
    " Note: the user typed the question in Romanized {name}; "
    "understand it and answer in proper {name} ({script} script)."
)


def build_messages(question: str, lang: str, mode: str, passages=None) -> list:
    meta = LANGS[lang]
    grounding = GROUNDING_CTX if mode in ("gold_context", "rag", "rag_translit") else GROUNDING_CB
    roman_note = ROMAN_NOTE.format(**meta) if mode == "rag_translit" else ""
    system = SYSTEM_TMPL.format(grounding=grounding, roman_note=roman_note, **meta)
    if passages:
        ctx = "\n\n".join(f"[{i+1}] {p}" for i, p in enumerate(passages))
        user = f"Context passages:\n{ctx}\n\nQuestion: {question}"
    else:
        user = f"Question: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _context_for(item: dict, pool_by_pid: dict, retrieval_by_qid: dict, mode: str):
    """Return (passages, retrieved_hit) for a question in a given mode."""
    if mode == "gold_context":
        return [item["context"]], True
    if mode in ("rag", "rag_translit"):
        rkey = "retrieval_translit" if mode == "rag_translit" else "retrieval"
        r = retrieval_by_qid.get((rkey, item["qid"]))
        if r is None:
            return [], False
        passages = [pool_by_pid[p]["text"] for p in r["retrieved_pids"] if p in pool_by_pid]
        return passages, r["hit"]
    return None, None


async def run_generation(model: str, modes: list, langs: list, limit: int = None):
    client = NimClient(model)
    try:
        for lang in langs:
            evals = load_jsonl(proc_path(f"eval_{lang}"))
            pool_by_pid = {r["pid"]: r for r in load_jsonl(proc_path(f"pool_{lang}"))}
            retrieval_by_qid = {}
            for rkey in ("retrieval", "retrieval_translit"):
                p = proc_path(f"{rkey}_{lang}")
                if p.exists():
                    for r in load_jsonl(p):
                        retrieval_by_qid[(rkey, r["qid"])] = r

            for mode in modes:
                if mode == "rag_translit" and lang == "en":
                    continue  # stress test is Indic-only
                out_path = gen_results_path(model, mode, lang)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                done = set()
                if out_path.exists():
                    done = {r["qid"] for r in load_jsonl(out_path) if r.get("answer")}
                items = evals[:limit] if limit else evals
                items = [e for e in items if e["qid"] not in done]
                if not items:
                    print(f"[gen:{lang}:{mode}] already complete ({len(done)}), skipping")
                    continue

                async def one(item):
                    passages, hit = _context_for(item, pool_by_pid, retrieval_by_qid, mode)
                    question = item["romanized_question"] if mode == "rag_translit" else item["question"]
                    messages = build_messages(question, lang, mode, passages)
                    t0 = time.time()
                    resp = await client.chat(messages)
                    return item, passages, hit, resp, time.time() - t0

                n_ok = 0
                with open(out_path, "a", encoding="utf-8") as f:
                    for coro in asyncio.as_completed([one(it) for it in items]):
                        item, passages, hit, resp, latency = await coro
                        n_ok += 1 if resp.get("content") else 0
                        f.write(json.dumps({
                            "qid": item["qid"],
                            "lang": lang,
                            "mode": mode,
                            "model": model,
                            "question": item["romanized_question"] if mode == "rag_translit" else item["question"],
                            "answer": resp.get("content"),
                            "error": resp.get("error"),
                            "latency": round(latency, 2),
                            "reasoning_chars": resp.get("reasoning_chars"),
                            "tokens": (resp.get("usage") or {}).get("total_tokens"),
                            "retrieved_hit": hit,
                            "n_passages": len(passages) if passages else 0,
                        }, ensure_ascii=False) + "\n")
                        f.flush()
                print(f"[gen:{lang}:{mode}] {n_ok}/{len(items)} answered (skipped {len(done)} existing)")
    finally:
        await client.aclose()


if __name__ == "__main__":
    import argparse
    from src.config import ALL_LANGS, MODES, PRIMARY_GENERATOR

    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=PRIMARY_GENERATOR)
    ap.add_argument("--modes", default=",".join(MODES))
    ap.add_argument("--langs", default=",".join(ALL_LANGS))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    asyncio.run(run_generation(
        args.model,
        args.modes.split(","),
        args.langs.split(","),
        args.limit,
    ))
