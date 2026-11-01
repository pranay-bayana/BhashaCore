#!/usr/bin/env python3
"""
Knowledge ingestion pipeline for BhashaCore - Wikipedia edition.

Downloads Wikipedia articles on popular topics across all 6 languages.
Uses Wikipedia's search API to find articles on specific topics,
then fetches those articles in batches.

Usage:
    python scripts/ingest_knowledge_v2.py --langs en hi ta te kn ml --articles-per-lang 20
"""

import argparse
import hashlib
import json
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Iterator, Dict, List, Tuple
from dataclasses import dataclass, asdict

import requests

from src.config import LANGS, PROC_DIR, ROOT

KNOWLEDGE_DIR = ROOT / "data" / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

RAW_DIR = KNOWLEDGE_DIR / "raw"
PROC_KNOWLEDGE_DIR = KNOWLEDGE_DIR / "processed"
METADATA_DIR = KNOWLEDGE_DIR / "metadata"

for _d in (KNOWLEDGE_DIR, RAW_DIR, PROC_KNOWLEDGE_DIR, METADATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

WIKIPEDIA_LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "kn": "kn",
    "ml": "ml",
}

USER_AGENT = "BhashaCore/1.0 (research project; contact: research@example.com)"

ARTICLES_PER_LANG = 20


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = "".join(c for c in text if unicodedata.category(c) != "C" or c in "\n\t")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_passages(text: str, max_chars: int = 500, overlap: int = 50) -> list:
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    passages = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(current) + len(sentence) + 1 <= max_chars:
            current = (current + " " + sentence).strip() if current else sentence
        else:
            if current:
                passages.append(current)
            current = sentence
    if current:
        passages.append(current)
    if not passages and text:
        for i in range(0, len(text), max_chars - overlap):
            chunk = text[i : i + max_chars]
            if chunk.strip():
                passages.append(chunk.strip())
    return [p for p in passages if p.strip()]


def search_wikipedia(lang_code: str, query: str, limit: int = 10) -> list:
    """Search Wikipedia for articles matching a query."""
    base_url = f"https://{lang_code}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
    }
    try:
        resp = requests.get(base_url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30, verify=False)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("query", {}).get("search", [])
        return [{"title": r["title"], "pageid": r["pageid"]} for r in results]
    except Exception as e:
        print(f"  [Wikipedia {lang_code}] Search error: {e}")
        return []


def fetch_wikipedia_articles(lang_code: str, count: int = ARTICLES_PER_LANG) -> list[dict]:
    """Fetch Wikipedia articles for a language.
    
    Strategy: Search for popular topics, then fetch those articles.
    This is more efficient than random retrieval.
    """
    articles = []
    
    # Search terms for general knowledge topics
    search_queries = [
        "history", "science", "geography", "culture", "literature",
        "mathematics", "physics", "chemistry", "biology", "astronomy",
        "history of India", "history of India", "Indian history",
        "world history", "ancient history", "modern history",
        "world geography", "Indian geography", "world countries",
        "world religions", "world religions", "major religions",
        "science and technology", "science and technology in India",
        "Indian science and technology", "Indian space research",
        "Indian culture", "Indian culture and heritage",
        "Indian culture and heritage",
    ]
    
    # Limit queries per language to avoid rate limiting
    queries = search_queries[:count]
    
    all_articles = []
    seen_titles = set()
    
    for query in queries:
        try:
            results = search_wikipedia(lang_code, query, limit=5)
            for result in results:
                if result["title"] not in seen_titles:
                    seen_titles.add(result["title"])
                    articles.append(result)
                    if len(articles) >= count:
                        break
        except Exception as e:
            print(f"  [Wikipedia {lang_code}] Search error for '{query}': {e}")
            continue
        
        if len(articles) >= count:
            break
    
    # Fetch the articles
    articles_data = []
    for article in articles:
        try:
            resp = requests.get(
                f"https://{lang_code}.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "prop": "extracts",
                    "explaintext": 1,
                    "pageids": article["pageid"],
                    "format": "json",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=30,
                verify=False,
            )
            resp.raise_for_status()
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for pid_str, page_data in pages.items():
                title = page_data.get("title", "")
                text = page_data.get("extract", "")
                page_id = page_data.get("pageid", pid_str)
                url = f"https://{lang_code}.wikipedia.org/wiki/{page_data.get('title', '').replace(' ', '_')}"
                if text.strip():
                    articles_data.append({
                        "title": title,
                        "text": text,
                        "url": url,
                        "pageid": page_id,
                    })
        except Exception as e:
            print(f"  [Wikipedia {lang_code}] Error fetching article {article['title']}: {e}")
            continue
        
        time.sleep(1)  # Be polite to Wikipedia API
    
    return articles_data


