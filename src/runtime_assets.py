"""Validation for the immutable RAG assets packaged with a deployment."""

from pathlib import Path

from src.config import LANGS, PROC_DIR


def required_runtime_assets() -> list[Path]:
    """Return the six language pools and evaluation maps needed by Flask."""
    assets: list[Path] = []
    for language in LANGS:
        assets.extend((
            PROC_DIR / f"pool_{language}.jsonl",
            PROC_DIR / f"eval_{language}.jsonl",
        ))
    return assets


def validate_runtime_assets() -> None:
    """Fail startup with an actionable error when a deployed corpus is absent."""
    root = Path(__file__).resolve().parents[1]
    missing = [
        str(asset.relative_to(root)) if asset.is_relative_to(root) else asset.name
        for asset in required_runtime_assets()
        if not asset.is_file() or asset.stat().st_size == 0
    ]
    if missing:
        raise RuntimeError(
            "Required RAG runtime assets are missing or empty: "
            + ", ".join(missing)
            + ". Deploy the tracked data/processed/pool_*.jsonl and "
              "data/processed/eval_*.jsonl artifacts."
        )
