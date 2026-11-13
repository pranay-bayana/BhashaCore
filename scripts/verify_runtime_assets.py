#!/usr/bin/env python3
"""Fail fast if the six-language RAG assets needed by a deployment are absent."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime_assets import required_runtime_assets, validate_runtime_assets


if __name__ == "__main__":
    validate_runtime_assets()
    for asset in required_runtime_assets():
        print(f"OK {asset.relative_to(ROOT)}")
