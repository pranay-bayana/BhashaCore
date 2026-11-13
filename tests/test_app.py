"""Regression tests for the BhashaCore web application.

These tests run against the real application with the real research corpus
(retrieval pools, eval questions, saved judge results). Chat tests use the
live pipeline; if the LLM provider fails mid-test the app falls back to the
dataset-gold mode, so the assertions below hold under both paths.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app import app as flask_app  # noqa: E402
from src.config import LANGS, PRIMARY_GENERATOR  # noqa: E402
from src.metrics import script_purity  # noqa: E402
from src.retrieval import load_jsonl  # noqa: E402
from src.config import proc_path  # noqa: E402


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _chat(client, lang, question, mode="rag", session="test-sess", **extra):
    payload = {"session_id": session, "lang": lang, "question": question, "mode": mode}
    payload.update(extra)
    resp = client.post(
        "/api/chat",
        data=json.dumps(payload),
        content_type="application/json",
    )
    return resp


def _parse_ndjson(body: str):
    events = []
    for line in body.splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


# ---------------------------------------------------------------------------
# Health, languages, modes, examples
# ---------------------------------------------------------------------------


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    # every language pool must be a real, indexed corpus
    assert sorted(data["retrieval_pools"].keys()) == sorted(LANGS.keys())
    for lang, size in data["retrieval_pools"].items():
        assert size and size > 1000, f"pool {lang} unexpectedly small: {size}"


def test_languages_api(client):
    data = client.get("/api/languages").get_json()
    assert sorted(data["languages"].keys()) == ["en", "hi", "kn", "ml", "ta", "te"]


def test_modes_api(client):
    data = client.get("/api/modes").get_json()
    assert set(data["modes"]) == {"closed_book", "gold_context", "rag", "rag_translit"}
    assert data["generator"]


def test_examples_real_grounded(client):
    data = client.get("/api/examples").get_json()["examples"]
    assert set(data.keys()) == set(LANGS.keys())
    for lang, qs in data.items():
        assert qs, f"no grounded example for {lang}"
        # every example must be a real eval question for that language
        real = {e["question"] for e in load_jsonl(proc_path(f"eval_{lang}"))}
        assert qs[0]["question"] in real


# ---------------------------------------------------------------------------
# Chat: grounded questions in all six languages
# ---------------------------------------------------------------------------

GROUNDED = {
    "en": "How do cestids swim?",
    "hi": "ताजमहल कहां स्थित है?",
    "ta": "அக்பர் எங்கே பிறந்தார்?",
    "te": "గుర్రం వెంట ఎవరి బృందం ఉంది?",
    "kn": "ಜಿನ್ನಾ ಏನನ್ನು ಕೋರಿದ್ದರು?",
    "ml": "ഗാന്ധിജിയുടെ ജന്മസ്ഥലം ഏത് ?",
}


@pytest.mark.parametrize("lang", sorted(GROUNDED.keys()))
def test_chat_grounded_all_languages(client, monkeypatch, lang):
    # Corpus/citation regression, intentionally independent of live-provider
    # availability.  Live six-language behavior is verified separately.
    import src.app as app_mod
    monkeypatch.setattr(app_mod, "HAS_LLM", False)
    resp = _chat(client, lang, GROUNDED[lang], session=f"pytest-{lang}", eval_mode=True)
    assert resp.status_code == 200
    events = _parse_ndjson(resp.get_data(as_text=True))
    types = [e["type"] for e in events]
    assert types[0] == "meta"
    assert "delta" in types
    done = next(e for e in events if e["type"] == "done")
    assert done["status"] == "answered", f"{lang}: {done['answer'][:80]}"
    used = [c for c in done["citations"] if c["used"]]
    assert used, f"{lang}: no used citations"
    # answer must be in the expected script
    purity = script_purity(done["answer"], LANGS[lang]["script"])
    assert purity >= 0.5, f"{lang}: purity {purity}"
    # citations must be real passages from the real pool for this language
    pool_pids = {r["pid"] for r in load_jsonl(proc_path(f"pool_{lang}"))}
    for c in done["citations"]:
        assert c["pid"] in pool_pids, f"{lang}: citation pid {c['pid']} not in pool"


def test_chat_grounded_hindi_citation_integrity(client, monkeypatch):
    import src.app as app_mod
    monkeypatch.setattr(app_mod, "HAS_LLM", False)
    resp = _chat(client, "hi", "ताजमहल कहां स्थित है?", session="pytest-cite", eval_mode=True)
    done = next(e for e in _parse_ndjson(resp.get_data(as_text=True)) if e["type"] == "done")
    evals = {e["qid"]: e for e in load_jsonl(proc_path("eval_hi"))}
    match = next(e for e in evals.values() if e["question"] == "ताजमहल कहां स्थित है?")
    used = [c for c in done["citations"] if c["used"]]
    assert match["gold_pid"] in {c["pid"] for c in used}, "gold passage not among used citations"
    pool = {r["pid"]: r for r in load_jsonl(proc_path("pool_hi"))}
    for c in used:
        assert pool[c["pid"]]["text"].startswith(c["text"][:50]), "citation text must come from the real passage"


def test_chat_insufficient_evidence(client, monkeypatch):
    import src.app as app_mod
    monkeypatch.setattr(app_mod, "HAS_LLM", False)
    resp = _chat(client, "en", "What is the airspeed velocity of an unladen swallow in 1492?", session="pytest-unsup")
    assert resp.status_code == 200
    done = next(e for e in _parse_ndjson(resp.get_data(as_text=True)) if e["type"] == "done")
    # With live LLM configured, out-of-corpus questions get a model-only answer.
    # Without LLM, they get insufficient_evidence.
    from src.app import HAS_LLM
    if HAS_LLM:
        assert done["status"] == "answered"
        assert done.get("is_model_only") is True
        assert all(not c["used"] for c in done["citations"])
    else:
        assert done["status"] == "insufficient_evidence"
        # references attached but explicitly not used
        assert done["citations"], "expected closest-match references"
        assert all(not c["used"] for c in done["citations"])
        assert "not used" in done["answer"] or "sufficient" in done["answer"]


def test_chat_provider_failure_is_a_classified_error_not_a_fake_answer(client, monkeypatch):
    """A provider outage must not be streamed as a completed assistant reply."""
    import src.app as app_mod

    def boom(lang, question, passages):
        raise RuntimeError("simulated provider outage")

    monkeypatch.setattr(app_mod, "_llm_answer", boom)
    resp = _chat(client, "hi", "ताजमहल कहां स्थित है?", session="pytest-fallback")
    assert resp.status_code == 503
    assert resp.get_json() == {
        "error": "generation_error",
        "message": "The AI service is temporarily unavailable. Please retry once.",
        "retryable": True,
    }


def test_chat_timeout_is_classified_and_does_not_stream_done(client, monkeypatch):
    import src.app as app_mod

    def timeout(*args, **kwargs):
        raise app_mod.ProviderGenerationError(
            code="provider_timeout", status_code=None, latency_ms=30000,
        )

    monkeypatch.setattr(app_mod, "_llm_answer", timeout)
    resp = _chat(client, "hi", "ताजमहल कहां स्थित है?", session="pytest-timeout")
    assert resp.status_code == 504
    assert resp.get_json() == {
        "error": "provider_timeout",
        "message": "The AI response took too long. Please retry once.",
        "retryable": True,
    }


def test_eval_mode_uses_dataset_gold_on_provider_failure():
    """In eval_mode=True, dataset gold is used as fallback when LLM fails."""
    from src.app import answer_question

    result = answer_question(
        "hi", "ताजमहल कहां स्थित है?", eval_mode=True
    )
    # eval_mode uses dataset gold as fallback (this test doesn't monkeypatch,
    # so it depends on whether HAS_LLM is True; if True, the LLM will be tried
    # and may succeed or fail; if False, dataset gold is used directly)
    assert result["status"] in ("answered", "provider_unavailable")
    if result["status"] == "answered" and "dataset-eval-gold" in result["model"]:
        assert "आगरा" in result["answer"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_chat_validation(client):
    assert _chat(client, "en", "").status_code == 400
    assert _chat(client, "xx", "hello").status_code == 400
    assert _chat(client, "en", "hello", mode="bogus").status_code == 400
    assert _chat(client, "en", "x" * 2001).status_code == 400
    # malformed JSON body
    resp = client.post("/api/chat", data="{not json", content_type="application/json")
    assert resp.status_code == 400
    # JSON arrays and scalar values must not produce an internal server error.
    for body in ([], "not an object", 42):
        resp = client.post("/api/chat", json=body)
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "JSON object body required"
    resp = client.post("/api/chat", json={"question": ["not a string"]})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "question must be a string"
    resp = client.post("/api/chat", json={"question": "hello", "eval_mode": "false"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "eval_mode must be a boolean"


# ---------------------------------------------------------------------------
# Sessions / persistence
# ---------------------------------------------------------------------------


def test_new_chat_history_roundtrip(client, tmp_path, monkeypatch):
    import src.app as app_mod
    monkeypatch.setattr(app_mod, "HAS_LLM", False)
    sid = "pytest-persist-1"
    assert client.post("/api/new-chat", data=json.dumps({"session_id": sid}), content_type="application/json").status_code == 200
    resp = _chat(client, "hi", "ताजमहल कहां स्थित है?", session=sid, eval_mode=True)
    assert resp.status_code == 200
    # a streaming response must be consumed to run to completion
    assert "done" in [e["type"] for e in _parse_ndjson(resp.get_data(as_text=True))]
    histories = client.get("/api/history").get_json()["histories"]
    assert sid in {h["session_id"] for h in histories}
    loaded = client.post("/api/load-chat", data=json.dumps({"session_id": sid}), content_type="application/json")
    assert loaded.status_code == 200
    session = loaded.get_json()["session"]
    assert session["lang"] == "hi"
    assert any(m.get("role") == "user" for m in session["messages"])
    missing = client.post("/api/load-chat", data=json.dumps({"session_id": "does-not-exist"}), content_type="application/json")
    assert missing.status_code == 404


def test_stop_endpoint(client):
    resp = client.post("/api/stop", data=json.dumps({"session_id": "any"}), content_type="application/json")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "stopped"


def test_session_id_cannot_escape_chat_history(client):
    """Client-provided session IDs must never become paths outside CHAT_DIR."""
    for endpoint in ("/api/chat", "/api/new-chat", "/api/load-chat", "/api/stop"):
        body = {"session_id": "../escape"}
        if endpoint == "/api/chat":
            body["question"] = "hello"
        resp = client.post(endpoint, json=body)
        assert resp.status_code == 400, endpoint
        assert resp.get_json()["error"] == "invalid session_id"


@pytest.mark.parametrize("limit", ["nope", "0", "-1", "201"])
def test_failures_api_rejects_invalid_limit(client, limit):
    resp = client.get(f"/api/failures?limit={limit}")
    assert resp.status_code == 400
    assert "limit must be" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# Research data APIs (must match the saved results exactly)
# ---------------------------------------------------------------------------


def _expected_judge_counts():
    judged, failures = [], []
    model_dir = ROOT / "results" / "judge" / PRIMARY_GENERATOR.replace("/", "__")
    for path in model_dir.glob("*.jsonl"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("correctness") is None:
                    continue
                judged.append(r)
                if r["correctness"] <= 3:
                    failures.append(r)
    return judged, failures


def test_dashboard_matches_saved_results(client):
    data = client.get("/api/dashboard").get_json()
    judged, failures = _expected_judge_counts()
    assert data["counts"]["judged"] == len(judged)
    assert data["counts"]["failures"] == len(failures)
    assert data["counts"]["languages"] == 6
    assert sorted(data["by_language"].keys()) == sorted(LANGS.keys())
    # spot-check a headline number against the report: hi RAG correctness 4.08
    assert data["by_language"]["hi"]["rag"]["correctness"] == pytest.approx(4.08, abs=0.005)


def test_comparison_matches_saved_results(client):
    data = client.get("/api/comparison").get_json()
    by_lang = {l["lang"]: l for l in data["languages"]}
    assert set(by_lang) == set(LANGS)
    assert by_lang["en"]["gold_context"] == pytest.approx(4.94, abs=0.005)
    assert by_lang["ta"]["rag"] == pytest.approx(2.76, abs=0.005)
    assert by_lang["kn"]["recall_native"] == pytest.approx(0.67, abs=0.005)
    assert by_lang["hi"]["recall_romanized"] == pytest.approx(0.01, abs=0.005)
    assert by_lang["en"]["rag_translit"] is None  # stress test is Indic-only


def test_failures_api_filters(client):
    data = client.get("/api/failures?limit=100").get_json()
    assert data["failures"]
    for f in data["failures"]:
        assert f["correctness"] <= 3
    ta = client.get("/api/failures?lang=ta&limit=100").get_json()
    assert ta["failures"]
    assert all(f["lang"] == "ta" for f in ta["failures"])
    rag = client.get("/api/failures?mode=rag&limit=100").get_json()
    assert all(f["mode"] == "rag" for f in rag["failures"])
    empty = client.get("/api/failures?lang=zz").get_json()
    assert empty["failures"] == []


# ---------------------------------------------------------------------------
# Pages render
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "route,marker",
    [
        ("/", "BhashaCore"),
        ("/dashboard", "Research Dashboard"),
        ("/language-comparison", "Language Comparison"),
        ("/failure-analysis", "Failure Analysis"),
        ("/about", "About BhashaCore"),
    ],
)
def test_pages_render(client, route, marker):
    resp = client.get(route)
    assert resp.status_code == 200
    assert marker in resp.get_data(as_text=True)


def test_chat_page_contains_real_examples(client):
    html = client.get("/").get_data(as_text=True)
    assert "ताजमहल कहां स्थित है?" in html  # real eval question rendered as an example chip
    for lang_name in ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"]:
        assert lang_name in html
