"""Language instruction and priority resolution system for BhashaCore.

Handles:
1. Natural language response instructions in user messages (e.g. 'Explain in Telugu').
2. Persistent conversation language preferences ('From now on, answer in Hindi').
3. Reset instructions ('Switch back to auto-detect').
4. Exact language priority ordering:
   1) Explicit instruction in latest message
   2) Previously established conversation preference
   3) Manual language selector
   4) Auto-detected language of user message
5. Generation system prompt language directives.
"""
from __future__ import annotations

import re
from src.config import LANGS, INDIC_LANGS

LANG_MAP: dict[str, str] = {
    # English
    "english": "en",
    "inglish": "en",
    "angrezi": "en",
    "angreezi": "en",
    "aanglam": "en",
    "aangilam": "en",
    "इंग्लिश": "en",
    "अंग्रेजी": "en",
    "अंग्रेज़ी": "en",
    "ఇంగ్లీష్": "en",
    "ఆంగ్లం": "en",
    "ஆங்கிலம்": "en",
    "ಇಂಗ್ಲಿಷ್": "en",
    "ഇംഗ്ലീഷ്": "en",

    # Hindi
    "hindi": "hi",
    "hindustani": "hi",
    "हिंदी": "hi",
    "हिन्दी": "hi",
    "హిందీ": "hi",
    "இந்தி": "hi",
    "ಹಿಂದಿ": "hi",
    "ഹിന്ദി": "hi",

    # Telugu
    "telugu": "te",
    "telegu": "te",
    "telugulo": "te",
    "telugula": "te",
    "తెలుగు": "te",
    "తెలుగులో": "te",
    "तेलुगु": "te",
    "தெலுங்கு": "te",
    "ತೆಲುಗು": "te",
    "തെലുങ്ക്": "te",

    # Tamil
    "tamil": "ta",
    "tamizh": "ta",
    "thamizh": "ta",
    "tamilil": "ta",
    "tamizhil": "ta",
    "thamizhil": "ta",
    "தமிழ்": "ta",
    "தமிழில்": "ta",
    "तमिल": "ta",
    "తమిళం": "ta",
    "తమిళంలో": "ta",
    "ತಮಿಳು": "ta",
    "തമിഴ്": "ta",

    # Kannada
    "kannada": "kn",
    "kanada": "kn",
    "kannadadalli": "kn",
    "kannadalli": "kn",
    "ಕನ್ನಡ": "kn",
    "ಕನ್ನಡದಲ್ಲಿ": "kn",
    "कन्नड़": "kn",
    "కన్నడ": "kn",
    "కన్నడంలో": "kn",
    "கன்னடம்": "kn",
    "കന്നഡ": "kn",

    # Malayalam
    "malayalam": "ml",
    "malayaalam": "ml",
    "malayalathil": "ml",
    "malayaalathil": "ml",
    "മലയാളം": "ml",
    "മലയാളത്തിൽ": "ml",
    "मलयालम": "ml",
    "మలయాళం": "ml",
    "మలయాళంలో": "ml",
    "மலையாளம்": "ml",
}

RESET_PATTERNS = [
    r"\b(?:switch\s+(?:back\s+)?to|back\s+to|reset\s+(?:language\s+to\s+)?|go\s+back\s+to)?\s*auto[-\s]?detect\b",
    r"\breset\s+language\b",
    r"\bdefault\s+language\b",
    r"ऑटो[-\s]?डिटेक्ट",
    r"ఆటో[-\s]?డిటెక్ట్",
    r"தானியங்கு",
    r"ಆಟೋ[-\s]?ಡಿಟೆಕ್ಟ್",
    r"ഓട്ടോ[-\s]?ഡിറ്റക്ട്",
]

