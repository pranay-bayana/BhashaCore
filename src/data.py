"""Data acquisition & sampling.

- IndicQA (hi/ta/te/kn/ml): parsed from raw SQuAD-format JSON (XQuAD-style, so
  question ids are shared across languages AND with the original SQuAD dev set
  in English -> perfectly parallel evaluation across all 6 languages).
- English control: the SAME question ids taken from SQuAD v1.1 validation.
- Retrieval pool per language: every IndicQA/SQuAD-dev context for that
  language (gold passage guaranteed present) + N_DISTRACTORS passages sampled
  from IndicCorp v2 (streamed, never fully downloaded). English distractors
  come from SQuAD train (IndicCorp v2 has no English split) - noted in the
  report as a caveat.
"""
import hashlib
import json
import random

from datasets import load_dataset
from huggingface_hub import hf_hub_download

from src.config import (
    INDIC_LANGS,
    LANGS,
    N_DISTRACTORS,
    N_EVAL,
    PROC_DIR,
    SEED,
    proc_path,
)
from src.metrics import script_purity
from src.translit import romanize


def _pid_for(text: str) -> str:
    return "p_" + hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def parse_squad_format(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    records = []
    for article in data.get("data", []):
        for para in article.get("paragraphs", []):
            context = (para.get("context") or "").strip()
            if not context:
                continue
            for qa in para.get("qas", []):
                answers = []
                for a in qa.get("answers", []):
                    t = (a.get("text") or "").strip()
                    if t and t not in answers:
                        answers.append(t)
                qid = qa.get("id")
                if not qid or not answers:
                    continue
                records.append({
                    "qid": qid,
                    "question": (qa.get("question") or "").strip(),
                    "context": context,
                    "answers": answers,
                })
    return records


def load_squad_dev() -> dict:
    ds = load_dataset("rajpurkar/squad", split="validation")
    records = {}
    for r in ds:
        answers = [t for t in (r["answers"]["text"] or []) if t]
        if not answers:
            continue
        records[r["id"]] = {
            "qid": r["id"],
            "question": r["question"].strip(),
            "context": r["context"].strip(),
            "answers": answers,
        }
    return records


_INDICCORP_PARQUET = (
    "https://huggingface.co/datasets/ai4bharat/IndicCorpV2/resolve/"
    "refs%2Fconvert%2Fparquet/indiccorp_v2/partial-{split}/0000.parquet"
)


def sample_indiccorp(lang: str, n: int) -> list:
    split = LANGS[lang]["indiccorp_split"]
    script = LANGS[lang]["script"]
    url = _INDICCORP_PARQUET.format(split=split)
    ds = load_dataset("parquet", data_files={"train": url}, split="train", streaming=True)
    out, seen = [], set()
    i = -1
    for i, row in enumerate(ds):
        if i > 120_000 or len(out) >= n:
            break
        t = None
        for k in ("text", "sentence", "content", "document", "body"):
            if row.get(k):
                t = str(row[k]).strip()
                break
        if t is None and row:
            t = str(next(iter(row.values()))).strip()
        if not t or len(t) < 80 or len(t) > 1200:
            continue
        if script_purity(t, script) < 0.7:  # skip noisy/code-mixed crawl rows
            continue
        h = hashlib.md5(t.encode("utf-8")).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        out.append({"pid": "ic_" + h[:12], "text": t, "source": "indiccorp_v2"})
    print(f"[indiccorp:{lang}] sampled {len(out)} distractor passages (scanned {i+1} rows)")
    return out


def squad_train_distractors(n: int) -> list:
    ds = load_dataset("rajpurkar/squad", split="train")
    rng = random.Random(SEED)
    idxs = rng.sample(range(len(ds)), min(4 * n, len(ds)))
    out, seen = [], set()
    for i in idxs:
        t = ds[i]["context"].strip()
        if len(t) < 80:
            continue
        h = hashlib.md5(t.encode("utf-8")).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        out.append({"pid": "sq_" + h[:12], "text": t, "source": "squad_train"})
        if len(out) >= n:
            break
    return out


def build_all():
    rng = random.Random(SEED)

    # ---- IndicQA per language -------------------------------------------------
    indic = {}
    for lang in INDIC_LANGS:
        p = hf_hub_download("ai4bharat/IndicQA", f"data/indicqa.{lang}.json", repo_type="dataset")
        recs = parse_squad_format(p)
        indic[lang] = {r["qid"]: r for r in recs}
        print(f"[indicqa:{lang}] {len(indic[lang])} questions parsed")

    shared = set.intersection(*(set(indic[l].keys()) for l in INDIC_LANGS))
    squad_dev = load_squad_dev()
    en_shared = shared & set(squad_dev.keys())
    print(f"[ids] shared across 5 Indic langs: {len(shared)}; also present in SQuAD dev (en): {len(en_shared)}")

    parallel = len(en_shared) >= N_EVAL
    chosen_ids = set(rng.sample(sorted(en_shared), N_EVAL)) if parallel else None
    if not parallel:
        print("[warn] parallel sampling unavailable -> per-language independent samples")

    # ---- per-language eval sets + pools ---------------------------------------
    for lang in ["en"] + INDIC_LANGS:
        if lang == "en":
            if parallel:
                recs = [squad_dev[i] for i in sorted(chosen_ids)]
                base_recs = [squad_dev[q] for q in shared if q in squad_dev]
            else:
                ids = rng.sample(sorted(squad_dev.keys()), N_EVAL)
                recs = [squad_dev[i] for i in ids]
                base_recs = recs
            distractors = squad_train_distractors(N_DISTRACTORS)
        else:
            if parallel:
                recs = [indic[lang][i] for i in sorted(chosen_ids)]
                base_recs = list(indic[lang].values())
            else:
                ids = rng.sample(sorted(indic[lang].keys()), min(N_EVAL, len(indic[lang])))
                recs = [indic[lang][i] for i in ids]
                base_recs = list(indic[lang].values())
            distractors = sample_indiccorp(lang, N_DISTRACTORS)

        # pool = all contexts of this language (gold guaranteed in pool) + distractors
        pool, seen_pids = [], set()
        for r in base_recs:
            pid = _pid_for(r["context"])
            if pid not in seen_pids:
                seen_pids.add(pid)
                pool.append({"pid": pid, "text": r["context"], "source": "qa_context"})
        pool.extend(distractors)

        with open(proc_path(f"eval_{lang}"), "w", encoding="utf-8") as f:
            for r in recs:
                rec = {
                    "qid": r["qid"], "lang": lang, "question": r["question"],
                    "context": r["context"], "answers": r["answers"],
                    "gold_pid": _pid_for(r["context"]),
                }
                if lang != "en":
                    rec["romanized_question"] = romanize(r["question"], LANGS[lang]["script"])
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        with open(proc_path(f"pool_{lang}"), "w", encoding="utf-8") as f:
            for p in pool:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        print(f"[build:{lang}] eval={len(recs)} pool={len(pool)} (contexts={len(pool)-len(distractors)}, distractors={len(distractors)})")

    print(f"[done] parallel={parallel} n_eval={N_EVAL} languages={len(INDIC_LANGS)+1}")


if __name__ == "__main__":
    build_all()
