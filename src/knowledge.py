"""Knowledge acquisition pipeline for BhashaCore.

Downloads, normalizes, and indexes knowledge from public sources for
multilingual RAG evaluation. All data sources are documented with license
and provenance information.

Sources:
1. AI4Bharat IndicCorp v2 (already used in existing pipeline)
   - License: CC0 / Public Domain (via AI4Bharat)
   - Source: https://huggingface.co/datasets/ai4bharat/IndicCorpV2
   - Languages: All 6 supported Indic languages + English

2. Wikipedia (via REST API)
   - License: CC BY-SA 3.0 / CC BY-SA 4.0
   - Source: https://www.wikipedia.org/
   - Languages: en, hi, ta, te, kn, ml (Wikipedia codes: en, hi, ta, te, kn, ml)

Data layout (all under data/knowledge/):
  knowledge/
    raw/                    Raw downloaded data (never modified)
      wiki_en/              Wikipedia English articles
      wiki_hi/              Wikipedia Hindi articles
      ...
    processed/              Cleaned, deduplicated, chunked passages
      pool_<lang>.jsonl     BM25-ready pool for each language
    metadata/               Per-source metadata (license, download date, count)
"""

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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KNOWLEDGE_DIR = ROOT / "data" / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

RAW_DIR = KNOWLEDGE_DIR / "raw"
PROC_KNOWLEDGE_DIR = KNOWLEDGE_DIR / "processed"
METADATA_DIR = KNOWLEDGE_DIR / "metadata"

for _d in (KNOWLEDGE_DIR, RAW_DIR, PROC_KNOWLEDGE_DIR, METADATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Wikipedia language codes for our 6 languages
WIKIPEDIA_LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "kn": "kn",
    "ml": "ml",
}

# User-Agent for Wikipedia API (required by Wikimedia terms of use)
USER_AGENT = "BhashaCore/1.0 (research project; contact: research@example.com)"

# Number of Wikipedia articles to download per language (keep manageable)
ARTICLES_PER_LANG = 200


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class SourceRecord:
    """A single cleaned passage with provenance."""
    pid: str
    lang: str
    source: str          # e.g. "wikipedia", "indiccorp"
    source_url: str      # Original URL
    title: str           # Article title (if applicable)
    text: str            # Cleaned passage text
    category: str = ""   # Optional category/topic
    created_at: str = ""  # ISO timestamp


