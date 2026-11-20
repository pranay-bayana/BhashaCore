import json
from datetime import datetime, timedelta, timezone

import pytest

import src.app as app_module
from src.auth import GuestSession, db


EXTENSION_HEADERS = {
    "Origin": "chrome-extension://abcdefghijklmnopabcdefghijklmnop",
    "X-BhashaCore-Extension": "1",
}


@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, ALLOW_ANONYMOUS_CHAT=True)
    with app_module.app.app_context():
        app_module.limiter.reset()
        db.drop_all()
        db.create_all()
    with app_module.app.test_client() as test_client:
        yield test_client


def response_for(items):
    return json.dumps({"translations": [{"id": item["id"], "text": f"translated {item['text']}"} for item in items]})


def test_translation_requires_chrome_extension_origin(client):
    response = client.post("/api/translate", json={"target_lang": "hi", "segments": [{"id": "a", "text": "Hello"}]})
    assert response.status_code == 403
    assert response.get_json()["error"] == "extension_origin_required"


def test_translation_validates_request_bounds(client):
    response = client.post("/api/translate", json={"target_lang": "xx", "segments": []}, headers=EXTENSION_HEADERS)
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_translation_request"
    response = client.post("/api/translate", json={"target_lang": "hi", "segments": [{"id": "a", "text": "x" * 801}]}, headers=EXTENSION_HEADERS)
    assert response.status_code == 400
    assert "too long" in response.get_json()["message"]


def test_translation_maps_validated_provider_json_and_is_cors_enabled(client, monkeypatch):
    items = [{"id": "a", "text": "Hello"}, {"id": "b", "text": "World"}]
    monkeypatch.setattr(app_module, "_live_provider_answer", lambda *_args, **_kwargs: response_for(items))
    response = client.post("/api/translate", json={"target_lang": "te", "segments": items}, headers=EXTENSION_HEADERS)
    assert response.status_code == 200
    assert response.get_json() == {"target_lang": "te", "translations": [{"id": "a", "text": "translated Hello"}, {"id": "b", "text": "translated World"}]}
    assert response.headers["Access-Control-Allow-Origin"] == EXTENSION_HEADERS["Origin"]


def test_translation_rejects_malformed_provider_mapping(client, monkeypatch):
    monkeypatch.setattr(app_module, "_live_provider_answer", lambda *_args, **_kwargs: '{"translations":[{"id":"wrong","text":"bad"}]}')
    response = client.post("/api/translate", json={"target_lang": "ta", "segments": [{"id": "a", "text": "Hello"}]}, headers=EXTENSION_HEADERS)
    assert response.status_code == 502
    assert response.get_json()["error"] == "translation_response_invalid"


def test_translation_normalizes_provider_timeout_without_exposing_details(client, monkeypatch):
    def timeout(*_args, **_kwargs):
        raise app_module.ProviderGenerationError(code="provider_timeout", status_code=None, latency_ms=123)
    monkeypatch.setattr(app_module, "_live_provider_answer", timeout)
    response = client.post("/api/translate", json={"target_lang": "ta", "segments": [{"id": "a", "text": "Hello"}]}, headers=EXTENSION_HEADERS)
    assert response.status_code == 504
    payload = response.get_json()
    assert payload["error"] == "provider_timeout"
    assert "123" not in payload["message"]


def test_translation_never_reserves_or_consumes_chat_guest_quota(client, monkeypatch):
    items = [{"id": "a", "text": "Hello"}]
    monkeypatch.setattr(app_module, "_live_provider_answer", lambda *_args, **_kwargs: response_for(items))
    guest_id = "translator-guest"
    with app_module.app.app_context():
        db.session.add(GuestSession(
            id=guest_id, message_count=0,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            data_json='{"conversations":{}}',
        ))
        db.session.commit()
    with client.session_transaction() as session:
        session["guest_id"] = guest_id
    response = client.post("/api/translate", json={"target_lang": "ml", "segments": items}, headers=EXTENSION_HEADERS)
    assert response.status_code == 200
    with app_module.app.app_context():
        refreshed = app_module.db.session.get(app_module.GuestSession, guest_id)
        assert refreshed.message_count == 0


def test_translation_preflight_is_limited_to_extension_origin(client):
    response = client.options("/api/translate", headers=EXTENSION_HEADERS)
    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Headers"] == "Content-Type, X-BhashaCore-Extension"
    assert client.options("/api/translate").status_code == 403


@pytest.mark.parametrize("content", [
    "not json",
    '{"translations":[]}',
    '{"translations":[{"id":"a","text":""}]}',
])
def test_provider_response_validation_rejects_invalid_output(content):
    with pytest.raises(ValueError):
        app_module._parse_translation_result(content, {"a"})
