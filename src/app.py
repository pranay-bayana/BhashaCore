"""BhashaCore web application.

Real BM25 retrieval over the project's per-language research corpus, honest
evidence-sufficiency behaviour, real citations, and NDJSON streaming chat.

Generation source (honest, never fabricated):
  - If an NVIDIA NIM key is configured  -> real LLM generation via src.nim.NimClient.
  - Otherwise                          -> for questions that match an indexed
    evaluation question AND whose gold passage is retrieved, the answer is the
    dataset's own gold answer (real data, labelled `dataset-eval-gold`).
    Everything else returns an explicit "insufficient evidence" notice with the
    closest low-confidence matches attached as references (not used).
"""

import csv
import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path
from threading import Event, Lock

from flask import Flask, Response, jsonify, render_template, request, g, session, flash, redirect, url_for, send_from_directory, current_app
from flask_wtf.csrf import CSRFError, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Gunicorn does not load Flask's development dotenv files. Load the local file
# once, without overriding environment variables supplied by the host.
load_dotenv(ROOT / ".env", override=False)

from src.config import (  # noqa: E402
    INDIC_LANGS,
    JUDGE_DIR,
    LANGS,
    LLM_CALL_TIMEOUT,
    MAX_OUT_TOKENS,
    MODES,
    PRIMARY_GENERATOR,
    PROC_DIR,
    SUMMARY_DIR,
    TOP_K,
    gen_results_path,
    judge_results_path,
    proc_path,
)
from src.langkit import (  # noqa: E402
    bridge_to_native,
    bridge_variants,
    detect_script_and_language,
    effective_input_style,
    romanize_output,
)
from src.retrieval import PoolIndex, load_jsonl  # noqa: E402
from src.translations import (  # noqa: E402
    get_all_translations,
    get_available_languages,
    get_language_name,
    get_translations,
    resolve_lang,
    t as _t,
)
from src.auth import (Conversation, Message, GuestSession, authenticate, complete_guest_response,
                      create_user, current_user, db, create_reset_token, delete_user,
                      get_or_create_guest_session, get_owned_conversation, init_auth, login_required,
                      release_guest_response, reserve_guest_response,
                      reset_password)  # noqa: E402
from src.emailer import send_password_reset  # noqa: E402


def _normalize_romanized(text: str) -> str:
    """Normalize romanized text for matching (remove diacritics, normalize digraphs)."""
    text = (text or "").lower()
    # Remove common diacritics
    for src, dst in [("è", "e"), ("é", "e"), ("à", "a"), ("á", "a"), ("ì", "i"), ("í", "i"),
                     ("ò", "o"), ("ó", "o"), ("ù", "u"), ("ú", "u"), ("ñ", "n"),
                     ("ā", "a"), ("ī", "i"), ("ū", "u"), ("ē", "e"), ("ō", "o"),
                     ("ṃ", "m"), ("ṁ", "m"), ("ḥ", "h"), ("ṇ", "n"), ("ḍ", "d"),
                     ("ṭ", "t"), ("ḍ", "d"), ("ś", "s"), ("ṣ", "s")]:
        text = text.replace(src, dst)
    # Normalize common digraphs
    for src, dst in [("kh", "k"), ("gh", "g"), ("ch", "c"), ("jh", "j"), ("th", "t"),
                     ("dh", "d"), ("ph", "p"), ("bh", "b"), ("ṛ", "r"), ("ṝ", "r"),
                     ("ḷ", "l"), ("ai", "ai"), ("au", "au"), ("aa", "a"), ("ii", "i"),
                     ("uu", "u"), ("ee", "e"), ("oo", "o"), ("ae", "ae"), ("oe", "oe")]:
        text = text.replace(src, dst)
    return text


_ENGLISH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "can", "could", "did", "do", "does", "doing", "for", "from", "had", "has",
    "have", "he", "her", "hers", "him", "his", "how", "i", "if", "in", "into",
    "is", "it", "its", "just", "like", "may", "me", "might", "mo", "more", "most",
    "must", "my", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
    "or", "other", "our", "ours", "out", "over", "own", "quite", "rather", "really",
    "s", "said", "same", "see", "seemed", "seemed", "seeing", "seems", "several",
    "shall", "she", "should", "show", "showed", "shown", "shows", "since", "so",
    "some", "such", "t", "take", "taken", "tell", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "thus", "to", "too", "under", "until", "up", "us",
    "us", "use", "used", "uses", "very", "w", "was", "we", "well", "were", "what",
    "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas",
    "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while",
    "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "would",
    "yet", "you", "your", "yours", "yourself", "yourselves",
}

def _is_mostly_english(text: str) -> bool:
    """Return True if most words in the text are common English words."""
    words = text.split()
    if not words:
        return False
    strip_chars = '.,!?;:\'"()[]{}'
    english_count = sum(1 for w in words if w.lower().strip(strip_chars) in _ENGLISH_STOPWORDS)
    return english_count / len(words) > 0.5


def _detect_romanized_language(question: str) -> str | None:
    """Try to detect the Indic language for romanized (Latin-script) input.

    Strategy: transliterate the Latin input to each Indic language script.
    If transliteration produces mostly target-script characters (>= 95%),
    the input is likely Romanized Indic in that language. English text
    transliterated to Indic script typically retains many Latin characters
    (score ~0.85-0.90), so 0.95 cleanly separates Romanized Indic from
    English.

    When multiple languages pass the transliteration threshold (which
    happens because any Latin text transliterates to 100% target script),
    disambiguate by doing BM25 retrieval in each candidate language's pool
    using the bridged query and picking the language with the highest score.
    """
    from src.langkit import bridge_to_native

    if not question or not question.strip():
        return None

    # If most words are English, don't treat as Romanized Indic
    if _is_mostly_english(question):
        return None

    # First pass: transliterate to each language and score
    candidates: dict[str, float] = {}
    for code in INDIC_LANGS:
        try:
            bridged = bridge_to_native(question, code)
            if not bridged.strip():
                continue
            total_chars = sum(1 for c in bridged if c.isalpha())
            if total_chars == 0:
                continue
            script_chars = sum(1 for c in bridged if ord(c) > 127 and c.isalpha())
            score = script_chars / total_chars
            if score > 0:
                candidates[code] = score
        except Exception:
            continue

    if not candidates:
        return None

    best_lang, best_score = max(candidates.items(), key=lambda kv: kv[1])

    # If only one language passes the transliteration test, use it
    if best_score >= 0.85 and len(candidates) == 1:
        return best_lang

    # If multiple languages pass (or the best score is borderline), use
    # retrieval quality as tiebreaker: retrieve in each candidate language
    # using the bridged query and pick the language with the highest score.
    if best_score >= 0.85:
        best_lang, best_score = None, 0.0
        for code in candidates:
            try:
                bridged = bridge_to_native(question, code)
                index = _pool_index(code)
                hits = index.search(bridged, TOP_K)
                if hits:
                    max_score = max(s for _, s in hits)
                    if max_score > best_score:
                        best_score, best_lang = max_score, code
            except Exception:
                continue
        return best_lang

    return None


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
_production = os.environ.get("APP_ENV", "development").lower() == "production"
if _production and not os.environ.get("FLASK_SECRET_KEY"):
    raise RuntimeError("FLASK_SECRET_KEY is required when APP_ENV=production")
if _production and not os.environ.get("REDIS_URL"):
    raise RuntimeError("REDIS_URL is required when APP_ENV=production")
if _production and os.environ.get("SESSION_COOKIE_SECURE", "").lower() != "true":
    raise RuntimeError("SESSION_COOKIE_SECURE=true is required when APP_ENV=production")
_database_url = os.environ.get("DATABASE_URL")
if _production and not _database_url:
    raise RuntimeError("DATABASE_URL is required when APP_ENV=production")
if _production and _database_url and not _database_url.startswith(("postgresql://", "postgresql+psycopg://")):
    raise RuntimeError("DATABASE_URL must use PostgreSQL when APP_ENV=production")
_trusted_hosts = [host.strip() for host in os.environ.get("TRUSTED_HOSTS", "").split(",") if host.strip()]
if _production and not _trusted_hosts:
    raise RuntimeError("TRUSTED_HOSTS is required when APP_ENV=production")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or "bhashacore-dev-secret-key-2026-multilingual-evaluation"
