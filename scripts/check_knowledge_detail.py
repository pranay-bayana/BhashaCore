from src.retrieval import load_jsonl
from src.config import PROC_DIR
import json

for lang in ['en', 'hi', 'ta', 'te', 'kn', 'ml']:
    kf = PROC_DIR / f'pool_{lang}_knowledge.jsonl'
    kno = load_jsonl(kf) if kf.exists() else []
    print(f'{lang.upper()}: {len(kno)} knowledge passages')
    for r in kno[:3]:
        print(f'  pid={r.get("pid","?")} lang={r.get("lang","?")} source={r.get("source","?")}')
        print(f"    title={r.get('title','')[:60]}")
        print(f"    text={r.get('text','')[:120]}")
        print()