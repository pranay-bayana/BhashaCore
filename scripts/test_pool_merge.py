#!/usr/bin/env python3
"""Test that pool_{lang}_knowledge.jsonl is merged into pool_{lang} retrieval."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import _pool_index
from src.retrieval import load_jsonl
from src.config import PROC_DIR

for lang in ["en", "hi", "ta", "te", "kn", "ml"]:
    index = _pool_index(lang)
    pool_records = load_jsonl(PROC_DIR / f"pool_{lang}.jsonl")
    kf = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
    kno_records = load_jsonl(kf) if kf.exists() else []
    
    total_expected = len(pool_records) + len(kno_records)
    index_count = len(index.records)
    
    print(f"{lang.upper()}: pool={len(pool_records)}, knowledge={len(kno_records)}, "
          f"index={index_count}, expected={total_expected}, "
          f"{'PASS' if index_count == total_expected else 'MISMATCH'}")
    
    # Test that knowledge records are searchable
    if kno_records:
        # Search for text from a knowledge passage
        sample_text = kno_records[0].get("text", "")
        if sample_text:
            first_word = sample_text.split()[0] if sample_text.split() else ""
            if first_word:
                hits = index.search(first_word, 5)
                hit_pids = [p for p, _ in hits]
                knowledge_found = any(r["pid"] in hit_pids for r in kno_records)
                print(f"  Knowledge record searchable: {'YES' if knowledge_found else 'NO'}")