@dataclass
class SourceMetadata:
    """Metadata about a data source."""
    name: str
    url: str
    license: str
    language: str
    download_date: str  # ISO timestamp
    record_count: int
    notes: str = ""


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Clean and normalize text for indexing.

    - Unicode NFC normalization
    - Remove control characters
    - Collapse whitespace
    - Strip leading/trailing whitespace
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    # Remove control characters except newlines and tabs
    text = "".join(c for c in text if unicodedata.category(c) != "C" or c in "\n\t")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_passages(text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping passages of approximately max_chars characters.

    Tries to split at sentence boundaries first, then falls back to character
    splitting. Each passage is at most max_chars characters long.
    """
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    # Split into sentences (naive: split on sentence-ending punctuation + space)
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

    # If no sentence boundaries found, split by character chunks
    if not passages and text:
        for i in range(0, len(text), max_chars - overlap):
            chunk = text[i : i + max_chars]
            if chunk.strip():
                passages.append(chunk.strip())

    return [p for p in passages if p.strip()]


# ---------------------------------------------------------------------------
# Wikipedia ingestion
# ---------------------------------------------------------------------------

def fetch_wikipedia_articles(lang_code: str, count: int = ARTICLES_PER_LANG) -> list[dict]:
    """Fetch random Wikipedia articles for a given language.

    Returns a list of dicts with keys: title, text, url, pageid.
    """
    articles = []
    base_url = f"https://{lang_code}.wikipedia.org/w/api.php"

    # Get random page IDs - with retries for rate limiting
    params = {
        "action": "query",
        "list": "random",
        "rnnamespace": 0,  # Main namespace only (articles, not talk pages)
        "rnlimit": min(count, 500),  # API limit
        "format": "json",
    }

    page_ids = []
    max_retries = 5
    for attempt in range(max_retries):
        try:
            resp = requests.get(base_url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30, verify=False)
            resp.raise_for_status()
            data = resp.json()
            page_ids = [item["id"] for item in data.get("query", {}).get("random", [])]
            break
        except Exception as e:
            print(f"  [Wikipedia {lang_code}] Error fetching random pages (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))  # Exponential backoff
            else:
                return []

    # Fetch page content in batches
    for i in range(0, len(page_ids), 50):
        batch = page_ids[i : i + 50]
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,  # Plain text, not HTML
            "pageids": "|".join(str(pid) for pid in batch),
            "format": "json",
        }
        fetched = False
        for attempt in range(max_retries):
            try:
                resp = requests.get(base_url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30, verify=False)
                resp.raise_for_status()
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for pid_str, page_data in pages.items():
                    title = page_data.get("title", "")
                    text = page_data.get("extract", "")
                    page_id = page_data.get("pageid", pid_str)
                    url = f"https://{lang_code}.wikipedia.org/wiki/{page_data.get('title', '').replace(' ', '_')}"
                    if text.strip():
                        articles.append({
                            "title": title,
                            "text": text,
                            "url": url,
                            "pageid": page_id,
                        })
                fetched = True
                break
            except Exception as e:
                print(f"  [Wikipedia {lang_code}] Error fetching batch (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                else:
                    print(f"  [Wikipedia {lang_code}] Giving up on batch after {max_retries} attempts")
        if fetched:
            time.sleep(3)  # Be polite to Wikipedia API - wait between batches

    return articles


def ingest_wikipedia(lang_code: str, count: int = ARTICLES_PER_LANG) -> dict:
    """Download and process Wikipedia articles for a language.

    Returns a dict with metadata about what was collected.
    """
    print(f"[Wikipedia {lang_code}] Fetching up to {count} articles...")

    articles = fetch_wikipedia_articles(lang_code, count)
    print(f"  Downloaded {len(articles)} articles")

    if not articles:
        return None

    # Save raw data
    raw_dir = RAW_DIR / f"wikipedia_{lang_code}"
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / f"wikipedia_{lang_code}_raw.jsonl"
    with open(raw_path, "w", encoding="utf-8") as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + "\n")

    # Process: clean, split into passages, assign PIDs
    processed_records = []
    seen_texts = set()  # Deduplication

    for article in articles:
        text = normalize_text(article["text"])
        if not text or len(text) < 50:  # Skip very short texts
            continue

        passages = split_into_passages(text, max_chars=500, overlap=50)

        for passage in passages:
            passage_norm = passage.strip()
            if not passage_norm or len(passage_norm) < 30:  # Skip very short passages
                continue

            # Deduplicate by text
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

    # Save processed data
    proc_path = PROC_KNOWLEDGE_DIR / f"wikipedia_{lang_code}.jsonl"
    with open(proc_path, "w", encoding="utf-8") as f:
        for record in processed_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Save metadata
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

    return {
        "name": "Wikipedia",
        "url": f"https://{lang_code}.wikipedia.org/",
        "license": "CC BY-SA 3.0 / CC BY-SA 4.0",
        "language": lang_code,
        "download_date": datetime.now(timezone.utc).isoformat(),
        "record_count": len(processed_records),
        "notes": f"{len(articles)} articles downloaded, {len(processed_records)} passages extracted",
    }


# ---------------------------------------------------------------------------
# Build retrieval pool from processed knowledge
# ---------------------------------------------------------------------------

def build_pool_from_processed(lang: str) -> list[dict]:
    """Load all processed knowledge for a language and return as pool records."""
    records = []
    proc_dir = PROC_KNOWLEDGE_DIR

    for p in proc_dir.glob(f"*_{lang}.jsonl"):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    return records


def build_pools_for_all_languages() -> dict[str, int]:
    """Build retrieval pools for all languages from processed knowledge.

    Returns a dict mapping language code to number of passages in pool.
    """
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

        # Deduplicate by pid
        seen_pids = set()
        unique_records = []
        for r in records:
            if r["pid"] not in seen_pids:
                seen_pids.add(r["pid"])
                unique_records.append(r)

        # Save combined pool
        pool_path = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
        with open(pool_path, "w", encoding="utf-8") as f:
            for r in unique_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        results[lang] = len(unique_records)
        print(f"  {lang}: {len(unique_records)} passages in pool")

    return results


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def ingest_all(langs: list[str] = None, articles_per_lang: int = ARTICLES_PER_LANG) -> dict:
    """Run the full ingestion pipeline for all languages.

    Returns a dictionary with metadata about what was ingested.
    """
    if langs is None:
        langs = list(LANGS.keys())

    results = {}

    for lang in langs:
        print(f"\n{'='*60}")
        print(f"Processing language: {lang}")
        print(f"{'='*60}")

        # Download and process Wikipedia
        meta = ingest_wikipedia(lang, articles_per_lang)
        results[lang] = meta

    # Build combined pools
    print(f"\n{'='*60}")
    print("Building retrieval pools")
    print(f"{'='*60}")
    pool_results = build_pools_for_all_languages()
    results["pools"] = pool_results

    return results


if __name__ == "__main__":
    ingest_all()