import sys
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Never let a developer's .env point deterministic test suite at external DB in sandbox
os.environ["DATABASE_URL"] = f"sqlite:///{ROOT / 'instance' / 'pytest_bhashacore.sqlite3'}"

from src.app import app, limiter

@pytest.fixture(autouse=True)
def disable_csrf_in_tests():
    app.config["WTF_CSRF_ENABLED"] = False
    try:
        limiter.reset()
    except Exception:
        pass
    yield
    app.config["WTF_CSRF_ENABLED"] = True
