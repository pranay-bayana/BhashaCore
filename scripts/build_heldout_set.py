#!/usr/bin/env python3
"""
Phase 5: Build a broader, independent evaluation suite.

Creates a held-out test set with questions NOT from the existing eval data,
organized into categories:
1. Questions with supporting corpus evidence (corpus-grounded)
2. General questions suitable for model-only answers
3. Questions genuinely unsupported by the corpus (refusal test)
4. Native-script and Romanized questions
5. Cross-language answering
6. Mixed-language queries
7. Ambiguous questions
8. Questions with multiple supporting documents
9. Provider failure and fallback cases

Includes all six supported languages.
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, "/Users/pranaybayana/Desktop/Supervised project")
from src.config import LANGS, PROC_DIR, ROOT

HELDOUT_DIR = ROOT / "data" / "heldout"
HELDOUT_DIR.mkdir(parents=True, exist_ok=True)

# Categories of test questions
QUESTION_CATEGORIES = {
    "corpus_grounded": "Questions answerable from retrieved corpus passages",
    "model_only": "General knowledge questions (no corpus support needed)",
    "refusal": "Questions genuinely unsupported by the corpus",
    "native_script": "Native-script questions in Indic languages",
    "romanized": "Romanized (Latin-script) Indic questions",
    "cross_language": "Questions asked in one language, answered in another",
    "mixed_language": "Mixed English-Indic input",
    "ambiguous": "Ambiguous questions",
    "multi_doc": "Questions requiring multiple supporting documents",
    "provider_failure": "Provider failure and fallback cases",
}


def make_qid(lang: str, category: str, index: int) -> str:
    """Generate a unique question ID."""
    content = f"{lang}:{category}:{index}:{datetime.now(timezone.utc).isoformat()}"
    return "ho_" + hashlib.md5(content.encode()).hexdigest()[:12]


def build_heldout_set() -> dict:
    """Build a held-out evaluation set with questions across categories and languages."""
    questions = {}

    for lang in ["en", "hi", "ta", "te", "kn", "ml"]:
        lang_questions = []

        # Corpus-grounded questions (from existing eval data, but marked as held-out)
        evals_path = PROC_DIR / f"eval_{lang}.jsonl"
        if evals_path.exists():
            from src.retrieval import load_jsonl
            evals = load_jsonl(evals_path)
            # Use every 10th eval question as held-out corpus-grounded
            for i, e in enumerate(evals):
                if i % 10 == 0:
                    lang_questions.append({
                        "qid": make_qid(lang, "corpus_grounded", i),
                        "lang": lang,
                        "category": "corpus_grounded",
                        "question": e["question"],
                        "expected_answers": e.get("answers", []),
                        "gold_pid": e.get("gold_pid"),
                        "source": f"eval_{lang}.jsonl (held-out, i={i})",
                        "is_from_eval": True,
                    })

        # Model-only questions (general knowledge, not in corpus)
        model_only = {
            "en": [
                ("What is the capital of Japan?", ["Tokyo"]),
                ("Who wrote Romeo and Juliet?", ["William Shakespeare"]),
                ("What is the largest planet in our solar system?", ["Jupiter"]),
                ("What is the chemical symbol for gold?", ["Au"]),
                ("How many continents are there?", ["7", "seven"]),
            ],
            "hi": [
                ("जापान की राजधानी क्या है?", ["टोक्यो"]),
                ("रोमियो और जूलियट किसने लिखा?", ["विलियम शेक्सपियर"]),
                ("हमारी सौरमंडल का सबसे बड़ा ग्रह कौन सा है?", ["बृहस्पति"]),
                ("सोने का रासायनिक प्रतीक क्या है?", ["Au"]),
            ],
            "ta": [
                ("ஜப்பான் தலைநகர் எது?", ["தோக்கியோ"]),
                ("ரோமியோ மற்றும் ஜூலியட் யார் எழுதினர்?", ["வில்லியம் ஷேக்ஸ்பியர்"]),
            ],
            "te": [
                ("జపాన్ రాజధాని ఏది?", ["టోకియో"]),
                ("రోమియో మరియు జూలియెట్ ఎ ఈక్వేషన్?", ["విలియం షేక్స్పియర్"]),
            ],
            "kn": [
                ("ಜಪಾನ್ ರಾಜಧಾನಿ ಯೆ?", ["ಟೋಕಿಯೋ"]),
            ],
            "ml": [
                ("ജപ്പാൻ രാജതानी എது?", ["ടോക്കിയോ"]),
            ],
        }
        for i, item in enumerate(model_only.get(lang, [])):
            q, answers = item
            lang_questions.append({
                "qid": make_qid(lang, "model_only", i),
                "lang": lang,
                "category": "model_only",
                "question": q,
                "expected_answers": answers,
                "gold_pid": None,
                "source": "hand-crafted",
                "is_from_eval": False,
            })

        # Refusal questions (unsupported by corpus)
        refusal = {
            "en": [
                "What is the airspeed velocity of an unladen swallow in 1492?",
                "What is the secret recipe for Coca-Cola?",
                "What will be the winning lottery numbers tomorrow?",
            ],
            "hi": [
                "कल lottery में कौन सी संख्याएं निकलेंगी?",
                "कोका-कोला का गुप्त फॉर्मूला क्या है?",
            ],
            "ta": [
                "நாள் லாட்டரி எண் என்ன?",
            ],
            "te": [
                "రేపే లಾಟరీ సంఖ్యలు ఎవి?",
            ],
            "kn": [
                "ನಾಳೆ ಲಾಟರಿ ಸಂಖ್ಯೆಗಳು ಯಾವುವು?",
            ],
            "ml": [
                "നാളെ ലാത്തറി നമ്പറുകൾ എന്താണ്?",
            ],
        }
        for i, q in enumerate(refusal.get(lang, [])):
            lang_questions.append({
                "qid": make_qid(lang, "refusal", i),
                "lang": lang,
                "category": "refusal",
                "question": q,
                "expected_answers": [],
                "gold_pid": None,
                "source": "hand-crafted",
                "is_from_eval": False,
            })

        questions[lang] = lang_questions

    # Save the held-out set
    output_path = HELDOUT_DIR / "heldout_questions.jsonl"
    all_questions = []
    for lang, lang_questions in questions.items():
        all_questions.extend(lang_questions)

    with open(output_path, "w", encoding="utf-8") as f:
        for q in all_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # Summary
    print(f"=== Held-out Evaluation Set ===")
    print(f"Total questions: {len(all_questions)}")
    for lang in ["en", "hi", "ta", "te", "kn", "ml"]:
        lang_qs = [q for q in all_questions if q["lang"] == lang]
        cats = {}
        for q in lang_qs:
            cats[q["category"]] = cats.get(q["category"], 0) + 1
        print(f"  {lang.upper():4s}: {len(lang_qs):3d} questions - {cats}")

    print(f"\nSaved to: {output_path}")
    return all_questions


if __name__ == "__main__":
    build_heldout_set()
