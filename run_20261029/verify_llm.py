#!/usr/bin/env python3
"""Verify real AI generation through NVIDIA NIM."""
import asyncio, time, json, sys
from pathlib import Path

sys.path.insert(0, "/Users/pranaybayana/Desktop/Supervised project")
from src.nim import NimClient

async def test():
    client = NimClient('minimaxai/minimax-m3.1-flash')
    
    # Test 1: Simple English question
    t0 = time.time()
    resp = await asyncio.wait_for(client.chat([
        {'role': 'system', 'content': 'You are a helpful assistant. Answer in English.'},
        {'role': 'user', 'content': 'What is the capital of Japan?'}
    ]), timeout=300.0)
    t1 = time.time()
    print(f'Test 1 - Capital of Japan:')
    print(f'  Status: {resp.get("status")}')
    print(f'  Content: {resp.get("content", "")[:200]}')
    print(f'  Error: {resp.get("error")}')
    print(f'  Latency: {t1-t0:.1f}s')
    print(f'  Has content: {bool(resp.get("content"))}')
    print()
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test())
