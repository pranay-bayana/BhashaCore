"""Tests for the dedicated BhashaCore Application Guide assistant."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE_DATA_FILE = ROOT / "frontend" / "src" / "components" / "guide" / "guideData.ts"


def test_guide_data_file_exists():
    assert GUIDE_DATA_FILE.exists(), "guideData.ts must exist"


def test_all_twelve_required_topics_covered():
    content = GUIDE_DATA_FILE.read_text(encoding="utf-8")
    required_ids = [
        "new_chat",
        "six_languages",
        "auto_detection",
        "manual_selection",
        "explicit_instructions",
        "persistent_preferences",
        "rag_retrieval",
        "citations_evidence",
        "guest_trial",
        "signin_history",
        "research_dashboard",
        "capabilities_limitations",
    ]
    for topic_id in required_ids:
        assert f"id: '{topic_id}'" in content, f"Missing required topic: {topic_id}"


def test_six_languages_supported_in_guide():
    content = GUIDE_DATA_FILE.read_text(encoding="utf-8")
    languages = ["en:", "hi:", "te:", "ta:", "kn:", "ml:"]
    for lang in languages:
        assert lang in content, f"Language key {lang} not found in guideData.ts"


def test_guide_component_integrated_in_app():
    app_tsx = (ROOT / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "BhashaCoreGuide" in app_tsx, "BhashaCoreGuide must be imported and mounted in App.tsx"
    assert "<BhashaCoreGuide" in app_tsx, "<BhashaCoreGuide must be rendered in App.tsx"


def test_guide_does_not_call_chat_api_or_consume_quota():
    """Verify Guide component does NOT POST to /api/chat or consume guest trial slots."""
    guide_tsx = (ROOT / "frontend" / "src" / "components" / "guide" / "BhashaCoreGuide.tsx").read_text(encoding="utf-8")
    assert "/api/chat" not in guide_tsx, "Guide must be separate from the main chat API"
    assert "guest_message_count" not in guide_tsx, "Guide must not mutate guest message count"