app.config["SQLALCHEMY_DATABASE_URI"] = _database_url or f"sqlite:///{ROOT / 'instance' / 'bhashacore_dev_v2.sqlite3'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 1800}
if _database_url and _database_url.startswith(("postgresql://", "postgresql+psycopg://")):
    # Suitable for managed session poolers: bounded connections, stale-connection
    # detection, a finite checkout wait, and TLS required by the DB driver.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"].update({
        "pool_size": 5,
        "max_overflow": 5,
        "pool_timeout": 30,
        # psycopg automatically prepares frequently-used statements by default.
        # Transaction poolers may route consecutive requests to different backend
        # sessions, so keep statements client-side for pooler compatibility.
        "connect_args": {
            "connect_timeout": 10,
            "sslmode": "require",
            "prepare_threshold": None,
        },
    })
app.config["RATELIMIT_STORAGE_URI"] = os.environ.get("REDIS_URL", "memory://")
app.config["RATELIMIT_HEADERS_ENABLED"] = True
app.config["RATELIMIT_ENABLED"] = os.environ.get("RATELIMIT_ENABLED", "true").lower() != "false"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["TRUSTED_HOSTS"] = _trusted_hosts or None
app.config["ALLOW_ANONYMOUS_CHAT"] = not _production and os.environ.get("ALLOW_ANONYMOUS_CHAT", "true").lower() == "true"
init_auth(app)
csrf = CSRFProtect(app)
limiter = Limiter(key_func=get_remote_address, app=app, storage_uri=app.config["RATELIMIT_STORAGE_URI"], enabled=app.config.get("RATELIMIT_ENABLED", True))


def chat_access_required(view):
    """Production chat always belongs to an authenticated account."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not app.config["ALLOW_ANONYMOUS_CHAT"] and current_user() is None:
            return jsonify({"error": "authentication required"}), 401
        return view(*args, **kwargs)
    return wrapped


@app.errorhandler(CSRFError)
def csrf_error(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "csrf_invalid",
            "message": "Your security token expired. Refreshing it and retrying once.",
        }), 400
    return render_template("csrf_error.html"), 400


@app.errorhandler(400)
def handle_bad_request(error):
    if request.path.startswith("/api/"):
        desc = getattr(error, "description", "bad request")
        return jsonify({"error": desc}), 400
    return "Bad Request", 400


@app.errorhandler(500)
def handle_server_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "internal server error"}), 500
    return "Internal Server Error", 500


@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    """Keep database outages observable without turning API failures into HTML/500s.

    Persistence is required for sessions, history and chat ownership.  A failed
    database must therefore never be silently replaced with local storage in a
    deployed process.  Log the traceback for the operator and return a stable,
    non-sensitive response to API clients instead.
    """
    app.logger.exception("Database request failed", exc_info=error)
    db.session.rollback()
    if request.path.startswith("/api/") or request.path == "/health":
        return jsonify({
            "error": "database_unavailable",
            "message": "The data service is temporarily unavailable. Please try again shortly.",
        }), 503
    return "Service temporarily unavailable", 503


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data: https:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "script-src 'self' 'unsafe-inline'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'"
    )
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

    # Ensure interface language cookie stays synchronized
    cookie_to_set = getattr(g, "_set_cookie_lang", None)
    if cookie_to_set and cookie_to_set in get_available_languages():
        response.set_cookie("bhashacore-ui-lang", cookie_to_set, max_age=365 * 24 * 3600, path="/", samesite="Lax")
        response.set_cookie("bhashacore-lang", cookie_to_set, max_age=365 * 24 * 3600, path="/", samesite="Lax")
    return response

# ---------------------------------------------------------------------------
# LLM availability (checked once, honestly reported to the UI)
# ---------------------------------------------------------------------------


def _llm_configured() -> bool:
    """Check if an LLM API key is configured (no network probe).

    Network reachability is verified per-request when generation is attempted.
    This avoids a fragile one-time import-time probe that can fail transiently
    and permanently disable live generation for the life of the process.
    Never exposes the key value.
    """
    provider = os.environ.get("GENERATION_PROVIDER", "nvidia").lower()
    if provider == "sarvam":
        return bool(os.environ.get("SARVAM_API_KEY"))
    try:
        from src.nim import get_api_key

        get_api_key()
        return True
    except Exception:
        return False


def _active_generator_model() -> str:
    """Return the configured live provider model without probing inference."""
    if os.environ.get("GENERATION_PROVIDER", "nvidia").lower() == "sarvam":
        return os.environ.get("SARVAM_MODEL", "sarvam-105b-conversations")
    return os.environ.get("NVIDIA_MODEL", PRIMARY_GENERATOR)


class ProviderGenerationError(RuntimeError):
    """A safe, classified failure returned by a live generation provider."""

    def __init__(self, *, code: str, status_code: int | None, latency_ms: int):
        super().__init__(code)
        self.code = code
        self.status_code = status_code
        self.latency_ms = latency_ms


def _live_provider_answer(messages: list[dict[str, str]]) -> str:
    """Run one verified provider request while preserving existing route contracts."""
    from src.generation_provider import GenerationRequest, create_generation_provider

    provider = create_generation_provider()
    try:
        result = _run_async(provider.generate(GenerationRequest(
            messages=messages,
            model=_active_generator_model(),
            max_tokens=MAX_OUT_TOKENS,
            temperature=0,
        )), timeout=LLM_CALL_TIMEOUT)
    finally:
        try:
            _run_async(provider.aclose())
        except Exception:
            pass
    if not result.completed or not result.content:
        # Never include a provider response body, prompt, or credential in a
        # client response or log.  These structured fields are enough to
        # diagnose the failure while keeping the public API safe.
        current_app.logger.warning(
            "generation provider failed provider=%s model=%s code=%s status=%s latency_ms=%s",
            result.provider, result.model, result.error_code, result.status_code,
            result.latency_ms,
        )
        raise ProviderGenerationError(
            code=result.error_code or "provider_error",
            status_code=result.status_code,
            latency_ms=result.latency_ms,
        )
    return result.content


def _public_provider_error(exc: Exception) -> tuple[dict, int]:
    """Map provider failures to actionable, non-sensitive API errors."""
    code = exc.code if isinstance(exc, ProviderGenerationError) else "generation_error"
    if code in {"provider_http_401", "provider_http_403"}:
        message, status = "The AI service authentication needs attention. Please try again later.", 502
    elif code in {"provider_http_429", "provider_rate_limited"}:
        message, status = "The AI service is busy. Please wait a moment and retry once.", 429
    elif code == "provider_timeout":
        message, status = "The AI response took too long. Please retry once.", 504
    elif code in {"provider_transport_error", "provider_incomplete_stream"}:
        message, status = "The AI response was interrupted. Please retry once.", 502
    else:
        message, status = "The AI service is temporarily unavailable. Please retry once.", 503
    return {"error": code, "message": message, "retryable": True}, status


HAS_LLM = _llm_configured()
GENERATOR_LABEL = (
    _active_generator_model() if HAS_LLM else "dataset-eval-gold (live generation unavailable)"
)

# ---------------------------------------------------------------------------
# Interface language support (UI internationalization)
# ---------------------------------------------------------------------------

def _resolve_interface_lang() -> str:
    """Resolve the interface language for the current request.

    Priority: URL ?lang= param > session interface_lang > cookie bhashacore-ui-lang / bhashacore-lang > Accept-Language header > en.
    Stores the result on flask.g for use by templates and endpoints.
    """
    if hasattr(g, "_interface_lang"):
        return g._interface_lang  # type: ignore[attr-defined]

    url_lang = request.args.get("lang")
    session_lang = session.get("interface_lang")
    cookie_lang = request.cookies.get("bhashacore-ui-lang") or request.cookies.get("bhashacore-lang")
    accept_language = request.headers.get("Accept-Language")

    lang = resolve_lang(url_lang, cookie_lang, accept_language, session_lang=session_lang)
    if url_lang and url_lang in get_available_languages():
        session["interface_lang"] = lang
        g._set_cookie_lang = lang
    elif cookie_lang and cookie_lang in get_available_languages() and session.get("interface_lang") != cookie_lang:
        session["interface_lang"] = cookie_lang

    g._interface_lang = lang  # type: ignore[attr-defined]
    return lang


@app.before_request
def _set_interface_lang():
    """Ensure interface language is resolved for every request."""
    _resolve_interface_lang()


# Jinja2 globals for template translation
app.jinja_env.globals["t"] = _t
app.jinja_env.globals["get_interface_lang"] = _resolve_interface_lang
app.jinja_env.globals["get_available_languages"] = get_available_languages
app.jinja_env.globals["get_language_name"] = get_language_name
app.jinja_env.globals["get_translations"] = get_translations
app.jinja_env.globals["get_all_translations"] = get_all_translations
app.jinja_env.globals["current_user"] = current_user


# ---------------------------------------------------------------------------
# Retrieval engine: lazy per-language BM25 index over the real corpus
# ---------------------------------------------------------------------------
_index_cache: dict = {}
_index_lock = Lock()
_eval_cache: dict = {}
_eval_lock = Lock()


def _pool_index(lang: str) -> PoolIndex:
    with _index_lock:
        if lang not in _index_cache:
            # Merge the base research pool with any ingested knowledge pool.
            # The ingestion pipeline writes new records to pool_{lang}_knowledge.jsonl,
            # but the base pool pool_{lang}.jsonl must always remain readable.
            pool_records = load_jsonl(proc_path(f"pool_{lang}"))
            knowledge_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
            if knowledge_file.exists():
                knowledge_records = load_jsonl(knowledge_file)
                # Deduplicate by pid, preferring knowledge records (newer)
                seen_pids = {r["pid"] for r in pool_records}
                for r in knowledge_records:
                    if r["pid"] not in seen_pids:
                        pool_records.append(r)
                        seen_pids.add(r["pid"])
            _index_cache[lang] = PoolIndex(pool_records)
        return _index_cache[lang]


def _evals(lang: str) -> list:
    with _eval_lock:
        if lang not in _eval_cache:
            _eval_cache[lang] = load_jsonl(proc_path(f"eval_{lang}"))
        return _eval_cache[lang]


def _question_norm(text: str) -> str:
    from src.metrics import _normalize

    return _normalize(text or "")


def _eval_tokens(text: str) -> set:
    return set(_question_norm(text).split())


def find_eval_match(lang: str, question: str, romanized: bool = False):
    """Exact or high token-overlap match against the real evaluation questions.

    Romanized input matches the dataset's ``romanized_question`` field so a
    Latin-script Indic question can still ground against its gold passage.
    """
    qn = _question_norm(question)
    if not qn:
        return None
    field = "romanized_question" if romanized else "question"
    evals = _evals(lang)
    for e in evals:
        if _question_norm(e.get(field, "")) == qn:
            return e
    qt = set(qn.split())
    if not qt:
        return None
    best, best_score = None, 0.0
    for e in evals:
        et = _eval_tokens(e.get(field, ""))
        if not et:
            continue
        overlap = len(qt & et) / max(len(qt), len(et))
        if overlap > best_score:
            best, best_score = e, overlap
    return best if best_score >= 0.8 else None


def retrieve(lang: str, question: str, top_k: int = TOP_K) -> list:
    """Real BM25 retrieval; returns ranked real passages from the corpus."""
    return retrieve_multi(lang, [question], top_k)


def retrieve_multi(lang: str, queries: list, top_k: int = TOP_K) -> list:
    """Multi-query retrieval: search the pool with each query variant and
    merge by best score (dual retrieval for romanized input).

    The paired experiment (scripts/eval_romanized_bridge.py, saved to
    results/summary/retrieval_romanized_bridge.csv) measured on the same
    eval questions: baseline 0.00-0.09 recall -> bridge 0.13-0.45, with
    the dual merge best overall — hence dual is wired for romanized input.
    """
    index = _pool_index(lang)
    best: dict = {}
    for q in queries:
        for pid, score in index.search(q, top_k):
            if score > best.get(pid, 0.0):
                best[pid] = score
    ranked = sorted(best.items(), key=lambda kv: -kv[1])[:top_k]
    citations = []
    for rank, (pid, score) in enumerate(ranked, start=1):
        rec = index.by_pid.get(pid, {})
        citations.append(
            {
                "rank": rank,
                "pid": pid,
                "score": round(float(score), 3),
                "source": rec.get("source", ""),
                "text": (rec.get("text") or "")[:600],
            }
        )
    return citations


INSUFFICIENT_NOTICE = (
    "The indexed research corpus does not contain sufficient information to answer "
    "this question reliably. Closest low-confidence matches are attached as "
    "references, but they were not used to generate an answer."
)

# A passage "genuinely supports" an answer when it contains (nearly) all of
# the answer's tokens. Below this threshold a passage that merely shares a
# common word (e.g. Telugu "bRndM"/troop in unrelated village passages) is
# NOT treated as support.
SUPPORT_THRESHOLD = 0.8


def _support(passage_text: str, answer: str) -> float:
    """Fraction of the answer's (script-aware) tokens present in the passage."""
    from src.metrics import _tokens

    ans_toks = set(_tokens(answer or ""))
    if not ans_toks:
        return 0.0
    pas_toks = set(_tokens(passage_text or ""))
    return len(ans_toks & pas_toks) / len(ans_toks)