PERSISTENT_PATTERNS = [
    r"\bfrom\s+now\s+on\b",
    r"\balways\b",
    r"\bcontinue\s+(?:replying|answering|responding|speaking)?\b",
    r"\bgoing\s+forward\b",
    r"\bhenceforth\b",
    r"\bfor\s+(?:the\s+rest\s+of\s+)?this\s+(?:chat|conversation)\b",
    r"\bab\s+se\b",
    r"\baage\s+se\b",
    r"\bhamesha\b",
    r"अब\s*से",
    r"आगे\s*से",
    r"हमेशा",
    r"\bippati\s+nunchi\b",
    r"\bika\s+nunchi\b",
    r"\bika\s*pai\b",
    r"ఇప్పటి\s*(?:నుండి|నుంచి)",
    r"ఇక\s*నుండి",
    r"ఇకపై",
    r"ఎల్లప్పుడూ",
    r"\binime\b",
    r"\binimel\b",
    r"இனிமேல்",
    r"எப்போதும்",
    r"\billiinda\b",
    r"\binnumunde\b",
    r"ಇಲ್ಲಿಂದ",
    r"ಇನ್ನು\s*ಮುಂದೆ",
    r"ಯಾವಾಗಲೂ",
    r"\bini\s+muthal\b",
    r"\bini\s+thottu\b",
    r"ഇനി\s*മുതൽ",
    r"എപ്പോഴും",
]

DIRECTIVE_PATTERNS = [
    # English directive phrases
    (r"\b(?:answer|respond|reply|explain|tell|speak|write|give(?:\s+the)?\s+answer|output|translate)\s+(?:this|it|me)?\s*(?:only\s+|all\s+)?(?:in|using)\s+([A-Za-z]+)\b", 1),
    (r"\b(?:can\s+you\s+|please\s+)?(?:explain|answer|respond|reply|write|give)\s+(?:this\s+)?in\s+([A-Za-z]+)\b", 1),
    (r"\bI\s+want\s+(?:the\s+)?(?:response|answer|reply)\s+in\s+([A-Za-z]+)\b", 1),
    (r"\b(?:respond|answer|reply)\s+only\s+in\s+([A-Za-z]+)\b", 1),
    (r"\b(?:always|continue)\s+(?:replying|answering|responding|speaking)\s+in\s+([A-Za-z]+)\b", 1),
    (r"\b(?:in|into|using)\s+([A-Za-z]+)(?:\s+(?:only|please))?[\s.?!,]*$", 1),
    (r"^([A-Za-z]+)\s+only\b", 1),
    (r"^([A-Za-z]+)\s+please\b", 1),

    # Romanized Indic
    (r"\b([A-Za-z]+)\s*lo\s*(?:cheppu|cheppandi|ivvandi|raayi|rayandi|kavali|samadhanam|answer|vivarinchu|vivarinchandi)\b", 1),
    (r"\b(?:samadhanam|answer|jawab)\s+([A-Za-z]+)\s*lo\b", 1),
    (r"\b([A-Za-z]+)\s*lo[\s.?!,]*$", 1),
    (r"\b([A-Za-z]+)\s*me(?:in)?\s*(?:do|dijiye|batao|bataiye|samjhao|likho|bolo|jawab|uttar|kaho)\b", 1),
    (r"\b(?:jawab|uttar|answer)\s+([A-Za-z]+)\s*me(?:in)?\b", 1),
    (r"\b([A-Za-z]+)\s*me(?:in)?[\s.?!,]*$", 1),
    (r"\b([A-Za-z]+)\s*(?:la|il)\s*(?:sollunga|solla|pesunga|ezhudhunga|badhil|vilakkunga)\b", 1),
    (r"\b(?:badhil|answer)\s+([A-Za-z]+)\s*(?:la|il)\b", 1),
    (r"\b([A-Za-z]+)\s*(?:la|il)[\s.?!,]*$", 1),
    (r"\b([A-Za-z]+)\s*(?:dalli|alli)\s*(?:heli|helri|uttarisi|vivarisi|bari|bariyiri)\b", 1),
    (r"\b([A-Za-z]+)\s*(?:thil|il)\s*(?:parayuka|parayu|parayamo|utharam|ezhuthu)\b", 1),

    # Native scripts
    (r"([^\s]+)\s*లో\s*(?:సమాధానం|జవాబు|చెప్పు|చెప్పండి|ఇవ్వండి|రాయండి|రాయి|కావాలి|తెలుపండి|వివరించండి)", 1),
    (r"(?:సమాధానం|జవాబు)\s*([^\s]+)\s*లో", 1),
    (r"([^\s]+)లో\s*సమాధానం", 1),
    (r"([^\s]+)లో[\s.,!?]*$", 1),
    (r"([^\s]+)\s*में\s*(?:जवाब|उत्तर|बताओ|बताइए|समझाओ|समझाइए|लिखिए|लिखो|दीजिए|दो|चाहिए)", 1),
    (r"(?:जवाब|उत्तर)\s*([^\s]+)\s*में", 1),
    (r"([^\s]+)\s*में[\s.,!?]*$", 1),
    (r"([^\s]+)\s*(?:லில்|ல்|இல்)\s*(?:பதில்|விடை|சொல்லுங்கள்|கூறுங்கள்|எழுதுங்கள்|விளக்குங்கள்)", 1),
    (r"(?:பதில்|விடை)\s*([^\s]+)\s*(?:லில்|ல்|இல்)", 1),
    (r"([^\s]+)(?:லில்|ல்|இல்)[\s.,!?]*$", 1),
    (r"([^\s]+)\s*(?:ದಲ್ಲಿ|ನಲ್ಲಿ)\s*(?:ಉತ್ತರ|ಹೇಳಿ|ವಿವರಿಸಿ|ಕೊಡಿ|ಬರೆಯಿರಿ)", 1),
    (r"(?:ಉತ್ತರ)\s*([^\s]+)\s*(?:ದಲ್ಲಿ|ನಲ್ಲಿ)", 1),
    (r"([^\s]+)\s*(?:ത്തിൽ|ൽ|യിൽ)\s*(?:ഉത്തരം|മറുപടി|പറയൂ|നൽകൂ|എഴുതൂ|വിശദീകരിക്കൂ)", 1),
    (r"(?:ഉത്തരം|മറുപടി)\s*([^\s]+)\s*(?:ത്തിൽ|ൽ|യിൽ)", 1),
]