def ingest_wikipedia(lang_code: str, count: int = ARTICLES_PER_LANG) -> dict:
    """Download and process Wikipedia articles for a language."""
    print(f"[Wikipedia {lang_code}] Fetching up to {count} articles...")
    
    articles = fetch_wikipedia_articles(lang_code, count)
    print(f"  Downloaded {len(articles)} articles")
    
    if not articles:
        return None

    raw_dir = RAW_DIR / f"wikipedia_{lang_code}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"wikipedia_{lang_code}_raw.jsonl"
    with open(raw_path, "w", encoding="utf-8") as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + "\n")

    processed_records = []
    seen_texts = set()

    for article in articles:
        text = normalize_text(article["text"])
        if not text or len(text) < 50:
            continue

        passages = split_into_passages(text, max_chars=500, overlap=50)

        for passage in passages:
            passage_norm = passage.strip()
            if not passage_norm or len(passage_norm) < 30:
                continue
            if passage_norm in seen_texts:
                continue
            seen_texts.add(passage_norm)

            pid = "wp_" + hashlib.md5(f"{lang_code}:{article['title']}:{passage_norm}".encode()).hexdigest()[:16]
            record = {
                "pid": pid,
                "lang": lang_code,
                "source": "wikipedia",
                "source_url": article["url"],
                "title": article["title"],
                "text": passage_norm,
                "category": "wikipedia",
            }
            processed_records.append(record)

    proc_path = PROC_KNOWLEDGE_DIR / f"wikipedia_{lang_code}.jsonl"
    with open(proc_path, "w", encoding="utf-8") as f:
        for record in processed_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    metadata = {
        "name": "Wikipedia",
        "url": f"https://{lang_code}.wikipedia.org/",
        "license": "CC BY-SA 3.0 / CC BY-SA 4.0",
        "language": lang_code,
        "download_date": datetime.now(timezone.utc).isoformat(),
        "record_count": len(processed_records),
        "notes": f"{len(articles)} articles downloaded, {len(processed_records)} passages extracted",
    }
    metadata_path = METADATA_DIR / f"wikipedia_{lang_code}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

    print(f"  Processed {len(processed_records)} passages from {len(articles)} articles")
    return metadata


def build_pool_from_processed(lang: str) -> list:
    """Load all processed knowledge for a language and return as pool records."""
    records = []
    for p in PROC_KNOWLEDGE_DIR.glob(f"*_{lang}.jsonl"):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records


def build_pools_for_all_languages() -> dict[str, int]:
    """Build retrieval pools for all languages from processed knowledge."""
    results = {}
    for lang in LANGS:
        proc_dir = PROC_KNOWLEDGE_DIR
        files = list(proc_dir.glob(f"*_{lang}.jsonl"))
        if not files:
            print(f"  {lang}: No processed knowledge found")
            continue
        records = []
        for p in files:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        seen_pids = set()
        unique_records = []
        for r in records:
            if r["pid"] not in seen_pids:
                seen_pids.add(r["pid"])
                unique_records.append(r)
        pool_path = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
        with open(pool_path, "w", encoding="utf-8") as f:
            for r in unique_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        results[lang] = len(unique_records)
        print(f"  {lang}: {len(unique_records)} passages in pool")
    return results


def ingest_all(langs: list[str] = None, articles_per_lang: int = ARTICLES_PER_LANG) -> dict:
    """Run the full ingestion pipeline for all languages."""
    if langs is None:
        langs = list(LANGS.keys())
    results = {}
    for lang in langs:
        print(f"\n{'='*60}")
        print(f"Processing language: {lang}")
        print(f"{'='*60}")
        meta = ingest_wikipedia(lang, articles_per_lang)
        results[lang] = meta
    print(f"\n{'='*60}")
    print("Building retrieval pools")
    print(f"{'='*60}")
    pool_results = build_pools_for_all_languages()
    results["pools"] = pool_results
    return results


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Ingest knowledge for BhashaCore")
    ap.add_argument("--langs", nargs="+", default=["en", "hi", "ta", "te", "kn", "ml"])
    ap.add_argument("--articles-per-lang", type=int, default=ARTICLES_PER_LANG)
    args = ap.parse_args()
    ingest_all(langs=args.langs, articles_per_lang=args.articles_per_lang)