def _run_async(coro, timeout: float = None):
    """Run an async coroutine in a new event loop with optional timeout."""
    import asyncio

    if timeout is not None:
        coro = asyncio.wait_for(coro, timeout=timeout)
    return asyncio.run(coro)


def _llm_answer(question: str, passages: list, answer_lang: str, answer_script: str) -> str:
    """Real generation through the NVIDIA NIM endpoint (requires key).

    The system prompt directs the ANSWER language and script independently of
    the question's language — this is where translation (meaning across
    languages) happens, performed by the LLM and attributed to it.

    Uses a bounded timeout so the app never hangs on a slow provider.
    """
    from src.generate import GROUNDING_CTX

    meta = LANGS[answer_lang]
    if answer_lang == "en" or answer_script == "latin":
        lang_directive = "Answer in English (Latin script)."
    elif answer_script == "romanized":
        lang_directive = f"Answer in {meta['name']} written in Latin script (romanized {meta['name']})."
    else:
        lang_directive = f"Answer in {meta['name']} (write in the {meta['script']} script)."
    system = (
        "You are BhashaCore, a helpful government-services assistant for Indian citizens. "
        f"{lang_directive} Be concise: at most 3 sentences. {GROUNDING_CTX}"
    )
    ctx = "\n\n".join(f"[{i + 1}] {p}" for i, p in enumerate(passages))
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Context passages:\n{ctx}\n\nQuestion: {question}"},
    ]
    return _live_provider_answer(messages)


