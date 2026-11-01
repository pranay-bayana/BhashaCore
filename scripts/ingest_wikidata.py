#!/usr/bin/env python3
"""
Wikidata ingestion pipeline for BhashaCore knowledge base.

Wikidata provides structured multilingual entity data (labels, descriptions,
aliases) under CC0 license. This is an alternative source when Wikipedia
is rate-limited.

Usage:
    python scripts/ingest_wikidata.py --langs en hi ta te kn ml --entities-per-lang 100
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import LANGS, PROC_DIR, ROOT

KNOWLEDGE_DIR = ROOT / "data" / "knowledge"
RAW_DIR = KNOWLEDGE_DIR / "raw" / "wikidata"
PROC_KNOWLEDGE_DIR = KNOWLEDGE_DIR / "processed"
METADATA_DIR = KNOWLEDGE_DIR / "metadata"

for _d in (KNOWLEDGE_DIR, RAW_DIR, PROC_KNOWLEDGE_DIR, METADATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

USER_AGENT = "BhashaCore/1.0 (research project; contact: research@example.com)"

WIKIDATA_API = "https://www.wikidata.org/w/api.php"

# Notable entity QIDs to seed each language (broad coverage: people, places,
# organisations, concepts). These are language-neutral Wikidata items.
SEED_QIDS = [
    "Q668",      # India
    "Q593",      # Delhi
    "Q1384",     # Mumbai
    "Q1604",     # Kolkata
    "Q60",       # Tamil Nadu
    "Q1605",     # Hyderabad
    "Q1606",     # Bengaluru
    "Q1549",     # Kerala
    "Q1266",     # Karnataka
    "Q1339",     # Gujarat
    "Q1544",     # Maharashtra
    "Q1616",     # Uttar Pradesh
    "Q1609",     # Bihar
    "Q1563",     # Assam
    "Q1568",     # Odisha
    "Q1533",     # Punjab
    "Q1571",     # Rajasthan
    "Q1548",     # Madhya Pradesh
    "Q1622",     # West Bengal
    "Q30",       # United States
    "Q33",       # France
    "Q145",      # United Kingdom
    "Q183",      # Germany
    "Q155",      # Japan
    "Q17",       # China
    "Q142",      # Egypt
    "Q39",       # Brazil
    "Q45",       # Canada
    "Q16",       # Russia
    "Q801",      # Mahatma Gandhi
    "Q408",      # Jawaharlal Nehru
    "Q12216",    # Indira Gandhi
    "Q316",      # Albert Einstein
    "Q937",      # Isaac Newton
    "Q7258",     # Charles Darwin
    "Q520",      # Leonardo da Vinci
    "Q42946",    # Marie Curie
    "Q8436",     # Rabindranath Tagore
    "Q1369",     # C. V. Raman
    "Q5061",     # Mother Teresa
    "Q7480",     # APJ Abdul Kalam
    "Q163918",   # Narendra Modi
    "Q1833",     # World War II
    "Q1870",     # Indian independence movement
    "Q19653",    # Mughal Empire
    "Q841",      # Maurya Empire
    "Q1517",     # Gupta Empire
    "Q802",      # Delhi Sultanate
    "Q326",      # Hinduism
    "Q8294",     # Buddhism
    "Q9547",     # Jainism
    "Q188",      # Sikhism
    "Q395",      # Islam
    "Q196",      # Christianity
    "Q285",      # Cricket
    "Q2980",     # Football
    "Q156",      # Olympic Games
    "Q11455",    # Hindi language
    "Q7965",     # Tamil language
    "Q33365",    # Telugu language
    "Q33332",    # Kannada language
    "Q36372",    # Malayalam language
    "Q1297",     # English language
    "Q1435",     # Sanskrit language
    "Q1323",     # Ganges
    "Q1326",     # Yamuna
    "Q1325",     # Brahmaputra
    "Q1508",     # Himalayas
    "Q47126",    # Thar Desert
    "Q275",      # Asia
    "Q300",      # Europe
    "Q15",       # Africa
    "Q46",       # North America
    "Q49",       # South America
    "Q399",      # Australia
    "Q742",      # Antarctica
    "Q114",      # Taj Mahal
    "Q23554",    # Red Fort
    "Q183226",   # Qutub Minar
    "Q15423",    # Gateway of India
    "Q8824",     # ISRO
    "Q1561",     # Indian Railways
    "Q15442",    # Reserve Bank of India
    "Q1783036",  # Supreme Court of India
    "Q1783033",  # Parliament of India
    "Q1036",     # Currency
    "Q37341",    # Indian Rupee
    "Q150",      # Rupee
]


def normalize_text(text: str) -> str:
    if not text:
        return ""
    import unicodedata
    import re
    text = unicodedata.normalize("NFC", text)
    text = "".join(c for c in text if unicodedata.category(c) != "C" or c in "\n\t")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_passages(text: str, max_chars: int = 500, overlap: int = 50) -> list:
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    import re
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


def wikidata_lang_code(lang: str) -> str:
    """Map BhashaCore lang code to Wikidata language code."""
    return {
        "en": "en",
        "hi": "hi",
        "ta": "ta",
        "te": "te",
        "kn": "kn",
        "ml": "ml",
    }[lang]


def search_entities(lang_code: str, query: str, limit: int = 20) -> list:
    """Search Wikidata for entities matching a query in a language."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": lang_code,
        "format": "json",
        "limit": limit,
        "type": "item",
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.get(
                WIKIDATA_API,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
                verify=False,
            )
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  [Wikidata] 429 rate limit, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return data.get("search", [])
        except Exception as e:
            print(f"  [Wikidata] Search error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return []


def fetch_entity(qid: str, lang_code: str) -> dict | None:
    """Fetch a Wikidata entity with labels/descriptions in a language."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels|descriptions|aliases",
        "languages": lang_code,
        "format": "json",
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.get(
                WIKIDATA_API,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
                verify=False,
            )
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  [Wikidata] 429 rate limit, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            entities = data.get("entities", {})
            if qid in entities:
                return entities[qid]
            return None
        except Exception as e:
            print(f"  [Wikidata] Fetch error for {qid} (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return None


def ingest_wikidata(lang: str, entities_per_lang: int = 100) -> dict:
    """Ingest Wikidata entities for a language."""
    lang_code = wikidata_lang_code(lang)
    print(f"\n[Wikidata {lang}] Fetching up to {entities_per_lang} entities...")

    # Collect QIDs: seed QIDs + search results
    collected_qids = set()
    all_entities = []

    # First, try seed QIDs
    seed_batch = SEED_QIDS[:entities_per_lang]
    for qid in seed_batch:
        entity = fetch_entity(qid, lang_code)
        if entity:
            all_entities.append(entity)
            collected_qids.add(qid)
        time.sleep(0.5)  # be polite

    # Then search for additional entities
    search_queries = [
        "India", "Delhi", "Mumbai", "Kolkata", "Bengaluru", "Hyderabad",
        "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "Sanskrit",
        "cricket", "football", "Olympics", "Gandhi", "Nehru", "Tagore",
        "Himalayas", "Ganges", "Taj Mahal", "ISRO",
    ]
    for query in search_queries:
        if len(all_entities) >= entities_per_lang:
            break
        results = search_entities(lang_code, query, limit=10)
        for result in results:
            qid = result.get("id")
            if qid and qid not in collected_qids and len(all_entities) < entities_per_lang:
                entity = fetch_entity(qid, lang_code)
                if entity:
                    all_entities.append(entity)
                    collected_qids.add(qid)
                time.sleep(0.5)
        time.sleep(1)

    print(f"  Fetched {len(all_entities)} entities")

    if not all_entities:
        return None

    # Save raw data
    raw_dir = RAW_DIR / lang
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"wikidata_{lang}_raw.jsonl"
    with open(raw_path, "w", encoding="utf-8") as f:
        for entity in all_entities:
            f.write(json.dumps(entity, ensure_ascii=False) + "\n")

    # Process into passages
    processed_records = []
    seen_texts = set()

    for entity in all_entities:
        qid = entity.get("id", "")
        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        aliases = entity.get("aliases", {})

        label = labels.get(lang_code, {}).get("value", "")
        description = descriptions.get(lang_code, {}).get("value", "")
        alias_entries = aliases.get(lang_code, [])
        alias_list = [a.get("value", "") for a in alias_entries if isinstance(a, dict)]

        # Build passage text
        parts = []
        if label:
            parts.append(label)
        if description:
            parts.append(description)
        if alias_list:
            parts.append("Also known as: " + ", ".join(alias_list))

        text = normalize_text(". ".join(parts))
        if not text or len(text) < 20:
            continue

        passages = split_into_passages(text, max_chars=500, overlap=50)
        for passage in passages:
            passage_norm = passage.strip()
            if not passage_norm or len(passage_norm) < 20:
                continue
            if passage_norm in seen_texts:
                continue
            seen_texts.add(passage_norm)
            pid = "wd_" + hashlib.md5(f"{lang}:{qid}:{passage_norm}".encode()).hexdigest()[:16]
            record = {
                "pid": pid,
                "lang": lang,
                "source": "wikidata",
                "source_url": f"https://www.wikidata.org/wiki/{qid}",
                "title": label or qid,
                "text": passage_norm,
                "category": "wikidata",
                "wikidata_id": qid,
            }
            processed_records.append(record)

    # Write processed knowledge
    proc_path = PROC_KNOWLEDGE_DIR / f"wikidata_{lang}.jsonl"
    with open(proc_path, "w", encoding="utf-8") as f:
        for record in processed_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    metadata = {
        "name": "Wikidata",
        "url": "https://www.wikidata.org/",
        "license": "CC0 1.0 Universal",
        "language": lang,
        "download_date": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "record_count": len(processed_records),
        "notes": f"{len(all_entities)} entities fetched, {len(processed_records)} passages extracted",
    }
    metadata_path = METADATA_DIR / f"wikidata_{lang}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

    print(f"  Processed {len(processed_records)} passages from {len(all_entities)} entities")
    return metadata


def rebuild_pools() -> dict[str, int]:
    """Rebuild pool_{lang}_knowledge.jsonl from all processed knowledge sources."""
    results = {}
    for lang in LANGS:
        records = []
        for p in PROC_KNOWLEDGE_DIR.glob(f"*_{lang}.jsonl"):
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


def main():
    ap = argparse.ArgumentParser(description="Ingest Wikidata knowledge for BhashaCore")
    ap.add_argument("--langs", nargs="+", default=["en", "hi", "ta", "te", "kn", "ml"])
    ap.add_argument("--entities-per-lang", type=int, default=100)
    args = ap.parse_args()

    results = {}
    for lang in args.langs:
        meta = ingest_wikidata(lang, args.entities_per_lang)
        results[lang] = meta
        time.sleep(2)  # delay between languages

    print(f"\n{'='*60}")
    print("Rebuilding retrieval pools")
    print(f"{'='*60}")
    pool_results = rebuild_pools()
    results["pools"] = pool_results

    print(f"\n{'='*60}")
    print("INGESTION COMPLETE")
    print(f"{'='*60}")
    return results


if __name__ == "__main__":
    main()
