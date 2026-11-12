"""Integration tests: the multilingual chat pipeline end to end.

Deterministic tests use the dataset-gold fallback (LLM monkeypatched to
fail) so they never depend on live model behaviour; live-LLM tests are
marked and assert only the honest contract, never exact wording.
"""

import json
import sys
from pathlib import Path

from functools import lru_cache

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.app as app_mod  # noqa: E402
from src.config import INDIC_LANGS, LANGS, proc_path  # noqa: E402
from src.langkit import bridge_to_native  # noqa: E402
from src.metrics import script_purity  # noqa: E402
from src.retrieval import PoolIndex, load_jsonl  # noqa: E402
from src.translit import romanize  # noqa: E402


@pytest.fixture()
def client():
    app_mod.app.config["TESTING"] = True
    with app_mod.app.test_client() as c:
        yield c


def _chat(client, body):
    defaults = {"session_id": "multi-sess", "mode": "rag"}
    defaults.update(body)
    resp = client.post("/api/chat", data=json.dumps(defaults), content_type="application/json")
    events = []
    for line in resp.get_data(as_text=True).splitlines():
        if line.strip():
            events.append(json.loads(line))
    return resp, events


def _done(events):
    return next(e for e in events if e["type"] == "done")


def _force_dataset_gold(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("simulated provider outage")

    monkeypatch.setattr(app_mod, "_llm_answer", boom)


# ---------------------------------------------------------------------------
# Input language resolution
# ---------------------------------------------------------------------------


def test_auto_detect_resolves_native_script(client, monkeypatch):
    _force_dataset_gold(monkeypatch)
    _, events = _chat(client, {"input_lang": "auto", "question": "ताजमहल कहां स्थित है?", "eval_mode": True})
    done = _done(events)
    assert done["input_lang"] == "hi"
    assert done["input_detected_script"] == "Devanagari"
    assert not done["input_ambiguous"]


def test_auto_detect_latin_is_flagged_ambiguous(client, monkeypatch):
    _force_dataset_gold(monkeypatch)
    # Latin input must NOT be silently treated as English without a flag
    _, events = _chat(client, {"input_lang": "auto", "question": "What is the airspeed velocity of an unladen swallow?", "eval_mode": True})
    done = _done(events)
    assert done["input_lang"] == "en"
    assert done["input_ambiguous"] is True
    assert done["input_detected_script"] == "Latin"


def test_legacy_lang_field_still_works(client, monkeypatch):
    _force_dataset_gold(monkeypatch)
    _, events = _chat(client, {"lang": "hi", "question": "ताजमहल कहां स्थित है?", "eval_mode": True})
    done = _done(events)
    assert done["input_lang"] == "hi"


def test_validation_rejects_new_field_garbage(client, monkeypatch):
    _force_dataset_gold(monkeypatch)
    assert _chat(client, {"input_lang": "hi", "input_style": "bogus", "question": "x"})[0].status_code == 400
    assert _chat(client, {"input_lang": "hi", "answer_script": "bogus", "question": "x"})[0].status_code == 400
    assert _chat(client, {"input_lang": "hi", "answer_lang": "xx", "question": "x"})[0].status_code == 400
    assert _chat(client, {"input_lang": "zz", "question": "x"})[0].status_code == 400


# ---------------------------------------------------------------------------
# Romanized input: dual retrieval + grounding (per Indic language)
# ---------------------------------------------------------------------------


def _romanized_grounded_question(lang):
    """Find (deterministically, from the real data) the shortest evaluation
    question whose romanization still retrieves its gold passage via dual
    retrieval — the measured 15-45% of questions that stay answerable."""
    evals = load_jsonl(proc_path(f"eval_{lang}"))
    index = PoolIndex(load_jsonl(proc_path(f"pool_{lang}")))
    grounded = []
    for e in evals:
        rq = e["romanized_question"]
        bq = bridge_to_native(rq, lang)
        best = {}
        for q in (rq, bq):
            for pid, score in index.search(q, 5):
                best[pid] = max(best.get(pid, 0.0), score)
        top5 = sorted(best, key=lambda p: -best[p])[:5]
        if e["gold_pid"] in top5:
            grounded.append(e)
    grounded.sort(key=lambda e: len(e["romanized_question"]))
    assert grounded, f"{lang}: no dual-retrieval grounded romanized question found"
    return grounded[0]


@pytest.mark.parametrize("lang", INDIC_LANGS)
def test_romanized_input_grounded_answer_per_language(client, monkeypatch, lang):
    """Romanized (Latin-script) Indic input must be bridged, dual-retrieved,
    and answered in the native script with genuine citations.

    Uses deterministic dataset-gold mode (eval_mode=True) so the test is fast
    and repeatable. The live-LLM behavior is tested separately in one smoke test.
    """
    _force_dataset_gold(monkeypatch)
    e = _romanized_grounded_question(lang)
    _, events = _chat(client, {"input_lang": lang, "input_style": "romanized",
                               "question": e["romanized_question"], "eval_mode": True})
    done = _done(events)
    assert done["status"] == "answered", f"{lang}: romanized question did not ground: {done['answer'][:60]}"
    assert done["input_style"] == "romanized"
    assert done["bridged_query"], "expected a back-transliterated query"
    expected_script = LANGS[lang]["script"]
    assert script_purity(done["answer"], expected_script) >= 0.5, done["answer"][:60]
    used = [c for c in done["citations"] if c["used"]]
    assert used, "grounded romanized answer must cite the passages that support it"
    assert any(c["pid"] == e["gold_pid"] for c in used), "gold passage must be among used citations"


@pytest.mark.parametrize("lang", INDIC_LANGS)
def test_romanized_input_style_auto_detected(client, monkeypatch, lang):
    """With input_style=auto, Latin text for an explicitly selected Indic
    language is treated as romanized (never as English)."""
    _force_dataset_gold(monkeypatch)
    e = _romanized_grounded_question(lang)
    _, events = _chat(client, {"input_lang": lang, "input_style": "auto", "question": e["romanized_question"], "eval_mode": True})
    done = _done(events)
    assert done["input_style"] == "romanized"


def test_romanized_conversational_input_refuses_honestly(client, monkeypatch):
    """A conversational romanized input that the corpus cannot support must
    be refused when no live LLM is available — with the bridged query shown
    and references not used."""
    _force_dataset_gold(monkeypatch)
    monkeypatch.setattr(app_mod, "HAS_LLM", False)
    _, events = _chat(client, {"input_lang": "te", "input_style": "romanized", "question": "em chestunnav?"})
    done = _done(events)
    assert done["status"] == "insufficient_evidence"
    assert done["bridged_query"], "the pipeline should still show its normalization"
    assert all(not c["used"] for c in done["citations"])


# ---------------------------------------------------------------------------
# Answer language and script controls
# ---------------------------------------------------------------------------


def test_answer_script_romanized_is_deterministic_transliteration(client, monkeypatch):
    """Romanized output is transliteration of the SAME answer, deterministic
    in dataset-gold mode (no live model involved)."""
    _force_dataset_gold(monkeypatch)
    _, events = _chat(client, {"input_lang": "hi", "input_style": "native",
                               "question": "ताजमहल कहां स्थित है?", "answer_script": "romanized",
                               "eval_mode": True})
    done = _done(events)
    assert done["status"] == "answered"
    assert done["answer_script"] == "romanized"
    expected = romanize("आगरा", "Devanagari")
    assert script_purity(done["answer"], "Latin") >= 0.8, done["answer"]
    assert expected in done["answer"], "transliteration must preserve the gold answer's words"


def test_answer_script_native_stays_native(client, monkeypatch):
    _force_dataset_gold(monkeypatch)
    _, events = _chat(client, {"input_lang": "hi", "question": "ताजमहल कहां स्थित है?", "answer_script": "native", "eval_mode": True})
    done = _done(events)
    assert script_purity(done["answer"], "Devanagari") >= 0.8


def test_translation_honestly_degrades_without_llm(client, monkeypatch):
    """Cross-language answering requires translation, which only the LLM
    performs. In dataset-gold mode the app must say so instead of pretending."""
    _force_dataset_gold(monkeypatch)
    _, events = _chat(client, {"input_lang": "hi", "question": "ताजमहल कहां स्थित है?", "answer_lang": "te", "eval_mode": True})
    done = _done(events)
    assert done["status"] == "answered"
    assert done["answer_lang"] == "te"
    assert done["translation_note"], "must disclose that translation was unavailable"
    assert "unavailable" in done["translation_note"]
    # the gold answer is still shown, in its original language
    assert "आगरा" in done["answer"]


# --- One live-LLM smoke test (marked, not run by default in CI) ---
@pytest.mark.live_llm
def test_translation_live_llm_smoke(client):
    """A single live-LLM smoke test for translation path (not run in deterministic CI)."""
    _, events = _chat(client, {"input_lang": "hi", "question": "ताजमहल कहां स्थित है?", "answer_lang": "en"})
    done = _done(events)
    assert done["status"] == "answered"
    assert done["answer_lang"] == "en"
    assert script_purity(done["answer"], "Latin") >= 0.5, done["answer"][:80]
    used = [c for c in done["citations"] if c["used"]]
    assert used, "cross-language answers still cite their evidence anchor"


def test_answer_language_malayalam_live_llm(client):
    _, events = _chat(client, {"input_lang": "hi", "question": "ताजमहल कहां स्थित है?", "answer_lang": "ml"})
    done = _done(events)
    assert done["status"] == "answered"
    assert done["answer_lang"] == "ml"
    assert script_purity(done["answer"], "Malayalam") >= 0.5, done["answer"][:80]


def test_original_question_preserved_in_session(client):
    """The original question must be stored verbatim, even when a normalized
    or bridged query was used internally."""
    e = _romanized_grounded_question("te")
    sid = "multi-preserve"
    _chat(client, {"session_id": sid, "input_lang": "te", "input_style": "romanized",
                   "question": e["romanized_question"]})
    loaded = client.post("/api/load-chat", data=json.dumps({"session_id": sid}), content_type="application/json")
    session = loaded.get_json()["session"]
    user_msgs = [m for m in session["messages"] if m.get("role") == "user"]
    assert user_msgs[-1]["content"] == e["romanized_question"]
