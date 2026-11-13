from pathlib import Path

import pytest

import src.runtime_assets as runtime_assets


def test_required_runtime_assets_cover_every_language():
    assets = runtime_assets.required_runtime_assets()
    assert len(assets) == 12
    for language in ("en", "hi", "te", "ta", "kn", "ml"):
        assert any(asset.name == f"pool_{language}.jsonl" for asset in assets)
        assert any(asset.name == f"eval_{language}.jsonl" for asset in assets)
    runtime_assets.validate_runtime_assets()


def test_runtime_asset_validation_explains_missing_corpus(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime_assets, "PROC_DIR", Path(tmp_path))
    with pytest.raises(RuntimeError, match="Required RAG runtime assets") as exc:
        runtime_assets.validate_runtime_assets()
    assert "pool_en.jsonl" in str(exc.value)
