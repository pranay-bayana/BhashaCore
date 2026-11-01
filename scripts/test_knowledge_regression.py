#!/usr/bin/env python3
"""
Regression test for Priority 1: knowledge-index mismatch.

Ingests a unique test document into pool_{lang}_knowledge.jsonl,
rebuilds the app's retrieval index, asks a question answerable only
from that document, and verifies live retrieval finds it with correct provenance.

Tests BOTH the retrieval path (direct PoolIndex.search) and verifies
the document appears in answer_question citations with correct provenance.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import _pool_index, answer_question
from src.retrieval import load_jsonl
from src.config import PROC_DIR


def test_knowledge_retrieval_regression(lang: str = "en"):
    """Ingest a unique document and verify it's retrievable via the app path."""
    # --- Step 1: Create a unique test document ---
    unique_title = "TEST_UNIQUE_DOC_BHASHACORE_REGRESSION"
    unique_text = ("The BhashaCore regression test document describes a fictional "
                   "ancient library called the Archive of Echoes located in "
                   "Kashi. It contains scrolls about forgotten rivers and the "
                   "secret garden of night-blooming jasmine.")
    test_question = "Where is the Archive of Echoes located?"

    # Build a unique pid
    pid = "test_" + hashlib.md5(f"{lang}:{unique_title}:{unique_text}".encode()).hexdigest()[:16]

    # --- Step 2: Write to pool_{lang}_knowledge.jsonl ---
    knowledge_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
    record = {
        "pid": pid,
        "lang": lang,
        "source": "regression-test",
        "source_url": "https://example.org/regression-test-archive-of-echoes",
        "title": unique_title,
        "text": unique_text,
        "category": "regression-test",
    }

    # Append to knowledge file (preserving existing records)
    existing = []
    if knowledge_file.exists():
        existing = load_jsonl(knowledge_file)
    existing.append(record)
    with open(knowledge_file, "w", encoding="utf-8") as f:
        for r in existing:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"  Ingested test document: pid={pid}, title={unique_title}")

    # --- Step 3: Clear the app's index cache so it reloads ---
    from src import app as app_module
    if lang in app_module._index_cache:
        del app_module._index_cache[lang]

    # --- Step 4: Verify retrieval finds the document (direct PoolIndex path) ---
    index = _pool_index(lang)
    hits = index.search(test_question, 5)
    hit_pids = [p for p, _ in hits]

    assert pid in hit_pids, (
        f"FAIL: Test document pid={pid} NOT found in retrieval hits for '{test_question}'. "
        f"Hit pids: {hit_pids}"
    )

    rank = hit_pids.index(pid) + 1
    print(f"  PASS: Test document retrieved at rank {rank} for question '{test_question}'")

    # --- Step 5: Verify document appears in answer_question citations ---
    result = answer_question(lang, question=test_question, input_style="native", eval_mode=True)

    citation_pids = [c["pid"] for c in result["citations"]]
    assert pid in citation_pids, (
        f"FAIL: Test document pid={pid} not in citations. Citation pids: {citation_pids}"
    )
    print(f"  PASS: Test document appears in answer_question citations")

    # Verify provenance
    cit = next(c for c in result["citations"] if c["pid"] == pid)
    assert cit["source"] == "regression-test", (
        f"FAIL: Wrong source {cit['source']}, expected 'regression-test'"
    )
    assert cit["source_url"] == "https://example.org/regression-test-archive-of-echoes"
    assert cit["title"] == unique_title
    print(f"  PASS: Provenance correct - source={cit['source']}, title={cit['title'][:40]}")

    # --- Step 6: Verify provenance through the live app retrieval path ---
    # The document should be findable through _pool_index (same path used by live chat)
    index2 = _pool_index(lang)  # Should use cached index now
    hits2 = index2.search(test_question, 5)
    hit_pids2 = [p for p, _ in hits2]
    assert pid in hit_pids2, (
        f"FAIL: Test document not retrievable through cached index"
    )
    print(f"  PASS: Document retrievable through live app retrieval path (cached index)")

    # --- Step 7: Clean up (restore original knowledge file) ---
    existing_without_test = [r for r in existing if r["pid"] != pid]
    with open(knowledge_file, "w", encoding="utf-8") as f:
        for r in existing_without_test:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Clear cache again to restore clean state
    if lang in app_module._index_cache:
        del app_module._index_cache[lang]

    print(f"  Cleaned up test document from {knowledge_file}")
    return True


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Knowledge-index regression test")
    ap.add_argument("--lang", default="en", help="Language to test")
    args = ap.parse_args()

    print(f"=== Knowledge-Index Regression Test ({args.lang.upper()}) ===")
    success = test_knowledge_retrieval_regression(args.lang)
    print(f"\n{'='*50}")
    print(f"RESULT: {'PASS' if success else 'FAIL'}")
    print(f"{'='*50}")
    sys.exit(0 if success else 1)
