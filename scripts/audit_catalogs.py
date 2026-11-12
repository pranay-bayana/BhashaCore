"""Script to audit translation keys across all 6 catalogs."""

import json
from pathlib import Path

CATALOGS_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "localization" / "catalogs"
LANGS = ["en", "hi", "te", "ta", "kn", "ml"]

def main():
    catalogs = {}
    for l in LANGS:
        p = CATALOGS_DIR / f"{l}.json"
        with open(p, "r", encoding="utf-8") as f:
            catalogs[l] = json.load(f)

    en_keys = set(catalogs["en"].keys())
    print(f"Total English keys: {len(en_keys)}")

    all_keys = set(en_keys)
    for l in LANGS[1:]:
        lang_keys = set(catalogs[l].keys())
        missing = en_keys - lang_keys
        extra = lang_keys - en_keys
        print(f"[{l.upper()}] Keys: {len(lang_keys)} | Missing: {len(missing)} | Extra: {len(extra)}")
        if missing:
            print(f"  Missing sample: {list(missing)[:5]}")

if __name__ == "__main__":
    main()
