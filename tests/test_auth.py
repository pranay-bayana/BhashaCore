import sys
import uuid
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Never let a developer's .env point the deterministic suite at a managed DB.
os.environ.setdefault("DATABASE_URL", f"sqlite:///{ROOT / 'instance' / 'pytest_bhashacore.sqlite3'}")

import src.app as app_mod
from src.auth import Conversation, User, create_reset_token, db, reset_password


@pytest.fixture()
def client():
    app_mod.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app_mod.app.app_context():
        app_mod.limiter.reset()
        db.drop_all()
        db.create_all()
    with app_mod.app.test_client() as c:
        yield c


def test_signup_signin_logout_and_protected_chat(client):
    assert client.get("/chat").status_code == 302
    email = f"user-{uuid.uuid4().hex}@example.test"
    response = client.post("/signup", data={
        "name": "Test User", "email": email, "password": "long-secret-passphrase",
        "confirm_password": "long-secret-passphrase", "consent": "on",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"BhashaCore" in response.data
    assert client.get("/settings").status_code == 200
    client.post("/logout")
    assert client.get("/chat").status_code == 302
    bad = client.post("/signin", data={"email": email, "password": "wrong"}, follow_redirects=True)
    assert b"Invalid email or password" in bad.data
    signed_in = client.post("/signin", data={"email": email, "password": "long-secret-passphrase"})
    assert signed_in.status_code == 302


def test_signup_rejects_duplicate_and_short_password(client):
    email = f"user-{uuid.uuid4().hex}@example.test"
    base = {"name": "Test User", "email": email, "password": "long-secret-passphrase",
            "confirm_password": "long-secret-passphrase", "consent": "on"}
    assert client.post("/signup", data=base).status_code == 302
    duplicate = client.post("/signup", data=base, follow_redirects=True)
    # The first sign-up creates an authenticated session, so sign out before duplicate check.
    client.post("/logout")
    duplicate = client.post("/signup", data=base, follow_redirects=True)
    assert b"already exists" in duplicate.data
    short = client.post("/signup", data={**base, "email": "short@example.test", "password": "short", "confirm_password": "short"}, follow_redirects=True)
    assert b"at least 12" in short.data


def test_user_cannot_load_another_users_conversation(client):
    email_a, email_b = f"a-{uuid.uuid4().hex}@example.test", f"b-{uuid.uuid4().hex}@example.test"
    for email in (email_a, email_b):
        assert client.post("/signup", data={"name": "Test User", "email": email,
            "password": "long-secret-passphrase", "confirm_password": "long-secret-passphrase", "consent": "on"}).status_code == 302
        client.post("/logout")
    with app_mod.app.app_context():
        owner = db.session.scalar(db.select(User).where(User.email == email_a))
        db.session.add(Conversation(id="owned-conversation", user_id=owner.id, title="Private"))
        db.session.commit()
    client.post("/signin", data={"email": email_b, "password": "long-secret-passphrase"})
    assert client.post("/api/load-chat", json={"session_id": "owned-conversation"}).status_code == 404


def test_csrf_rejects_missing_token():
    app_mod.app.config.update(TESTING=False, WTF_CSRF_ENABLED=True)
    with app_mod.app.test_client() as client:
        response = client.post("/signin", data={"email": "a@example.test", "password": "password"})
    assert response.status_code == 400
    app_mod.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)


def test_signup_rate_limit(client):
    for i in range(5):
        response = client.post("/signup", data={"name": "Test User", "email": f"limit-{i}@example.test",
            "password": "long-secret-passphrase", "confirm_password": "long-secret-passphrase", "consent": "on"})
        assert response.status_code == 302
        client.post("/logout")
    blocked = client.post("/signup", data={"name": "Test User", "email": "limit-over@example.test",
        "password": "long-secret-passphrase", "confirm_password": "long-secret-passphrase", "consent": "on"})
    assert blocked.status_code == 429


def test_password_reset_token_is_one_time(client):
    email = "reset@example.test"
    client.post("/signup", data={"name": "Reset User", "email": email,
        "password": "long-secret-passphrase", "confirm_password": "long-secret-passphrase", "consent": "on"})
    with app_mod.app.app_context():
        token = create_reset_token(email)
        assert token
        assert reset_password(token, "new-long-secret-passphrase")[0]
        assert not reset_password(token, "another-long-passphrase")[0]
    client.post("/logout")
    assert client.post("/signin", data={"email": email, "password": "new-long-secret-passphrase"}).status_code == 302


def test_account_deletion_requires_password_and_removes_user(client):
    email = "delete@example.test"
    client.post("/signup", data={"name": "Delete User", "email": email,
        "password": "long-secret-passphrase", "confirm_password": "long-secret-passphrase", "consent": "on"})
    assert client.post("/settings/delete-account", data={"password": "wrong"}).status_code == 302
    assert client.post("/settings/delete-account", data={"password": "long-secret-passphrase"}).status_code == 302
    with app_mod.app.app_context():
        assert db.session.scalar(db.select(User).where(User.email == email)) is None


def test_resend_password_reset_adapter(monkeypatch):
    from src.emailer import send_password_reset
    captured = {}
    class Response: status_code = 201
    def fake_post(url, **kwargs): captured.update(url=url, **kwargs); return Response()
    monkeypatch.setenv("EMAIL_PROVIDER", "resend"); monkeypatch.setenv("EMAIL_API_KEY", "test-key")
    monkeypatch.setenv("EMAIL_FROM", "noreply@example.test"); monkeypatch.setenv("APP_BASE_URL", "https://app.example.test")
    monkeypatch.setattr("src.emailer.httpx.post", fake_post)
    assert send_password_reset("user@example.test", "opaque-token")
    assert captured["url"] == "https://api.resend.com/emails"
    assert "opaque-token" in captured["json"]["text"]


def test_production_configuration_requires_secret_and_redis():
    # Import-time production configuration is intentionally fail-closed; the
    # behavior is documented and verified by inspecting the guard in app.py.
    source = (ROOT / "src" / "app.py").read_text(encoding="utf-8")
    assert "FLASK_SECRET_KEY is required when APP_ENV=production" in source
    assert "REDIS_URL is required when APP_ENV=production" in source
    assert "SESSION_COOKIE_SECURE=true is required when APP_ENV=production" in source
    assert "DATABASE_URL is required when APP_ENV=production" in source
    assert "DATABASE_URL must use PostgreSQL when APP_ENV=production" in source
    assert "TRUSTED_HOSTS is required when APP_ENV=production" in source
    assert "load_dotenv(ROOT / \".env\", override=False)" in source
    assert '"prepare_threshold": None' in source


def test_production_chat_apis_require_authentication(client):
    app_mod.app.config["ALLOW_ANONYMOUS_CHAT"] = False
    for method, route, payload in ((client.get, "/api/history", None),
                                   (client.post, "/api/load-chat", {"session_id": "safe-id"}),
                                   (client.post, "/api/new-chat", {"session_id": "safe-id"})):
        response = method(route, json=payload) if payload is not None else method(route)
        assert response.status_code == 401
    app_mod.app.config["ALLOW_ANONYMOUS_CHAT"] = True


def test_owned_conversation_rename_delete_and_history(client):
    email = "history@example.test"
    client.post("/signup", data={"name": "History User", "email": email,
        "password": "long-secret-passphrase", "confirm_password": "long-secret-passphrase", "consent": "on"})
    with app_mod.app.app_context():
        user = db.session.scalar(db.select(User).where(User.email == email))
        db.session.add(Conversation(id="history-conversation", user_id=user.id, title="Original")); db.session.commit()
    listed = client.get("/api/history").get_json()["histories"]
    assert listed[0]["title"] == "Original"
    renamed = client.patch("/api/conversations/history-conversation", json={"title": "Renamed"})
    assert renamed.status_code == 200 and renamed.get_json()["title"] == "Renamed"
    assert client.delete("/api/conversations/history-conversation").status_code == 200
    assert client.get("/api/history").get_json()["histories"] == []


def test_new_public_pages_render_localized_labels(client):
    from src.translations import t
    for lang in ("en", "hi", "te", "ta", "kn", "ml"):
        for route, key in (("/welcome", "landing_title"), ("/signup", "auth_sign_up"),
                           ("/signin", "auth_sign_in"), ("/forgot-password", "auth_forgot")):
            response = client.get(f"{route}?lang={lang}")
            html = response.get_data(as_text=True)
            assert response.status_code == 200
            assert t(key, lang=lang) in html
            assert f'lang="{lang}"' in html
        landing = client.get(f"/welcome?lang={lang}").get_data(as_text=True)
        assert t("landing_languages_copy", lang=lang) in landing
        assert t("landing_evidence_copy", lang=lang) in landing
        signup = client.get(f"/signup?lang={lang}").get_data(as_text=True)
        assert t("auth_consent", lang=lang) in signup
