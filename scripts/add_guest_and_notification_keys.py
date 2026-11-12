import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NEW_KEYS = {
    "en": {
        "notifications_title": "Notifications",
        "notifications_empty_title": "All caught up",
        "notifications_empty_desc": "You have no new notifications right now.",
        "notifications_mark_all_read": "Mark all as read",
        "notifications_clear": "Clear all",
        "notifications_system_label": "System",
        "notifications_research_label": "Research",
        "guest_trial_badge": "Free Guest Trial",
        "guest_trial_status": "{remaining} of 3 free questions remaining",
        "guest_limit_title": "You've reached the 3-question trial limit",
        "guest_limit_desc": "Create a free account or sign in to continue chatting, unlock unlimited questions, and save your conversation history across devices.",
        "guest_limit_composer_placeholder": "Trial limit reached (3/3) · Sign in to continue asking questions",
        "guest_sidebar_info": "Guest Session · In-memory only",
        "guest_sidebar_save_hint": "Conversations are kept in memory and not saved. Sign in to save and organize your conversation history.",
        "guest_signin_btn": "Sign in to continue",
        "guest_create_account_btn": "Create free account"
    },
    "hi": {
        "notifications_title": "सूचनाएं",
        "notifications_empty_title": "सब कुछ पढ़ लिया",
        "notifications_empty_desc": "आपके पास अभी कोई नई सूचना नहीं है।",
        "notifications_mark_all_read": "सभी पढ़े हुए चिह्नित करें",
        "notifications_clear": "सभी हटाएं",
        "notifications_system_label": "सिस्टम",
        "notifications_research_label": "अनुसंधान",
        "guest_trial_badge": "निःशुल्क अतिथि परीक्षण",
        "guest_trial_status": "3 में से {remaining} प्रश्न शेष",
        "guest_limit_title": "आप 3 प्रश्नों की परीक्षण सीमा तक पहुंच गए हैं",
        "guest_limit_desc": "बातचीत जारी रखने, असीमित प्रश्न पूछने और अपना बातचीत इतिहास सहेजने के लिए एक निःशुल्क खाता बनाएं या साइन इन करें।",
        "guest_limit_composer_placeholder": "परीक्षण सीमा समाप्त (3/3) · प्रश्न पूछना जारी रखने के लिए साइन इन करें",
        "guest_sidebar_info": "अतिथि सत्र · केवल मेमोरी में",
        "guest_sidebar_save_hint": "बातचीत केवल मेमोरी में रखी जाती है और सहेजी नहीं जाती है। अपने बातचीत इतिहास को सहेजने के लिए साइन इन करें।",
        "guest_signin_btn": "जारी रखने के लिए साइन इन करें",
        "guest_create_account_btn": "निःशुल्क खाता बनाएं"
    },
    "te": {
        "notifications_title": "నోటిఫికేషన్‌లు",
        "notifications_empty_title": "అన్నీ చూసేశారు",
        "notifications_empty_desc": "ప్రస్తుతం మీకు ఎలాంటి కొత్త నోటిఫికేషన్‌లు లేవు.",
        "notifications_mark_all_read": "అన్నీ చదివినట్లు గుర్తించండి",
        "notifications_clear": "అన్నీ తొలగించు",
        "notifications_system_label": "సిస్టమ్",
        "notifications_research_label": "పరిశోధన",
        "guest_trial_badge": "ఉచిత అతిథి ట్రయల్",
        "guest_trial_status": "3 ఉచిత ప్రశ్నలలో {remaining} మిగిలి ఉన్నాయి",
        "guest_limit_title": "మీరు 3 ప్రశ్నల ట్రయల్ పరిమితిని చేరుకున్నారు",
        "guest_limit_desc": "చాటింగ్ కొనసాగించడానికి, అపరిమిత ప్రశ్నలను అన్‌లాక్ చేయడానికి మరియు మీ సంభాషణ చరిత్రను సేవ్ చేయడానికి ఉచిత ఖాతాను సృష్టించండి లేదా సైన్ ఇన్ చేయండి.",
        "guest_limit_composer_placeholder": "ట్రయల్ పరిమితి ముగిసింది (3/3) · ప్రశ్నలు అడగడం కొనసాగించడానికి సైన్ ఇన్ చేయండి",
        "guest_sidebar_info": "అతిథి సెషన్ · మెమరీలో మాత్రమే",
        "guest_sidebar_save_hint": "సంభాషణలు మెమరీలో మాత్రమే ఉంచబడతాయి మరియు సేవ్ చేయబడవు. చరిత్రను సేవ్ చేయడానికి సైన్ ఇన్ చేయండి.",
        "guest_signin_btn": "కొనసాగించడానికి సైన్ ఇన్ చేయండి",
        "guest_create_account_btn": "ఉచిత ఖాతాను సృష్టించండి"
    },
    "ta": {
        "notifications_title": "அறிவிப்புகள்",
        "notifications_empty_title": "அனைத்தும் படிக்கப்பட்டன",
        "notifications_empty_desc": "உங்களுக்கு இப்போது புதிய அறிவிப்புகள் எதுவும் இல்லை.",
        "notifications_mark_all_read": "அனைத்தையும் படித்ததாகக் குறிக்கவும்",
        "notifications_clear": "அனைத்தையும் அழிக்கவும்",
        "notifications_system_label": "அமைப்பு",
        "notifications_research_label": "ஆராய்ச்சி",
        "guest_trial_badge": "இலவச விருந்தினர் சோதனை",
        "guest_trial_status": "3 இலவச கேள்விகளில் {remaining} மீதமுள்ளன",
        "guest_limit_title": "நீங்கள் 3 கேள்விகள் சோதனை வரம்பை அடைந்துவிட்டீர்கள்",
        "guest_limit_desc": "உரையாடலைத் தொடரவும், வரம்பற்ற கேள்விகளைத் திறக்கவும் மற்றும் உங்கள் உரையாடல் வரலாற்றைச் சேமிக்கவும் இலவச கணக்கை உருவாக்கவும் அல்லது உள்நுழையவும்.",
        "guest_limit_composer_placeholder": "சோதனை வரம்பு முடிந்தது (3/3) · தொடர்ந்து கேள்விகள் கேட்க உள்நுழையவும்",
        "guest_sidebar_info": "விருந்தினர் அமர்வு · நினைவகத்தில் மட்டுமே",
        "guest_sidebar_save_hint": "உரையாடல்கள் நினைவகத்தில் மட்டுமே வைக்கப்படுகின்றன, சேமிக்கப்படுவதில்லை. வரலாற்றைச் சேமிக்க உள்நுழையவும்.",
        "guest_signin_btn": "தொடர உள்நுழைக",
        "guest_create_account_btn": "இலவச கணக்கை உருவாக்கவும்"
    },
    "kn": {
        "notifications_title": "ಸೂಚನೆಗಳು",
        "notifications_empty_title": "ಎಲ್ಲವನ್ನೂ ಓದಲಾಗಿದೆ",
        "notifications_empty_desc": "ನಿಮಗೆ ಪ್ರಸ್ತುತ ಯಾವುದೇ ಹೊಸ ಸೂಚನೆಗಳಿಲ್ಲ.",
        "notifications_mark_all_read": "ಎಲ್ಲವನ್ನೂ ಓದಿದೆ ಎಂದು ಗುರುತಿಸಿ",
        "notifications_clear": "ಎಲ್ಲವನ್ನೂ ತೆರವುಗೊಳಿಸಿ",
        "notifications_system_label": "ವ್ಯವಸ್ಥೆ",
        "notifications_research_label": "ಸಂಶೋಧನೆ",
        "guest_trial_badge": "ಉಚಿತ ಅತಿಥಿ ಪ್ರಯೋಗ",
        "guest_trial_status": "3 ಉಚಿತ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ {remaining} ಉಳಿದಿವೆ",
        "guest_limit_title": "ನೀವು 3 ಪ್ರಶ್ನೆಗಳ ಪ್ರಯೋಗ ಮಿತಿಯನ್ನು ತಲುಪಿದ್ದೀರಿ",
        "guest_limit_desc": "ಸಂಭಾಷಣೆಯನ್ನು ಮುಂದುವರಿಸಲು, ಅನಿಯಮಿತ ಪ್ರಶ್ನೆಗಳನ್ನು ಅನ್‌ಲಾಕ್ ಮಾಡಲು ಮತ್ತು ನಿಮ್ಮ ಸಂಭಾಷಣೆ ಇತಿಹಾಸವನ್ನು ಉಳಿಸಲು ಉಚಿತ ಖಾತೆಯನ್ನು ರಚಿಸಿ ಅಥವಾ ಸೈನ್ ಇನ್ ಮಾಡಿ.",
        "guest_limit_composer_placeholder": "ಪ್ರಯೋಗ ಮಿತಿ ತಲುಪಿದೆ (3/3) · ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಲು ಸೈನ್ ಇನ್ ಮಾಡಿ",
        "guest_sidebar_info": "ಅತಿಥಿ ಅಧಿವೇಶನ · ಮೆಮೊರಿಯಲ್ಲಿ ಮಾತ್ರ",
        "guest_sidebar_save_hint": "ಸಂಭಾಷಣೆಗಳನ್ನು ಮೆಮೊರಿಯಲ್ಲಿ ಮಾತ್ರ ಇರಿಸಲಾಗುತ್ತದೆ ಮತ್ತು ಉಳಿಸಲಾಗುವುದಿಲ್ಲ. ಇತಿಹಾಸವನ್ನು ಉಳಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ.",
        "guest_signin_btn": "ಮುಂದುವರಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ",
        "guest_create_account_btn": "ಉಚಿತ ಖಾತೆಯನ್ನು ರಚಿಸಿ"
    },
    "ml": {
        "notifications_title": "അറിയിപ്പുകൾ",
        "notifications_empty_title": "എല്ലാം വായിച്ചു",
        "notifications_empty_desc": "നിങ്ങൾക്ക് ഇപ്പോൾ പുതിയ അറിയിപ്പുകളൊന്നുമില്ല.",
        "notifications_mark_all_read": "എല്ലാം വായിച്ചതായി അടയാളപ്പെടുത്തുക",
        "notifications_clear": "എല്ലാം മായ്‌ക്കുക",
        "notifications_system_label": "സിസ്റ്റം",
        "notifications_research_label": "ഗവേഷണം",
        "guest_trial_badge": "സൗജന്യ അതിഥി ട്രയൽ",
        "guest_trial_status": "3 സൗജന്യ ചോദ്യങ്ങളിൽ {remaining} ബാക്കിയുണ്ട്",
        "guest_limit_title": "നിങ്ങൾ 3 ചോദ്യങ്ങളുടെ ട്രയൽ പരിധിയിലെത്തി",
        "guest_limit_desc": "ചാറ്റിംഗ് തുടരുന്നതിനും പരിധിയില്ലാത്ത ചോദ്യങ്ങൾ അൺലോക്ക് ചെയ്യുന്നതിനും സംഭാഷണ ചരിത്രം സംരക്ഷിക്കുന്നതിനും ഒരു സൗജന്യ അക്കൗണ്ട് സൃഷ്ടിക്കുക അല്ലെങ്കിൽ സൈൻ ഇൻ ചെയ്യുക.",
        "guest_limit_composer_placeholder": "ട്രയൽ പരിധിയിലെത്തി (3/3) · ചോദ്യങ്ങൾ ചോദിക്കാൻ സൈൻ ഇൻ ചെയ്യുക",
        "guest_sidebar_info": "അതിഥി സെഷൻ · മെമ്മറിയിൽ മാത്രം",
        "guest_sidebar_save_hint": "സംഭാഷണങ്ങൾ മെമ്മറിയിൽ മാത്രമേ സൂക്ഷിക്കൂ, സേവ് ചെയ്യില്ല. ചരിത്രം സംരക്ഷിക്കാൻ സൈൻ ഇൻ ചെയ്യുക.",
        "guest_signin_btn": "തുടരാൻ സൈൻ ഇൻ ചെയ്യുക",
        "guest_create_account_btn": "സൗജന്യ അക്കൗണ്ട് സൃഷ്ടിക്കുക"
    }
}

for lang, keys in NEW_KEYS.items():
    # Update frontend
    fe_path = ROOT / "frontend" / "src" / "localization" / "catalogs" / f"{lang}.json"
    if fe_path.exists():
        data = json.loads(fe_path.read_text(encoding="utf-8"))
        data.update(keys)
        fe_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {fe_path}")

    # Update backend
    be_path = ROOT / "src" / "translations" / f"{lang}.json"
    if be_path.exists():
        data = json.loads(be_path.read_text(encoding="utf-8"))
        data.update(keys)
        be_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {be_path}")

print("Done updating localization catalogs.")
