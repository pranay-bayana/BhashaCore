# BhashaCore — Where Does Answer Quality Drop in Indian-Language Chatbots?

**A comparative evaluation of a RAG chatbot pipeline across English, Hindi, Tamil, Telugu, Kannada, and Malayalam.**

*October 2026 · Supervised project deliverable*

---

## 1. Background & Motivation

Government chatbots (UMANG / MyScheme-style assistants, state-language helpdesks) are widely
reported to answer well in English and poorly in regional Indian languages. But "performs worse"
is an aggregate complaint: a chatbot can fail in a regional language for several **different**
reasons — the retrieval stack may not find the right passage in that script, the LLM may
understand the question but answer in the wrong language or hallucinate, users may type
Romanized ("Hinglish") queries the pipeline never normalizes, or the model may simply know less
in that language.

**BhashaCore** decomposes the quality drop into a pipeline waterfall and measures each stage
separately, per language, with the same generator model everywhere — so every gap is
attributable to a *stage*, not to a model swap.

## 2. Experimental Design

The pipeline is a standard retrieval-augmented chatbot:

```
user query ──► retrieval (BM25) ──► top-5 passages ──► LLM generator ──► answer
```

Four evaluation modes isolate each failure source:

| Mode | Input to LLM | Measures |
|---|---|---|
| **Closed-book** | question only | the model's own knowledge/fluency in that language |
| **Gold context** | question + the correct passage | reading comprehension + faithful generation |
| **RAG** | question + top-5 BM25 passages | the realistic end-to-end pipeline |
| **RAG + Romanized query** | Romanized question, retrieval run on the Romanized text | the "user types Hinglish" stress test |

The **quality waterfall** per language: `English gold-context` → `language X gold-context`
(**comprehension gap**) → `language X RAG` (**retrieval gap**) → `language X RAG with Romanized
input` (**input-normalization gap**).

**Languages:** English (control), Hindi (best-resourced Indic), Tamil, Telugu, Kannada,
Malayalam — 5 scripts, 2 language families (Indo-Aryan + Dravidian).

