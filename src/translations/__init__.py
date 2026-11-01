"""Translation system for BhashaCore UI internationalization.

Loads translation JSON files from src/translations/ and provides:
- A Jinja2 template global function `t(key, **kwargs)` for server-side rendering
- Client-side translation support via the /api/translations endpoint
- Interface language detection from URL query param, cookie, or Accept-Language header
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

# New authenticated-product surface. Kept alongside the existing JSON catalog
# until its next catalog export; `t()` treats these exactly like JSON keys.
EXTRA_TRANSLATIONS = {
 "en": {"auth_sign_in":"Sign in","auth_sign_up":"Create account","auth_email":"Email","auth_password":"Password","auth_full_name":"Full name","auth_confirm_password":"Confirm password","auth_show":"Show","auth_forgot":"Forgot password?","auth_reset":"Reset password","auth_send_reset":"Send reset link","auth_new_password":"New password","auth_settings":"Settings","auth_profile":"Profile","auth_delete_account":"Delete account","auth_confirm_delete":"Confirm password","auth_history":"Chat history","auth_loading_history":"Loading conversations…","auth_no_history":"No saved conversations yet.","auth_rename":"Rename","auth_delete":"Delete","auth_history_error":"Could not load conversation history.","auth_title":"Conversation title","auth_delete_confirm":"Delete this conversation permanently?","landing_eyebrow":"Research-grounded multilingual AI","landing_title":"Ask clearly. Research across languages.","landing_copy":"BhashaCore combines multilingual retrieval, source provenance, and language-aware answering.","landing_open":"Open workspace","landing_start":"Get started"},
 "hi": {"auth_sign_in":"साइन इन","auth_sign_up":"खाता बनाएं","auth_email":"ईमेल","auth_password":"पासवर्ड","auth_full_name":"पूरा नाम","auth_confirm_password":"पासवर्ड की पुष्टि करें","auth_show":"दिखाएं","auth_forgot":"पासवर्ड भूल गए?","auth_reset":"पासवर्ड रीसेट करें","auth_send_reset":"रीसेट लिंक भेजें","auth_new_password":"नया पासवर्ड","auth_settings":"सेटिंग्स","auth_profile":"प्रोफ़ाइल","auth_delete_account":"खाता हटाएं","auth_confirm_delete":"पासवर्ड की पुष्टि करें","auth_history":"चैट इतिहास","auth_loading_history":"वार्तालाप लोड हो रहे हैं…","auth_no_history":"कोई सहेजा वार्तालाप नहीं।","auth_rename":"नाम बदलें","auth_delete":"हटाएं","auth_history_error":"चैट इतिहास लोड नहीं हो सका।","auth_title":"वार्तालाप शीर्षक","auth_delete_confirm":"इस वार्तालाप को स्थायी रूप से हटाएं?","landing_eyebrow":"शोध-आधारित बहुभाषी एआई","landing_title":"स्पष्ट पूछें। भाषाओं में शोध करें।","landing_copy":"BhashaCore बहुभाषी खोज, स्रोत प्रमाण और भाषा-सचेत उत्तर जोड़ता है।","landing_open":"कार्यस्थान खोलें","landing_start":"शुरू करें"},
 "te": {"auth_sign_in":"సైన్ ఇన్","auth_sign_up":"ఖాతా సృష్టించండి","auth_email":"ఇమెయిల్","auth_password":"పాస్‌వర్డ్","auth_full_name":"పూర్తి పేరు","auth_confirm_password":"పాస్‌వర్డ్ నిర్ధారించండి","auth_show":"చూపు","auth_forgot":"పాస్‌వర్డ్ మర్చిపోయారా?","auth_reset":"పాస్‌వర్డ్ రీసెట్","auth_send_reset":"రీసెట్ లింక్ పంపు","auth_new_password":"కొత్త పాస్‌వర్డ్","auth_settings":"సెట్టింగ్‌లు","auth_profile":"ప్రొఫైల్","auth_delete_account":"ఖాతా తొలగించండి","auth_confirm_delete":"పాస్‌వర్డ్ నిర్ధారించండి","auth_history":"చాట్ చరిత్ర","auth_loading_history":"సంభాషణలు లోడ్ అవుతున్నాయి…","auth_no_history":"సేవ్ చేసిన సంభాషణలు లేవు.","auth_rename":"పేరు మార్చండి","auth_delete":"తొలగించండి","auth_history_error":"చాట్ చరిత్ర లోడ్ కాలేదు.","auth_title":"సంభాషణ శీర్షిక","auth_delete_confirm":"ఈ సంభాషణను శాశ్వతంగా తొలగించాలా?","landing_eyebrow":"పరిశోధన ఆధారిత బహుభాషా AI","landing_title":"స్పష్టంగా అడగండి. భాషలలో పరిశోధించండి.","landing_copy":"BhashaCore బహుభాషా శోధన, మూలాధారాలు మరియు భాషా అవగాహనతో సమాధానాలను కలుపుతుంది.","landing_open":"వర్క్‌స్పేస్ తెరవండి","landing_start":"ప్రారంభించండి"},
 "ta": {"auth_sign_in":"உள்நுழைய","auth_sign_up":"கணக்கை உருவாக்கவும்","auth_email":"மின்னஞ்சல்","auth_password":"கடவுச்சொல்","auth_full_name":"முழுப் பெயர்","auth_confirm_password":"கடவுச்சொல்லை உறுதிப்படுத்தவும்","auth_show":"காட்டு","auth_forgot":"கடவுச்சொல் மறந்துவிட்டதா?","auth_reset":"கடவுச்சொல்லை மீட்டமை","auth_send_reset":"மீட்டமைப்பு இணைப்பை அனுப்பு","auth_new_password":"புதிய கடவுச்சொல்","auth_settings":"அமைப்புகள்","auth_profile":"சுயவிவரம்","auth_delete_account":"கணக்கை நீக்கு","auth_confirm_delete":"கடவுச்சொல்லை உறுதிப்படுத்தவும்","auth_history":"அரட்டை வரலாறு","auth_loading_history":"உரையாடல்கள் ஏற்றப்படுகின்றன…","auth_no_history":"சேமித்த உரையாடல்கள் இல்லை.","auth_rename":"மறுபெயரிடு","auth_delete":"நீக்கு","auth_history_error":"அரட்டை வரலாற்றை ஏற்ற முடியவில்லை.","auth_title":"உரையாடல் தலைப்பு","auth_delete_confirm":"இந்த உரையாடலை நிரந்தரமாக நீக்கவா?","landing_eyebrow":"ஆராய்ச்சி அடிப்படையிலான பன்மொழி AI","landing_title":"தெளிவாகக் கேளுங்கள். மொழிகளில் ஆராயுங்கள்.","landing_copy":"BhashaCore பன்மொழி தேடல், மூல ஆதாரம் மற்றும் மொழி உணர்வுள்ள பதில்களை இணைக்கிறது.","landing_open":"பணியிடத்தைத் திறக்கவும்","landing_start":"தொடங்குங்கள்"},
 "kn": {"auth_sign_in":"ಸೈನ್ ಇನ್","auth_sign_up":"ಖಾತೆ ರಚಿಸಿ","auth_email":"ಇಮೇಲ್","auth_password":"ಪಾಸ್‌ವರ್ಡ್","auth_full_name":"ಪೂರ್ಣ ಹೆಸರು","auth_confirm_password":"ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ","auth_show":"ತೋರಿಸಿ","auth_forgot":"ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?","auth_reset":"ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ","auth_send_reset":"ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ಕಳುಹಿಸಿ","auth_new_password":"ಹೊಸ ಪಾಸ್‌ವರ್ಡ್","auth_settings":"ಸೆಟ್ಟಿಂಗ್‌ಗಳು","auth_profile":"ಪ್ರೊಫೈಲ್","auth_delete_account":"ಖಾತೆ ಅಳಿಸಿ","auth_confirm_delete":"ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ","auth_history":"ಚಾಟ್ ಇತಿಹಾಸ","auth_loading_history":"ಸಂಭಾಷಣೆಗಳು ಲೋಡ್ ಆಗುತ್ತಿವೆ…","auth_no_history":"ಉಳಿಸಿದ ಸಂಭಾಷಣೆಗಳಿಲ್ಲ.","auth_rename":"ಮರುಹೆಸರಿಸಿ","auth_delete":"ಅಳಿಸಿ","auth_history_error":"ಚಾಟ್ ಇತಿಹಾಸ ಲೋಡ್ ಆಗಲಿಲ್ಲ.","auth_title":"ಸಂಭಾಷಣೆ ಶೀರ್ಷಿಕೆ","auth_delete_confirm":"ಈ ಸಂಭಾಷಣೆಯನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸಬೇಕೇ?","landing_eyebrow":"ಸಂಶೋಧನೆ ಆಧಾರಿತ ಬಹುಭಾಷಾ AI","landing_title":"ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿ. ಭಾಷೆಗಳಲ್ಲಿ ಸಂಶೋಧಿಸಿ.","landing_copy":"BhashaCore ಬಹುಭಾಷಾ ಹುಡುಕಾಟ, ಮೂಲ ಆಧಾರ ಮತ್ತು ಭಾಷಾ ಅರಿವಿನ ಉತ್ತರಗಳನ್ನು ಒಗ್ಗೂಡಿಸುತ್ತದೆ.","landing_open":"ಕಾರ್ಯಕ್ಷೇತ್ರ ತೆರೆಯಿರಿ","landing_start":"ಪ್ರಾರಂಭಿಸಿ"},
 "ml": {"auth_sign_in":"സൈൻ ഇൻ","auth_sign_up":"അക്കൗണ്ട് സൃഷ്ടിക്കുക","auth_email":"ഇമെയിൽ","auth_password":"പാസ്‌വേഡ്","auth_full_name":"പൂർണ്ണ പേര്","auth_confirm_password":"പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക","auth_show":"കാണിക്കുക","auth_forgot":"പാസ്‌വേഡ് മറന്നോ?","auth_reset":"പാസ്‌വേഡ് പുനഃസജ്ജമാക്കുക","auth_send_reset":"റീസെറ്റ് ലിങ്ക് അയയ്ക്കുക","auth_new_password":"പുതിയ പാസ്‌വേഡ്","auth_settings":"ക്രമീകരണങ്ങൾ","auth_profile":"പ്രൊഫൈൽ","auth_delete_account":"അക്കൗണ്ട് ഇല്ലാതാക്കുക","auth_confirm_delete":"പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക","auth_history":"ചാറ്റ് ചരിത്രം","auth_loading_history":"സംഭാഷണങ്ങൾ ലോഡ് ചെയ്യുന്നു…","auth_no_history":"സംരക്ഷിച്ച സംഭാഷണങ്ങളില്ല.","auth_rename":"പേരുമാറ്റുക","auth_delete":"ഇല്ലാതാക്കുക","auth_history_error":"ചാറ്റ് ചരിത്രം ലോഡ് ചെയ്യാനായില്ല.","auth_title":"സംഭാഷണ ശീർഷകം","auth_delete_confirm":"ഈ സംഭാഷണം ശാശ്വതമായി ഇല്ലാതാക്കണോ?","landing_eyebrow":"ഗവേഷണ അധിഷ്ഠിത ബഹുഭാഷാ AI","landing_title":"വ്യക്തമായി ചോദിക്കൂ. ഭാഷകളിൽ ഗവേഷണം നടത്തൂ.","landing_copy":"BhashaCore ബഹുഭാഷാ തിരയൽ, ഉറവിട തെളിവ്, ഭാഷാബോധമുള്ള ഉത്തരങ്ങൾ എന്നിവ കൂട്ടിച്ചേർക്കുന്നു.","landing_open":"വർക്ക്സ്പേസ് തുറക്കുക","landing_start":"ആരംഭിക്കുക"},
}
EXTRA_TRANSLATIONS["en"]["auth_logout"] = "Sign out"
EXTRA_TRANSLATIONS["hi"]["auth_logout"] = "साइन आउट"
EXTRA_TRANSLATIONS["te"]["auth_logout"] = "సైన్ అవుట్"
EXTRA_TRANSLATIONS["ta"]["auth_logout"] = "வெளியேறு"
EXTRA_TRANSLATIONS["kn"]["auth_logout"] = "ಸೈನ್ ಔಟ್"
EXTRA_TRANSLATIONS["ml"]["auth_logout"] = "സൈൻ ഔട്ട്"
EXTRA_TRANSLATIONS["en"]["auth_consent"] = "I accept the terms and privacy notice."
EXTRA_TRANSLATIONS["hi"]["auth_consent"] = "मैं शर्तें और गोपनीयता सूचना स्वीकार करता/करती हूं।"
EXTRA_TRANSLATIONS["te"]["auth_consent"] = "నేను నిబంధనలు మరియు గోప్యతా సూచనను అంగీకరిస్తున్నాను."
EXTRA_TRANSLATIONS["ta"]["auth_consent"] = "விதிமுறைகளையும் தனியுரிமை அறிவிப்பையும் ஏற்கிறேன்."
EXTRA_TRANSLATIONS["kn"]["auth_consent"] = "ನಾನು ನಿಯಮಗಳು ಮತ್ತು ಗೌಪ್ಯತಾ ಸೂಚನೆಯನ್ನು ಒಪ್ಪುತ್ತೇನೆ."
EXTRA_TRANSLATIONS["ml"]["auth_consent"] = "ഞാൻ നിബന്ധനകളും സ്വകാര്യതാ അറിയിപ്പും അംഗീകരിക്കുന്നു."
EXTRA_TRANSLATIONS["en"].update({"landing_languages":"Six languages","landing_languages_copy":"Native script, Romanized input, and independent interface and answer-language controls.","landing_evidence":"Evidence first","landing_evidence_copy":"BM25 retrieval surfaces source passages and marks references used to support an answer.","landing_research":"Research visibility","landing_research_copy":"Compare measured retrieval and answer-quality results across the evaluated language set.","settings_language":"Interface language","settings_language_copy":"Use the language selector in the header. Your selection is saved in a browser cookie.","settings_security":"Account security","settings_security_copy":"Password reset delivery needs a configured email provider.","settings_delete_copy":"This permanently deletes your profile and saved conversations.","auth_password_hint":"Use a password of at least 12 characters.","auth_workspace":"Sign in to your research workspace."})
EXTRA_TRANSLATIONS["hi"].update({"landing_languages":"छह भाषाएं","landing_languages_copy":"मूल लिपि, रोमन इनपुट और स्वतंत्र इंटरफ़ेस व उत्तर भाषा नियंत्रण।","landing_evidence":"साक्ष्य पहले","landing_evidence_copy":"BM25 खोज स्रोत अंश दिखाती है और उत्तर में उपयोग हुए संदर्भों को चिह्नित करती है।","landing_research":"शोध दृश्यता","landing_research_copy":"मापे गए खोज और उत्तर-गुणवत्ता परिणामों की तुलना करें।","settings_language":"इंटरफ़ेस भाषा","settings_language_copy":"हेडर में भाषा चयनकर्ता का उपयोग करें। चयन ब्राउज़र कुकी में सहेजा जाता है।","settings_security":"खाता सुरक्षा","settings_security_copy":"पासवर्ड रीसेट डिलीवरी के लिए ईमेल प्रदाता आवश्यक है।","settings_delete_copy":"यह आपकी प्रोफ़ाइल और सहेजे वार्तालापों को स्थायी रूप से हटाता है।","auth_password_hint":"कम से कम 12 वर्ण का पासवर्ड उपयोग करें।","auth_workspace":"अपने शोध कार्यस्थान में साइन इन करें।"})
EXTRA_TRANSLATIONS["te"].update({"landing_languages":"ఆరు భాషలు","landing_languages_copy":"స్థానిక లిపి, రోమనైజ్డ్ ఇన్‌పుట్ మరియు స్వతంత్ర భాష నియంత్రణలు.","landing_evidence":"ఆధారం ముందుగా","landing_evidence_copy":"BM25 శోధన మూల భాగాలను చూపి ఉపయోగించిన ఆధారాలను గుర్తిస్తుంది.","landing_research":"పరిశోధన దృశ్యం","landing_research_copy":"కొలిచిన శోధన మరియు సమాధాన నాణ్యత ఫలితాలను పోల్చండి.","settings_language":"ఇంటర్‌ఫేస్ భాష","settings_language_copy":"హెడర్‌లోని భాష ఎంపికను ఉపయోగించండి. ఎంపిక కుకీలో సేవ్ అవుతుంది.","settings_security":"ఖాతా భద్రత","settings_security_copy":"పాస్‌వర్డ్ రీసెట్ పంపడానికి ఇమెయిల్ ప్రొవైడర్ కావాలి.","settings_delete_copy":"ఇది మీ ప్రొఫైల్ మరియు సేవ్ చేసిన సంభాషణలను శాశ్వతంగా తొలగిస్తుంది.","auth_password_hint":"కనీసం 12 అక్షరాల పాస్‌వర్డ్ ఉపయోగించండి.","auth_workspace":"మీ పరిశోధన వర్క్‌స్పేస్‌లో సైన్ ఇన్ చేయండి."})
EXTRA_TRANSLATIONS["ta"].update({"landing_languages":"ஆறு மொழிகள்","landing_languages_copy":"தாய்மொழி எழுத்து, ரோமானிய உள்ளீடு மற்றும் தனித்த மொழிக் கட்டுப்பாடுகள்.","landing_evidence":"ஆதாரம் முதலில்","landing_evidence_copy":"BM25 தேடல் மூலப் பகுதிகளைக் காட்டி பயன்படுத்திய ஆதாரங்களைக் குறிக்கிறது.","landing_research":"ஆராய்ச்சி பார்வை","landing_research_copy":"அளவிடப்பட்ட தேடல் மற்றும் பதில் தர முடிவுகளை ஒப்பிடுங்கள்.","settings_language":"இடைமுக மொழி","settings_language_copy":"தலைப்பில் உள்ள மொழித் தேர்வியைப் பயன்படுத்தவும். தேர்வு குக்கியில் சேமிக்கப்படும்.","settings_security":"கணக்கு பாதுகாப்பு","settings_security_copy":"கடவுச்சொல் மீட்டமைப்புக்கு மின்னஞ்சல் வழங்குநர் தேவை.","settings_delete_copy":"இது உங்கள் சுயவிவரத்தையும் சேமித்த உரையாடல்களையும் நிரந்தரமாக நீக்கும்.","auth_password_hint":"குறைந்தது 12 எழுத்துகள் கொண்ட கடவுச்சொல்லைப் பயன்படுத்தவும்.","auth_workspace":"உங்கள் ஆராய்ச்சி பணியிடத்தில் உள்நுழையவும்."})
EXTRA_TRANSLATIONS["kn"].update({"landing_languages":"ಆರು ಭಾಷೆಗಳು","landing_languages_copy":"ಸ್ಥಳೀಯ ಲಿಪಿ, ರೋಮನೀಕೃತ ಇನ್‌ಪುಟ್ ಮತ್ತು ಸ್ವತಂತ್ರ ಭಾಷಾ ನಿಯಂತ್ರಣಗಳು.","landing_evidence":"ಮೊದಲು ಆಧಾರ","landing_evidence_copy":"BM25 ಹುಡುಕಾಟ ಮೂಲ ಭಾಗಗಳನ್ನು ತೋರಿಸಿ ಬಳಸಿದ ಉಲ್ಲೇಖಗಳನ್ನು ಗುರುತಿಸುತ್ತದೆ.","landing_research":"ಸಂಶೋಧನಾ ದೃಶ್ಯ","landing_research_copy":"ಅಳತೆಯಾದ ಹುಡುಕಾಟ ಮತ್ತು ಉತ್ತರ-ಗುಣಮಟ್ಟದ ಫಲಿತಾಂಶಗಳನ್ನು ಹೋಲಿಸಿ.","settings_language":"ಇಂಟರ್‌ಫೇಸ್ ಭಾಷೆ","settings_language_copy":"ಹೆಡರ್‌ನ ಭಾಷಾ ಆಯ್ಕೆಯನ್ನು ಬಳಸಿ. ಆಯ್ಕೆ ಕುಕಿಯಲ್ಲಿ ಉಳಿಯುತ್ತದೆ.","settings_security":"ಖಾತೆ ಭದ್ರತೆ","settings_security_copy":"ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸುವ ವಿತರಣೆಗೆ ಇಮೇಲ್ ಪೂರೈಕೆದಾರ ಬೇಕು.","settings_delete_copy":"ಇದು ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಉಳಿಸಿದ ಸಂಭಾಷಣೆಗಳನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸುತ್ತದೆ.","auth_password_hint":"ಕನಿಷ್ಠ 12 ಅಕ್ಷರಗಳ ಪಾಸ್‌ವರ್ಡ್ ಬಳಸಿ.","auth_workspace":"ನಿಮ್ಮ ಸಂಶೋಧನಾ ಕಾರ್ಯಕ್ಷೇತ್ರಕ್ಕೆ ಸೈನ್ ಇನ್ ಮಾಡಿ."})
EXTRA_TRANSLATIONS["ml"].update({"landing_languages":"ആറ് ഭാഷകൾ","landing_languages_copy":"സ്വദേശി ലിപി, റൊമനൈസ്ഡ് ഇൻപുട്ട്, സ്വതന്ത്ര ഭാഷാ നിയന്ത്രണങ്ങൾ.","landing_evidence":"തെളിവ് ആദ്യം","landing_evidence_copy":"BM25 തിരയൽ ഉറവിടഭാഗങ്ങൾ കാണിക്കുകയും ഉപയോഗിച്ച അവലംബങ്ങൾ അടയാളപ്പെടുത്തുകയും ചെയ്യുന്നു.","landing_research":"ഗവേഷണ ദൃശ്യത","landing_research_copy":"അളന്ന തിരയൽ, ഉത്തരം-ഗുണനിലവാര ഫലങ്ങൾ താരതമ്യം ചെയ്യുക.","settings_language":"ഇന്റർഫേസ് ഭാഷ","settings_language_copy":"ഹെഡറിലെ ഭാഷാ തിരഞ്ഞെടുപ്പ് ഉപയോഗിക്കുക. തിരഞ്ഞെടുപ്പ് കുക്കിയിൽ സൂക്ഷിക്കും.","settings_security":"അക്കൗണ്ട് സുരക്ഷ","settings_security_copy":"പാസ്‌വേഡ് റീസെറ്റ് ഡെലിവറിക്ക് ഇമെയിൽ ദാതാവ് ആവശ്യമാണ്.","settings_delete_copy":"ഇത് നിങ്ങളുടെ പ്രൊഫൈലും സംരക്ഷിച്ച സംഭാഷണങ്ങളും സ്ഥിരമായി ഇല്ലാതാക്കും.","auth_password_hint":"കുറഞ്ഞത് 12 അക്ഷരങ്ങളുള്ള പാസ്‌വേഡ് ഉപയോഗിക്കുക.","auth_workspace":"നിങ്ങളുടെ ഗവേഷണ വർക്ക്സ്പേസിലേക്ക് സൈൻ ഇൻ ചെയ്യുക."})


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

    data = {**EXTRA_TRANSLATIONS.get(lang, {}), **data}
    _translation_cache[lang] = data
    return data


def resolve_lang(
    url_lang: Optional[str] = None,
    cookie_lang: Optional[str] = None,
    accept_language: Optional[str] = None,
) -> str:
    """Resolve the interface language from multiple sources with priority:
    1. URL query parameter (?lang=xx)
    2. Cookie (bhashacore-lang=xx)
    3. Accept-Language header
    4. Default: en
    """
    SUPPORTED = {"en", "hi", "ta", "te", "kn", "ml"}

    if url_lang and url_lang in SUPPORTED:
        return url_lang

    if cookie_lang and cookie_lang in SUPPORTED:
        return cookie_lang

    if accept_language:
        # Parse Accept-Language header like "en-US,en;q=0.9,hi;q=0.8"
        for part in accept_language.split(","):
            lang = part.split(";")[0].strip().lower()
            # Handle language-region codes like en-US -> en
            lang = lang.split("-")[0]
            if lang in SUPPORTED:
                return lang

    return "en"


def t(key: str, lang: str = None, **kwargs: Any) -> str:
    """Translate a key for the given language with optional interpolation.

    Usage:
        t("chat_send", lang="hi")  -> "भेजें"
        t("status_answered", lang="en", count=3)  -> "Answered — grounded in 3 retrieved passages"

    Falls back to English if the key is missing in the target language,
    and returns the key itself if not found in English either.

    If lang is None, tries to get the current request language from Flask's g object.
    """
    import flask

    if lang is None:
        try:
            lang = flask.g._interface_lang  # type: ignore[attr-defined]
        except (AttributeError, RuntimeError):
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

    # Interpolate {key} placeholders from kwargs
    if kwargs:
        try:
            value = value.format(**kwargs)
        except (KeyError, IndexError):
            pass  # Return unformatted if interpolation fails

    return value


def t_lazy(key: str, **kwargs: Any) -> str:
    """Lazy translation that returns a callable for deferred evaluation.
    Useful when the language isn't known at definition time.
    """
    import flask

    def _resolve(lang: str = None) -> str:
        if lang is None:
            try:
                lang = flask.g._interface_lang  # type: ignore[attr-defined]
            except (AttributeError, RuntimeError):
                lang = "en"
        return t(key, lang=lang, **kwargs)
    return _resolve


def get_available_languages() -> Dict[str, str]:
    """Return mapping of language codes to their native names."""
    return {
        "en": "English",
        "hi": "हिन्दी",
        "ta": "தமிழ்",
        "te": "తెలుగు",
        "kn": "ಕನ್ನಡ",
        "ml": "മലയാളം",
    }


def get_language_name(lang: str) -> str:
    """Get the native name for a language code."""
    names = get_available_languages()
    return names.get(lang, lang)
