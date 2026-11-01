#!/usr/bin/env python3
"""Add more Wikidata entities for under-represented languages."""
import hashlib
import json
import sys
import time
import unicodedata
import re
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/Users/pranaybayana/Desktop/Supervised project")
from src.config import LANGS, PROC_DIR
from src.knowledge import normalize_text, split_into_passages

import requests

USER_AGENT = "BhashaCore/1.0 (research project; contact: research@example.com)"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

KNOWLEDGE_DIR = Path("/Users/pranaybayana/Desktop/Supervised project/data/knowledge")
RAW_DIR = KNOWLEDGE_DIR / "raw"
METADATA_DIR = KNOWLEDGE_DIR / "MANIFESTS"

MORE_QUERIES = {
    "ml": ["Kerala", "Thiruvananthapuram", "Kochi", "Malayalam language", "Onam",
           "Sadhya", "Kathakali", "Mohiniyattam", "Backwaters", "Spices"],
    "te": ["Telangana", "Andhra Pradesh", "Telugu language", "Hyderabad",
           "Charminar", "Ugadi", "Kuchipudi"],
    "hi": ["Rajasthan", "Punjab", "Haryana", "Hindi language", "Diwali",
           "Holi", "Yoga", "Ayurveda"],
}

lang_code_map = {"en": "en", "hi": "hi", "ta": "ta", "te": "te", "kn": "kn", "ml": "ml"}


def load_existing_pids(lang):
    pool_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
    pids = set()
    if pool_file.exists():
        for line in pool_file.read_text(encoding="utf-8").strip().split("\n"):
            if line.strip():
                try:
                    pids.add(json.loads(line)["pid"])
                except json.JSONDecodeError:
                    pass
    return pids


def append_to_pool(lang, records):
    existing_pids = load_existing_pids(lang)
    pool_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
    new_records = 0
    with open(pool_file, "a", encoding="utf-8") as f:
        for r in records:
            if r["pid"] not in existing_pids:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                existing_pids.add(r["pid"])
                new_records += 1
    return new_records


def save_manifest(source, lang, meta):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    manifest_path = METADATA_DIR / f"{source}_{lang}_{timestamp}.json"
    manifest_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def wikidata_request(params, max_retries=5):
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
                wait = 15 * (attempt + 1)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return None


def search_entities(lang_code, query, limit=10):
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": lang_code,
        "format": "json",
        "limit": limit,
        "type": "item",
    }
    data = wikidata_request(params)
    return data.get("search", []) if data else []


def fetch_entity(qid, lang_code):
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels|descriptions|aliases",
        "languages": lang_code,
        "format": "json",
    }
    data = wikidata_request(params)
    if data and "entities" in data and qid in data["entities"]:
        return data["entities"][qid]
    return None


def main():
    seen_texts_global = set()
    total_new = 0

    for lang in ["ml", "te", "hi"]:
        lang_code = lang_code_map[lang]
        queries = MORE_QUERIES.get(lang, [])
        existing_pids = load_existing_pids(lang)
        all_records = []

        print(f"\n[{lang.upper()}] Searching {len(queries)} queries...")

        for query in queries:
            results = search_entities(lang_code, query, limit=10)
            for result in results:
                qid = result.get("id")
                if not qid:
                    continue
                entity = fetch_entity(qid, lang_code)
                if not entity:
                    time.sleep(0.7)
                    continue

                labels = entity.get("labels", {})
                descriptions = entity.get("descriptions", {})
                aliases = entity.get("aliases", {})

                label = labels.get(lang_code, {}).get("value", "")
                description = descriptions.get(lang_code, {}).get("value", "")
                alias_entries = aliases.get(lang_code, [])
                alias_list = [a.get("value", "") for a in alias_entries if isinstance(a, dict)]

                parts = []
                if label:
                    parts.append(label)
                if description:
                    parts.append(description)
                if alias_list:
                    parts.append("Also known as: " + ", ".join(alias_list))

                text = normalize_text(". ".join(parts))
                if not text or len(text) < 20:
                    time.sleep(0.7)
                    continue

                passages = split_into_passages(text, max_chars=500, overlap=50)
                for passage in passages:
                    p = passage.strip()
                    if not p or len(p) < 20 or p in seen_texts_global:
                        continue
                    seen_texts_global.add(p)
                    pid = "wd_" + hashlib.md5(f"{lang}:{qid}:{p}".encode()).hexdigest()[:16]
                    if pid in existing_pids:
                        continue
                    record = {
                        "pid": pid,
                        "lang": lang,
                        "source": "wikidata",
                        "source_url": f"https://www.wikidata.org/wiki/{qid}",
                        "title": label or qid,
                        "text": p,
                        "category": "wikidata",
                        "wikidata_id": qid,
                        "ingested_at": datetime.now(timezone.utc).isoformat(),
                    }
                    all_records.append(record)

                time.sleep(0.7)
            time.sleep(1.5)

        if all_records:
            new = append_to_pool(lang, all_records)
            total_new += new
            print(f"  Added {new} new records from {len(all_records)} passages")

            manifest = {
                "source": "wikidata",
                "url": "https://www.wikidata.org/",
                "license": "CC0 1.0 Universal",
                "language": lang,
                "download_date": datetime.now(timezone.utc).isoformat(),
                "record_count": len(all_records),
                "new_records": new,
                "notes": f"Additional Wikidata entities for {lang}",
            }
            save_manifest("wikidata_extra", lang, manifest)
        else:
            print("  No new records")

        time.sleep(5)

    print(f"\nTotal new Wikidata records: {total_new}")

    # Show final pool sizes
    print("\nFinal pool sizes:")
    for lang in ["en", "hi", "ta", "te", "kn", "ml"]:
        pool_file = PROC_DIR / f"pool_{lang}_knowledge.jsonl"
        if pool_file.exists():
            count = sum(1 for line in pool_file.read_text(encoding="utf-8").strip().split("\n") if line.strip())
            print(f"  {lang.upper()}: {count} passages")


if __name__ == "__main__":
    main()