ROMANIZED_MARKERS: dict[str, set[str]] = {
    "hi": {
        "kya", "hai", "hain", "kaise", "kahan", "kyun", "hoga", "hogi", "nahi", "nahin",
        "apna", "mera", "meri", "tere", "tera", "batao", "bataiye", "karo", "kijiye",
        "raha", "rahe", "rahi", "mein", "aur", "chahiye", "samjhao", "dijiye", "shuru"
    },
    "te": {
        "enti", "emiti", "ela", "elaga", "evaru", "ekkada", "enduku", "cheppu", "cheppandi",
        "cheyyali", "undi", "unnaru", "leka", "ante", "ani", "gurinchi", "meeda", "kosam",
        "ippudu", "appudu", "eppudu", "kavali", "chala", "ledu", "ledhu", "ivvandi", "raayi"
    },
    "ta": {
        "enna", "eppadi", "yaar", "enge", "yen", "edhukku", "solla", "sollunga", "pannu",
        "pannunga", "irukku", "irukkanga", "illai", "illa", "paththi", "patti", "kaga",
        "ippo", "eppo", "venum", "kudunga", "parunga", "theriyuma", "romba"
    },
    "kn": {
        "enu", "hege", "yaaru", "elli", "yaake", "heli", "helri", "maadi", "madu", "ide",
        "idhe", "illa", "bagge", "kosama", "ega", "aaga", "yavaga", "beku", "kodi", "nodi",
        "gothilla", "chennagi", "thumba"
    },
    "ml": {
        "enthaanu", "enthanu", "enthina", "engine", "engane", "aaru", "evide", "enthukond",
        "parayamo", "parayu", "cheyyuka", "cheyyu", "undu", "illa", "kurichu", "vendathu",
        "ippol", "eppol", "venam", "tharu", "nokku"
    },
}


