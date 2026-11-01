"""Aggregate judged results -> summary tables, charts, failure examples, report data.

Outputs:
  results/summary/summary.csv          per model x language x mode metrics
  results/summary/retrieval.csv        per language retrieval metrics (native + romanized)
  report/tables.md                     markdown tables for the report
  report/figures/*.png                 charts
  report/failures_examples.md          curated-raw failure examples per language
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import (
    ALL_LANGS,
    FIGURES_DIR,
    INDIC_LANGS,
    JUDGE_DIR,
    LANGS,
    MODES,
    N_EVAL,
    PRIMARY_GENERATOR,
    JUDGE_MODEL,
    REPORT_DIR,
    RUN_LIMIT,
    SEED,
    SUMMARY_DIR,
    TOP_K,
    judge_results_path,
    proc_path,
)
from src.metrics import failure_flags
from src.retrieval import load_jsonl

LANG_ORDER = ["en"] + INDIC_LANGS
LANG_LABEL = {k: f"{k.upper()} ({v['name']})" for k, v in LANGS.items()}
MODE_LABEL = {
    "closed_book": "Closed-book",
    "gold_context": "Gold context",
    "rag": "RAG",
    "rag_translit": "RAG + Romanized query",
}
MODE_ORDER = ["closed_book", "gold_context", "rag", "rag_translit"]


def discovered_gen_models() -> list:
    models = []
    if JUDGE_DIR.exists():
        for d in sorted(JUDGE_DIR.iterdir()):
            if d.is_dir() and any(d.glob("*.jsonl")):
                models.append(d.name.replace("__", "/"))
    return models


def collect() -> pd.DataFrame:
    rows = []
    for gen_model in discovered_gen_models():
        for lang in ALL_LANGS:
            evals = {r["qid"]: r for r in load_jsonl(proc_path(f"eval_{lang}"))}
            for mode in MODES:
                p = judge_results_path(gen_model, mode, lang)
                if not p.exists():
                    continue
                for r in load_jsonl(p):
                    ev = evals.get(r["qid"], {})
                    flags = failure_flags({
                        "mode": mode,
                        "expected_script": LANGS[lang]["script"],
                        "answer": r.get("answer") or "",
                        "retrieved_hit": r.get("retrieved_hit"),
                        "judge": {
                            "correctness": r.get("correctness"),
                            "faithfulness": r.get("faithfulness"),
                            "issues": r.get("issues", []),
                        },
                    })
                    rows.append({
                        "gen_model": gen_model, "lang": lang, "mode": mode, "qid": r["qid"],
                        "em": r.get("em"), "f1": r.get("f1"),
                        "correctness": r.get("correctness"),
                        "faithfulness": r.get("faithfulness"),
                        "purity": r.get("purity"),
                        "retrieved_hit": r.get("retrieved_hit"),
                        "issues": r.get("issues", []), "flags": flags,
                        "question": ev.get("question", ""), "answers": ev.get("answers", []),
                        "answer": r.get("answer", ""),
                        "gloss_question": r.get("gloss_question", ""),
                        "gloss_reference": r.get("gloss_reference", ""),
                        "gloss_answer": r.get("gloss_answer", ""),
                    })
    df = pd.DataFrame(rows)
    if not df.empty:
        # keep only successfully-judged rows; if a qid was judged twice (parse-error
        # retry), keep the latest judgement
        df = df[df["correctness"].notna()]
        df = df.drop_duplicates(subset=["gen_model", "lang", "mode", "qid"], keep="last")
    return df


def retrieval_summary() -> pd.DataFrame:
    rows = []
    for lang in ALL_LANGS:
        for key, label in (("retrieval", "rag"), ("retrieval_translit", "rag_translit")):
            p = proc_path(f"{key}_{lang}")
            if not p.exists():
                continue
            recs = load_jsonl(p)
            if recs:
                rows.append({
                    "lang": lang, "mode": label, "n": len(recs),
                    f"recall@{TOP_K}": sum(r["hit"] for r in recs) / len(recs),
                    "mrr@10": sum(r["mrr10"] for r in recs) / len(recs),
                })
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (gm, lang, mode), g in df.groupby(["gen_model", "lang", "mode"]):
        out.append({
            "gen_model": gm, "lang": lang, "mode": mode, "n": len(g),
            "em": g["em"].mean(), "f1": g["f1"].mean(),
            "correctness": g["correctness"].mean(),
            "pct_good": (g["correctness"] >= 4).mean(),
            "faithfulness": g["faithfulness"].dropna().mean() if g["faithfulness"].notna().any() else float("nan"),
            "purity": g["purity"].mean(),
            "in_lang_rate": (g["purity"] >= 0.8).mean(),
        })
    return pd.DataFrame(out)


def _style_lang(lang):
    return LANG_ORDER.index(lang)


def chart_correctness(s: pd.DataFrame, path: Path):
    plt.figure(figsize=(10, 5))
    modes = [m for m in MODE_ORDER if (s["mode"] == m).any()]
    width = 0.2
    xs = range(len(LANG_ORDER))
    for i, m in enumerate(modes):
        vals = []
        for lang in LANG_ORDER:
            sub = s[(s["lang"] == lang) & (s["mode"] == m)]
            vals.append(sub["correctness"].iloc[0] if len(sub) else 0)
        plt.bar([x + (i - len(modes) / 2) * width for x in xs], vals,
                width, label=MODE_LABEL[m])
    plt.xticks(list(xs), [LANG_LABEL[l] for l in LANG_ORDER], fontsize=9)
    plt.ylabel("Judge correctness (0-5)")
    plt.title("Answer correctness by language and mode")
    plt.ylim(0, 5)
    plt.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def chart_f1_em(s: pd.DataFrame, path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    modes = [m for m in MODE_ORDER if (s["mode"] == m).any()]
    for ax, metric, title in ((axes[0], "f1", "Token F1"), (axes[1], "em", "Exact match")):
        for i, m in enumerate(modes):
            vals = []
            for lang in LANG_ORDER:
                sub = s[(s["lang"] == lang) & (s["mode"] == m)]
                vals.append(sub[metric].iloc[0] if len(sub) else 0)
            ax.bar([x + (i - len(modes) / 2) * 0.2 for x in range(len(LANG_ORDER))], vals, 0.2, label=MODE_LABEL[m])
        ax.set_xticks(range(len(LANG_ORDER)))
        ax.set_xticklabels([l.upper() for l in LANG_ORDER], fontsize=9)
        ax.set_title(title)
    axes[0].legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def chart_retrieval(ret: pd.DataFrame, path: Path):
    plt.figure(figsize=(8, 4))
    langs = [l for l in LANG_ORDER if ((ret["lang"] == l) & (ret["mode"] == "rag")).any()]
    native = [ret[(ret["lang"] == l) & (ret["mode"] == "rag")][f"recall@{TOP_K}"].iloc[0] for l in langs]
    roman = []
    for l in langs:
        sub = ret[(ret["lang"] == l) & (ret["mode"] == "rag_translit")]
        roman.append(sub[f"recall@{TOP_K}"].iloc[0] if len(sub) else 0)
    xs = range(len(langs))
    plt.bar([x - 0.18 for x in xs], native, 0.36, label="Native-script query")
    plt.bar([x + 0.18 for x in xs], roman, 0.36, label="Romanized query")
    plt.xticks(list(xs), [l.upper() for l in langs])
    plt.ylabel(f"Recall@{TOP_K}")
    plt.title("BM25 retrieval quality: native vs Romanized queries")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def chart_failures(df: pd.DataFrame, path: Path):
    plt.figure(figsize=(10, 5))
    fails = df[(df["correctness"].notna()) & (df["correctness"] <= 3)]
    cats = ["retrieval_miss", "unfaithful_to_context", "wrong_language_or_codemixed",
            "hallucinated", "wrong_answer", "refusal_like", "incomplete"]
    langs = [l for l in LANG_ORDER if (fails["lang"] == l).any()]
    bottoms = [0.0] * len(langs)
    for cat in cats:
        vals = []
        for l in langs:
            sub = fails[fails["lang"] == l]
            n = max(len(sub), 1)
            vals.append(len(sub[sub["flags"].apply(lambda fl: cat in fl)]) / n)
        plt.bar([LANG_LABEL[l] for l in langs], vals, 0.6, bottom=bottoms, label=cat)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    plt.xticks(fontsize=9, rotation=15)
    plt.ylabel("Share of failed answers (correctness <= 3)")
    plt.title("Failure taxonomy by language")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def md_table(df: pd.DataFrame, index_cols: list, value_col: str, title: str) -> str:
    piv = df.pivot_table(index=index_cols[0], columns=index_cols[1], values=value_col, aggfunc="mean")
    piv = piv.reindex(LANG_ORDER)
    cols = [m for m in MODE_ORDER if m in piv.columns]
    piv = piv[cols]
    lines = [f"### {title}", "", "| Language | " + " | ".join(MODE_LABEL.get(c, c) for c in cols) + " |",
             "|" + "---|" * (len(cols) + 1)]
    for lang, row in piv.iterrows():
        cells = [f"{v:.2f}" if pd.notna(v) else "-" for v in row]
        lines.append(f"| {LANG_LABEL[lang]} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def failure_examples(df: pd.DataFrame) -> str:
    out = ["# Failure examples (auto-selected raw material)", ""]
    for lang in INDIC_LANGS:
        out.append(f"\n## {LANG_LABEL[lang]}\n")
        g = df[(df["lang"] == lang)]
        picks = []
        # comprehension failures with gold context
        sub = g[(g["mode"] == "gold_context") & (g["correctness"] <= 3)].nsmallest(3, "correctness")
        picks += [("gold_context comprehension", r["qid"], r) for _, r in sub.iterrows()]
        # RAG failures where retrieval succeeded (model still failed)
        sub = g[(g["mode"] == "rag") & (g["retrieved_hit"] == True) & (g["correctness"] <= 3)].nsmallest(3, "correctness")
        picks += [("RAG failed despite successful retrieval", r["qid"], r) for _, r in sub.iterrows()]
        # transliteration-caused drops (unique per qid; judged rows only)
        rag = g[(g["mode"] == "rag") & (g["correctness"].notna())].drop_duplicates("qid").set_index("qid")
        tr = g[(g["mode"] == "rag_translit") & (g["correctness"].notna())].drop_duplicates("qid").set_index("qid")
        drops = []
        for qid in tr.index:
            if qid in rag.index and pd.notna(tr.loc[qid, "correctness"]) and pd.notna(rag.loc[qid, "correctness"]):
                d = rag.loc[qid, "correctness"] - tr.loc[qid, "correctness"]
                if d > 0:
                    drops.append((d, qid, tr.loc[qid]))
        drops.sort(key=lambda t: -t[0])
        picks += [("Romanized-query drop (native was fine)", qid, r)
                  for _, qid, r in drops[:3] if (r["correctness"] or 5) <= 3]
        # wrong language / code-mixing
        sub = g[(g["purity"] < 0.6) & (g["correctness"].notna())].nsmallest(3, "purity")
        picks += [("Answer not in target script", r["qid"], r) for _, r in sub.iterrows()]

        seen = set()
        for label, qid, r in picks:
            key = (label, qid)
            if key in seen:
                continue
            seen.add(key)
            out += [
                f"### [{label}] `{qid}`",
                f"- **Question:** {r['question']}",
                f"- **Gloss (Q):** {r['gloss_question']}",
                f"- **Gold answer:** {r['gloss_reference']} | original: {' | '.join(r['answers'][:2])}",
                f"- **Bot answer:** {r['answer']}",
                f"- **Gloss (A):** {r['gloss_answer']}",
                f"- **Flags:** {', '.join(r['flags']) or 'none'} | correctness={r['correctness']} purity={r['purity']}",
                "",
            ]
    return "\n".join(out)


def model_comparison_table(s: pd.DataFrame) -> str:
    models = sorted(s["gen_model"].unique())
    if len(models) < 2:
        return ""
    lines = [
        "### Generator family comparison (judge correctness, 0-5)",
        "",
        "| Language | Mode | " + " | ".join(models) + " |",
        "|" + "---|" * (len(models) + 2),
    ]
    for lang in LANG_ORDER:
        for mode in ("gold_context", "rag"):
            cells, any_data = [], False
            for gm in models:
                sub = s[(s["gen_model"] == gm) & (s["lang"] == lang) & (s["mode"] == mode)]
                cells.append(f"{sub['correctness'].iloc[0]:.2f}" if len(sub) else "-")
                any_data = any_data or bool(len(sub))
            if any_data:
                lines.append(f"| {LANG_LABEL[lang]} | {MODE_LABEL[mode]} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main():
    df = collect()
    if df.empty:
        print("No judged results found yet.")
        return
    s = summarize(df)
    ret = retrieval_summary()

    # Include evaluation configuration in the report for reproducibility
    config_info = (
        f"\n---\n"
        f"Evaluation configuration:\n"
        f"  - Languages: {', '.join(ALL_LANGS)}\n"
        f"  - Eval questions per language: {N_EVAL}\n"
        f"  - Per-language RUN_LIMIT: {RUN_LIMIT}\n"
        f"  - Pipeline modes: {', '.join(MODES)}\n"
        f"  - Primary generator: {PRIMARY_GENERATOR}\n"
        f"  - Judge model: {JUDGE_MODEL}\n"
        f"  - Top-K retrieval: {TOP_K}\n"
        f"  - Seed: {SEED}"
    )
    (REPORT_DIR / "CONFIG_SNAPSHOT.md").write_text(config_info, encoding="utf-8")
    s.to_csv(SUMMARY_DIR / "summary.csv", index=False)
    ret.to_csv(SUMMARY_DIR / "retrieval.csv", index=False)

    model = s["gen_model"].iloc[0]
    sm = s[s["gen_model"] == model]
    chart_correctness(sm, FIGURES_DIR / "correctness_by_lang_mode.png")
    chart_f1_em(sm, FIGURES_DIR / "f1_em_by_lang_mode.png")
    if not ret.empty:
        chart_retrieval(ret, FIGURES_DIR / "retrieval_native_vs_roman.png")
    chart_failures(df[df["gen_model"] == model], FIGURES_DIR / "failure_taxonomy.png")

    parts = ["# Auto-generated tables", ""]
    parts.append(md_table(sm, ["lang", "mode"], "correctness", "Judge correctness (0-5)"))
    parts.append(md_table(sm, ["lang", "mode"], "em", "Exact match"))
    parts.append(md_table(sm, ["lang", "mode"], "f1", "Token F1"))
    parts.append(md_table(sm, ["lang", "mode"], "faithfulness", "Faithfulness to context (1-5)"))
    parts.append(md_table(sm, ["lang", "mode"], "in_lang_rate", "Responses in target language/script (purity >= 0.8)"))
    comp = model_comparison_table(s)
    if comp:
        parts.append(comp)
    (REPORT_DIR / "tables.md").write_text("\n".join(parts), encoding="utf-8")
    (REPORT_DIR / "failures_examples.md").write_text(failure_examples(df[df["gen_model"] == model]), encoding="utf-8")
    print(f"[analyze] model={model} rows={len(df)}")
    print(sm[["lang", "mode", "correctness", "em", "f1", "in_lang_rate"]].to_string(index=False))


if __name__ == "__main__":
    main()
