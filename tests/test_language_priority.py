"""Tests for language priority order and natural language response instructions.

Priority Order:
1. Explicit language instruction in latest message
2. Previously established language preference in current conversation
3. Manually selected language in language selector
4. Auto-detected language of current user message
"""
import json
import pytest
from src.app import app, db
from src.lang_instruction import (
    extract_language_instruction,
    strip_language_instruction,
    detect_user_input_language,
    build_language_system_directive,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def _chat_req(client, payload):
    defaults = {"session_id": "test-sess", "mode": "rag"}
    defaults.update(payload)
    resp = client.post(
        "/api/chat",
        data=json.dumps(defaults),
        content_type="application/json",
    )
    events = []
    for line in resp.get_data(as_text=True).splitlines():
        if line.strip():
            try:
                events.append(json.loads(line))
            except Exception:
                pass
    return resp, events


def _done_event(events):
    return next((e for e in events if e.get("type") == "done"), None)


class TestLanguageExtraction:
    def test_explicit_instructions(self):
        cases = [
            ("Explain photosynthesis in Telugu", "te", False, False),
            ("List major government schemes in India in English", "en", False, False),
            ("Tell me about solar energy in Tamil please", "ta", False, False),
            ("Answer this question in Hindi", "hi", False, False),
            ("give the answer in Kannada", "kn", False, False),
            ("Explain climate change in Malayalam", "ml", False, False),
            ("దీనికి సమాధానం తెలుగులో ఇవ్వండి", "te", False, False),
            ("Yeh sawal ka jawab Hindi me do", "hi", False, False),
            ("Idhuku badhil Tamil la sollunga", "ta", False, False),
        ]
        for text, expected_lang, expected_persistent, expected_reset in cases:
            res = extract_language_instruction(text)
            assert res["explicit_lang"] == expected_lang, f"Failed on: {text}"
            assert res["is_persistent"] == expected_persistent, f"Failed persistence on: {text}"
            assert res["is_reset"] == expected_reset, f"Failed reset on: {text}"

    def test_persistent_instructions(self):
        cases = [
            ("From now on, answer in Telugu", "te", True, False),
            ("Always respond in English in this conversation", "en", True, False),
            ("Continue answering in Hindi", "hi", True, False),
            ("Ab se Hindi me batao", "hi", True, False),
            ("Ippati nunchi Telugu lo cheppandi", "te", True, False),
            ("Inime Tamil la sollunga", "ta", True, False),
        ]
        for text, expected_lang, expected_persistent, expected_reset in cases:
            res = extract_language_instruction(text)
            assert res["explicit_lang"] == expected_lang, f"Failed on: {text}"
            assert res["is_persistent"] is True, f"Failed persistence on: {text}"

    def test_reset_instructions(self):
        cases = [
            ("Switch back to auto-detect", None, False, True),
            ("reset language", None, False, True),
            ("back to auto-detect", None, False, True),
            ("ఆటో-డిటెక్ట్", None, False, True),
            ("தானியங்கு", None, False, True),
        ]
        for text, expected_lang, expected_persistent, expected_reset in cases:
            res = extract_language_instruction(text)
            assert res["is_reset"] is True, f"Failed reset on: {text}"

    def test_strip_instructions(self):
        assert strip_language_instruction("Explain photosynthesis in Telugu") == "Explain photosynthesis"
        assert strip_language_instruction("List government schemes in English.") == "List government schemes"
        assert strip_language_instruction("Tell me about solar energy in Tamil please") == "Tell me about solar energy"


class TestLanguageDetection:
    def test_english_query_detection(self):
        # The exact query that previously failed
        assert detect_user_input_language("List major government schemes in India") == "en"
        assert detect_user_input_language("What is photosynthesis?") == "en"
        assert detect_user_input_language("How to maintain a healthy lifestyle?") == "en"
        assert detect_user_input_language("Explain climate change in simple terms") == "en"

    def test_indic_native_scripts(self):
        assert detect_user_input_language("భారతదేశంలో ప్రధాన ప్రభుత్వ పథకాలు ఏమిటి?") == "te"
        assert detect_user_input_language("भारत में प्रमुख सरकारी योजनाएं क्या हैं?") == "hi"
        assert detect_user_input_language("இந்தியாவில் உள்ள முக்கிய அரசு திட்டங்கள் யாவை?") == "ta"
        assert detect_user_input_language("ಭಾರತದಲ್ಲಿನ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಯಾವುವು?") == "kn"
        assert detect_user_input_language("ഭാരതത്തിലെ പ്രധാന സർക്കാർ പദ്ധതികൾ ഏവ?") == "ml"


class TestSystemDirective:
    def test_directive_content(self):
        directive_en = build_language_system_directive("en")
        assert "MANDATORY LANGUAGE DIRECTIVE" in directive_en
        assert "English" in directive_en
        assert "factual evidence" in directive_en

        directive_te = build_language_system_directive("te")
        assert "Telugu" in directive_te
        assert "Telugu script" in directive_te

        directive_ta = build_language_system_directive("ta")
        assert "Tamil" in directive_ta
        assert "Tamil script" in directive_ta


class TestChatLanguagePriorityFlow:
    def test_auto_detect_english_query_resolves_to_english(self, client, monkeypatch):
        """English query in auto-detect mode MUST resolve answer_lang='en', NEVER Tamil ('ta')."""
        from tests.test_multilingual import _force_dataset_gold
        _force_dataset_gold(monkeypatch)

        payload = {
            "session_id": "test-lang-en-1",
            "question": "List major government schemes in India",
            "input_lang": "auto",
            "eval_mode": True,
        }
        resp, events = _chat_req(client, payload)
        assert resp.status_code == 200
        done = _done_event(events)
        assert done is not None
        assert done["answer_lang"] == "en"
        assert done["input_lang"] == "en"

    def test_manual_selection_overrides_autodetect(self, client, monkeypatch):
        """Selected Telugu + English question -> Telugu answer."""
        from tests.test_multilingual import _force_dataset_gold
        _force_dataset_gold(monkeypatch)

        payload = {
            "session_id": "test-lang-te-override",
            "question": "What is photosynthesis?",
            "input_lang": "auto",
            "answer_lang": "te",
            "eval_mode": True,
        }
        resp, events = _chat_req(client, payload)
        assert resp.status_code == 200
        done = _done_event(events)
        assert done is not None
        assert done["answer_lang"] == "te"

    def test_manual_english_selection_with_indic_question(self, client, monkeypatch):
        """Selected English + Telugu question -> English answer."""
        from tests.test_multilingual import _force_dataset_gold
        _force_dataset_gold(monkeypatch)

        payload = {
            "session_id": "test-lang-en-override",
            "question": "భారతదేశంలో ప్రధాన ప్రభుత్వ పథకాలు ఏమిటి?",
            "input_lang": "auto",
            "answer_lang": "en",
            "eval_mode": True,
        }
        resp, events = _chat_req(client, payload)
        assert resp.status_code == 200
        done = _done_event(events)
        assert done is not None
        assert done["answer_lang"] == "en"

    def test_explicit_instruction_in_message_highest_priority(self, client, monkeypatch):
        """Explicit 'in Telugu' in query overrides manual 'en' selection."""
        from tests.test_multilingual import _force_dataset_gold
        _force_dataset_gold(monkeypatch)

        payload = {
            "session_id": "test-lang-explicit",
            "question": "List major government schemes in India in Telugu",
            "input_lang": "auto",
            "answer_lang": "en",  # manual selector says en, but prompt says Telugu!
            "eval_mode": True,
        }
        resp, events = _chat_req(client, payload)
        assert resp.status_code == 200
        done = _done_event(events)
        assert done is not None
        assert done["answer_lang"] == "te"

    def test_persistent_preference_across_turns(self, client, monkeypatch):
        """'From now on, answer in Kannada' persists until 'Switch back to auto-detect'."""
        from tests.test_multilingual import _force_dataset_gold
        _force_dataset_gold(monkeypatch)

        sid = "test-lang-persist-session"

        # Turn 1: Set persistence to Kannada
        p1 = {
            "session_id": sid,
            "question": "From now on, answer in Kannada: What is solar energy?",
            "input_lang": "auto",
            "eval_mode": True,
        }
        _, ev1 = _chat_req(client, p1)
        d1 = _done_event(ev1)
        assert d1["answer_lang"] == "kn"

        # Turn 2: Follow-up question in English without explicit instruction -> remains Kannada!
        p2 = {
            "session_id": sid,
            "question": "How does it generate electricity?",
            "input_lang": "auto",
            "eval_mode": True,
        }
        _, ev2 = _chat_req(client, p2)
        d2 = _done_event(ev2)
        assert d2["answer_lang"] == "kn"

        # Turn 3: Reset to auto-detect
        p3 = {
            "session_id": sid,
            "question": "Switch back to auto-detect: What is rainfall?",
            "input_lang": "auto",
            "eval_mode": True,
        }
        _, ev3 = _chat_req(client, p3)
        d3 = _done_event(ev3)
        assert d3["answer_lang"] == "en"  # reverted to auto-detected English!
