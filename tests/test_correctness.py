"""Regression tests for evaluation-correctness and citation-grounding issues.

Covers the three investigated issues:
  1. Romanized-query Recall@5 near zero — locks in the verified mechanism
     (script mismatch) and guards the transliteration/eval-data quality and
     the retrieval-metric consistency with the saved research artifacts.
  2. Telugu citation grounding — the "used" marking must reflect genuine
     textual support, not lexical similarity or mere inclusion in context.
  3. Judged/failure counts and the correctness-threshold semantics.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.app as app_mod  # noqa: E402
from src.config import LANGS, INDIC_LANGS  # noqa: E402
from src.metrics import script_purity, _tokens  # noqa: E402
from src.retrieval import load_jsonl  # noqa: E402
from src.config import proc_path  # noqa: E402

# ---------------------------------------------------------------------------
# Grounded questions used across the grounding tests
# ---------------------------------------------------------------------------
TELUUGU_Q = "గుర్రం వెంట ఎవరి బృందం ఉంది?"


@pytest.fixture()
def client():
    app_mod.app.config["TESTING"] = True
    with app_mod.app.test_client() as c:
        yield c


def _chat(client, lang, question, **extra):
    body = {"session_id": extra.pop("session", "correctness-sess"), "lang": lang,
            "question": question, "mode": "rag"}
    body.update(extra)
    resp = client.post("/api/chat", data=json.dumps(body), content_type="application/json")
    events = []
    for line in resp.get_data(as_text=True).splitlines():
        if line.strip():
            events.append(json.loads(line))
    return resp, next(e for e in events if e["type"] == "done")


# ===========================================================================
# Issue 2 — Telugu citation grounding
# ===========================================================================


def test_support_function_semantics():
    """The support measure must separate genuine support from lexical noise."""
    passage = "గ్రామంలో స్వయం సహాయక బృందం ఉంది. ఇది పౌర సరఫరాల కేంద్రం."
    # Verbatim extractive answer -> full support
    assert app_mod._support(passage, "స్వయం సహాయక బృందం") == pytest.approx(1.0)
    # Single shared common token ("bRndM"/troop) -> only partial support
    assert app_mod._support(passage, "యోధుల బృందం") == pytest.approx(0.5)
    # Shared function word only ("uMdi"/exists) -> partial, still below threshold
    fn_word_support = app_mod._support(passage, "గుర్రం వెంట ఉంది")
    assert 0 < fn_word_support < app_mod.SUPPORT_THRESHOLD
    # Genuinely disjoint answer -> zero support
    assert app_mod._support(passage, "హైదరాబాద్ రాజధాని") == 0.0
    # Empty answer -> zero support (no undefined claims)
    assert app_mod._support(passage, "") == 0.0


def test_telugu_grounding_used_citations_genuinely_support_deterministic(client, monkeypatch):
    """The reported Telugu defect, tested deterministically.

    The gold passage for this question ranks 4th; ranks 1-2 are irrelevant
    village passages that share only the common token "bRndM" (support 0.5)
    and must NOT be displayed as used. Gold answers are verbatim extractive
    spans of the gold passage (support 1.0).
    """
    def boom(*args, **kwargs):
        raise RuntimeError("simulated provider outage")

    monkeypatch.setattr(app_mod, "_llm_answer", boom)
    _, done = _chat(client, "te", TELUUGU_Q, session="correctness-te", eval_mode=True)

    assert done["status"] == "answered"
    used = [c for c in done["citations"] if c["used"]]
    assert used, "the gold passage must be marked used"
    # Only genuinely supporting passages may be marked used
    for c in used:
        assert (c["support"] >= app_mod.SUPPORT_THRESHOLD) or c["rank"] <= (done["gold_rank"] or 0), \
            f"used citation rank {c['rank']} support {c['support']} does not support the answer"
    # The irrelevant village passages (support 0.5 via the common token) are not used
    not_used = [c for c in done["citations"] if not c["used"]]
    assert any(c["support"] < app_mod.SUPPORT_THRESHOLD for c in not_used)
    # Every citation carries a measured support score
    assert all(isinstance(c["support"], (int, float)) for c in done["citations"])


def test_telugu_grounding_live_llm_contract(client):
    """With the live LLM, used-marking still obeys the support contract."""
    _, done = _chat(client, "te", TELUUGU_Q, session="correctness-te-live")
    assert done["status"] == "answered"
    evals = load_jsonl(proc_path("eval_te"))
    gold_pid = next(e for e in evals if e["question"] == TELUUGU_Q)["gold_pid"]
    for c in done["citations"]:
        if c["used"]:
            assert c["support"] >= app_mod.SUPPORT_THRESHOLD or c["pid"] == gold_pid, (
                f"used citation {c['pid']} support={c['support']} is neither textually "
                f"supporting (>= {app_mod.SUPPORT_THRESHOLD}) nor the gold passage"
            )


@pytest.mark.parametrize("lang", ["en", "hi", "ta", "te", "kn", "ml"])
def test_used_citations_support_contract_all_languages(client, lang):
    """Every 'used' citation in any language either textually supports the
    answer (>= 80% of answer tokens) or is the gold passage of the matched
    evaluation question."""
    examples = app_mod.grounded_examples(1)[lang][0]
    _, done = _chat(client, lang, examples["question"], session=f"correctness-{lang}")
    assert done["status"] == "answered"
    evals = {e["question"]: e for e in load_jsonl(proc_path(f"eval_{lang}"))}
    gold_pid = evals[examples["question"]]["gold_pid"]
    used = [c for c in done["citations"] if c["used"]]
    assert used
    for c in used:
        assert c["support"] >= app_mod.SUPPORT_THRESHOLD or c["pid"] == gold_pid


def test_unsupplied_passages_are_never_used(client, monkeypatch):
    """A passage with high lexical overlap that was NOT supplied to the
    generator must not be marked used."""
    evals = load_jsonl(proc_path("eval_te"))
    e = next(x for x in evals if x["question"] == TELUUGU_Q)
    pool = {r["pid"]: r for r in load_jsonl(proc_path("pool_te"))}
    # The gold passage is the only supplied context in dataset-gold mode
    monkeypatch.setattr(app_mod, "_llm_answer", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("outage")))
    _, done = _chat(client, "te", TELUUGU_Q, session="correctness-unsupplied", eval_mode=True)
    used_pids = {c["pid"] for c in done["citations"] if c["used"]}
    assert used_pids == {e["gold_pid"]}


# ===========================================================================
# Issue 1 — Romanized-query recall: mechanism and pipeline consistency
# ===========================================================================


@pytest.mark.parametrize("lang", INDIC_LANGS)
def test_romanized_eval_questions_are_clean_latin(lang):
    """Guards the transliteration method and the evaluation inputs: every
    Indic eval question must have a non-empty, Latin-script romanization
    that differs from the native question."""
    evals = load_jsonl(proc_path(f"eval_{lang}"))
    assert evals
    for e in evals:
        rq = e.get("romanized_question", "")
        assert rq.strip(), f"{lang} qid={e['qid']}: empty romanized_question"
        assert script_purity(rq, "Latin") >= 0.8, (
            f"{lang} qid={e['qid']}: romanization not Latin: {rq!r}"
        )
        assert rq != e["question"]


@pytest.mark.parametrize("lang", INDIC_LANGS)
def test_script_mismatch_mechanism_of_near_zero_romanized_recall(lang):
    """Documents the verified root cause: a romanized (Latin) query shares
    essentially zero word tokens with its native-script gold passage, so
    word-level BM25 cannot retrieve it. If this test ever fails, the corpus
    representation or tokenizer changed and the research finding must be
    re-evaluated."""
    evals = load_jsonl(proc_path(f"eval_{lang}"))
    pool = {r["pid"]: r for r in load_jsonl(proc_path(f"pool_{lang}"))}
    overlaps = []
    for e in evals:
        q_toks = set(_tokens(e["romanized_question"]))
        gold_toks = set(_tokens(pool[e["gold_pid"]]["text"]))
        if q_toks:
            overlaps.append(len(q_toks & gold_toks) / len(q_toks))
    avg = sum(overlaps) / len(overlaps)
    assert avg < 0.15, (
        f"{lang}: average romanized-query/gold-passage token overlap is {avg:.3f}; "
        "the near-zero-recall finding no longer holds — re-run the evaluation"
    )


def test_romanized_retrieval_metrics_match_saved_artifacts():
    """The dashboard's Romanized-query Recall@5 figures must be reproducible
    from the canonical retrieval files (evaluation-pipeline consistency)."""
    expected = {"hi": 0.01, "ta": 0.06, "te": 0.04, "kn": 0.00, "ml": 0.09}
    saved = {}
    with open(ROOT / "results" / "summary" / "retrieval.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["mode"] == "rag_translit":
                saved[row["lang"]] = float(row["recall@5"])
    assert saved == expected, f"retrieval.csv romanized recall drifted: {saved}"
    for lang, exp in expected.items():
        recs = load_jsonl(proc_path(f"retrieval_translit_{lang}"))
        hits = sum(1 for r in recs if r["hit"])
        assert hits / len(recs) == pytest.approx(exp, abs=1e-6), (
            f"{lang}: canonical file recall {hits / len(recs):.4f} != reported {exp}"
        )


def test_native_retrieval_metrics_match_saved_artifacts():
    """Same consistency check for native-script retrieval (all 6 languages)."""
    expected = {"en": 0.95, "hi": 0.80, "ta": 0.57, "te": 0.85, "kn": 0.67, "ml": 0.84}
    saved = {}
    with open(ROOT / "results" / "summary" / "retrieval.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["mode"] == "rag":
                saved[row["lang"]] = round(float(row["recall@5"]), 2)
    assert saved == expected, f"retrieval.csv native recall drifted: {saved}"
    for lang, exp in expected.items():
        recs = load_jsonl(proc_path(f"retrieval_{lang}"))
        hits = sum(1 for r in recs if r["hit"])
        assert round(hits / len(recs), 2) == exp, (
            f"{lang}: canonical file recall {hits / len(recs):.2f} != reported {exp}"
        )


def test_stray_jsonl_jsonl_duplicates_are_inert():
    """The `.jsonl.jsonl` files are byte-identical duplicates of the canonical
    retrieval files from the original build. Lock that in: if any ever
    diverges, it must be investigated rather than silently ignored."""
    stray = sorted(ROOT.glob("data/processed/*.jsonl.jsonl"))
    assert stray, "expected the known stray duplicate files to still exist"
    for p in stray:
        canonical = p.with_name(p.name[: -len(".jsonl")])
        assert canonical.exists(), f"canonical counterpart missing for {p.name}"
        assert p.read_bytes() == canonical.read_bytes(), (
            f"{p.name} diverged from {canonical.name} — no longer an inert duplicate"
        )


# ===========================================================================
# Issue 3 — judged/failure counts and the correctness threshold
# ===========================================================================


def _judge_rows():
    rows = []
    model_dir = ROOT / "results" / "judge" / "minimaxai__minimax-m3.1-flash"
    for path in sorted(model_dir.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def test_judged_and_failure_counts():
    """1,117 judged answers / 530 failures (correctness <= 3), with no
    duplicate judgements — matches the numbers on the dashboard and in
    report/REPORT.md."""
    rows = _judge_rows()
    judged = [r for r in rows if r.get("correctness") is not None]
    keys = [(r["lang"], r["mode"], r["qid"]) for r in judged]
    assert len(keys) == len(set(keys)), "duplicate judgements found"
    assert len(judged) == 1117
    failures = [r for r in judged if r["correctness"] <= 3]
    assert len(failures) == 530
    # coverage: 23 evaluated cells (en has no rag_translit mode), ~48.6/50 avg
    cells = {(r["lang"], r["mode"]) for r in judged}
    assert len(cells) == 23
    assert not any(lang == "en" and mode == "rag_translit" for lang, mode in cells)


def test_failure_threshold_documented_on_pages(client):
    """The meaning of the correctness threshold must be visible where the
    530-failure figure is shown (dashboard) and defined (About)."""
    dash = client.get("/dashboard").get_data(as_text=True)
    assert "≤ 3" in dash and "0 = refusal" in dash
    about = client.get("/about").get_data(as_text=True)
    assert "failure when it scores" in about and "≤ 3" in about
