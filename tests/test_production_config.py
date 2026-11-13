"""Tests for production environment configuration requirements."""

import os
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run_app_import_with_env(env_overrides: dict[str, str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", "import wsgi"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


def test_production_requires_flask_secret_key():
    res = _run_app_import_with_env({"APP_ENV": "production", "FLASK_SECRET_KEY": ""})
    assert res.returncode != 0
    assert "FLASK_SECRET_KEY is required when APP_ENV=production" in res.stderr


def test_production_requires_redis_url():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "",
    })
    assert res.returncode != 0
    assert "REDIS_URL is required when APP_ENV=production" in res.stderr


def test_production_requires_session_cookie_secure():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "false",
    })
    assert res.returncode != 0
    assert "SESSION_COOKIE_SECURE=true is required when APP_ENV=production" in res.stderr


def test_production_requires_database_url_postgresql():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "",
    })
    assert res.returncode != 0
    assert "DATABASE_URL is required when APP_ENV=production" in res.stderr

    res_sqlite = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "sqlite:///local.sqlite3",
    })
    assert res_sqlite.returncode != 0
    assert "DATABASE_URL must use PostgreSQL when APP_ENV=production" in res_sqlite.stderr


def test_production_requires_trusted_hosts():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "",
    })
    assert res.returncode != 0
    assert "TRUSTED_HOSTS is required when APP_ENV=production" in res.stderr


def test_production_sarvam_requires_sarvam_api_key():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "bhashacore.onrender.com",
        "GENERATION_PROVIDER": "sarvam",
        "SARVAM_API_KEY": "",
    })
    assert res.returncode != 0
    assert "SARVAM_API_KEY is required when GENERATION_PROVIDER=sarvam in production" in res.stderr


def test_production_rejects_unsupported_generation_provider():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "bhashacore.onrender.com",
        "GENERATION_PROVIDER": "openai",
    })
    assert res.returncode != 0
    assert "GENERATION_PROVIDER must be sarvam or nvidia in production" in res.stderr


def test_production_configuration_valid_startup():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key-high-entropy-production",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "bhashacore.onrender.com,127.0.0.1",
        "GENERATION_PROVIDER": "sarvam",
        "SARVAM_API_KEY": "test_sarvam_key",
        "SARVAM_MODEL": "sarvam-105b-conversations",
    })
    assert res.returncode == 0, f"Startup failed with: {res.stderr}"


def test_production_allows_guest_chat_by_default():
    res = _run_app_import_with_env({
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key-high-entropy-production",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "bhashacore.onrender.com,127.0.0.1",
        "GENERATION_PROVIDER": "sarvam",
        "SARVAM_API_KEY": "test_sarvam_key",
        "SARVAM_MODEL": "sarvam-105b-conversations",
    })
    assert res.returncode == 0, f"Startup failed with: {res.stderr}"

    env = dict(os.environ, **{
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key-high-entropy-production",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "bhashacore.onrender.com,127.0.0.1",
        "GENERATION_PROVIDER": "sarvam",
        "SARVAM_API_KEY": "test_sarvam_key",
        "SARVAM_MODEL": "sarvam-105b-conversations",
    })
    res_code = subprocess.run(
        [sys.executable, "-c", "import wsgi; assert wsgi.app.config['ALLOW_ANONYMOUS_CHAT'] is True"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res_code.returncode == 0, res_code.stderr


def test_production_disables_guest_chat_when_explicitly_configured():
    env = dict(os.environ, **{
        "APP_ENV": "production",
        "FLASK_SECRET_KEY": "test-secret-key-high-entropy-production",
        "REDIS_URL": "redis://localhost:6379/0",
        "SESSION_COOKIE_SECURE": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "TRUSTED_HOSTS": "bhashacore.onrender.com,127.0.0.1",
        "GENERATION_PROVIDER": "sarvam",
        "SARVAM_API_KEY": "test_sarvam_key",
        "SARVAM_MODEL": "sarvam-105b-conversations",
        "ALLOW_ANONYMOUS_CHAT": "false",
    })
    res_code = subprocess.run(
        [sys.executable, "-c", "import wsgi; assert wsgi.app.config['ALLOW_ANONYMOUS_CHAT'] is False"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res_code.returncode == 0, res_code.stderr


def test_render_blueprint_matches_repo_spec():
    import yaml

    render_path = ROOT / "render.yaml"
    assert render_path.is_file(), "render.yaml must exist"
    data = yaml.safe_load(render_path.read_text(encoding="utf-8"))
    assert "services" in data
    assert len(data["services"]) == 1
    service = data["services"][0]

    assert service["type"] == "web"
    assert service["name"] == "bhashacore"
    assert service["runtime"] == "python"
    assert service["plan"] == "free"
    assert service["startCommand"] == "flask --app wsgi db upgrade && gunicorn --config gunicorn.conf.py wsgi:app"
    assert service["healthCheckPath"] == "/health"
    assert "pip install" in service["buildCommand"]
    assert "npm run build" in service["buildCommand"]
    assert "preDeployCommand" not in service

    # Verify python version matches .python-version
    py_version_file = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    env_vars = {item["key"]: item.get("value") for item in service["envVars"]}
    assert env_vars.get("PYTHON_VERSION") == py_version_file
    assert env_vars.get("NODE_VERSION") == "22.14.0"
    assert env_vars.get("WEB_CONCURRENCY") == "1"
    assert env_vars.get("GENERATION_PROVIDER") == "sarvam"
    assert env_vars.get("SARVAM_MODEL") == "sarvam-105b-conversations"
    assert env_vars.get("APP_ENV") == "production"
    assert env_vars.get("SESSION_COOKIE_SECURE") == "true"
