from src.retrieval import load_jsonl
from src.config import PROC_DIR

for lang in ['en', 'hi', 'ta', 'te', 'kn', 'ml']:
    pool_file = PROC_DIR / f'pool_{lang}.jsonl'
    kn_file = PROC_DIR / f'pool_{lang}_knowledge.jsonl'
    pools = load_jsonl(pool_file) if pool_file.exists() else []
    kno = load_jsonl(kf) if kf.exists() else []
    print(f'{lang.upper()}: base_pool={len(pools)}, knowledge={len(kno)}, total={len(pools)+len(kno)}')
EOF