def answer_question(
    lang: str,
    question: str,
    top_k: int = TOP_K,
    input_style: str = "auto",
    answer_lang: str = None,
    answer_script: str = "native",
    eval_mode: bool = False,
) -> dict:
    """Full honest multilingual RAG decision:

    resolve input style -> (dual) retrieval -> eval match -> ground -> answer
    in the requested language/script -> evidence-support marking.

    In normal chat mode (eval_mode=False), dataset gold answers are NEVER
    returned as model output. Live-provider failures are raised to the route,
    which returns a classified error rather than pretending an error is an
    assistant completion. Dataset gold answers are only used when
    eval_mode=True (evaluation/test scripts).

    Citation marking contract (regression-tested):
      * ``used`` is True only for passages that were actually supplied to the
        generator AND genuinely support the grounded answer textually
        (>= 80% of the answer's script-aware tokens appear in the passage),
        or for the gold passage of a matched evaluation question (the
        dataset-designated source of the answer).
      * Every citation carries a measured ``support`` score.
    """
    # --- input style + query variants -------------------------------------
    style = effective_input_style(question, lang, input_style)
    bridged_queries = []
    queries = [question]
    if style == "romanized" and lang in INDIC_LANGS:
        bridged_queries = bridge_variants(question, lang)
        strict_bridge = bridge_to_native(question, lang)
        queries = [question] + ([strict_bridge] if strict_bridge.strip() else [])

    citations = retrieve_multi(lang, queries, top_k)
    eval_match = None
    if style == "romanized":
        # First chance: match the typed romanization against the dataset's
        # own romanized questions; second chance: match bridged variants
        # (strict + casual-digraph) against the native-script questions.
        eval_match = find_eval_match(lang, question, romanized=True)
        if eval_match is None:
            for bq in bridged_queries:
                eval_match = find_eval_match(lang, bq)
                if eval_match is not None:
                    break
    else:
        eval_match = find_eval_match(lang, question)
    gold_pid = eval_match.get("gold_pid") if eval_match else None
    gold_rank = next((c["rank"] for c in citations if c["pid"] == gold_pid), None)

    context_pids: set = set()  # passages actually supplied to the generator
    model = GENERATOR_LABEL
    answer = ""
    answer_lang_eff = answer_lang or lang
    translation_note = None

    if gold_rank is not None:
        # The gold passage for a known evaluation question was retrieved:
        # grounded. Try live generation first.
        if HAS_LLM:
            try:
                # Feed the FULL passage text to the LLM (citations carry a
                # 600-char display copy; generation must use complete passages).
                index = _pool_index(lang)
                context_citations = citations[:gold_rank]
                full_texts = [index.by_pid[c["pid"]]["text"] for c in context_citations]
                answer = _llm_answer(question, full_texts, answer_lang_eff, answer_script)
                context_pids = {c["pid"] for c in context_citations}
                status = "answered"
            except Exception as exc:
                # Provider failure: report honestly, never fall back to dataset
                # gold in normal chat mode.
                if eval_mode:
                    answer = " | ".join(eval_match["answers"][:2])
                    context_pids = {gold_pid}
                    model = f"dataset-eval-gold (LLM unavailable: {str(exc)[:80]})"
                    status = "answered"
                    if answer_lang_eff != lang:
                        translation_note = (
                            f"Translation to {LANGS[answer_lang_eff]['name']} requires the "
                            "configured LLM, which is unavailable; the dataset's gold answer "
                            "is shown in its original language."
                        )
                else:
                    # A failed provider request is not an assistant answer.
                    # Let the route release a guest reservation and return a
                    # classified JSON error instead of streaming a fabricated
                    # fallback message as though it were model output.
                    raise
        else:
            # No LLM key configured at all.
            if eval_mode:
                answer = " | ".join(eval_match["answers"][:2])
                context_pids = {gold_pid}
                model = "dataset-eval-gold (no LLM key configured)"
                status = "answered"
                if answer_lang_eff != lang:
                    translation_note = (
                        f"Translation to {LANGS[answer_lang_eff]['name']} requires the "
                        "configured LLM, which is unavailable; the dataset's gold answer "
                        "is shown in its original language."
                    )
            else:
                raise ProviderGenerationError(
                    code="provider_not_configured", status_code=None, latency_ms=0,
                )
    else:
        # No known question, or its gold passage was not retrieved.
        if HAS_LLM and not eval_mode:
            # General knowledge question: answer from the model's own
            # knowledge, not corpus-grounded. No citations attached.
            from src.generate import GROUNDING_CTX

            meta = LANGS[answer_lang_eff]
            if answer_lang_eff == "en" or answer_script == "latin":
                lang_directive = "Answer in English (Latin script)."
            elif answer_script == "romanized":
                lang_directive = f"Answer in {meta['name']} written in Latin script (romanized {meta['name']})."
            else:
                lang_directive = f"Answer in {meta['name']} (write in the {meta['script']} script)."
            system = (
                "You are BhashaCore, a helpful government-services assistant for Indian citizens. "
                f"{lang_directive} Be concise: at most 3 sentences. Answer from your own knowledge; "
                "do not claim the answer comes from any document or corpus."
            )
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Question: {question}"},
            ]
            try:
                answer = _live_provider_answer(messages)
                model = f"{GENERATOR_LABEL} (model-only, no corpus grounding)"
                status = "answered"
                # Model-only answers: no citations are used or relevant.
                for c in citations:
                    c["used"] = False
            except Exception:
                # See the grounded branch above.  In particular, do not turn
                # an incomplete SSE response into a completed chat message.
                raise
        else:
            answer = INSUFFICIENT_NOTICE
            status = "insufficient_evidence"

    # --- output script conversion (deterministic transliteration) ----------
    # Transliteration converts scripts, never meaning; the grounded answer and
    # its romanized display are the same words in different scripts.
    display_answer = answer
    if (
        answer_script == "romanized"
        and status == "answered"
        and answer_lang_eff in INDIC_LANGS
    ):
        display_answer = romanize_output(answer, answer_lang_eff)

    # --- evidence-support marking (docstring contract above) ----------------
    index = _pool_index(lang)
    for c in citations:
        full_text = index.by_pid[c["pid"]]["text"]
        c["support"] = round(_support(full_text, answer if status == "answered" else ""), 2)
        was_supplied = c["pid"] in context_pids
        if status == "answered" and was_supplied:
            c["used"] = (c["support"] >= SUPPORT_THRESHOLD) or (c["pid"] == gold_pid)
        else:
            c["used"] = False

    return {
        "answer": display_answer,
        "status": status,
        "citations": citations,
        "model": model,
        "lang": lang,
        "gold_rank": gold_rank,
        "input_style": style,
        "bridged_query": bridged_queries[0] if bridged_queries else None,
        "bridged_queries": bridged_queries,
        "answer_lang": answer_lang_eff,
        "answer_script": answer_script,
        "translation_note": translation_note,
        "is_model_only": status == "answered" and gold_rank is None,
    }


# ---------------------------------------------------------------------------
# Chat session persistence
# ---------------------------------------------------------------------------
CHAT_DIR = ROOT / "chat_history"
CHAT_DIR.mkdir(parents=True, exist_ok=True)
_chat_states: dict = {}
_chat_lock = Lock()
STOP_EVENTS: dict = {}
_stop_lock = Lock()

# Session IDs are client-provided and also form part of a filename. Keep the
# accepted format deliberately small so persistence cannot escape CHAT_DIR.
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _valid_session_id(value) -> bool:
    return isinstance(value, str) and bool(_SESSION_ID_RE.fullmatch(value))


