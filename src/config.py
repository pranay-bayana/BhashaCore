"""Central configuration for the BhashaCore evaluation pipeline."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
RESULTS_DIR = ROOT / "results"
GEN_DIR = RESULTS_DIR / "gen"
JUDGE_DIR = RESULTS_DIR / "judge"
SUMMARY_DIR = RESULTS_DIR / "summary"
REPORT_DIR = ROOT / "report"
FIGURES_DIR = REPORT_DIR / "figures"

for _d in (RAW_DIR, PROC_DIR, GEN_DIR, JUDGE_DIR, SUMMARY_DIR, REPORT_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- languages
LANGS = {
    "en": {"name": "English", "script": "Latin", "indiccorp_split": None},
    "hi": {"name": "Hindi", "script": "Devanagari", "indiccorp_split": "hin_Deva"},
    "ta": {"name": "Tamil", "script": "Tamil", "indiccorp_split": "tam_Taml"},
    "te": {"name": "Telugu", "script": "Telugu", "indiccorp_split": "tel_Telu"},
    "kn": {"name": "Kannada", "script": "Kannada", "indiccorp_split": "kan_Knda"},
    "ml": {"name": "Malayalam", "script": "Malayalam", "indiccorp_split": "mal_Mlym"},
}
INDIC_LANGS = ["hi", "ta", "te", "kn", "ml"]
ALL_LANGS = ["en"] + INDIC_LANGS

# ---------------------------------------------------------------- experiment parameters
SEED = 42
N_EVAL = 100            # eval questions per language available in data
RUN_LIMIT = {"en": 50, "hi": 50, "ta": 50, "te": 50, "kn": 50, "ml": 50}  # per-language questions per language actually run (quota-aware); first-N slice, identical across modes within a language
N_DISTRACTORS = 3000    # IndicCorp passages added to each retrieval pool
TOP_K = 5               # passages retrieved for RAG modes
MAX_OUT_TOKENS = int(os.environ.get("BHASHACORE_MAX_TOKENS", "1024"))
CONCURRENCY = 3         # parallel API calls (in-flight cap)
LAUNCH_PACE = 8.0       # seconds between request launches (429 avoidance)
RATE_LIMIT_SLEEP = 20.0  # per-attempt sleep after HTTP 429
COOLDOWN_ON_429 = 45.0   # global pause for all launches of this client after a 429
TIMEOUT_CONNECT = 15.0
TIMEOUT_READ = 300.0    # cold-start gate on some NIM models is ~130s
MAX_RETRIES = 8

# Bounded timeout for live LLM calls in the chat app (seconds).
# The NVIDIA NIM endpoint may cold-start slowly but must not block indefinitely.
# Set via BHASHACORE_LLM_TIMEOUT env; default 300s to match internal client timeout.
LLM_CALL_TIMEOUT = float(os.environ.get("BHASHACORE_LLM_TIMEOUT", "300.0"))

MODES = ["closed_book", "gold_context", "rag", "rag_translit"]
# rag_translit (Romanized query stress test) runs for Indic languages only.

# ---------------------------------------------------------------- models (NVIDIA NIM)
# Same generator across all languages -> quality gaps are attributable to language.
# Measured endpoint behaviour: glm-5.3-flash serializes at ~100-280s/call (used only
# for the flagship subset); minimax-m3.1-flash answers in 1-4s under 8-way concurrency.
PRIMARY_GENERATOR = "minimaxai/minimax-m3.1-flash"
SECONDARY_GENERATORS = ["z-ai/glm-5.3-flash"]  # flagship robustness subset (n=25/lang)
JUDGE_MODEL = "meta/muse-glimmer-30b"   # fast, Hindi+Tamil capable, different family
                                                # from both generators (probed 2026-10-25)


def gen_results_path(model: str, mode: str, lang: str) -> Path:
    safe = model.replace("/", "__")
    return GEN_DIR / safe / f"{mode}_{lang}.jsonl"


def judge_results_path(model: str, mode: str, lang: str) -> Path:
    safe = model.replace("/", "__")
    return JUDGE_DIR / safe / f"{mode}_{lang}.jsonl"


def proc_path(name: str) -> Path:
    return PROC_DIR / f"{name}.jsonl"
