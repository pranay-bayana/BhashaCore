import json
import uuid
import pytest
from src import app as app_mod
from src.auth import db, User, Conversation, Message, GuestSession

@pytest.fixture()
def client():
    app_mod.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, ALLOW_ANONYMOUS_CHAT=True)
    with app_mod.app.app_context():
        app_mod.limiter.reset()
        db.drop_all()
        db.create_all()
        yield app_mod.app.test_client()

def test_guest_session_continuity_stays_separate_after_authentication(client, monkeypatch):
    # Persistence and ownership do not require a real external completion.
    monkeypatch.setattr(app_mod, "_live_provider_answer", lambda messages: "Test completion")
    # 1. Fresh guest -> 0/3
    st = client.get("/api/guest-status").get_json()
    assert st["authenticated"] is False
    assert st["guest_message_count"] == 0
    assert st["guest_quota_reached"] is False
    assert st["guest_remaining"] == 3

    # History starts empty
    hist = client.get("/api/history").get_json()
    assert hist["histories"] == []

    # 2. First successful response
    sid = "guest-sess-1"
    q1 = "What is photosynthesis?"
    r1 = client.post("/api/chat", json={"session_id": sid, "question": q1, "lang": "en"})
    assert r1.status_code == 200

    # Status is now 1/3
    st1 = client.get("/api/guest-status").get_json()
    assert st1["guest_message_count"] == 1
    assert st1["guest_remaining"] == 2

    # History now contains the guest conversation
    hist1 = client.get("/api/history").get_json()
    assert len(hist1["histories"]) == 1
    assert hist1["histories"][0]["session_id"] == sid
    assert "photosynthesis" in hist1["histories"][0]["title"].lower()

    # /api/load-chat returns the messages
    load1 = client.post("/api/load-chat", json={"session_id": sid}).get_json()
    assert load1["status"] == "loaded"
    msgs = load1["session"]["messages"]
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == q1
    assert msgs[1]["role"] == "assistant"

    # 3. Duplicate request should NOT increment quota
    dup = client.post("/api/chat", json={"session_id": sid, "question": q1, "lang": "en"})
    assert dup.status_code == 200
    st_dup = client.get("/api/guest-status").get_json()
    assert st_dup["guest_message_count"] == 1, "Duplicate question must not increment quota"

    # 4. Failed request (e.g. invalid json or unsupported language) should NOT increment quota
    bad = client.post("/api/chat", json={"session_id": sid, "question": "Invalid", "lang": "invalid_lang_code"})
    assert bad.status_code == 400
    st_bad = client.get("/api/guest-status").get_json()
    assert st_bad["guest_message_count"] == 1, "Failed request must not increment quota"

    # 5. Second response in a different conversation (separate chat test)
    sid2 = "guest-sess-2"
    q2 = "Explain climate change"
    r2 = client.post("/api/chat", json={"session_id": sid2, "question": q2, "lang": "en"})
    assert r2.status_code == 200
    st2 = client.get("/api/guest-status").get_json()
    assert st2["guest_message_count"] == 2

    hist2 = client.get("/api/history").get_json()
    assert len(hist2["histories"]) == 2

    # 6. Third response (reaches 3/3 limit)
    q3 = "List major government schemes"
    r3 = client.post("/api/chat", json={"session_id": sid2, "question": q3, "lang": "en"})
    assert r3.status_code == 200
    st3 = client.get("/api/guest-status").get_json()
    assert st3["guest_message_count"] == 3
    assert st3["guest_quota_reached"] is True
    assert st3["guest_remaining"] == 0

    # A second successful turn in the same temporary conversation appends to
    # its transcript instead of replacing the first turn.
    sid2_messages = client.post("/api/load-chat", json={"session_id": sid2}).get_json()["session"]["messages"]
    assert [message["content"] for message in sid2_messages if message["role"] == "user"] == [q2, q3]

    # 7. Fourth response -> 403 Forbidden guest_quota_exceeded
    r4 = client.post("/api/chat", json={"session_id": sid2, "question": "Fourth Question", "lang": "en"})
    assert r4.status_code == 403
    assert r4.get_json()["error"] == "guest_quota_exceeded"

    # 8. User signs up/in -> guest conversations stay isolated from the account.
    email = f"guest-converted-{uuid.uuid4().hex[:8]}@example.com"
    signup_res = client.post("/api/auth/signup", json={
        "name": "Converted Guest",
        "email": email,
        "password": "SecurePassword123!Safe",
    })
    assert signup_res.status_code == 200

    # Status is now authenticated
    st_auth = client.get("/api/guest-status").get_json()
    assert st_auth["authenticated"] is True
    assert st_auth["guest_quota_reached"] is False

    # Guest conversations remain temporary and must never become authenticated
    # account history merely because the browser signs in.
    auth_hist = client.get("/api/history").get_json()
    sids = [h["session_id"] for h in auth_hist["histories"]]
    assert sid not in sids
    assert sid2 not in sids

    # Authenticated user can continue chatting freely without 403 quota lock!
    auth_chat = client.post("/api/chat", json={"session_id": "auth-owned-chat", "question": "Question 4 as Authenticated", "lang": "en"})
    assert auth_chat.status_code == 200


def test_guest_provider_failure_does_not_consume_trial(client, monkeypatch):
    def unavailable(*args, **kwargs):
        raise TimeoutError("provider timed out")

    monkeypatch.setattr(app_mod, "answer_question", unavailable)
    response = client.post("/api/chat", json={
        "session_id": "failed-guest-request", "question": "Will this fail?", "lang": "en",
    })
    assert response.status_code == 503
    assert response.get_json() == {
        "error": "generation_error",
        "message": "The AI service is temporarily unavailable. Please retry once.",
        "retryable": True,
    }
    status = client.get("/api/guest-status").get_json()
    assert status["guest_message_count"] == 0
    assert client.get("/api/history").get_json()["histories"] == []


def test_guest_reservations_cap_parallel_generation_at_three(client):
    from flask import session
    from src.auth import release_guest_response, reserve_guest_response

    with app_mod.app.test_request_context("/"):
        _, first, _ = reserve_guest_response(session, "first")
        _, second, _ = reserve_guest_response(session, "second")
        guest, third, _ = reserve_guest_response(session, "third")
        _, fourth, _ = reserve_guest_response(session, "fourth")
        assert (first, second, third, fourth) == ("reserved", "reserved", "reserved", "quota")
        assert release_guest_response(guest.id, "third") == 0
        _, replacement, _ = reserve_guest_response(session, "replacement")
        assert replacement == "reserved"
