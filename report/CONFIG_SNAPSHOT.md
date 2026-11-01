
---
Evaluation configuration:
  - Languages: en, hi, ta, te, kn, ml
  - Eval questions per language: 100
  - Per-language RUN_LIMIT: {'en': 50, 'hi': 50, 'ta': 50, 'te': 50, 'kn': 50, 'ml': 50}
  - Pipeline modes: closed_book, gold_context, rag, rag_translit
  - Primary generator: minimaxai/minimax-m3.1-flash
  - Judge model: meta/muse-glimmer-30b
  - Top-K retrieval: 5
  - Seed: 42