def extract_language_instruction(text: str) -> dict:
    """Parse language intent from user text.

    Returns:
      explicit_lang: 'en' | 'hi' | 'te' | 'ta' | 'kn' | 'ml' | None
      is_persistent: bool (e.g. 'from now on', 'always')
      is_reset: bool (e.g. 'switch back to auto-detect')
    """
    if not text or not text.strip():
        return {"explicit_lang": None, "is_persistent": False, "is_reset": False}

    cleaned = text.strip()

    # Check reset instruction
    for p in RESET_PATTERNS:
        if re.search(p, cleaned, re.IGNORECASE):
            return {"explicit_lang": None, "is_persistent": False, "is_reset": True}

    is_persistent = any(re.search(p, cleaned, re.IGNORECASE) for p in PERSISTENT_PATTERNS)

    explicit_lang = None
    for pattern, group_idx in DIRECTIVE_PATTERNS:
        m = re.search(pattern, cleaned, re.IGNORECASE)
        if m:
            raw_lang = m.group(group_idx).lower().strip(".,!?\'\"")
            if raw_lang in LANG_MAP:
                explicit_lang = LANG_MAP[raw_lang]
                break

    return {
        "explicit_lang": explicit_lang,
        "is_persistent": is_persistent,
        "is_reset": False,
    }


def strip_language_instruction(text: str) -> str:
    """Remove explicit language instructions from a question to get core query."""
    if not text:
        return ""
    cleaned = text
    # Strip trailing/leading directive patterns
    cleaned = re.sub(r"\b(?:in|into|using)\s+(?:english|hindi|telugu|tamil|kannada|malayalam)\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(
        r"\b(?:answer|respond|reply|explain|tell|speak|write|give(?:\s+the)?\s+answer|output|translate)\s+(?:this|it|me)?\s*(?:only\s+|all\s+)?(?:in|using)\s+(?:english|hindi|telugu|tamil|kannada|malayalam)\b.*$",
        "", cleaned, flags=re.I
    )
    cleaned = re.sub(r"\b(?:answer|respond|reply|explain)\s+in\s+[a-z]+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\b[a-z]+\s*lo\s*(?:cheppu|cheppandi|ivvandi|raayi|rayandi|kavali|samadhanam|answer|vivarinchu|vivarinchandi)\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\b[a-z]+\s*me(?:in)?\s*(?:do|dijiye|batao|bataiye|samjhao|likho|bolo|jawab|uttar|kaho)\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\b[a-z]+\s*(?:la|il)\s*(?:sollunga|solla|pesunga|ezhudhunga|badhil|vilakkunga)\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\b[a-z]+\s*(?:dalli|alli)\s*(?:heli|helri|uttarisi|vivarisi|bari|bariyiri)\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\b[a-z]+\s*(?:thil|il)\s*(?:parayuka|parayu|parayamo|utharam|ezhuthu)\b", "", cleaned, flags=re.I)

    # Native scripts
    cleaned = re.sub(r"[^\s]+\s*లో\s*(?:సమాధానం|జవాబు|చెప్పు|చెప్పండి|ఇవ్వండి|రాయండి|రాయి|కావాలి|తెలుపండి|వివరించండి)", "", cleaned)
    cleaned = re.sub(r"[^\s]+\s*में\s*(?:जवाब|उत्तर|बताओ|बताइए|समझाओ|समझाइए|लिखिए|लिखो|दीजिए|दो|चाहिए)", "", cleaned)
    cleaned = re.sub(r"[^\s]+\s*(?:லில்|ல்|இல்)\s*(?:பதில்|விடை|சொல்லுங்கள்|கூறுங்கள்|எழுதுங்கள்|விளக்குங்கள்)", "", cleaned)
    cleaned = re.sub(r"[^\s]+\s*(?:ದಲ್ಲಿ|ನಲ್ಲಿ)\s*(?:ಉತ್ತರ|ಹೇಳಿ|ವಿವರಿಸಿ|ಕೊಡಿ|ಬರೆಯಿರಿ)", "", cleaned)
    cleaned = re.sub(r"[^\s]+\s*(?:ത്തിൽ|ൽ|യിൽ)\s*(?:ഉത്തരം|മറുപടി|പറയൂ|നൽകൂ|എഴുതൂ|വിശദീകരിക്കൂ)", "", cleaned)

    cleaned = re.sub(r"[.,!?:;]+$", "", cleaned).strip()
    return cleaned if len(cleaned) >= 2 else text