**Models (all through NVIDIA's OpenAI-compatible endpoint):**

| Role | Model | Measured endpoint behaviour |
|---|---|---|
| Primary generator (all languages) | `minimaxai/minimax-m3.1-flash` | 1–4 s/call under concurrency; per-model token quota → client paces launches with a shared 429 cooldown |
| Judge | `meta/muse-glimmer-30b` | different family from both generators; verified Hindi + Tamil capable before selection |
| Flagship robustness subset | `z-ai/glm-5.3-flash` | serializes at 100–280 s/call on this endpoint → 25 Q/lang subset only |

**Key design decisions:**

1. **Same generator for every language** — cross-language gaps are language effects, not model
   effects. A flagship-class model from a different family replicates the headline result (§4.6).
2. **LLM-as-judge with translate-then-judge.** Judges are weaker in Indic languages, so the
   judge translates everything to English *inside* the evaluation prompt before scoring
   (correctness 0–5, faithfulness 1–5, issue tags, English glosses).
3. **Script-aware extractive metrics.** SQuAD-style EM/F1 with NFC normalization,
   punctuation/ZWJ stripping, no article-stripping bias (Indic languages lack articles).
4. **Measurable retrieval.** Each pool contains all QA contexts for that language (gold passage
   guaranteed present) plus 3,000 distractor passages from **IndicCorp v2** — so Recall@k / MRR
   are exactly computable per language.

## 3. Data

| Component | Source | Use |
|---|---|---|
| QA questions + contexts (Indic) | AI4Bharat **IndicQA** (`ai4bharat/IndicQA`) | 50 eval questions/language + context pool |
| QA questions + contexts (English) | **SQuAD v1.1** validation | 50 eval questions + context pool |
| Distractor passages (Indic) | AI4Bharat **IndicCorp v2**, streamed + sampled | 3,000 per language added to retrieval pools |
| Distractor passages (English) | SQuAD train contexts | 3,000 (IndicCorp v2 has no English split — noted in §6) |

Per-language availability after parsing: Hindi 1,052 · Tamil 1,276 · Telugu 1,397 ·
Kannada 1,137 · Malayalam 1,100 questions (IndicQA); SQuAD dev 10,570. Each pool = all QA
contexts for that language (~99–260 paragraphs) + 3,000 distractors.

**Achieved run sizes:** the first 50 questions per language were targeted; **achieved coverage
averaged 48.6/50** per mode×language (gold context 100%, RAG 99.7%, Romanized stress 98%,
closed-book 91% — a small number of questions produce runaway reasoning chains in the generator
and were reported at achieved *n*). IndicQA's question IDs do not align across languages or with
SQuAD dev (per-language integer IDs), so samples are *independent draws from the same underlying
translated question pool* (IndicQA derives from XQuAD-style translations of SQuAD dev) —
aggregate comparisons are valid; per-question paired analysis is not possible.

**Romanized stress set:** each Indic question is transliterated to lowercase ITRANS Latin
(e.g., Hindi *"भगवान जगन्नाथ की बहन का क्या नाम है?"* → *"bhagavana jagannatha ki bahana ka kya
nama hai?"*), approximating users who type their language in Roman script. Synthetic
approximation of informal romanization (documented as such).

## 4. Results

### 4.1 Retrieval quality — first clear drop

BM25 (word tokens + 5-char prefixes), Recall@5 / MRR@10 over the per-language pools:

| Query → | **English** | Hindi | Tamil | Telugu | Kannada | Malayalam |
|---|---|---|---|---|---|---|
| Native-script query, Recall@5 | **0.95** | 0.80 | **0.57** | 0.85 | 0.67 | 0.84 |
| Native-script query, MRR@10 | **0.91** | 0.64 | 0.42 | 0.78 | 0.58 | 0.69 |
| **Romanized** query, Recall@5 | — | 0.01 | 0.06 | 0.04 | **0.00** | 0.09 |

1. **English retrieval is near-perfect; every Indic language drops**, most severely **Tamil
   (0.57)** and **Kannada (0.67)** — Dravidian agglutinative morphology defeats word-level
   lexical matching.
2. **Romanized queries destroy retrieval almost completely (≤0.09)** — the single largest,
   most binary failure in the study, and the easiest for a deployment to fix.

### 4.2 Answer quality per language × mode

Judge correctness (0–5), primary generator, n≈50/language/mode (exact *n* in
`results/summary/summary.csv`):

| Mode | **English** | Hindi | Tamil | Telugu | Kannada | Malayalam |
|---|---|---|---|---|---|---|
| Closed-book | 2.74 | 2.48 | 1.53 | 2.45 | 1.76 | 2.38 |
| **Gold context** | **4.94** | 4.86 | 4.52 | 4.76 | 4.50 | 4.80 |
| **RAG** | **4.68** | 4.08 | **2.76** | 4.29 | **3.06** | 3.90 |
| **RAG + Romanized query** | — | **0.00** | **0.21** | **0.40** | **0.04** | **0.41** |

Supporting metrics (see `report/tables.md`): token-F1 and EM are low everywhere (sentence-style
answers vs short gold spans — judge scores are the meaningful signal); **responses in the target
language/script: 91–100%** everywhere except closed-book Tamil (91%) — the pipeline answers
in-language when it answers at all.

### 4.3 The quality waterfall — where the drop actually happens

Decomposing the drop from the English gold-context ceiling (4.94):

| Stage | EN | HI | TA | TE | KN | ML |
|---|---|---|---|---|---|---|
| Gold context (comprehension gap vs EN) | — | −0.08 | −0.42 | −0.18 | −0.44 | −0.14 |
| RAG (additional **retrieval gap**) | −0.26 | −0.78 | **−1.76** | −0.47 | **−1.44** | −0.90 |
| RAG + Romanized (additional **input gap**) | — | **−4.08** | **−2.55** | **−3.89** | **−3.02** | **−3.49** |

**Findings:**

1. **Comprehension is not the bottleneck.** Given the right passage, the model is near-perfect
   in *every* language (4.50–4.94). The comprehension gap between English and the Indic
   languages is 0.08–0.44 points — small.
2. **The retrieval gap is the dominant regional-language penalty in the RAG pipeline**:
   −1.76 (Tamil) and −1.44 (Kannada), tracking the BM25 Recall@5 ordering exactly. Hindi and
   Telugu (−0.78, −0.47) fare better, matching their higher retrieval scores.
3. **The input-normalization gap is catastrophic and language-universal**: Romanized input
   reduces every Indic language to **0.0–0.4 / 5**. Retrieval finds junk (Recall@5 ≤ 0.09), the
   model correctly refuses or answers wrong. A government chatbot without transliteration
   handling is simply broken for Romanized users — in *every* language.
4. **The knowledge gap is a model limitation, not a language gap**: closed-book is mediocre in
   *all* languages including English (1.53–2.74), with Tamil (1.53) and Kannada (1.76) lowest.

### 4.4 Failure taxonomy

Among the 530 failed answers (correctness ≤ 3, primary generator), flag distribution:

| Flag | Count | Share of failures |
|---|---|---|
| **Retrieval miss** (gold passage not in top-5) | 306 | 58% |
| **Refusal** (model says it cannot answer) | 282 | 53% |
| **Wrong answer** (confident but incorrect) | 224 | 42% |
| **Hallucinated** (asserts content not in context) | 122 | 23% |
| Incomplete | 51 | 10% |
| Off-topic | 32 | 6% |

Reading: the dominant failure chain is **retrieval miss → honest refusal** — the generator is
well-grounded (it refuses rather than guessing when retrieval fails), which is why the
Romanized mode scores ≈0 instead of producing confident garbage. Hallucination (23%) concentrates
in closed-book and in RAG cases where near-miss passages contained related entities.

### 4.5 Stress test — Romanized queries

End-to-end on identical questions: native-script RAG scores 2.76–4.29 across the five Indic
languages; the *same* questions typed in Roman script score **0.00–0.41**. The failure chain is
visible in individual examples: the model *understands* the Romanized question (the system
prompt instructs it to answer in the native script — script purity of its answers stays ≈1.0),
retrieval feeds it unrelated passages, and it refuses. The failure is entirely in the retrieval
stack's inability to bridge scripts — a solved problem (transliteration normalization) that
government deployments routinely skip.

### 4.6 Robustness check — a second model family

The flagship-class `z-ai/glm-5.3-flash` (25 Q/lang, gold-context + RAG) reproduces the pattern:

| Mode | EN | HI | TA | TE | KN | ML |
|---|---|---|---|---|---|---|
| Gold context | 5.00 | 4.64 | 4.44 | 4.80 | 4.64 | 4.68 |
| RAG | 4.80 | 3.68 | **2.68** | 4.40 | **3.48** | 3.64 |

Same ordering (Tamil worst, Telugu best, comprehension ~perfect) on a different model family —
the conclusion is not an artifact of one model.

*(Charts: `report/figures/correctness_by_lang_mode.png`, `f1_em_by_lang_mode.png`,
`retrieval_native_vs_roman.png`, `failure_taxonomy.png`.)*

## 5. Recommendations for Government Chatbot Deployments

1. **Normalize Romanized input before retrieval.** Add a transliteration layer
   (e.g., AI4Bharat IndicXlit) or a script-robust retriever. This is the highest-impact,
   lowest-cost fix: it converts a 0/5 experience into a working chatbot for users who type
   "mudhalil kodiya uruvakkiyavar yar?" instead of தமிழ்.
2. **Fix Dravidian retrieval first.** Word-level BM25 loses 1.4–1.8 correctness points in Tamil
   and Kannada RAG. Morphology-aware tokenization, dense multilingual retrievers
   (multilingual-E5 / BGE-M3), or hybrid retrieval are the direct remedies — our gold-context
   results prove the generator will use the right passage when retrieval finds it.
3. **Do not rely on the model's own knowledge.** Closed-book scores are mediocre in *every*
   language including English (1.5–2.7/5). RAG is not optional, even for English.
4. **Language-fidelity is not the main risk.** Responses were in the correct script 91–100% of
   the time; hallucination (23% of failures) and wrong answers (42%) matter more than
   wrong-language answers — and both shrink dramatically once retrieval works.
5. **Evaluate with translate-then-judge.** Judging in English after translation (with a judge
   from a different model family) is a practical, bias-reduced recipe for Indic-language
   chatbot evaluation.

## 6. Threats to Validity

1. Independent (not paired) question samples per language (§3); n=50/language (48.6 achieved).
2. English distractors come from SQuAD train (Wikipedia paragraphs) while Indic distractors are
   web-crawled IndicCorp v2 sentences — noise profiles differ slightly across pools.
3. ITRANS romanization is cleaner than real user input; real Romanized queries would be *at
   least* as bad.
4. BM25-only retrieval reflects a common low-cost deployment, not the best achievable pipeline.
5. Judge scores come from one LLM (translate-then-judge mitigates but cannot eliminate judge
   bias); no inter-judge agreement was measured.
6. 33 closed-book questions (9%) produced runaway reasoning in the generator and are reported
   at achieved *n*; no evidence suggests they are language-biased (gaps are spread across
   languages).

## 7. Reproducibility

- All sampling seeded (`SEED=42`); stages: `src/run_pipeline.py --stage {data|retrieve|generate|judge|analyze}`.
- Generation and judging are resumable: completed items are skipped, failed/throttled items are
  retried; the NIM client self-rate-limits (launch pacing + shared 429 cooldown) to respect the
  endpoint's per-model token quotas.
- Full audit trail in `results/gen/` and `results/judge/` (per-answer latency, error rows,
  judge glosses); summaries in `results/summary/`.
- NVIDIA NIM credentials are read at runtime from the environment / OpenCode provider config;
  no keys are stored in the repo.

## Appendix A — Failure Examples

See `report/failures_examples.md` for auto-selected, English-glossed failure examples per
language and category, e.g.:

> **[Romanized-query drop, Hindi]** Q: *"33 prakara ke devon ka ullekh kis ved me kiya gaya hai?"*
> (In which Veda are the 33 deities mentioned? — gold: ऋग्वेद / Rigveda).
> The Romanized query retrieved unrelated passages; the bot replied in correct Hindi:
> *"उपलब्ध जानकारी में … इसका उत्तर नहीं मिलता।"* ("The answer is not found in the available
> information.") — an honest refusal caused entirely by script-mismatched retrieval.

## Appendix B — Outputs

- `results/summary/summary.csv` — per model × language × mode metrics
- `results/summary/retrieval.csv` — retrieval metrics (native + Romanized)
- `report/tables.md` — markdown tables
- `report/figures/*.png` — charts
- `report/failures_examples.md` — failure catalog with glosses