def _save_chat(sid: str):
    # Guests and unauthenticated sessions are never persisted to disk or database
    if current_user() is None and not current_app.config.get("TESTING"):
        return
    try:
        state = _chat_states.get(sid)
        if state is None:
            return
        payload = {"lang": state["lang"], "messages": state["messages"]}
        title = state.get("title")
        if not title:
            first_user_msg = next((m.get("content") for m in state.get("messages", []) if m.get("role") == "user" and m.get("content")), None)
            if first_user_msg:
                first_q = first_user_msg.strip()
                title = first_q[:45] + ("…" if len(first_q) > 45 else "")
        if title:
            payload["title"] = title
            state["title"] = title
        (CHAT_DIR / f"{sid}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def get_chat_state(sid: str) -> dict:
    with _chat_lock:
        if sid not in _chat_states:
            _chat_states[sid] = {
                "lang": "en",
                "messages": [{"role": "system", "content": "You are BhashaCore, a helpful assistant."}],
            }
        return _chat_states[sid]


def load_chat_state_from_disk(sid: str):
    try:
        path = CHAT_DIR / f"{sid}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def list_chat_histories() -> list:
    # Guests and unauthenticated sessions must never display persistent past conversation files
    if current_user() is None and not current_app.config.get("TESTING"):
        return []
    out = []
    # Sort newest first by last modified time
    for p in sorted(CHAT_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            msgs = data.get("messages", [])
            # Meaningful title from saved title or first user question
            title = (data.get("title") or "").strip()
            if not title:
                first_user_msg = next((m.get("content") for m in msgs if m.get("role") == "user" and m.get("content")), None)
                if first_user_msg and first_user_msg.strip():
                    first_q = first_user_msg.strip()
                    title = first_q[:45] + ("…" if len(first_q) > 45 else "")
                else:
                    # Skip empty session files without any user messages
                    continue
            out.append(
                {
                    "session_id": p.stem,
                    "title": title,
                    "lang": data.get("lang", "en"),
                    "message_count": len(msgs),
                    "created": p.stat().st_mtime,
                }
            )
        except Exception:
            continue
    return out


# ---------------------------------------------------------------------------
# Real research data loaders (dashboard / comparison / failures / examples)
# ---------------------------------------------------------------------------


def _read_summary_rows(gen_model: str = PRIMARY_GENERATOR) -> list:
    path = SUMMARY_DIR / "summary.csv"
    if not path.exists():
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["gen_model"] == gen_model:
                rows.append(r)
    return rows


def _read_retrieval_rows() -> list:
    path = SUMMARY_DIR / "retrieval.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_judge_rows(gen_model: str = PRIMARY_GENERATOR) -> list:
    rows = []
    model_dir = JUDGE_DIR / gen_model.replace("/", "__")
    if not model_dir.exists():
        return rows
    for path in sorted(model_dir.glob("*.jsonl")):
        mode = path.stem.split("_")[0] if "_" in path.stem else path.stem
        # mode is prefix up to language suffix; parse from each row instead
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                r["_file"] = path.stem
                rows.append(r)
    return rows


def _eval_question_map(lang: str) -> dict:
    return {e["qid"]: e["question"] for e in _evals(lang)}


def grounded_examples(max_per_lang: int = 3) -> dict:
    """Real evaluation questions whose gold passage BM25 retrieves (top-5)."""
    from src.config import ALL_LANGS

    examples = {}
    for lang in ALL_LANGS:
        try:
            ret = {r["qid"]: r for r in load_jsonl(proc_path(f"retrieval_{lang}"))}
            hits = [e for e in _evals(lang) if e["qid"] in ret and ret[e["qid"]]["hit"]]
            hits.sort(key=lambda e: len(e["question"]))
            examples[lang] = [
                {"question": e["question"], "answers": e["answers"][:2]}
                for e in hits[:max_per_lang]
            ]
        except Exception:
            examples[lang] = []
    return examples


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@app.post("/api/chat")
@limiter.limit("20 per hour")
@chat_access_required
def api_chat():
    """Ask a question; streams NDJSON events: meta, delta*, done|error.

    Multilingual controls (all optional; legacy `lang` still works):
      input_lang    : "auto" | en|hi|ta|te|kn|ml   (auto = script detection)
      input_style   : "auto" | "native" | "romanized"
      answer_lang   : en|hi|ta|te|kn|ml            (default: the input language)
      answer_script : "native" | "romanized" | "latin"
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object body required"}), 400
    raw_question = data.get("question")
    if raw_question is not None and not isinstance(raw_question, str):
        return jsonify({"error": "question must be a string"}), 400
    question = (raw_question or "").strip()
    mode = data.get("mode", "rag")
    supplied_sid = data.get("session_id")
    sid = str(uuid.uuid4()) if supplied_sid is None else supplied_sid
    input_lang = data.get("input_lang") or data.get("lang") or "auto"
    input_style = data.get("input_style", "auto")
    answer_lang = data.get("answer_lang") or None
    if answer_lang in ("auto", "", None):
        answer_lang = None
    answer_script = data.get("answer_script", "native")
    eval_mode = data.get("eval_mode", False)

    if not question:
        return jsonify({"error": "question is required"}), 400
    if len(question) > 2000:
        return jsonify({"error": "question too long (max 2000 chars)"}), 400
    if not _valid_session_id(sid):
        return jsonify({"error": "invalid session_id"}), 400
    if not isinstance(eval_mode, bool):
        return jsonify({"error": "eval_mode must be a boolean"}), 400
    if input_style not in ("auto", "native", "romanized"):
        return jsonify({"error": f"unsupported input_style: {input_style}"}), 400
    if answer_script not in ("native", "romanized", "latin"):
        return jsonify({"error": f"unsupported answer_script: {answer_script}"}), 400
    if answer_lang is not None and answer_lang not in LANGS:
        return jsonify({"error": f"unsupported answer language: {answer_lang}"}), 400
    if mode not in MODES:
        return jsonify({"error": f"unsupported mode: {mode}"}), 400

    # Resolve the input language. Latin-script input is inherently ambiguous
    # (English vs romanized Indic): auto-detection tries to detect romanized
    # Indic via eval-set matching; if that fails, it defaults to English and
    # flags the ambiguity; explicit selection removes the ambiguity.
    detection = detect_script_and_language(question)
    input_ambiguous = False
    if input_lang == "auto":
        if detection["lang"] is None:
            # Latin script (or mixed): could be English or romanized Indic.
            # Try to detect romanized Indic via eval-set matching.
            detected_lang = _detect_romanized_language(question)
            if detected_lang is not None:
                input_lang = detected_lang
            else:
                # Fall back to English but flag as ambiguous so the UI can warn.
                input_lang = "en"
                input_ambiguous = True
        else:
            input_lang = detection["lang"]
    elif input_lang not in LANGS:
        return jsonify({"error": f"unsupported language: {input_lang}"}), 400

    lang = input_lang  # retrieval pool + eval corpus follow the input language
    if answer_lang is None:
        answer_lang = lang

    # Authenticated chats are persisted in the database and scoped to their
    # owner. Guest sessions enforce a 3-message trial limit and remain in memory.
    user = current_user()
    guest_request_key = None
    cached_guest_result = None
    guest_conversation_data = None
    if user:
        conversation = get_owned_conversation(user, sid)
        if conversation is None:
            existing = db.session.get(Conversation, sid)
            if existing is not None:
                return jsonify({"error": "conversation not found"}), 404
            conversation = Conversation(id=sid, user_id=user.id, title=question[:240])
            db.session.add(conversation)
        elif conversation.title in ("New chat", "New conversation"):
            conversation.title = question[:240]
        db.session.add(Message(conversation_id=sid, role="user", content=question))
        db.session.commit()
        guest_sess = None
    else:
        # A database row lock makes the three-response trial safe across tabs
        # and Gunicorn workers. The reservation itself is not a consumed slot.
        request_fingerprint = json.dumps({
            "session_id": sid, "question": question, "input_lang": input_lang,
            "input_style": input_style, "answer_lang": answer_lang,
            "answer_script": answer_script, "mode": mode,
        }, sort_keys=True, ensure_ascii=False)
        guest_request_key = hashlib.sha256(request_fingerprint.encode("utf-8")).hexdigest()
        guest_sess, reservation, cached = reserve_guest_response(session, guest_request_key)
        if reservation == "quota":
            return jsonify({
                "error": "guest_quota_exceeded",
                "message": "You have reached the 3-question trial limit. Please sign in or create an account to continue chatting.",
                "guest_message_count": guest_sess.message_count,
                "guest_limit": 3,
                "guest_quota_reached": True,
            }), 403
        if reservation == "in_progress":
            return jsonify({"error": "duplicate_request_in_progress"}), 409
        if reservation == "completed":
            cached_guest_result = (cached or {}).get("result")

    # Generate the grounded answer first to verify success before committing quota usage
    try:
        result = cached_guest_result or answer_question(
            lang, question, input_style=input_style, answer_lang=answer_lang,
            answer_script=answer_script, eval_mode=eval_mode,
        )
    except Exception as exc:
        if user is None and guest_request_key:
            release_guest_response(guest_sess.id, guest_request_key)
        payload, status = _public_provider_error(exc)
        current_app.logger.exception(
            "chat generation failed code=%s provider_status=%s latency_ms=%s",
            payload["error"], getattr(exc, "status_code", None), getattr(exc, "latency_ms", None),
        )
        return jsonify(payload), status

    # Only completed assistant answers consume a trial slot. Provider errors
    # and timeouts release their reservation and never appear in guest history.
    if user is None:
        successful = result.get("status") in ("answered", "insufficient_evidence")
        if successful and cached_guest_result is None:
            guest_conversation_data = {
                "session_id": sid,
                "title": (question[:40] + ("…" if len(question) > 40 else "")).strip(),
                "created": time.time(),
                "updated": time.time(),
                "lang": lang,
                "messages": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": result["answer"],
                     "status": result["status"], "citations": result.get("citations", [])},
                ],
            }
            guest_count_now = complete_guest_response(
                guest_sess.id, guest_request_key, guest_conversation_data, result
            )
            session["guest_message_count"] = guest_count_now
            session.modified = True
        elif cached_guest_result is not None:
            guest_count_now = guest_sess.message_count
        else:
            guest_count_now = release_guest_response(guest_sess.id, guest_request_key)
    else:
        guest_count_now = None

    state = get_chat_state(sid)
    state["lang"] = lang
    with _stop_lock:
        if sid in STOP_EVENTS:
            STOP_EVENTS[sid].set()
        STOP_EVENTS[sid] = Event()
    stop_event = STOP_EVENTS[sid]

    state["messages"].append({"role": "user", "content": question})
    is_testing = bool(current_app.config.get("TESTING", False))
    # Persist immediately only in test harness for pytest assertions; never for guest visitors
    if not user and is_testing:
        _save_chat(sid)

    # WSGI consumes this generator after the request context is gone.  It does
    # not need request/session data at that point, but it does need an
    # application context for the final SQLAlchemy commit.
    stream_app = current_app._get_current_object()

    def generate():
        t0 = time.time()
        yield json.dumps(
            {
                "type": "meta",
                "session_id": sid,
                "lang": lang,
                "input_lang": lang,
                "input_style": input_style,
                "answer_lang": answer_lang,
                "answer_script": answer_script,
                "mode": mode,
                "model": GENERATOR_LABEL,
                "guest_message_count": guest_count_now,
                "guest_limit": 3 if user is None else None,
                "guest_quota_reached": (guest_count_now is not None and guest_count_now >= 3),
            },
            ensure_ascii=False,
        ) + "\n"
        try:
            if stop_event.is_set():
                yield json.dumps({"type": "done", "answer": "", "status": "stopped", "citations": [], "model": result["model"], "latency_ms": int((time.time() - t0) * 1000), "guest_message_count": guest_count_now}, ensure_ascii=False) + "\n"
                return
            # stream the answer progressively in a few chunks
            text = result["answer"]
            step = max(1, len(text) // 6)
            for i in range(0, len(text), step):
                if stop_event.is_set():
                    break
                yield json.dumps({"type": "delta", "text": text[i : i + step]}, ensure_ascii=False) + "\n"
            if stop_event.is_set():
                yield json.dumps({"type": "done", "answer": "", "status": "stopped", "citations": [], "model": result["model"], "latency_ms": int((time.time() - t0) * 1000), "guest_message_count": guest_count_now}, ensure_ascii=False) + "\n"
                return
            event = {
                "type": "done",
                "answer": text,
                "status": result["status"],
                "citations": result["citations"],
                "model": result["model"],
                "gold_rank": result["gold_rank"],
                "latency_ms": int((time.time() - t0) * 1000),
                # language-processing metadata (UI shows it on demand)
                "input_lang": lang,
                "input_style": result["input_style"],
                "input_detected_script": detection["script"],
                "input_ambiguous": input_ambiguous,
                "bridged_query": result["bridged_query"],
                "answer_lang": result["answer_lang"],
                "answer_script": result["answer_script"],
                "translation_note": result["translation_note"],
                "is_model_only": result.get("is_model_only", False),
                "guest_message_count": guest_count_now,
                "guest_limit": 3 if user is None else None,
                "guest_quota_reached": (guest_count_now is not None and guest_count_now >= 3),
            }
            yield json.dumps(event, ensure_ascii=False) + "\n"
            state["messages"].append({"role": "assistant", "content": text, "status": result["status"]})
            if not user and is_testing:
                _save_chat(sid)
            if user:
                with stream_app.app_context():
                    db.session.add(Message(conversation_id=sid, role="assistant", content=text,
                                           metadata_json=json.dumps({"status": result["status"]})))
                    db.session.commit()
        except Exception as exc:
            stream_app.logger.exception("chat stream failed")
            payload, _ = _public_provider_error(exc)
            yield json.dumps({"type": "error", **payload}, ensure_ascii=False) + "\n"

    resp = Response(generate(), mimetype="application/x-ndjson")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp


@app.post("/api/stop")
@chat_access_required
def api_stop():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object body required"}), 400
    sid = data.get("session_id", "")
    if not _valid_session_id(sid):
        return jsonify({"error": "invalid session_id"}), 400
    with _stop_lock:
        ev = STOP_EVENTS.get(sid)
        if ev:
            ev.set()
    return jsonify({"status": "stopped"})


@app.post("/api/new-chat")
@chat_access_required
def api_new_chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object body required"}), 400
    supplied_sid = data.get("session_id")
    sid = str(uuid.uuid4()) if supplied_sid is None else supplied_sid
    if not _valid_session_id(sid):
        return jsonify({"error": "invalid session_id"}), 400
    user = current_user()
    if user:
        # Check if user already has an unused "New chat" with 0 messages:
        # reuse it to avoid duplicate empty chats
        empty_conv = db.session.scalar(
            db.select(Conversation)
            .where(Conversation.user_id == user.id, Conversation.title.in_(("New chat", "New conversation")))
            .filter(~Conversation.messages.any())
            .order_by(Conversation.created_at.desc())
        )
        if empty_conv and supplied_sid is None:
            sid = empty_conv.id
        else:
            conversation = get_owned_conversation(user, sid)
            if conversation is None:
                if db.session.get(Conversation, sid) is not None:
                    sid = str(uuid.uuid4())
                conversation = Conversation(id=sid, user_id=user.id, title="New chat")
                db.session.add(conversation)
                db.session.commit()
    else:
        guest_sess = get_or_create_guest_session(session)
        if guest_sess:
            try:
                d = json.loads(guest_sess.data_json or "{}")
                d["active_session_id"] = sid
                guest_sess.data_json = json.dumps(d)
                db.session.commit()
            except Exception:
                db.session.rollback()
    with _chat_lock:
        _chat_states[sid] = {
            "lang": "en",
            "messages": [{"role": "system", "content": "You are BhashaCore, a helpful assistant."}],
        }
        if user is None and current_app.config.get("TESTING"):
            _save_chat(sid)
    with _stop_lock:
        ev = STOP_EVENTS.pop(sid, None)
        if ev:
            ev.set()
    return jsonify({"status": "new_chat", "session_id": sid})


@app.get("/api/guest-status")
def api_guest_status():
    user = current_user()
    if user:
        return jsonify({
            "authenticated": True,
            "guest_message_count": 0,
            "guest_limit": 3,
            "guest_remaining": None,
            "guest_quota_reached": False,
        })
    guest_sess = get_or_create_guest_session(session)
    count = guest_sess.message_count
    return jsonify({
        "authenticated": False,
        "guest_message_count": count,
        "guest_limit": 3,
        "guest_remaining": max(0, 3 - count),
        "guest_quota_reached": count >= 3,
    })


@app.post("/api/guest-reset")
def api_guest_reset():
    guest_id = session.get("guest_id")
    if guest_id:
        guest_sess = db.session.get(GuestSession, guest_id)
        if guest_sess:
            try:
                db.session.delete(guest_sess)
                db.session.commit()
            except Exception:
                db.session.rollback()
    session.pop("guest_id", None)
    session.pop("guest_message_count", None)
    session.pop("last_guest_q", None)
    session.modified = True
    return jsonify({"status": "ok", "guest_message_count": 0})


@app.get("/api/history")
@chat_access_required
def api_history():
    user = current_user()
    if user:
        conversations = db.session.scalars(db.select(Conversation).where(Conversation.user_id == user.id)
            .order_by(Conversation.updated_at.desc())).all()
        return jsonify({"histories": [{"session_id": c.id, "title": c.title, "created": c.updated_at.timestamp()}
                                       for c in conversations]})

    # Return temporary guest conversations
    guest_sess = get_or_create_guest_session(session)
    if guest_sess and guest_sess.data_json:
        try:
            d = json.loads(guest_sess.data_json)
            convs = list(d.get("conversations", {}).values())
            convs.sort(key=lambda x: x.get("updated", 0), reverse=True)
            return jsonify({"histories": [
                {
                    "session_id": c["session_id"],
                    "title": c["title"],
                    "created": c.get("created", c.get("updated", time.time())),
                }
                for c in convs
            ]})
        except Exception:
            pass

    if current_app.config.get("TESTING"):
        return jsonify({"histories": list_chat_histories()})
    return jsonify({"histories": []})


@app.patch("/api/conversations/<conversation_id>")
def rename_conversation(conversation_id):
    data = request.get_json(silent=True)
    title = data.get("title", "").strip() if isinstance(data, dict) else ""
    if not 1 <= len(title) <= 240:
        return jsonify({"error": "title must be between 1 and 240 characters"}), 400
    user = current_user()
    if user:
        conversation = get_owned_conversation(user, conversation_id)
        if conversation:
            conversation.title = title
            db.session.commit()
            return jsonify({"id": conversation.id, "title": conversation.title})
        return jsonify({"error": "conversation not found"}), 404

    # Guest rename
    guest_sess = get_or_create_guest_session(session)
    if guest_sess and guest_sess.data_json:
        try:
            d = json.loads(guest_sess.data_json)
            if conversation_id in d.get("conversations", {}):
                d["conversations"][conversation_id]["title"] = title
                guest_sess.data_json = json.dumps(d)
                db.session.commit()
                return jsonify({"id": conversation_id, "title": title})
        except Exception:
            db.session.rollback()

    return jsonify({"error": "conversation not found"}), 404


@app.delete("/api/conversations/<conversation_id>")
def delete_conversation(conversation_id):
    user = current_user()
    deleted = False
    if user:
        conversation = get_owned_conversation(user, conversation_id)
        if conversation:
            db.session.delete(conversation)
            db.session.commit()
            deleted = True
    else:
        # Guest delete
        guest_sess = get_or_create_guest_session(session)
        if guest_sess and guest_sess.data_json:
            try:
                d = json.loads(guest_sess.data_json)
                if conversation_id in d.get("conversations", {}):
                    d["conversations"].pop(conversation_id, None)
                    guest_sess.data_json = json.dumps(d)
                    db.session.commit()
                    deleted = True
            except Exception:
                db.session.rollback()

    if not deleted:
        return jsonify({"error": "conversation not found"}), 404
    with _chat_lock:
        _chat_states.pop(conversation_id, None)
    return jsonify({"status": "deleted"})


@app.post("/api/load-chat")
@chat_access_required
def api_load_chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object body required"}), 400
    sid = data.get("session_id", "")
    if not _valid_session_id(sid):
        return jsonify({"error": "invalid session_id"}), 400
    user = current_user()
    if user:
        conversation = get_owned_conversation(user, sid)
        if conversation is None:
            return jsonify({"status": "not_found"}), 404
        messages = []
        for m in conversation.messages:
            meta = {}
            if m.metadata_json:
                try:
                    meta = json.loads(m.metadata_json)
                except Exception:
                    pass
            messages.append({
                "role": m.role,
                "content": m.content,
                "status": meta.get("status"),
                "citations": meta.get("citations", []),
            })
        loaded = {"session_id": sid, "title": conversation.title, "lang": "en", "messages": messages}
        return jsonify({"status": "loaded", "session": loaded})

    # Guest session load
    guest_sess = get_or_create_guest_session(session)
    if guest_sess and guest_sess.data_json:
        try:
            d = json.loads(guest_sess.data_json)
            conv = d.get("conversations", {}).get(sid)
            if conv:
                loaded = {
                    "session_id": sid,
                    "title": conv.get("title", "New chat"),
                    "lang": conv.get("lang", "en"),
                    "messages": conv.get("messages", []),
                }
                return jsonify({"status": "loaded", "session": loaded})
        except Exception:
            pass

    if current_app.config.get("TESTING"):
        loaded = load_chat_state_from_disk(sid)
        if loaded:
            with _chat_lock:
                _chat_states[sid] = {
                    "lang": loaded.get("lang", "en"),
                    "messages": loaded.get("messages", []),
                }
            return jsonify({"status": "loaded", "session": loaded})
    return jsonify({"status": "not_found"}), 404


@app.get("/api/languages")
def api_languages():
    return jsonify({"languages": LANGS})


@app.get("/api/modes")
def api_modes():
    return jsonify({"modes": MODES, "generator": GENERATOR_LABEL})


@app.get("/api/examples")
def api_examples():
    return jsonify({"examples": grounded_examples()})


@app.get("/api/dashboard")
def api_dashboard():
    summary = _read_summary_rows()
    retrieval = _read_retrieval_rows()
    judge_rows = _read_judge_rows()
    judged = [r for r in judge_rows if r.get("correctness") is not None]
    failures = [r for r in judged if r["correctness"] <= 3]
    by_lang = {}
    for r in summary:
        by_lang.setdefault(r["lang"], {})[r["mode"]] = {
            "n": int(r["n"]),
            "correctness": round(float(r["correctness"]), 2) if r["correctness"] else None,
            "faithfulness": round(float(r["faithfulness"]), 2) if r["faithfulness"] else None,
            "purity": round(float(r["purity"]), 3) if r["purity"] else None,
            "in_lang_rate": round(float(r["in_lang_rate"]), 2) if r["in_lang_rate"] else None,
            "f1": round(float(r["f1"]), 3) if r["f1"] else None,
            "em": round(float(r["em"]), 3) if r["em"] else None,
        }
    return jsonify(
        {
            "generator": PRIMARY_GENERATOR,
            "generator_active": GENERATOR_LABEL,
            "judge_model": next((r.get("judge_model") for r in judge_rows if r.get("judge_model")), None),
            "counts": {
                "judged": len(judged),
                "failures": len(failures),
                "languages": len(by_lang),
                "retrieval_rows": len(retrieval),
            },
            "by_language": by_lang,
            "retrieval": retrieval,
        }
    )


@app.get("/api/comparison")
def api_comparison():
    summary = _read_summary_rows()
    retrieval = _read_retrieval_rows()
    langs = []
    for code, meta in LANGS.items():
        rows = [r for r in summary if r["lang"] == code]
        by_mode = {r["mode"]: r for r in rows}

        def corr(mode):
            r = by_mode.get(mode)
            return round(float(r["correctness"]), 2) if r and r["correctness"] else None

        ret_native = next((r for r in retrieval if r["lang"] == code and r["mode"] == "rag"), None)
        ret_roman = next((r for r in retrieval if r["lang"] == code and r["mode"] == "rag_translit"), None)
        langs.append(
            {
                "lang": code,
                "name": meta["name"],
                "script": meta["script"],
                "closed_book": corr("closed_book"),
                "gold_context": corr("gold_context"),
                "rag": corr("rag"),
                "rag_translit": corr("rag_translit"),
                "recall_native": round(float(ret_native["recall@5"]), 2) if ret_native else None,
                "recall_romanized": round(float(ret_roman["recall@5"]), 2) if ret_roman else None,
            }
        )
    return jsonify({"languages": langs, "generator": PRIMARY_GENERATOR})


@app.get("/api/failures")
def api_failures():
    lang = request.args.get("lang")
    mode = request.args.get("mode")
    try:
        limit = int(request.args.get("limit", 50))
    except (TypeError, ValueError):
        return jsonify({"error": "limit must be an integer between 1 and 200"}), 400
    if not 1 <= limit <= 200:
        return jsonify({"error": "limit must be an integer between 1 and 200"}), 400
    judge_rows = _read_judge_rows()
    qmaps = {code: _eval_question_map(code) for code in LANGS}
    out = []
    for r in judge_rows:
        if r.get("correctness") is None or r["correctness"] > 3:
            continue
        if lang and r.get("lang") != lang:
            continue
        if mode and r.get("mode") != mode:
            continue
        q = qmaps.get(r.get("lang"), {}).get(r.get("qid"), "")
        out.append(
            {
                "qid": r.get("qid"),
                "lang": r.get("lang"),
                "mode": r.get("mode"),
                "correctness": r.get("correctness"),
                "faithfulness": r.get("faithfulness"),
                "issues": r.get("issues", []),
                "retrieved_hit": r.get("retrieved_hit"),
                "purity": r.get("purity"),
                "question": q,
                "gloss_question": r.get("gloss_question", ""),
                "gloss_reference": r.get("gloss_reference", ""),
                "answer": (r.get("answer") or "")[:300],
                "gloss_answer": (r.get("gloss_answer") or "")[:300],
            }
        )
    out.sort(key=lambda r: (r["correctness"] or 0))
    return jsonify({"failures": out[:limit], "total_matching": len(out)})


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@app.get("/welcome")
@app.get("/landing")
@app.get("/home")
def welcome():
    return render_template(
        "landing.html",
        languages=LANGS,
        modes=MODES,
        generator=GENERATOR_LABEL,
        examples=_example_questions(),
        authenticated=bool(current_user()),
    )


@app.route("/signup", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def signup():
    if current_user():
        return redirect(url_for("authenticated_chat"))
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        consent = request.form.get("consent")
        if password != confirm:
            flash("Passwords do not match.", "error")
        elif not consent:
            flash("Please accept the terms and privacy notice.", "error")
        else:
            created, error = create_user(name, email, password)
            if created:
                user = authenticate(email, password)
                session.clear()
                session["user_id"] = user.id
                flash("Your account is ready.", "success")
                return redirect(url_for("authenticated_chat"))
            flash(error, "error")
    return render_template("auth.html", form="signup")


@app.route("/signin", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def signin():
    if current_user():
        return redirect(url_for("authenticated_chat"))
    if request.method == "POST":
        user = authenticate(request.form.get("email", ""), request.form.get("password", ""))
        if user:
            session.clear()
            session["user_id"] = user.id
            target = request.args.get("next")
            if not target or not target.startswith("/") or target.startswith("//"):
                target = url_for("authenticated_chat")
            return redirect(target)
        flash("Invalid email or password.", "error")
    return render_template("auth.html", form="signin")


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("welcome"))


@app.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        token = create_reset_token(request.form.get("email", ""))
        # Delivery is intentionally decoupled: never disclose account presence.
        # A configured mail provider must consume this token to send the link.
        if token:
            try:
                send_password_reset(request.form.get("email", ""), token)
            except Exception:
                app.logger.warning("Password reset email delivery failed")
        flash("If that address has an account, a reset link will be sent.", "success")
        return redirect(url_for("signin"))
    return render_template("password_reset.html", mode="request")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_route(token):
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if password != confirm:
            flash("Passwords do not match.", "error")
        else:
            changed, error = reset_password(token, password)
            if changed:
                flash("Password changed. Please sign in.", "success")
                return redirect(url_for("signin"))
            flash(error, "error")
    return render_template("password_reset.html", mode="reset")


REACT_DIST = ROOT / "frontend" / "dist"


def _serve_spa_or_template(template_name, **context):
    if current_app.config.get("TESTING"):
        return render_template(template_name, **context)
    if request.args.get("legacy") == "1" or request.headers.get("X-Legacy-Template") == "1":
        return render_template(template_name, **context)
    if (REACT_DIST / "index.html").exists():
        html_content = (REACT_DIST / "index.html").read_text(encoding="utf-8")
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()
        html_content = html_content.replace(
            '<meta name="csrf-token" content="" />',
            f'<meta name="csrf-token" content="{token}" />'
        )
        response = Response(html_content, mimetype="text/html")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    return render_template(template_name, **context)


@app.route("/assets/<path:filename>")
def serve_react_assets(filename):
    return send_from_directory(REACT_DIST / "assets", filename)


@app.get("/api/csrf-token")
def api_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify({"csrf_token": generate_csrf()})


@app.get("/api/auth/me")
def api_auth_me():
    user = current_user()
    if user:
        return jsonify({"authenticated": True, "user": {"id": user.id, "name": user.name, "email": user.email}})
    return jsonify({"authenticated": False, "user": None})


@app.post("/api/auth/signin")
@limiter.limit("10 per hour")
def api_auth_signin():
    data = request.get_json(silent=True) or request.form
    email = data.get("email", "")
    password = data.get("password", "")
    user = authenticate(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401
    session.clear()
    session["user_id"] = user.id
    return jsonify({"status": "ok", "user": {"id": user.id, "name": user.name, "email": user.email}})


@app.post("/api/auth/signup")
@limiter.limit("5 per hour")
def api_auth_signup():
    data = request.get_json(silent=True) or request.form
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    ok, err = create_user(name, email, password)
    if not ok:
        return jsonify({"error": err}), 400
    user = authenticate(email, password)
    session.clear()
    session["user_id"] = user.id
    return jsonify({"status": "ok", "user": {"id": user.id, "name": user.name, "email": user.email}})


@app.post("/api/auth/logout")
def api_auth_logout():
    session.clear()
    return jsonify({"status": "ok"})


@app.get("/chat")
def authenticated_chat():
    if not app.config.get("ALLOW_ANONYMOUS_CHAT") and current_user() is None:
        return redirect(url_for("signin", next=request.path))
    return _serve_spa_or_template(
        "chat.html",
        languages=LANGS,
        modes=MODES,
        generator=GENERATOR_LABEL,
        examples=_example_questions(),
        authenticated=bool(current_user()),
    )


chat = authenticated_chat


@app.get("/settings")
@login_required
def settings():
    return render_template("settings.html", user=current_user())


@app.post("/settings/delete-account")
@login_required
@limiter.limit("3 per hour")
def delete_account():
    if delete_user(current_user(), request.form.get("password", "")):
        session.clear()
        flash("Your account and its conversations were deleted.", "success")
        return redirect(url_for("welcome"))
    flash("Password confirmation failed.", "error")
    return redirect(url_for("settings"))


def _example_questions():
    try:
        return grounded_examples()
    except Exception:
        return {}


@app.get("/")
def index():
    return _serve_spa_or_template(
        "landing.html",
        languages=LANGS,
        modes=MODES,
        generator=GENERATOR_LABEL,
        examples=_example_questions(),
        authenticated=bool(current_user()),
    )


@app.get("/dashboard")
def dashboard():
    return _serve_spa_or_template("dashboard.html", generator=GENERATOR_LABEL)


@app.get("/language-comparison")
def language_comparison():
    return _serve_spa_or_template("language_comparison.html", languages=LANGS, generator=GENERATOR_LABEL)


@app.get("/failure-analysis")
def failure_analysis():
    return _serve_spa_or_template("failure_analysis.html", languages=LANGS, generator=GENERATOR_LABEL)


@app.get("/about")
def about():
    return _serve_spa_or_template("about.html", generator=GENERATOR_LABEL, has_llm=HAS_LLM)


@app.get("/api/interface-lang")
def api_interface_lang():
    """Return available interface languages and the current selection."""
    lang = _resolve_interface_lang()
    return jsonify(
        {
            "current": lang,
            "current_name": get_language_name(lang),
            "available": get_available_languages(lang),
        }
    )


@app.get("/api/translations")
def api_translations():
    """Return translation dictionary for the requested or current interface language."""
    lang = request.args.get("lang") or _resolve_interface_lang()
    available = get_available_languages(lang)
    if lang not in available:
        lang = "en"
    return jsonify(
        {
            "lang": lang,
            "lang_name": get_language_name(lang, lang),
            "available": available,
            "translations": get_translations(lang),
        }
    )


@app.get("/api/translations/all")
def api_translations_all():
    """Return all translation catalogs across all 6 languages for zero-latency client switching."""
    from src.translations import LANGUAGE_NAMES_BY_INTERFACE
    return jsonify(
        {
            "languages": LANGUAGE_NAMES_BY_INTERFACE,
            "catalogs": get_all_translations(),
        }
    )



@app.post("/api/set-interface-lang")
def api_set_interface_lang():
    """Set the interface language cookie and session."""
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        lang = data.get("lang", "en")
    else:
        lang = request.form.get("lang", "en")

    available = get_available_languages()
    if lang not in available:
        return jsonify({"error": f"unsupported language: {lang}"}), 400

    session["interface_lang"] = lang
    g._interface_lang = lang

    resp = jsonify({"status": "ok", "lang": lang, "lang_name": get_language_name(lang)})
    resp.set_cookie("bhashacore-ui-lang", lang, max_age=365 * 24 * 3600, path="/", samesite="Lax")
    resp.set_cookie("bhashacore-lang", lang, max_age=365 * 24 * 3600, path="/", samesite="Lax")
    return resp


@app.get("/set-lang/<lang>")
def set_lang_route(lang):
    """Direct GET route to switch interface language and redirect back."""
    available = get_available_languages()
    if lang not in available:
        lang = "en"

    session["interface_lang"] = lang
    g._interface_lang = lang

    referrer = request.referrer
    if not referrer or not referrer.startswith(request.host_url):
        target = url_for("index")
    else:
        from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
        parsed = urlparse(referrer)
        qs = parse_qs(parsed.query)
        qs.pop("lang", None)
        new_query = urlencode(qs, doseq=True)
        target = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)) or url_for("index")

    resp = redirect(target)
    resp.set_cookie("bhashacore-ui-lang", lang, max_age=365 * 24 * 3600, path="/", samesite="Lax")
    resp.set_cookie("bhashacore-lang", lang, max_age=365 * 24 * 3600, path="/", samesite="Lax")
    return resp


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    indexed = {}
    for code in LANGS:
        try:
            indexed[code] = len(_pool_index(code).records)
        except Exception:
            indexed[code] = None
    # Fail readiness when persistence is unavailable.  This is intentionally
    # a small bounded query; it catches a bad deployment URL before users see
    # failures in sign-in, history or guest session creation.
    db.session.execute(db.text("SELECT 1"))
    return jsonify({
        "status": "ok",
        "generator": GENERATOR_LABEL,
        "llm_configured": HAS_LLM,
        "retrieval_pools": indexed,
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BhashaCore web app")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    # Warm the BM25 indexes so the first question is not slow.
    for code in LANGS:
        try:
            _pool_index(code)
        except Exception as exc:
            print(f"[warn] could not index pool for {code}: {exc}")
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)
