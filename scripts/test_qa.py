#!/usr/bin/env python3
"""
Test BhashaCore question answering with existing knowledge base.
Tests:
1. Native language questions that should be answerable from corpus
2. English questions
3. Citations rendering
4. Insufficient evidence handling
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import app
import httpx

async def test_qa():
    app.config["TESTING"] = True
    client = app.test_client()
    
    # Test questions that should be answerable from the indexed corpus
    test_cases = [
        # English questions
        ("en", "What is the capital of France?"),
        ("en", "Who was the first president of the United States?"),
        ("en", "What is the largest planet in our solar system?"),
        ("en", "Who wrote Romeo and Juliet?"),
        # Hindi questions
        ("hi", "भारत की राजधानी क्या है?"),
        ("hi", "भारत के प्रथम प्रधानमंत्री कौन थे?"),
        # Tamil questions
        ("ta", "தாய்நாடு எங்கே உள்ளது?"),
        # Telugu questions
        ("te", "హైదరాబాద్ ఎక్కడ ఉంది?"),
        # Kannada questions
        ("kn", "ಬೆಂಗಳೂರು ಎಂದರೇನು?"),
        # Malayalam questions
        ("ml", "തിരുവനന്തപുരം എന്നാൽ എന്താണ്?"),
    ]
    
    print("=" * 70)
    print("QUESTION ANSWERING TEST")
    print(f"{'='*60}")
    
    results = []
    for lang, question in tests:
        print(f"\n{lang.upper()}: {question[:60]}...")
        
        resp = client.post("/api/chat", json={
            "session_id": "test_eval",
            "lang": lang,
            "question": question,
            "mode": "rag"
        })
        
        if resp.status_code != 200:
            print(f"  ERROR: HTTP {resp.status_code}")
            continue
        
        data = resp.get_json()
        
        # Collect SSE stream
        answer = ""
        citations = []
        status = ""
        model = ""
        
        for line in resp.get_data(as_text=True).splitlines():
            if line.strip():
                try:
                    chunk = json.loads(line)
                    if chunk.get("type") == "done":
                        answer = chunk.get("answer", "")
                        citations = chunk.get("citations", [])
                        status = result.get("status", "unknown")
                        model = result.get("model", "")
                    elif chunk.get("type") == "error":
                        print(f"  ERROR: {chunk.get('error', '')}")
                        break
                except json.JSONDecodeError:
                    pass
        
        cited_passages = sum(1 for c in citations if c.get("used"))
        print(f"  Status: {result['status']}")
        print(f"  Answer: {answer[:80]}")
        print(f"  Citations used: {sum(1 for c in citations if c.get('used'))}/{len(citations)}")
        print()
    
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_qa()
PYEOF