def detect_romanized_indic_language(text: str) -> str | None:
    """Detect specific Romanized Indic language from distinctive vocabulary."""
    if not text:
        return None
    words = {w.lower().strip(".,!?\"\'") for w in text.split()}
    scores: dict[str, int] = {}
    for lang, markers in ROMANIZED_MARKERS.items():
        overlap = len(words & markers)
        if overlap > 0:
            scores[lang] = overlap
    if scores:
        return max(scores, key=scores.get)
    return None


def detect_user_input_language(text: str) -> str:
    """Determine the actual language of user input.

    Uses script purity for native Indic scripts (Devanagari, Telugu, Tamil,
    Kannada, Malayalam). For Latin-script text, checks for distinctive Romanized
    Indic tokens; if absent, defaults cleanly to English ('en').
    Does NOT use RAG retrieval cross-corpus guessing.
    """
    from src.langkit import detect_script_and_language

    detection = detect_script_and_language(text)
    script_lang = detection.get("lang")
    if script_lang in LANGS:
        return script_lang

    # Latin or mixed script: check for distinctive Romanized Indic tokens
    romanized_lang = detect_romanized_indic_language(text)
    if romanized_lang in LANGS:
        return romanized_lang

    # Default Latin to English
    return "en"


def build_language_system_directive(target_lang: str, answer_script: str = "native") -> str:
    """Generate the explicit, mandatory language instruction for the LLM prompt.

    Enforces that:
    - The LLM answers entirely in the resolved language.
    - It does not switch languages because retrieved passages are in another language.
    - Retrieved passages are treated strictly as factual evidence, not language guides.
    - Names, official scheme names, and technical terms are preserved.
    - If retrieved evidence is multilingual, it synthesizes it in the requested language.
    """
    meta = LANGS.get(target_lang, LANGS["en"])
    target_lang_name = meta["name"]
    target_script = meta["script"]

    if target_lang == "en" or answer_script == "latin":
        return (
            "MANDATORY LANGUAGE DIRECTIVE: You must generate the response ENTIRELY in English (using Latin script). "
            "Do not switch to any Indian language, even if the user question or retrieved context passages are in another language. "
            "Use the retrieved passages strictly as factual evidence, never as language-selection instructions. "
            "If retrieved evidence is multilingual or in another language, synthesize and translate the facts into English. "
            "Preserve official scheme names, entity names, and technical terms where appropriate."
        )

    if answer_script == "romanized":
        return (
            f"MANDATORY LANGUAGE DIRECTIVE: You must generate the response ENTIRELY in {target_lang_name} written in Latin script (Romanized {target_lang_name}). "
            f"Do not switch to any other language, even if the user question or retrieved context passages are in another language. "
            f"Use the retrieved passages strictly as factual evidence, never as language-selection instructions. "
            f"Synthesize and translate all facts into Romanized {target_lang_name}. "
            f"Preserve official scheme names, entity names, and technical terms where appropriate."
        )

    return (
        f"MANDATORY LANGUAGE DIRECTIVE: You must generate the response ENTIRELY in {target_lang_name} (written in the {target_script} script). "
        f"Do not switch to English or any other language, even if the user question or retrieved context passages are in another language. "
        f"Use the retrieved passages strictly as factual evidence, never as language-selection instructions. "
        f"If retrieved evidence is in English or another language, translate and synthesize the facts into {target_lang_name}. "
        f"Preserve official scheme names, entity names, and technical terms where appropriate."
    )
