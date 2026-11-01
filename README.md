# BhashaCore — Language-Agnostic Chatbot Evaluation

**Question:** Government chatbots perform worse in regional Indian languages — *where exactly does answer quality drop?*

BhashaCore builds a chatbot (RAG) pipeline and evaluates it across **English (control)** and five
Indic languages — **Hindi, Tamil, Telugu, Kannada, Malayalam** — decomposing quality into:

1. **Reading/generation gap** — same model, gold context given → measures the LLM's comprehension & generation per language (`gold_context`).
2. **Knowledge gap** — closed-book QA → what the model already knows in each language (`closed_book`).
3. **Retrieval gap** — RAG over a retrieval pool → added loss from BM25 retrieval in each script (`rag`).
4. **Input-normalization gap** — Romanized/transliterated queries through the same RAG → the realistic "user types Hinglish" stress test (`rag_translit`).

## Data

- **Knowledge base / retrieval pools:** AI4Bharat **IndicCorp v2** (`ai4bharat/IndicCorpV2`) — streamed & sampled per language.
- **QA evaluation:** AI4Bharat **IndicQA** (`ai4bharat/IndicQA`) for the five Indic languages; **SQuAD v1.1** validation as the English control.
- Retrieval pool per language = all QA contexts for that language + ~3k IndicCorp passages as distractors (gold passage guaranteed present → Recall@k / MRR are measurable).

## Models (NVIDIA-hosted)

All generation goes through NVIDIA's OpenAI-compatible endpoint (`integrate.api.nvidia.com/v1`):

- **Generator (primary):** `minimaxai/minimax-m3.1-flash` — fast flash-class model, the
  economical class governments actually deploy; identical across all languages so gaps
  are language effects, not model effects. (A flagship-class model, `z-ai/glm-5.3-flash`,
  is run on a 25-question/language subset as a robustness check.)
- **Judge (LLM-as-judge):** a *different* model family from the generator —
  translate-then-judge in English to avoid Indic-language judge bias.

## Metrics

- **Extractive:** EM, token-F1 (script-aware normalization: NFC, punctuation/ZWJ strip, no article removal bias for Indic).
- **Judge scores:** correctness 0–5, faithfulness 1–5 (context modes), response-language check.
- **Language quality:** script purity (Unicode-block ratio), % responses in-language, code-mixing detection.
- **Retrieval:** Recall@5, MRR@10 per language.
- **Failure taxonomy:** retrieval miss / unfaithful / wrong language / refusal / wrong answer, with hand-picked example failures + English glosses.

## Pipeline

```
uv venv .venv && uv pip install -r requirements.txt   # setup
.venv/bin/python -m src.run_pipeline --stage data      # download + sample + pools
.venv/bin/python -m src.run_pipeline --stage retrieve  # BM25 retrieval + metrics
.venv/bin/python -m src.run_pipeline --stage generate --model z-ai/glm-5.3
.venv/bin/python -m src.run_pipeline --stage judge
.venv/bin/python -m src.run_pipeline --stage analyze   # tables, charts, taxonomy
```

Output: `report/REPORT.md` (+ `report/figures/`) — the comparison report with per-language
accuracy/quality tables, the quality-drop waterfall, and example failures per language.

## Web app

```
.venv/bin/python src/app.py --port 8001     # http://127.0.0.1:8001
```

Pages: **Chat** (real BM25 retrieval over the indexed corpus, streaming NDJSON answers,
expandable citations), **Research Dashboard** (saved evaluation results),
**Language Comparison** (per-language quality waterfall), **Failure Analysis**
(filterable real failure records), **About** (metric definitions and limitations).

- Retrieval, citations and evidence-sufficiency checks run identically with or without a
  configured LLM key.
- With `NVIDIA_API_KEY` configured, grounded answers are generated live via the NVIDIA NIM
  endpoint; without it, grounded answers use the evaluation dataset's own gold answers
  (labelled `dataset-eval-gold`). Unsupported questions always receive an explicit
  "insufficient evidence" notice with closest-match references (not used).
- Session chat history is persisted under `chat_history/` (git-ignored).

### Tests

```
.venv/bin/python -m pytest tests/ -v            # API + retrieval + citation integrity (25 tests)
python3 tests/browser_e2e.py                    # Playwright end-to-end (47 checks)
```

## Reproducibility

All sampling is seeded (`SEED=42`). Generation/judge runs are **resumable**: completed question IDs
are skipped on re-run, so crashed batches cost nothing. The NVIDIA NIM key is read from the
environment / OpenCode config at runtime and never written into the repo.
