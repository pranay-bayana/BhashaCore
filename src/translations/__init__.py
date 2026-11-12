"""Translation system for BhashaCore UI internationalization.

Loads translation JSON files from src/translations/ and provides:
- A Jinja2 template global function `t(key, **kwargs)` for server-side rendering
- Client-side translation support via the /api/translations endpoint
- Interface language detection from URL query param, session, cookie, or Accept-Language header
- Safe fallback to English for missing keys
- Dynamic interpolation for values like {count}, {script}, etc.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

TRANSLATIONS_DIR = Path(__file__).resolve().parent

# Cache of loaded translation dictionaries
_translation_cache: Dict[str, Dict[str, str]] = {}

EXTRA_TRANSLATIONS = {
    "en": {
        "auth_sign_in": "Sign in",
        "auth_sign_up": "Create account",
        "auth_email": "Email",
        "auth_password": "Password",
        "auth_full_name": "Full name",
        "auth_confirm_password": "Confirm password",
        "auth_show": "Show",
        "auth_forgot": "Forgot password?",
        "auth_reset": "Reset password",
        "auth_send_reset": "Send reset link",
        "auth_new_password": "New password",
        "auth_settings": "Settings",
        "auth_profile": "Profile",
        "auth_delete_account": "Delete account",
        "auth_confirm_delete": "Confirm password",
        "auth_history": "Chat history",
        "auth_loading_history": "Loading conversations…",
        "auth_no_history": "No saved conversations yet.",
        "auth_rename": "Rename",
        "auth_delete": "Delete",
        "auth_history_error": "Could not load conversation history.",
        "auth_title": "Conversation title",
        "auth_delete_confirm": "Delete this conversation permanently?",
        "auth_logout": "Sign out",
        "auth_consent": "I accept the terms and privacy notice.",
        "auth_password_hint": "Use a password of at least 12 characters.",
        "auth_workspace": "Sign in to your research workspace.",
        "landing_eyebrow": "Research-grounded multilingual AI",
        "landing_title": "Intelligence Without Language Barriers.",
        "landing_copy": "Explore how AI understands, retrieves, and responds across India's diverse languages.",
        "landing_open": "Explore the Workspace",
        "landing_start": "Get started",
        "landing_cta_workspace": "Explore the Workspace",
        "landing_cta_research": "Explore Research",
        "landing_languages": "Six languages",
        "landing_languages_copy": "Native script, Romanized input, and independent interface and answer-language controls.",
        "landing_evidence": "Evidence first",
        "landing_evidence_copy": "BM25 retrieval surfaces source passages and marks references used to support an answer.",
        "landing_research": "Research visibility",
        "landing_research_copy": "Compare measured retrieval and answer-quality results across the evaluated language set.",
        "landing_sec_languages": "Supported Languages",
        "landing_sec_languages_desc": "Six Indian languages with script-aware tokenization, Romanized query bridging, and independent knowledge pools.",
        "landing_sec_retrieval": "How Multilingual Retrieval Works",
        "landing_sec_retrieval_desc": "Our architecture detects script families, handles Romanized typing, searches language-specific BM25 corpora, and scores evidence grounding.",
        "landing_sec_comp": "Research & Cross-Lingual Evaluation",
        "landing_sec_comp_desc": "Systematic evaluation measuring performance drops between English and regional Indic languages across closed-book and RAG settings.",
        "landing_sec_citations": "Grounded Answers & Citations",
        "landing_sec_citations_desc": "Every generated response is directly mapped to retrieved source passages with verified lexical support scores.",
        "landing_sec_eval": "Language-Specific Evaluation Modes",
        "landing_sec_eval_desc": "Rigorous benchmarking on IndicQA across Closed-Book, Gold Context, Native RAG, and Romanized RAG.",
        "landing_sec_capabilities": "Platform Capabilities",
        "landing_sec_capabilities_desc": "An enterprise-grade multilingual research environment for linguistic testing, retrieval diagnosis, and AI evaluation.",
        "settings_language": "Interface language",
        "settings_language_copy": "Website labels, navigation, and system messages.",
        "settings_security": "Account security",
        "settings_security_copy": "Password reset delivery needs a configured email provider.",
        "settings_delete_copy": "This permanently deletes your profile and saved conversations.",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_toggle": "Toggle theme",
        "lang_control_interface": "Interface Language",
        "lang_control_input": "Input Language",
        "lang_control_answer": "Answer Language",
        "lang_control_script": "Answer Script",
        "nav_home": "Overview",
        "lang_name_en": "English",
        "lang_name_hi": "Hindi",
        "lang_name_ta": "Tamil",
        "lang_name_te": "Telugu",
        "lang_name_kn": "Kannada",
        "lang_name_ml": "Malayalam",
        "session_answer_lang_en": "English",
        "session_answer_lang_hi": "Hindi",
        "session_answer_lang_ta": "Tamil",
        "session_answer_lang_te": "Telugu",
        "session_answer_lang_kn": "Kannada",
        "session_answer_lang_ml": "Malayalam",
        "chat_choose_language": "Choose language",
        "chat_advanced_options": "Advanced options",
        "chat_simple_model_label": "Model: Sarvam AI 105B",
        "chat_hero_headline": "Ask anything in your language",
        "chat_hero_subheadline": "A multilingual, research-backed chatbot for Indian languages",
        "research_hub_title": "Research & Evaluation Suite",
    },
    "hi": {
        "auth_sign_in": "साइन इन",
        "auth_sign_up": "खाता बनाएं",
        "auth_email": "ईमेल",
        "auth_password": "पासवर्ड",
        "auth_full_name": "पूरा नाम",
        "auth_confirm_password": "पासवर्ड की पुष्टि करें",
        "auth_show": "दिखाएं",
        "auth_forgot": "पासवर्ड भूल गए?",
        "auth_reset": "पासवर्ड रीसेट करें",
        "auth_send_reset": "रीसेट लिंक भेजें",
        "auth_new_password": "नया पासवर्ड",
        "auth_settings": "सेटिंग्स",
        "auth_profile": "प्रोफ़ाइल",
        "auth_delete_account": "खाता हटाएं",
        "auth_confirm_delete": "पासवर्ड की पुष्टि करें",
        "auth_history": "चैट इतिहास",
        "auth_loading_history": "वार्तालाप लोड हो रहे हैं…",
        "auth_no_history": "कोई सहेजा वार्तालाप नहीं।",
        "auth_rename": "नाम बदलें",
        "auth_delete": "हटाएं",
        "auth_history_error": "चैट इतिहास लोड नहीं हो सका।",
        "auth_title": "वार्तालाप शीर्षक",
        "auth_delete_confirm": "इस वार्तालाप को स्थायी रूप से हटाएं?",
        "auth_logout": "साइन आउट",
        "auth_consent": "मैं शर्तें और गोपनीयता सूचना स्वीकार करता/करती हूं।",
        "auth_password_hint": "कम से कम 12 वर्ण का पासवर्ड उपयोग करें।",
        "auth_workspace": "अपने शोध कार्यस्थान में साइन इन करें।",
        "landing_eyebrow": "शोध-आधारित बहुभाषी एआई",
        "landing_title": "भाषा बाधाओं के बिना बुद्धिमत्ता।",
        "landing_copy": "जानिए कैसे एआई भारत की विविध भाषाओं में समझता है, खोजता है और उत्तर देता है।",
        "landing_open": "कार्यस्थान का अन्वेषण करें",
        "landing_start": "शुरू करें",
        "landing_cta_workspace": "कार्यस्थान का अन्वेषण करें",
        "landing_cta_research": "शोध का अन्वेषण करें",
        "landing_languages": "छह भाषाएं",
        "landing_languages_copy": "मूल लिपि, रोमन इनपुट और स्वतंत्र इंटरफ़ेस व उत्तर भाषा नियंत्रण।",
        "landing_evidence": "साक्ष्य पहले",
        "landing_evidence_copy": "BM25 खोज स्रोत अंश दिखाती है और उत्तर में उपयोग हुए संदर्भों को चिह्नित करती है।",
        "landing_research": "शोध दृश्यता",
        "landing_research_copy": "मापे गए खोज और उत्तर-गुणवत्ता परिणामों की तुलना करें।",
        "landing_sec_languages": "समर्थित भाषाएं",
        "landing_sec_languages_desc": "लिपि-सचेत टोकनाइजेशन, रोमन प्रश्न सेतु और स्वतंत्र ज्ञान भंडार के साथ छह भारतीय भाषाएं।",
        "landing_sec_retrieval": "बहुभाषी खोज कैसे काम करती है",
        "landing_sec_retrieval_desc": "हमारी संरचना लिपि पहचानती है, रोमन टाइपिंग को संभालती है, भाषा-विशिष्ट BM25 खोजती है और साक्ष्य स्कोर करती है।",
        "landing_sec_comp": "शोध और भाषा तुलना",
        "landing_sec_comp_desc": "क्लोज्ड-बुक और RAG सेटिंग्स में अंग्रेजी और क्षेत्रीय भारतीय भाषाओं के बीच व्यवस्थित प्रदर्शन गिरावट का मापन।",
        "landing_sec_citations": "आधारित उत्तर और उद्धरण",
        "landing_sec_citations_desc": "उत्पन्न प्रत्येक उत्तर सीधे स्रोत अंशों से सत्यापित शाब्दिक समर्थन स्कोर के साथ जुड़ा होता है।",
        "landing_sec_eval": "भाषा-विशिष्ट मूल्यांकन",
        "landing_sec_eval_desc": "क्लोज्ड-बुक, गोल्ड संदर्भ, मूल RAG और रोमानीकृत RAG में IndicQA पर कठोर बेंचमार्किंग।",
        "landing_sec_capabilities": "उत्पाद क्षमताएं",
        "landing_sec_capabilities_desc": "भाषाई परीक्षण, खोज निदान और एआई मूल्यांकन के लिए निर्मित एंटरप्राइज-ग्रेड बहुभाषी शोध वातावरण।",
        "settings_language": "इंटरफ़ेस भाषा",
        "settings_language_copy": "वेबसाइट लेबल, नेविगेशन और सिस्टम संदेश।",
        "settings_security": "खाता सुरक्षा",
        "settings_security_copy": "पासवर्ड रीसेट डिलीवरी के लिए ईमेल प्रदाता आवश्यक है।",
        "settings_delete_copy": "यह आपकी प्रोफ़ाइल और सहेजे वार्तालापों को स्थायी रूप से हटाता है।",
        "theme_light": "लाइट",
        "theme_dark": "डार्क",
        "theme_toggle": "थीम बदलें",
        "lang_control_interface": "इंटरफ़ेस भाषा",
        "lang_control_input": "इनपुट भाषा",
        "lang_control_answer": "उत्तर भाषा",
        "lang_control_script": "उत्तर लिपि",
        "nav_home": "अवलोकन",
        "lang_name_en": "अंग्रेज़ी",
        "lang_name_hi": "हिंदी",
        "lang_name_ta": "तमिल",
        "lang_name_te": "तेलुगु",
        "lang_name_kn": "कन्नड़",
        "lang_name_ml": "मलयालम",
        "session_answer_lang_en": "अंग्रेज़ी",
        "session_answer_lang_hi": "हिंदी",
        "session_answer_lang_ta": "तमिल",
        "session_answer_lang_te": "तेलुगु",
        "session_answer_lang_kn": "कन्नड़",
        "session_answer_lang_ml": "मलयालम",
        "chat_choose_language": "भाषा चुनें",
        "chat_advanced_options": "उन्नत विकल्प",
        "chat_simple_model_label": "मॉडल: सर्वम एआई 105B",
        "chat_hero_headline": "अपनी भाषा में कुछ भी पूछें",
        "chat_hero_subheadline": "भारतीय भाषाओं के लिए एक बहुभाषी, शोध-समर्थित चैटबॉट",
        "research_hub_title": "शोध एवं मूल्यांकन सुइट",
    },
    "te": {
        "auth_sign_in": "సైన్ ఇన్",
        "auth_sign_up": "ఖాతా సృష్టించండి",
        "auth_email": "ఇమెయిల్",
        "auth_password": "పాస్‌వర్డ్",
        "auth_full_name": "పూర్తి పేరు",
        "auth_confirm_password": "పాస్‌వర్డ్ నిర్ధారించండి",
        "auth_show": "చూపు",
        "auth_forgot": "పాస్‌వర్డ్ మర్చిపోయారా?",
        "auth_reset": "పాస్‌వర్డ్ రీసెట్",
        "auth_send_reset": "రీసెట్ లింక్ పంపు",
        "auth_new_password": "కొత్త పాస్‌వర్డ్",
        "auth_settings": "సెట్టింగ్‌లు",
        "auth_profile": "ప్రొఫైల్",
        "auth_delete_account": "ఖాతా తొలగించండి",
        "auth_confirm_delete": "పాస్‌వర్డ్ నిర్ధారించండి",
        "auth_history": "చాట్ చరిత్ర",
        "auth_loading_history": "సంభాషణలు లోడ్ అవుతున్నాయి…",
        "auth_no_history": "సేవ్ చేసిన సంభాషణలు లేవు.",
        "auth_rename": "పేరు మార్చండి",
        "auth_delete": "తొలగించండి",
        "auth_history_error": "చాట్ చరిత్ర లోడ్ కాలేదు.",
        "auth_title": "సంభాషణ శీర్షిక",
        "auth_delete_confirm": "ఈ సంభాషణను శాశ్వతంగా తొలగించాలా?",
        "auth_logout": "సైన్ అవుట్",
        "auth_consent": "నేను నిబంధనలు మరియు గోప్యతా సూచనను అంగీకరిస్తున్నాను.",
        "auth_password_hint": "కనీసం 12 అక్షరాల పాస్‌వర్డ్ ఉపయోగించండి.",
        "auth_workspace": "మీ పరిశోధన వర్క్‌స్పేస్‌లో సైన్ ఇన్ చేయండి.",
        "landing_eyebrow": "పరిశోధన ఆధారిత బహుభాషా AI",
        "landing_title": "భాషా అడ్డంకులు లేని మేధస్సు.",
        "landing_copy": "భారతీయ విభిన్న భాషలలో AI ఎలా అర్థం చేసుకుంటుందో, సమాచారం సేకరిస్తుందో మరియు స్పందిస్తుందో అన్వేషించండి.",
        "landing_open": "వర్క్‌స్పేస్ అన్వేషించండి",
        "landing_start": "ప్రారంభించండి",
        "landing_cta_workspace": "వర్క్‌స్పేస్ అన్వేషించండి",
        "landing_cta_research": "పరిశోధనను అన్వేషించండి",
        "landing_languages": "ఆరు భాషలు",
        "landing_languages_copy": "స్థానిక లిపి, రోమనైజ్డ్ ఇన్‌పుట్ మరియు స్వతంత్ర భాష నియంత్రణలు.",
        "landing_evidence": "ఆధారం ముందుగా",
        "landing_evidence_copy": "BM25 శోధన మూల భాగాలను చూపి ఉపయోగించిన ఆధారాలను గుర్తిస్తుంది.",
        "landing_research": "పరిశోధన దృశ్యం",
        "landing_research_copy": "కొలిచిన శోధన మరియు సమాధాన నాణ్యత ఫలితాలను పోల్చండి.",
        "landing_sec_languages": "మద్దతు గల భాషలు",
        "landing_sec_languages_desc": "లిపి అవగాహన, రోమనైజ్డ్ ప్రశ్నల అనుసంధానం మరియు ప్రత్యేక విజ్ఞాన భాండాగారాలతో ఆరు భారతీయ భాషలు.",
        "landing_sec_retrieval": "బహుభాషా శోధన ఎలా పనిచేస్తుంది",
        "landing_sec_retrieval_desc": "మా సిస్టమ్ లిపిని గుర్తిస్తుంది, రోమనైజ్డ్ టైపింగ్‌ను నిర్వహిస్తుంది, భాషా-నిర్దిష్ట BM25 ద్వారా శోధిస్తుంది మరియు ఆధారాలను ధృవీకరిస్తుంది.",
        "landing_sec_comp": "పరిశోధన మరియు భాషా పోలిక",
        "landing_sec_comp_desc": "క్లోజ్డ్-బుక్ మరియు RAG సెట్టింగ్‌లలో ఆంగ్లం మరియు ప్రాంతీయ భారతీయ భాషల మధ్య పనితీరు మార్పులను కొలవండి.",
        "landing_sec_citations": "ఆధారిత సమాధానాలు మరియు ఆధారాలు",
        "landing_sec_citations_desc": "రూపొందించబడిన ప్రతి సమాధానం ధృవీకరించబడిన ఆధార స్కోరుతో మూల భాగాలకు నేరుగా జోడించబడుతుంది.",
        "landing_sec_eval": "భాషా-నిర్దిష్ట మూల్యాంకనం",
        "landing_sec_eval_desc": "క్లోజ్డ్-బుక్, గోల్డ్ కాంటెక్స్ట్, నేటివ్ RAG మరియు రోమనైజ్డ్ RAG రీతుల్లో IndicQA ఆధారిత నిష్పాక్షిక మూల్యాంకనం.",
        "landing_sec_capabilities": "ఉత్పత్తి సామర్థ్యాలు",
        "landing_sec_capabilities_desc": "భాషా పరిశోధన, సమాచార పునరుద్ధరణ మరియు AI మూల్యాంకనం కోసం రూపొందించిన అధునాతన పరిశోధనా వేదిక.",
        "settings_language": "ఇంటర్‌ఫేస్ భాష",
        "settings_language_copy": "వెబ్‌సైట్ లేబుల్‌లు, నావిగేషన్ మరియు సిస్టమ్ సందేశాలు.",
        "settings_security": "ఖాతా భద్రత",
        "settings_security_copy": "పాస్‌వర్డ్ రీసెట్ పంపడానికి ఇమెయిల్ ప్రొవైడర్ కావాలి.",
        "settings_delete_copy": "ఇది మీ ప్రొఫైల్ మరియు సేవ్ చేసిన సంభాషణలను శాశ్వతంగా తొలగిస్తుంది.",
        "theme_light": "లైట్",
        "theme_dark": "డార్క్",
        "theme_toggle": "థీమ్ మార్చండి",
        "lang_control_interface": "ఇంటర్‌ఫేస్ భాష",
        "lang_control_input": "ఇన్‌పుట్ భాష",
        "lang_control_answer": "సమాధానం భాష",
        "lang_control_script": "సమాధాన లిపి",
        "nav_home": "అవలోకనం",
        "lang_name_en": "ఆంగ్లం",
        "lang_name_hi": "హిందీ",
        "lang_name_ta": "తమిళం",
        "lang_name_te": "తెలుగు",
        "lang_name_kn": "కన్నడ",
        "lang_name_ml": "మలయాళం",
        "session_answer_lang_en": "ఆంగ్లం",
        "session_answer_lang_hi": "హిందీ",
        "session_answer_lang_ta": "తమిళం",
        "session_answer_lang_te": "తెలుగు",
        "session_answer_lang_kn": "కన్నడ",
        "session_answer_lang_ml": "మలయాళం",
        "chat_choose_language": "భాషను ఎంచుకోండి",
        "chat_advanced_options": "మరిన్ని ఎంపికలు",
        "chat_simple_model_label": "మోడల్: సర్వం AI 105B",
        "chat_hero_headline": "మీ భాషలో ఏదైనా అడగండి",
        "chat_hero_subheadline": "భారతీయ భాషల కోసం బహుభాషా, పరిశోధన-ఆధారిత చాట్‌బాట్",
        "research_hub_title": "పరిశోధన మరియు మూల్యాంకన సూట్",
    },
    "ta": {
        "auth_sign_in": "உள்நுழைய",
        "auth_sign_up": "கணக்கை உருவாக்கவும்",
        "auth_email": "மின்னஞ்சல்",
        "auth_password": "கடவுச்சொல்",
        "auth_full_name": "முழுப் பெயர்",
        "auth_confirm_password": "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
        "auth_show": "காட்டு",
        "auth_forgot": "கடவுச்சொல் மறந்துவிட்டதா?",
        "auth_reset": "கடவுச்சொல்லை மீட்டமை",
        "auth_send_reset": "மீட்டமைப்பு இணைப்பை அனுப்பு",
        "auth_new_password": "புதிய கடவுச்சொல்",
        "auth_settings": "அமைப்புகள்",
        "auth_profile": "சுயவிவரம்",
        "auth_delete_account": "கணக்கை நீக்கு",
        "auth_confirm_delete": "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
        "auth_history": "அரட்டை வரலாறு",
        "auth_loading_history": "உரையாடல்கள் ஏற்றப்படுகின்றன…",
        "auth_no_history": "சேமித்த உரையாடல்கள் இல்லை.",
        "auth_rename": "மறுபெயரிடு",
        "auth_delete": "நீக்கு",
        "auth_history_error": "அரட்டை வரலாற்றை ஏற்ற முடியவில்லை.",
        "auth_title": "உரையாடல் தலைப்பு",
        "auth_delete_confirm": "இந்த உரையாடலை நிரந்தரமாக நீக்கவா?",
        "auth_logout": "வெளியேறு",
        "auth_consent": "விதிமுறைகளையும் தனியுரிமை அறிவிப்பையும் ஏற்கிறேன்.",
        "auth_password_hint": "குறைந்தது 12 எழுத்துகள் கொண்ட கடவுச்சொல்லைப் பயன்படுத்தவும்.",
        "auth_workspace": "உங்கள் ஆராய்ச்சி பணியிடத்தில் உள்நுழையவும்.",
        "landing_eyebrow": "ஆராய்ச்சி அடிப்படையிலான பன்மொழி AI",
        "landing_title": "மொழி தடைகளற்ற நுண்ணறிவு.",
        "landing_copy": "இந்தியாவின் பல்வேறு மொழிகளில் AI எவ்வாறு புரிந்துகொள்கிறது, தேடுகிறது மற்றும் பதிலளிக்கிறது என்பதை ஆராயுங்கள்.",
        "landing_open": "பணியிடத்தை ஆராயுங்கள்",
        "landing_start": "தொடங்குங்கள்",
        "landing_cta_workspace": "பணியிடத்தை ஆராயுங்கள்",
        "landing_cta_research": "ஆராய்ச்சியை ஆராயுங்கள்",
        "landing_languages": "ஆறு மொழிகள்",
        "landing_languages_copy": "தாய்மொழி எழுத்து, ரோமானிய உள்ளீடு மற்றும் தனித்த மொழிக் கட்டுப்பாடுகள்.",
        "landing_evidence": "ஆதாரம் முதலில்",
        "landing_evidence_copy": "BM25 தேடல் மூலப் பகுதிகளைக் காட்டி பயன்படுத்திய ஆதாரங்களைக் குறிக்கிறது.",
        "landing_research": "ஆராய்ச்சி பார்வை",
        "landing_research_copy": "அளவிடப்பட்ட தேடல் மற்றும் பதில் தர முடிவுகளை ஒப்பிடுங்கள்.",
        "landing_sec_languages": "ஆதரிக்கப்படும் மொழிகள்",
        "landing_sec_languages_desc": "எழுத்து உணர்வு செயலாக்கம், ரோமானிய வினவல் இணைப்பு மற்றும் தனி அறிவுத் தொகுப்புகளுடன் ஆறு இந்திய மொழிகள்.",
        "landing_sec_retrieval": "பன்மொழி தேடல் எவ்வாறு செயல்படுகிறது",
        "landing_sec_retrieval_desc": "எழுத்து முறையைக் கண்டறிந்து, ரோமானிய தட்டச்சை நிர்வகித்து, மொழி சார்ந்த BM25 மூலம் தேடி சான்றுகளை உறுதிப்படுத்துகிறது.",
        "landing_sec_comp": "ஆராய்ச்சி மற்றும் மொழி ஒப்பீடு",
        "landing_sec_comp_desc": "மூடப்பட்ட புத்தகம் மற்றும் RAG சூழல்களில் ஆங்கிலத்திற்கும் பிராந்திய இந்திய மொழிகளுக்கும் இடையிலான செயல்திறன் இடைவெளிகளை ஆராய்கிறது.",
        "landing_sec_citations": "ஆதாரபூர்வமான பதில்கள் மற்றும் மேற்கோள்கள்",
        "landing_sec_citations_desc": "உருவாக்கப்படும் ஒவ்வொரு பதிலும் சரிபார்க்கப்பட்ட ஆதரவு மதிப்பெண்ணுடன் மூலப் பகுதிகளுடன் இணைக்கப்பட்டுள்ளது.",
        "landing_sec_eval": "மொழி சார்ந்த மதிப்பீடு",
        "landing_sec_eval_desc": "IndicQA தளத்தில் மூடப்பட்ட புத்தகம், தங்கச் சூழல், சொந்த RAG மற்றும் ரோமானிய RAG ஆகியவற்றில் முழுமையான மதிப்பீடு.",
        "landing_sec_capabilities": "தயாரிப்பு திறன்கள்",
        "landing_sec_capabilities_desc": "மொழியியல் சோதனை, மீட்டெடுப்பு பகுப்பாய்வு மற்றும் AI மதிப்பீட்டிற்கான முழுமையான பன்மொழி ஆராய்ச்சி சூழல்.",
        "settings_language": "இடைமுக மொழி",
        "settings_language_copy": "வலைத்தள லேபிள்கள், வழிசெலுத்தல் மற்றும் கணினி செய்திகள்.",
        "settings_security": "கணக்கு பாதுகாப்பு",
        "settings_security_copy": "கடவுச்சொல் மீட்டமைப்புக்கு மின்னஞ்சல் வழங்குநர் தேவை.",
        "settings_delete_copy": "இது உங்கள் சுயவிவரத்தையும் சேமித்த உரையாடல்களையும் நிரந்தரமாக நீக்கும்.",
        "theme_light": "லைட்",
        "theme_dark": "டார்க்",
        "theme_toggle": "தீம் மாற்றவும்",
        "lang_control_interface": "இடைமுக மொழி",
        "lang_control_input": "உள்ளீட்டு மொழி",
        "lang_control_answer": "பதில் மொழி",
        "lang_control_script": "பதில் எழுத்துமுறை",
        "nav_home": "கண்ணோட்டம்",
        "lang_name_en": "ஆங்கிலம்",
        "lang_name_hi": "இந்தி",
        "lang_name_ta": "தமிழ்",
        "lang_name_te": "தெலுங்கு",
        "lang_name_kn": "கன்னடம்",
        "lang_name_ml": "மலையாளம்",
        "session_answer_lang_en": "ஆங்கிலம்",
        "session_answer_lang_hi": "இந்தி",
        "session_answer_lang_ta": "தமிழ்",
        "session_answer_lang_te": "தெலுங்கு",
        "session_answer_lang_kn": "கன்னடம்",
        "session_answer_lang_ml": "மலையாளம்",
        "chat_choose_language": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "chat_advanced_options": "கூடுதல் விருப்பங்கள்",
        "chat_simple_model_label": "மாதிரி: சர்வம AI 105B",
        "chat_hero_headline": "உங்கள் மொழியில் எதையும் கேளுங்கள்",
        "chat_hero_subheadline": "இந்திய மொழிகளுக்கான பலமொழி, ஆராய்ச்சி ஆதரவு சாட்பாட்",
        "research_hub_title": "ஆராய்ச்சி மற்றும் மதிப்பீட்டு தளம்",
    },
    "kn": {
        "auth_sign_in": "ಸೈನ್ ಇನ್",
        "auth_sign_up": "ಖಾತೆ ರಚಿಸಿ",
        "auth_email": "ಇಮೇಲ್",
        "auth_password": "ಪಾಸ್‌ವರ್ಡ್",
        "auth_full_name": "ಪೂರ್ಣ ಹೆಸರು",
        "auth_confirm_password": "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
        "auth_show": "ತೋರಿಸಿ",
        "auth_forgot": "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?",
        "auth_reset": "ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ",
        "auth_send_reset": "ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ಕಳುಹಿಸಿ",
        "auth_new_password": "ಹೊಸ ಪಾಸ್‌ವರ್ಡ್",
        "auth_settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        "auth_profile": "ಪ್ರೊಫೈಲ್",
        "auth_delete_account": "ಖಾತೆ ಅಳಿಸಿ",
        "auth_confirm_delete": "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
        "auth_history": "ಚಾಟ್ ಇತಿಹಾಸ",
        "auth_loading_history": "ಸಂಭಾಷಣೆಗಳು ಲೋಡ್ ಆಗುತ್ತಿವೆ…",
        "auth_no_history": "ಉಳಿಸಿದ ಸಂಭಾಷಣೆಗಳಿಲ್ಲ.",
        "auth_rename": "ಮರುಹೆಸರಿಸಿ",
        "auth_delete": "ಅಳಿಸಿ",
        "auth_history_error": "ಚಾಟ್ ಇತಿಹಾಸ ಲೋಡ್ ಆಗಲಿಲ್ಲ.",
        "auth_title": "ಸಂಭಾಷಣೆ ಶೀರ್ಷಿಕೆ",
        "auth_delete_confirm": "ಈ ಸಂಭಾಷಣೆಯನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸಬೇಕೇ?",
        "auth_logout": "ಸೈನ್ ಔಟ್",
        "auth_consent": "ನಾನು ನಿಯಮಗಳು ಮತ್ತು ಗೌಪ್ಯತಾ ಸೂಚನೆಯನ್ನು ಒಪ್ಪುತ್ತೇನೆ.",
        "auth_password_hint": "ಕನಿಷ್ಠ 12 ಅಕ್ಷರಗಳ ಪಾಸ್‌ವರ್ಡ್ ಬಳಸಿ.",
        "auth_workspace": "ನಿಮ್ಮ ಸಂಶೋಧನಾ ಕಾರ್ಯಕ್ಷೇತ್ರಕ್ಕೆ ಸೈನ್ ಇನ್ ಮಾಡಿ.",
        "landing_eyebrow": "ಸಂಶೋಧನೆ ಆಧಾರಿತ ಬಹುಭಾಷಾ AI",
        "landing_title": "ಭಾಷಾ ಅಡೆತಡೆಗಳಿಲ್ಲದ ಬುದ್ಧಿವಂತಿಕೆ.",
        "landing_copy": "ಭಾರತದ ವೈವಿಧ್ಯಮಯ ಭಾಷೆಗಳಲ್ಲಿ AI ಹೇಗೆ ಗ್ರಹಿಸುತ್ತದೆ, ಮರುಪಡೆಯುತ್ತದೆ ಮತ್ತು ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತದೆ ಎಂಬುದನ್ನು ಅನ್ವೇಷಿಸಿ.",
        "landing_open": "ಕಾರ್ಯಕ್ಷೇತ್ರವನ್ನು ಅನ್ವೇಷಿಸಿ",
        "landing_start": "ಪ್ರಾರಂಭಿಸಿ",
        "landing_cta_workspace": "ಕಾರ್ಯಕ್ಷೇತ್ರವನ್ನು ಅನ್ವೇಷಿಸಿ",
        "landing_cta_research": "ಸಂಶೋಧನೆಯನ್ನು ಅನ್ವೇಷಿಸಿ",
        "landing_languages": "ಆರು ಭಾಷೆಗಳು",
        "landing_languages_copy": "ಸ್ಥಳೀಯ ಲಿಪಿ, ರೋಮನೀಕೃತ ಇನ್‌ಪುಟ್ ಮತ್ತು ಸ್ವತಂತ್ರ ಭಾಷಾ ನಿಯಂತ್ರಣಗಳು.",
        "landing_evidence": "ಮೊದಲು ಆಧಾರ",
        "landing_evidence_copy": "BM25 ಹುಡುಕಾಟ ಮೂಲ ಭಾಗಗಳನ್ನು ತೋರಿಸಿ ಬಳಸಿದ ಉಲ್ಲೇಖಗಳನ್ನು ಗುರುತಿಸುತ್ತದೆ.",
        "landing_research": "ಸಂಶೋಧನಾ ದೃಶ್ಯ",
        "landing_research_copy": "ಅಳತೆಯಾದ ಹುಡುಕಾಟ ಮತ್ತು ಉತ್ತರ-ಗುಣಮಟ್ಟದ ಫಲಿತಾಂಶಗಳನ್ನು ಹೋಲಿಸಿ.",
        "landing_sec_languages": "ಬೆಂಬಲಿತ ಭಾಷೆಗಳು",
        "landing_sec_languages_desc": "ಲಿಪಿ-ಅರಿವಿನ ಟೋಕನೈಸೇಶನ್, ರೋಮನೀಕೃತ ಪ್ರಶ್ನೆ ಸೇತುವೆ ಮತ್ತು ಸ್ವತಂತ್ರ ಜ್ಞಾನ ಭಂಡಾರಗಳೊಂದಿಗೆ ಆರು ಭಾರತೀಯ ಭಾಷೆಗಳು.",
        "landing_sec_retrieval": "ಬಹುಭಾಷಾ ಹುಡುಕಾಟ ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ",
        "landing_sec_retrieval_desc": "ಲಿಪಿಯನ್ನು ಪತ್ತೆಹಚ್ಚಿ, ರೋಮನೀಕೃತ ಟೈಪಿಂಗ್ ನಿರ್ವಹಿಸಿ, ಭಾಷಾ-ನಿರ್ದಿಷ್ಟ BM25 ಮೂಲಕ ಹುಡುಕಿ ಸಾಕ್ಷ್ಯವನ್ನು ಮೌಲ್ಯೀಕರಿಸುತ್ತದೆ.",
        "landing_sec_comp": "ಸಂಶೋಧನೆ ಮತ್ತು ಭಾಷಾ ಹೋಲಿಕೆ",
        "landing_sec_comp_desc": "ಕ್ಲೋಸ್ಡ್-ಬುಕ್ ಮತ್ತು RAG ಸೆಟ್ಟಿಂಗ್‌ಗಳಲ್ಲಿ ಇಂಗ್ಲಿಷ್ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಭಾರತೀಯ ಭಾಷೆಗಳ ನಡುವಿನ ಕಾರ್ಯಕ್ಷಮತೆಯ ಅಂತರಗಳನ್ನು ಅಳೆಯಿರಿ.",
        "landing_sec_citations": "ಆಧಾರಿತ ಉತ್ತರಗಳು ಮತ್ತು ಉಲ್ಲೇಖಗಳು",
        "landing_sec_citations_desc": "ರಚಿಸಲಾದ ಪ್ರತಿಯೊಂದು ಉತ್ತರವು ದೃಢೀಕರಿಸಿದ ಬೆಂಬಲ ಸ್ಕೋರ್‌ನೊಂದಿಗೆ ನೇರವಾಗಿ ಮೂಲ ಭಾಗಗಳಿಗೆ ಸಂಪರ್ಕಗೊಂಡಿರುತ್ತದೆ.",
        "landing_sec_eval": "ಭಾಷಾ-ನಿರ್ದಿಷ್ಟ ಮೌಲ್ಯಮಾಪನ",
        "landing_sec_eval_desc": "IndicQA ಬಳಸಿ ಕ್ಲೋಸ್ಡ್-ಬುಕ್, ಗೋಲ್ಡ್ ಕಂಟೆಕ್ಸ್ಟ್, ಸ್ಥಳೀಯ RAG ಮತ್ತು ರೋಮನೀಕೃತ RAG ವಿಧಾನಗಳಲ್ಲಿ ಕಟ್ಟುನಿಟ್ಟಾದ ಮೌಲ್ಯಮಾಪನ.",
        "landing_sec_capabilities": "ಉತ್ಪನ್ನದ ಸಾಮರ್ಥ್ಯಗಳು",
        "landing_sec_capabilities_desc": "ಭಾಷಾಶಾಸ್ತ್ರಜ್ಞರು ಮತ್ತು AI ಮೌಲ್ಯಮಾಪಕರಿಗಾಗಿ ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ಸುಧಾರಿತ ಬಹುಭಾಷಾ ಸಂಶೋಧನಾ ಕಾರ್ಯಕ್ಷೇತ್ರ.",
        "settings_language": "ಇಂಟರ್‌ಫೇಸ್ ಭಾಷೆ",
        "settings_language_copy": "ವೆಬ್‌ಸೈಟ್ ಲೇಬಲ್‌ಗಳು, ನ್ಯಾವಿಗೇಷನ್ ಮತ್ತು ಸಿಸ್ಟಮ್ ಸಂದೇಶಗಳು.",
        "settings_security": "ಖಾತೆಯ ಭದ್ರತೆ",
        "settings_security_copy": "ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸುವ ವಿತರಣೆಗೆ ಇಮೇಲ್ ಪೂರೈಕೆದಾರ ಬೇಕು.",
        "settings_delete_copy": "ಇದು ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಉಳಿಸಿದ ಸಂಭಾಷಣೆಗಳನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸುತ್ತದೆ.",
        "theme_light": "ಲೈಟ್",
        "theme_dark": "ಡಾರ್ಕ್",
        "theme_toggle": "ಥೀಮ್ ಬದಲಾಯಿಸಿ",
        "lang_control_interface": "ಇಂಟರ್‌ಫೇಸ್ ಭಾಷೆ",
        "lang_control_input": "ಇನ್‌ಪುಟ್ ಭಾಷೆ",
        "lang_control_answer": "ಉತ್ತರ ಭಾಷೆ",
        "lang_control_script": "ಉತ್ತರ ಲಿಪಿ",
        "nav_home": "ಅವಲೋಕನ",
        "lang_name_en": "ಇಂಗ್ಲಿಷ್",
        "lang_name_hi": "ಹಿಂದಿ",
        "lang_name_ta": "ತಮಿಳು",
        "lang_name_te": "ತೆಲುಗು",
        "lang_name_kn": "ಕನ್ನಡ",
        "lang_name_ml": "ಮಲಯಾಳಂ",
        "session_answer_lang_en": "ಇಂಗ್ಲಿಷ್",
        "session_answer_lang_hi": "ಹಿಂದಿ",
        "session_answer_lang_ta": "ತಮಿಳು",
        "session_answer_lang_te": "ತೆಲುಗು",
        "session_answer_lang_kn": "ಕನ್ನಡ",
        "session_answer_lang_ml": "ಮಲಯಾಳಂ",
        "chat_choose_language": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "chat_advanced_options": "ಹೆಚ್ಚುವರಿ ಆಯ್ಕೆಗಳು",
        "chat_simple_model_label": "ಮಾದರಿ: ಸರ್ವಮ್ AI 105B",
        "chat_hero_headline": "ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಏನನ್ನಾದರೂ ಕೇಳಿ",
        "chat_hero_subheadline": "ಭಾರತೀಯ ಭಾಷೆಗಳಿಗಾಗಿ ಬಹುಭಾಷಾ, ಸಂಶೋಧನಾ-ಆಧಾರಿತ ಚಾಟ್‌ಬಾಟ್",
        "research_hub_title": "ಸಂಶೋಧನೆ ಮತ್ತು ಮೌಲ್ಯಮಾಪನ ಸೂಟ್",
    },
    "ml": {
        "auth_sign_in": "സൈൻ ഇൻ",
        "auth_sign_up": "അക്കൗണ്ട് സൃഷ്ടിക്കുക",
        "auth_email": "ഇമെയിൽ",
        "auth_password": "പാസ്‌വേഡ്",
        "auth_full_name": "പൂർണ്ണ പേര്",
        "auth_confirm_password": "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക",
        "auth_show": "കാണിക്കുക",
        "auth_forgot": "പാസ്‌വേഡ് മറന്നോ?",
        "auth_reset": "പാസ്‌വേഡ് പുനഃസജ്ജമാക്കുക",
        "auth_send_reset": "റീസെറ്റ് ലിങ്ക് അയയ്ക്കുക",
        "auth_new_password": "പുതിയ പാസ്‌വേഡ്",
        "auth_settings": "ക്രമീകരണങ്ങൾ",
        "auth_profile": "പ്രൊഫൈൽ",
        "auth_delete_account": "അക്കൗണ്ട് ഇല്ലാതാക്കുക",
        "auth_confirm_delete": "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക",
        "auth_history": "ചാറ്റ് ചരിത്രം",
        "auth_loading_history": "സംഭാഷണങ്ങൾ ലോഡ് ചെയ്യുന്നു…",
        "auth_no_history": "സംരക്ഷിച്ച സംഭാഷണങ്ങളില്ല.",
        "auth_rename": "പേരുമാറ്റുക",
        "auth_delete": "ഇല്ലാതാക്കുക",
        "auth_history_error": "ചാറ്റ് ചരിത്രം ലോഡ് ചെയ്യാനായില്ല.",
        "auth_title": "സംഭാഷണ ശീർഷകം",
        "auth_delete_confirm": "ഈ സംഭാഷണം ശാശ്വതമായി ഇല്ലാതാക്കണോ?",
        "auth_logout": "സൈൻ ഔട്ട്",
        "auth_consent": "ഞാൻ നിബന്ധനകളും സ്വകാര്യതാ അറിയിപ്പും അംഗീകരിക്കുന്നു.",
        "auth_password_hint": "കുറഞ്ഞത് 12 അക്ഷരങ്ങളുള്ള പാസ്‌വേഡ് ഉപയോഗിക്കുക.",
        "auth_workspace": "നിങ്ങളുടെ ഗവേഷണ വർക്ക്സ്പേസിലേക്ക് സൈൻ ഇൻ ചെയ്യുക.",
        "landing_eyebrow": "ഗവേഷണ അധിഷ്ഠിത ബഹുഭാഷാ AI",
        "landing_title": "ഭാഷാ തടസ്സങ്ങളില്ലാത്ത ബുദ്ധിശക്തി.",
        "landing_copy": "ഇന്ത്യയിലെ വൈവിധ്യമാർന്ന ഭാഷകളിൽ AI എങ്ങനെ മനസ്സിലാക്കുന്നു, വിവരങ്ങൾ കണ്ടെത്തുന്നു, പ്രതികരിക്കുന്നു എന്ന് പരിശോധിക്കുക.",
        "landing_open": "വർക്ക്സ്പേസ് പരിശോധിക്കുക",
        "landing_start": "ആരംഭിക്കുക",
        "landing_cta_workspace": "വർക്ക്സ്പേസ് പരിശോധിക്കുക",
        "landing_cta_research": "ഗവേഷണം പരിശോധിക്കുക",
        "landing_languages": "ആറ് ഭാഷകൾ",
        "landing_languages_copy": "സ്വദേശി ലിപി, റൊമനൈസ്ഡ് ഇൻപുട്ട്, സ്വതന്ത്ര ഭാഷാ നിയന്ത്രണങ്ങൾ.",
        "landing_evidence": "തെളിവ് ആദ്യം",
        "landing_evidence_copy": "BM25 തിരയൽ ഉറവിടഭാഗങ്ങൾ കാണിക്കുകയും ഉപയോഗിച്ച അവലംബങ്ങൾ അടയാളപ്പെടുത്തുകയും ചെയ്യുന്നു.",
        "landing_research": "ഗവേഷണ ദൃശ്യത",
        "landing_research_copy": "അളന്ന തിരയൽ, ഉത്തരം-ഗുണനിലവാര ഫലങ്ങൾ താരതമ്യം ചെയ്യുക.",
        "landing_sec_languages": "പിന്തുണയ്ക്കുന്ന ഭാഷകൾ",
        "landing_sec_languages_desc": "ലിപി-അവബോധ ടോക്കണൈസേഷൻ, റൊമനൈസ്ഡ് അന്വേഷണങ്ങൾ, പ്രത്യേക വിജ്ഞാന ശേഖരങ്ങൾ എന്നിവയോടെ ആറ് ഇന്ത്യൻ ഭാഷകൾ.",
        "landing_sec_retrieval": "ബഹുഭാഷാ തിരയൽ എങ്ങനെ പ്രവർത്തിക്കുന്നു",
        "landing_sec_retrieval_desc": "ലിപി കണ്ടെത്തുകയും റൊമനൈസ്ഡ് ടൈപ്പിംഗ് കൈകാര്യം ചെയ്യുകയും ഭാഷാ-നിർദ്ദിഷ്ട BM25 തിരയുകയും തെളിവുകൾ സ്ഥിരീകരിക്കുകയും ചെയ്യുന്നു.",
        "landing_sec_comp": "ഗവേഷണവും ഭാഷാ താരതമ്യവും",
        "landing_sec_comp_desc": "ക്ലോസ്ഡ്-ബുക്ക്, RAG മോഡുകളിൽ ഇംഗ്ലീഷും പ്രാദേശിക ഇന്ത്യൻ ഭാഷകളും തമ്മിലുള്ള പ്രകടന വ്യത്യാസങ്ങൾ അളക്കുക.",
        "landing_sec_citations": "തെളിവ് അധിഷ്ഠിത ഉത്തരങ്ങളും അവലംബങ്ങളും",
        "landing_sec_citations_desc": "നൽകുന്ന ഓരോ ഉത്തരവും പരിശോധിച്ചുറപ്പിച്ച പിന്തുണ സ്കോറോടെ ഉറവിട ഭാഗങ്ങളുമായി നേരിട്ട് ബന്ധിപ്പിച്ചിരിക്കുന്നു.",
        "landing_sec_eval": "ഭാഷാ-നിർദ്ദിഷ്ട മൂല്യനിർണ്ണയം",
        "landing_sec_eval_desc": "ക്ലോസ്ഡ്-ബുക്ക്, ഗോൾഡ് കോൺടെക്സ്റ്റ്, സ്വദേശി RAG, റൊമനൈസ്ഡ് RAG എന്നിവയിൽ IndicQA അടിസ്ഥാനമാക്കിയുള്ള മൂല്യനിർണ്ണയം.",
        "landing_sec_capabilities": "ഉൽപ്പന്ന ശേഷികൾ",
        "landing_sec_capabilities_desc": "ഭാഷാ ഗവേഷണത്തിനും AI മൂല്യനിർണ്ണയത്തിനുമായി രൂപകൽപ്പന ചെയ്ത ആധുനിക ബഹുഭാഷാ ഗവേഷണ വർക്ക്സ്പേസ്.",
        "settings_language": "ഇന്റർഫേസ് ഭാഷ",
        "settings_language_copy": "വെബ്സൈറ്റ് ലേബലുകൾ, നാവിഗേഷൻ, സിസ്റ്റം സന്ദേശങ്ങൾ.",
        "settings_security": "അക്കൗണ്ട് സുരക്ഷ",
        "settings_security_copy": "പാസ്‌വേഡ് റീസെറ്റ് ഡെലിവറിക്ക് ഇമെയിൽ ദാതാവ് ആവശ്യമാണ്.",
        "settings_delete_copy": "ഇത് നിങ്ങളുടെ പ്രൊഫൈലും സംരക്ഷിച്ച സംഭാഷണങ്ങളും സ്ഥിരമായി ഇല്ലാതാക്കും.",
        "theme_light": "ലൈറ്റ്",
        "theme_dark": "ഡാർക്ക്",
        "theme_toggle": "തീം മാറ്റുക",
        "lang_control_interface": "ഇന്റർഫേസ് ഭാഷ",
        "lang_control_input": "ഇൻപുട്ട് ഭാഷ",
        "lang_control_answer": "ഉത്തരം ഭാഷ",
        "lang_control_script": "ഉത്തരം ലിപി",
        "nav_home": "അവലോകനം",
        "lang_name_en": "ഇംഗ്ലീഷ്",
        "lang_name_hi": "ഹിന്ദി",
        "lang_name_ta": "തമിഴ്",
        "lang_name_te": "തെലുങ്ക്",
        "lang_name_kn": "കന്നഡ",
        "lang_name_ml": "മലയാളം",
        "session_answer_lang_en": "ഇംഗ്ലീഷ്",
        "session_answer_lang_hi": "ഹിന്ദി",
        "session_answer_lang_ta": "തമിഴ്",
        "session_answer_lang_te": "തെലുങ്ക്",
        "session_answer_lang_kn": "കന്നഡ",
        "session_answer_lang_ml": "മലയാളം",
        "chat_choose_language": "ഭാഷ തിരഞ്ഞെടുക്കുക",
        "chat_advanced_options": "കൂടുതൽ ക്രമീകരണങ്ങൾ",
        "chat_simple_model_label": "മോഡൽ: സർവം AI 105B",
        "chat_hero_headline": "നിങ്ങളുടെ ഭാഷയിൽ എന്തും ചോദിക്കൂ",
        "chat_hero_subheadline": "ഭാരതീയ ഭാഷകൾക്കായുള്ള ബഹുഭാഷാ, ഗവേഷണ-പിന്തുണയുള്ള ചാറ്റ്ബോട്ട്",
        "research_hub_title": "ഗവേഷണവും മൂല്യനിർണ്ണയ സ്യൂട്ടും",
    },
}


def _load_translations(lang: str) -> Dict[str, str]:
    """Load translations for a language from JSON file, with caching."""
    if lang in _translation_cache:
        return _translation_cache[lang]

    path = TRANSLATIONS_DIR / f"{lang}.json"
    if not path.exists():
        # Fall back to English if the language file doesn't exist
        path = TRANSLATIONS_DIR / "en.json"

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {}

    # Merge: JSON file takes precedence over EXTRA_TRANSLATIONS fallbacks
    data = {**EXTRA_TRANSLATIONS.get(lang, {}), **data}
    _translation_cache[lang] = data
    return data


def resolve_lang(
    url_lang: Optional[str] = None,
    cookie_lang: Optional[str] = None,
    accept_language: Optional[str] = None,
    session_lang: Optional[str] = None,
) -> str:
    """Resolve the interface language from multiple sources with priority:
    1. URL query parameter (?lang=xx)
    2. Session (interface_lang)
    3. Cookie (bhashacore-ui-lang or bhashacore-lang)
    4. Accept-Language header
    5. Default: en
    """
    SUPPORTED = {"en", "hi", "ta", "te", "kn", "ml"}

    if url_lang and url_lang in SUPPORTED:
        return url_lang

    if session_lang and session_lang in SUPPORTED:
        return session_lang

    if cookie_lang and cookie_lang in SUPPORTED:
        return cookie_lang

    if accept_language:
        for part in accept_language.split(","):
            lang = part.split(";")[0].strip().lower().split("-")[0]
            if lang in SUPPORTED:
                return lang

    return "en"


def t(key: str, lang: str = None, **kwargs: Any) -> str:
    """Translate a key for the given language with optional interpolation.

    Falls back to English if the key is missing in the target language,
    and returns the key itself if not found in English either.
    """
    import flask

    if lang is None:
        try:
            lang = getattr(flask.g, "_interface_lang", None)
            if not lang and hasattr(flask, "session"):
                lang = flask.session.get("interface_lang")
        except (AttributeError, RuntimeError):
            lang = "en"
        if not lang:
            lang = "en"

    translations = _load_translations(lang)
    value = translations.get(key)

    if value is None:
        # Fall back to English
        if lang != "en":
            translations = _load_translations("en")
            value = translations.get(key)

    if value is None:
        return key  # Return the key itself as last resort

    if kwargs:
        try:
            value = value.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return value


def t_lazy(key: str, **kwargs: Any) -> Any:
    """Lazy translation that returns a callable for deferred evaluation."""
    import flask

    def _resolve(lang: str = None) -> str:
        if lang is None:
            try:
                lang = getattr(flask.g, "_interface_lang", None)
                if not lang and hasattr(flask, "session"):
                    lang = flask.session.get("interface_lang")
            except (AttributeError, RuntimeError):
                lang = "en"
            if not lang:
                lang = "en"
        return t(key, lang=lang, **kwargs)
    return _resolve


LANGUAGE_NAMES_BY_INTERFACE = {
    "en": {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
    },
    "hi": {
        "en": "अंग्रेज़ी",
        "hi": "हिंदी",
        "ta": "तमिल",
        "te": "तेलुगु",
        "kn": "कन्नड़",
        "ml": "मलयालम",
    },
    "ta": {
        "en": "ஆங்கிலம்",
        "hi": "இந்தி",
        "ta": "தமிழ்",
        "te": "தெலுங்கு",
        "kn": "கன்னடம்",
        "ml": "மலையாளம்",
    },
    "te": {
        "en": "ఆంగ్లం",
        "hi": "హిందీ",
        "ta": "తమిళం",
        "te": "తెలుగు",
        "kn": "కన్నడ",
        "ml": "మలయాళం",
    },
    "kn": {
        "en": "ಇಂಗ್ಲಿಷ್",
        "hi": "ಹಿಂದಿ",
        "ta": "ತಮಿಳು",
        "te": "ತೆಲುಗು",
        "kn": "ಕನ್ನಡ",
        "ml": "ಮಲಯಾಳಂ",
    },
    "ml": {
        "en": "ഇംഗ്ലീഷ്",
        "hi": "ഹിന്ദി",
        "ta": "തമിഴ്",
        "te": "തെലുങ്ക്",
        "kn": "കന്നഡ",
        "ml": "മലയാളം",
    },
}


def get_available_languages(target_lang: Optional[str] = None) -> Dict[str, str]:
    """Return mapping of language codes to their localized names according to the
    active or specified interface language.
    """
    if not target_lang:
        import flask
        try:
            target_lang = getattr(flask.g, "_interface_lang", None)
            if not target_lang and hasattr(flask, "session"):
                target_lang = flask.session.get("interface_lang")
        except (AttributeError, RuntimeError):
            target_lang = "en"
        if not target_lang:
            target_lang = "en"

    return dict(LANGUAGE_NAMES_BY_INTERFACE.get(target_lang, LANGUAGE_NAMES_BY_INTERFACE["en"]))


def get_language_name(lang: str, target_lang: Optional[str] = None) -> str:
    """Get the localized name for a language code in the target interface language."""
    names = get_available_languages(target_lang)
    return names.get(lang, lang)


def get_translations(lang: str) -> Dict[str, str]:
    """Get the full translation dictionary for a language code."""
    return dict(_load_translations(lang))


def get_all_translations() -> Dict[str, Dict[str, str]]:
    """Get all translations across all supported languages."""
    return {lang: dict(_load_translations(lang)) for lang in ["en", "hi", "te", "ta", "kn", "ml"]}
