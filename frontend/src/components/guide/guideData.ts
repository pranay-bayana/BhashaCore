import { LanguageCode } from '@/types/api';
import { GuideTopic, GuideCategory } from '@/types/guide';

export const GUIDE_TOPICS: GuideTopic[] = [
  {
    id: 'new_chat',
    category: 'getting_started',
    title: {
      en: 'How to Start a New Chat',
      hi: 'नई बातचीत कैसे शुरू करें',
      te: 'కొత్త చాట్ ఎలా ప్రారంభించాలి',
      ta: 'புதிய உரையாடலை எவ்வாறு தொடங்குவது',
      kn: 'ಹೊಸ ಚಾಟ್ ಅನ್ನು ಹೇಗೆ ಪ್ರಾರಂಭಿಸುವುದು',
      ml: 'ഒരു പുതിയ ചാറ്റ് എങ്ങനെ ആരംഭിക്കാം',
    },
    question: {
      en: 'How do I start a new conversation?',
      hi: 'मैं नई बातचीत कैसे शुरू करूं?',
      te: 'నేను కొత్త సంభాషణను ఎలా ప్రారంభించగలను?',
      ta: 'நான் எப்படி புதிய உரையாடலைத் தொடங்குவது?',
      kn: 'ನಾನು ಹೊಸ ಸಂಭಾಷಣೆಯನ್ನು ಹೇಗೆ ಪ್ರಾರಂಭಿಸುವುದು?',
      ml: 'ഞാൻ എങ്ങനെയാണ് ഒരു പുതിയ സംഭാഷണം ആരംഭിക്കുന്നത്?',
    },
    answer: {
      en: 'To start a fresh conversation, click the green "+ New chat" button in the left sidebar or the top header navigation. You can also press Ctrl+K (or Cmd+K on macOS). This clears the current workspace, creates a clean session ID, and focuses the composer.',
      hi: 'नई बातचीत शुरू करने के लिए, बाएं साइडबार या शीर्ष नेविगेशन में हरे "+ New chat" बटन पर क्लिक करें। आप Ctrl+K (या Mac पर Cmd+K) भी दबा सकते हैं। यह कार्यक्षेत्र को साफ़ करता है और नया सत्र बनाता है।',
      te: 'కొత్త సంభాషణను ప్రారంభించడానికి, ఎడమ సైడ్‌బార్ లేదా పైభాగంలో ఉన్న ఆకుపచ్చ "+ New chat" బటన్‌పై క్లిక్ చేయండి. మీరు Ctrl+K (లేదా Macలో Cmd+K) కూడా నొక్కవచ్చు. ఇది కొత్త సెషన్‌ను సృష్టిస్తుంది.',
      ta: 'புதிய உரையாடலைத் தொடங்க, இடது பக்கப்பட்டி அல்லது மேல் வழிசெலுத்தலில் உள்ள பச்சை "+ New chat" பொத்தானைக் கிளிக் செய்யவும். அல்லது Ctrl+K (Mac-ல் Cmd+K) அழுத்தலாம். இது புதிய அமர்வை உருவாக்கும்.',
      kn: 'ಹೊಸ ಸಂಭಾಷಣೆಯನ್ನು ಪ್ರಾರಂಭಿಸಲು, ಎಡ ಸೈಡ್‌ಬಾರ್ ಅಥವಾ ಮೇಲಿನ ನ್ಯಾವಿಗೇಶನ್‌ನಲ್ಲಿರುವ ಹಸಿರು "+ New chat" ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ. ಅಥವಾ Ctrl+K (Mac ನಲ್ಲಿ Cmd+K) ಒತ್ತಿ.',
      ml: 'ഒരു പുതിയ സംഭാഷണം ആരംഭിക്കാൻ, ഇടത് സൈഡ്ബാർ അല്ലെങ്കിൽ മുകളിലെ നാവിഗേഷനിലെ പച്ച "+ New chat" ബട്ടൺ ക്ലിക്കുചെയ്യുക. അല്ലെങ്കിൽ Ctrl+K (Mac-ൽ Cmd+K) അമർത്താം.',
    },
    keywords: ['new chat', 'start', 'begin', 'reset', 'clear', 'ctrl k', 'cmd k', 'नया', 'కొత్త', 'புதிய', 'ಹೊಸ', 'പുതിയ'],
    action: {
      type: 'navigate',
      target: 'chat',
      label: {
        en: 'Go to Chat Workspace',
        hi: 'चैट वर्कस्पेस पर जाएं',
        te: 'చాట్ వర్క్‌స్పేస్‌కి వెళ్లండి',
        ta: 'அரட்டைக்குச் செல்லவும்',
        kn: 'ಚಾಟ್‌ಗೆ ಹೋಗಿ',
        ml: 'ചാറ്റിലേക്ക് പോകുക',
      },
    },
  },
  {
    id: 'six_languages',
    category: 'languages',
    title: {
      en: 'Asking in Six Supported Languages',
      hi: 'छह समर्थित भाषाओं में पूछना',
      te: 'ఆరు మద్దతు గల భాషలలో అడగడం',
      ta: 'ஆறு ஆதரிக்கப்படும் மொழிகளில் கேட்பது',
      kn: 'ಆರು ಬೆಂಬಲಿತ ಭಾಷೆಗಳಲ್ಲಿ ಪ್ರಶ್ನಿಸುವುದು',
      ml: 'പിന്തുണയ്ക്കുന്ന ആറ് ഭാഷകളിൽ ചോദിക്കുന്നത്',
    },
    question: {
      en: 'Which languages are supported and how do I ask in them?',
      hi: 'कौन सी भाषाएं समर्थित हैं और मैं उनमें कैसे पूछूं?',
      te: 'ఏ భాషలకు మద్దతు ఉంది మరియు వాటిలో ఎలా అడగాలి?',
      ta: 'எந்த மொழிகள் ஆதரிக்கப்படுகின்றன, அவற்றில் எவ்வாறு கேட்பது?',
      kn: 'ಯಾವ ಭಾಷೆಗಳು ಬೆಂಬಲಿತವಾಗಿವೆ ಮತ್ತು ಅವುಗಳಲ್ಲಿ ಹೇಗೆ ಕೇಳುವುದು?',
      ml: 'ഏതൊക്കെ ഭാഷകളാണ് പിന്തുണയ്ക്കുന്നത്, അവയിൽ എങ്ങനെ ചോദിക്കാം?',
    },
    answer: {
      en: 'BhashaCore fully supports six languages: English (en), Hindi (hi), Telugu (te), Tamil (ta), Kannada (kn), and Malayalam (ml). You can type in the native script (e.g., తెలుగు, हिन्दी) or in Romanized letters (e.g., "photosynthesis ante enti"). Our script bridge handles Romanized Indic text automatically.',
      hi: 'भाषाकोर छह भाषाओं का समर्थन करता है: अंग्रेजी, हिंदी, तेलुगु, तमिल, कन्नड़ और मलयालम। आप मूल लिपि या रोमन अक्षरों ("Hinglish") में टाइप कर सकते हैं। हमारा स्क्रिप्ट ब्रिज इसे स्वचालित रूप से संभालता है।',
      te: 'భాషాకోర్ ఆరు భాషలకు పూర్తి మద్దతు ఇస్తుంది: ఇంగ్లీష్, హిందీ, తెలుగు, తమిళం, కన్నడ మరియు మలయాళం. మీరు స్థానిక లిపిలో లేదా రోమనైజ్డ్ అక్షరాలలో ("photosynthesis ante enti") టైప్ చేయవచ్చు.',
      ta: 'பாஷாகோர் ஆறு மொழிகளை ஆதரிக்கிறது: ஆங்கிலம், இந்தி, தெலுங்கு, தமிழ், கன்னடம் மற்றும் மலையாளம். நீங்கள் தமிழ் எழுத்துக்களிலோ அல்லது ஆங்கில எழுத்துக்களிலோ ("Tanglish") தட்டச்சு செய்யலாம்.',
      kn: 'ಭಾಷಾಕೋರ್ ಆರು ಭಾಷೆಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ: ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ, ತೆಲುಗು, ತಮಿಳು, ಕನ್ನಡ ಮತ್ತು ಮಲಯಾಳಂ. ನೀವು ಸ್ಥಳೀಯ ಲಿಪಿಯಲ್ಲಿ ಅಥವಾ ರೋಮನ್ ಅಕ್ಷರಗಳಲ್ಲಿ ಟೈಪ್ ಮಾಡಬಹುದು.',
      ml: 'ഭാഷാകോർ ആറ് ഭാഷകളെ പിന്തുണയ്ക്കുന്നു: ഇംഗ്ലീഷ്, ഹിന്ദി, തെലുങ്ക്, തമിഴ്, കന്നഡ, മലയാളം. നിങ്ങൾക്ക് മലയാളം ലിപിയിലോ അല്ലെങ്കിൽ റോമൻ അക്ഷരങ്ങളിലോ ("Manglish") ടൈപ്പ് ചെയ്യാം.',
    },
    keywords: ['languages', 'hindi', 'telugu', 'tamil', 'kannada', 'malayalam', 'english', 'scripts', 'romanized', 'hinglish', 'tanglish', 'భాషలు', 'மொழிகள்', 'ಭಾಷೆಗಳು', 'ഭാഷകൾ', 'भाषाएं'],
    action: {
      type: 'navigate',
      target: 'chat',
      label: {
        en: 'Try in Chat',
        hi: 'चैट में आज़माएं',
        te: 'చాట్‌లో ప్రయత్నించండి',
        ta: 'அரட்டையில் முயற்சிக்கவும்',
        kn: 'ಚಾಟ್‌ನಲ್ಲಿ ಪ್ರಯತ್ನಿಸಿ',
        ml: 'ചാറ്റിൽ പരീക്ഷിക്കുക',
      },
    },
  },
  {
    id: 'auto_detection',
    category: 'languages',
    title: {
      en: 'How Auto-Detect Works',
      hi: 'ऑटो-डिटेक्ट कैसे काम करता है',
      te: 'ఆటో-డిటెక్ట్ ఎలా పనిచేస్తుంది',
      ta: 'தானியங்கு கண்டறிதல் எவ்வாறு செயல்படுகிறது',
      kn: 'ಆಟೋ-ಡಿಟೆಕ್ಟ್ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ',
      ml: 'ഓട്ടോ-ഡിറ്റക്ട് എങ്ങനെ പ്രവർത്തിക്കുന്നു',
    },
    question: {
      en: 'How does automatic language detection work?',
      hi: 'स्वचालित भाषा पहचान कैसे काम करती है?',
      te: 'స్వయంచాలక భాషా గుర్తింపు ఎలా పనిచేస్తుంది?',
      ta: 'தானியங்கு மொழி கண்டறிதல் எவ்வாறு செயல்படுகிறது?',
      kn: 'ಸ್ವಯಂಚಾಲಿತ ಭಾಷಾ ಪತ್ತೆ ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ?',
      ml: 'യാന്ത്രിക ഭാഷ കണ്ടെത്തൽ എങ്ങനെ പ്രവർത്തിക്കുന്നു?',
    },
    answer: {
      en: 'When set to "Auto-detect" (default), BhashaCore analyzes the Unicode script purity of your input. Devanagari maps to Hindi, Telugu script to Telugu, etc. For Latin text, it checks for distinctive Indic vocabulary markers (e.g. "enti", "kya", "enna"); if absent, it reliably defaults to English. It never uses cross-corpus BM25 guessing.',
      hi: 'जब "ऑटो-डिटेक्ट" चुना जाता है, तो भाषाकोर इनपुट की यूनिकोड लिपि शुद्धता का विश्लेषण करता है। लैटिन लिपि के लिए यह विशिष्ट शब्दावली मार्करों की जांच करता है और कभी भी गलत भाषा का अनुमान नहीं लगाता।',
      te: '"Auto-detect" ఎంపిక చేసినప్పుడు, భాషాకోర్ మీ ఇన్‌పుట్ యొక్క యూ Longitudinal లిపిని విశ్లేషిస్తుంది. లాటిన్ అక్షరాల కోసం ఇది ప్రత్యేకమైన పద గుర్తులను పరిశీలిస్తుంది మరియు విశ్వసనీయంగా పనిచేస్తుంది.',
      ta: '"Auto-detect" இருக்கும் போது, உங்கள் உள்ளீட்டின் யுனிகோட் எழுத்துக்களை பாஷாகோர் பகுப்பாய்வு செய்கிறது. தவறான மொழி யூகங்கள் எதுவும் செய்யப்படுவதில்லை.',
      kn: '"Auto-detect" ಮೋಡ್‌ನಲ್ಲಿ, ನಿಮ್ಮ ಇನ್‌ಪುಟ್‌ನ ಯುನಿಕೋಡ್ ಲಿಪಿಯನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಸರಿಯಾದ ಭಾಷೆಯನ್ನು ಗುರುತಿಸಲಾಗುತ್ತದೆ.',
      ml: '"Auto-detect" മോഡിൽ, നിങ്ങളുടെ ഇൻപുട്ടിന്റെ യൂണികോഡ് ലിപി പരിശോധിച്ച് ശരിയായ ഭാഷ കൃത്യമായി തിരിച്ചറിയുന്നു.',
    },
    keywords: ['auto detect', 'automatic', 'detection', 'script purity', 'identify', 'पहचान', 'గుర్తింపు', 'கண்டறிதல்'],
  },
  {
    id: 'manual_selection',
    category: 'languages',
    title: {
      en: 'Manual Language Selection',
      hi: 'मैन्युअल भाषा चयन',
      te: 'మాన్యువల్ భాషా ఎంపిక',
      ta: 'கைமுறை மொழி தேர்வு',
      kn: 'ಹಸ್ತಚಾಲಿತ ಭಾಷಾ ಆಯ್ಕೆ',
      ml: 'മാനുവൽ ഭാഷ തിരഞ്ഞെടുക്കൽ',
    },
    question: {
      en: 'How do I manually choose the response language?',
      hi: 'मैं उत्तर की भाषा को मैन्युअल रूप से कैसे चुनूं?',
      te: 'సమాధానం యొక్క భాషను మాన్యువల్‌గా ఎలా ఎంచుకోవాలి?',
      ta: 'பதிலின் மொழியை நான் கைமுறையாக எவ்வாறு தேர்ந்தெடுப்பது?',
      kn: 'ಪ್ರತಿಕ್ರಿಯೆಯ ಭಾಷೆಯನ್ನು ಹಸ್ತಚಾಲಿತವಾಗಿ ಹೇಗೆ ಆಯ್ಕೆ ಮಾಡುವುದು?',
      ml: 'മറുപടിയുടെ ഭാഷ ഞാൻ എങ്ങനെ സ്വയം തിരഞ്ഞെടുക്കും?',
    },
    answer: {
      en: 'In the Chat workspace, click any language pill directly above the text box: English (EN), Hindi (HI), Telugu (TE), Tamil (TA), Kannada (KN), or Malayalam (ML). Your manual selection overrides auto-detection and instructs the assistant to answer in that specific language.',
      hi: 'चैट विंडो में, टेक्स्ट बॉक्स के ऊपर भाषा बटन पर क्लिक करें: English (EN), Hindi (HI), Telugu (TE), Tamil (TA), Kannada (KN), या Malayalam (ML)। यह चयन ऑटो-डिटेक्ट को ओवरराइड करता है।',
      te: 'చాట్ విండోలో, టెక్స్ట్ బాక్స్ పైన ఉన్న భాషా బటన్లపై క్లిక్ చేయండి: EN, HI, TE, TA, KN, లేదా ML. ఇది ఆటో-డిటెక్ట్‌ను ఓవర్‌రైడ్ చేస్తుంది.',
      ta: 'அரட்டை பக்கத்தில் உள்ளீடு பெட்டிக்கு மேலே உள்ள மொழி பொத்தான்களைக் கிளிக் செய்யவும்: EN, HI, TE, TA, KN, அல்லது ML.',
      kn: 'ಚಾಟ್ ಪುಟದಲ್ಲಿ ಟೆಕ್ಸ್ಟ್ ಬಾಕ್ಸ್ ಮೇಲಿರುವ ಭಾಷಾ ಬಟನ್‌ಗಳನ್ನು ಕ್ಲಿಕ್ ಮಾಡಿ: EN, HI, TE, TA, KN, ಅಥವಾ ML.',
      ml: 'ടെക്സ്റ്റ് ബോക്സിന് മുകളിലുള്ള ഭാഷാ ബട്ടണുകളിൽ ക്ലിക്ക് ചെയ്യുക: EN, HI, TE, TA, KN, അല്ലെങ്കിൽ ML.',
    },
    keywords: ['manual select', 'override', 'pills', 'buttons', 'selector', 'चयन', 'ఎంపిక', 'தேர்வு', 'ಆಯ್ಕೆ'],
    action: {
      type: 'navigate',
      target: 'chat',
      label: {
        en: 'Open Language Selector',
        hi: 'भाषा चयनकर्ता खोलें',
        te: 'భాషా ఎంపికను తెరవండి',
        ta: 'மொழி தேர்வியைத் திறக்கவும்',
        kn: 'ಭಾಷಾ ಆಯ್ಕೆ ತೆರೆಯಿರಿ',
        ml: 'ഭാഷാ സെലക്ടർ തുറക്കുക',
      },
    },
  },
  {
    id: 'explicit_instructions',
    category: 'languages',
    title: {
      en: 'Natural Language Prompt Instructions',
      hi: 'प्रॉम्प्ट में स्पष्ट भाषा निर्देश',
      te: 'ప్రాంప్ట్‌లో స్పష్టమైన భాషా సూచనలు',
      ta: 'கேள்வியில் வெளிப்படையான மொழி வழிமுறைகள்',
      kn: 'ಪ್ರಾಮ್ಪ್ಟ್‌ನಲ್ಲಿ ಸ್ಪಷ್ಟ ಭಾಷಾ ಸೂಚನೆಗಳು',
      ml: 'പ്രോംപ്റ്റിൽ വ്യക്തമായ ഭാഷാ നിർദ്ദേശങ്ങൾ',
    },
    question: {
      en: 'How do I tell the AI which language to answer in inside my prompt?',
      hi: 'मैं प्रॉम्प्ट के अंदर AI को उत्तर की भाषा कैसे बताऊं?',
      te: 'ప్రాంప్ట్ లోపల సమాధానం ఇవ్వాల్సిన భాషను AIకి ఎలా చెప్పాలి?',
      ta: 'எனது கேள்வியிலேயே AI-க்கு எந்த மொழியில் பதிலளிக்க வேண்டும் என்று சொல்வது எப்படி?',
      kn: 'ಪ್ರಾಮ್ಪ್ಟ್‌ನಲ್ಲಿಯೇ ಯಾವ ಭಾಷೆಯಲ್ಲಿ ಉತ್ತರಿಸಬೇಕೆಂದು AI ಗೆ ಹೇಳುವುದು ಹೇಗೆ?',
      ml: 'പ്രോംപ്റ്റിൽ തന്നെ ഏത് ഭാഷയിൽ മറുപടി നൽകണമെന്ന് AI-യോട് എങ്ങനെ പറയാം?',
    },
    answer: {
      en: 'You can directly include natural language instructions in your question. Examples: "Explain photosynthesis in Telugu", "List solar schemes in English", "Yeh sawal ka jawab Hindi me do", or "దీనికి సమాధానం తెలుగులో ఇవ్వండి". Explicit prompt instructions hold the highest priority (Tier 1) and immediately override manual UI selections.',
      hi: 'आप सीधे अपने प्रश्न में भाषा निर्देश शामिल कर सकते हैं, जैसे: "Explain photosynthesis in Telugu", "Yeh sawal ka jawab Hindi me do" या "దీనికి సమాధానం తెలుగులో ఇవ్వండి"। यह सर्वोच्च प्राथमिकता (Tier 1) रखता है।',
      te: 'మీరు మీ ప్రశ్నలోనే నేరుగా భాషా సూచనను ఇవ్వవచ్చు, ఉదాహరణకు: "Explain photosynthesis in Telugu" లేదా "దీనికి సమాధానం తెలుగులో ఇవ్వండి". ఇది అత్యధిక ప్రాధాన్యతను (Tier 1) కలిగి ఉంటుంది.',
      ta: 'உங்கள் கேள்வியிலேயே நேரடியாக வழிமுறைகளைச் சேர்க்கலாம்: "Explain photosynthesis in Telugu" அல்லது "தமிழில் பதில் சொல்லுங்கள்". இது மிக உயர்ந்த முன்னுரிமையைக் கொண்டுள்ளது (Tier 1).',
      kn: 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಯಲ್ಲಿಯೇ ನೀವು ಭಾಷಾ ಸೂಚನೆಯನ್ನು ನೀಡಬಹುದು: "Explain photosynthesis in Kannada" ಅಥವಾ "ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ". ಇದು ಅತ್ಯುನ್ನತ ಆದ್ಯತೆಯನ್ನು ಹೊಂದಿದೆ (Tier 1).',
      ml: 'നിങ്ങളുടെ ചോദ്യത്തിൽ തന്നെ ഭാഷാ നിർദ്ദേശം നൽകാം: "Explain climate change in Malayalam" അല്ലെങ്കിൽ "മലയാളത്തിൽ മറുപടി തരൂ". ഇതിന് ഏറ്റവും ഉയർന്ന മുൻഗണനയുണ്ട് (Tier 1).',
    },
    keywords: ['explicit', 'instruction', 'in telugu', 'in hindi', 'in english', 'prompt', 'directive', 'निर्देश', 'సూచనలు', 'வழிமுறைகள்'],
  },
  {
    id: 'persistent_preferences',
    category: 'languages',
    title: {
      en: 'Persistent Language Preferences',
      hi: 'स्थायी भाषा प्राथमिकताएं',
      te: 'స్థిరమైన భాషా ప్రాధాన్యతలు',
      ta: 'நிலையான மொழி விருப்பத்தேர்வுகள்',
      kn: 'ಸ್ಥಿರ ಭಾಷಾ ಆದ್ಯತೆಗಳು',
      ml: 'സ്ഥിരമായ ഭാഷ മുൻഗണനകൾ',
    },
    question: {
      en: 'How do I set a language preference for the entire conversation?',
      hi: 'मैं पूरी बातचीत के लिए भाषा प्राथमिकता कैसे सेट करूं?',
      te: 'మొత్తం సంభాషణ కోసం భాషా ప్రాధాన్యతను ఎలా సెట్ చేయాలి?',
      ta: 'முழு உரையாடலுக்கும் ஒரு மொழி விருப்பத்தை எவ்வாறு அமைப்பது?',
      kn: 'ಸಂಪೂರ್ಣ ಸಂಭಾಷಣೆಗೆ ಭಾಷಾ ಆದ್ಯತೆಯನ್ನು ಹೇಗೆ ಹೊಂದಿಸುವುದು?',
      ml: 'മുഴുവൻ സംഭാഷണത്തിനുമായി ഒരു ഭാഷാ മുൻഗണന എങ്ങനെ സജ്ജമാക്കാം?',
    },
    answer: {
      en: 'Use persistent triggers in your message, such as: "From now on, answer in Hindi", "Always respond in Telugu", "Ab se Hindi me batao", or "Ippati nunchi Telugu lo cheppandi". BhashaCore saves this preference in your conversation state and answers all subsequent questions in that language until you say "Switch back to auto-detect".',
      hi: '"From now on, answer in Hindi" या "Ab se Hindi me batao" जैसे वाक्यांशों का उपयोग करें। भाषाकोर इसे सत्र में सहेजता है और जब तक आप "Switch back to auto-detect" नहीं कहते, तब तक उसी भाषा में उत्तर देता है।',
      te: '"From now on, answer in Telugu" లేదా "ఇప్పటి నుంచి తెలుగులో చెప్పు" అని టైప్ చేయండి. మీరు "Switch back to auto-detect" అని చెప్పే వరకు బాట్ అన్ని ప్రశ్నలకు తెలుగులోనే సమాధానమిస్తుంది.',
      ta: '"From now on, answer in Tamil" அல்லது "இனிமேல் தமிழில் பதில் கூறுங்கள்" என்று கூறினால், நீங்கள் "Switch back to auto-detect" என்று மாற்றும் வரை அதே மொழியில் பதிலளிக்கும்.',
      kn: '"From now on, answer in Kannada" ಎಂದು ಟೈಪ್ ಮಾಡಿ. ನೀವು "Switch back to auto-detect" ಎಂದು ಹೇಳುವವರೆಗೆ ಅದೇ ಭಾಷೆಯಲ್ಲಿ ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತದೆ.',
      ml: '"From now on, answer in Malayalam" എന്ന് പറയുക. നിങ്ങൾ "Switch back to auto-detect" എന്ന് മാറ്റുന്നതുവരെ അതേ ഭാഷയിൽ തന്നെ മറുപടി നൽകും.',
    },
    keywords: ['persistent', 'from now on', 'always', 'switch back', 'reset', 'preference', 'स्थायी', 'స్థిరమైన', 'நிலையான', 'ಮುಂದುವರಿಸು'],
  },
  {
    id: 'rag_retrieval',
    category: 'rag_citations',
    title: {
      en: 'What RAG Means & How Retrieval Works',
      hi: 'RAG क्या है और खोज कैसे काम करती है',
      te: 'RAG అంటే ఏమిటి మరియు సమాచారం ఎలా సేకరించబడుతుంది',
      ta: 'RAG என்றால் என்ன & தகவல் எவ்வாறு மீட்டெடுக்கப்படுகிறது',
      kn: 'RAG ಎಂದರೇನು ಮತ್ತು ಮಾಹಿತಿ ಹೇಗೆ ಹುಡುಕಲ್ಪಡುತ್ತದೆ',
      ml: 'RAG എന്നാൽ എന്താണ് & വിവരങ്ങൾ എങ്ങനെ വീണ്ടെടുക്കുന്നു',
    },
    question: {
      en: 'What is RAG and how does BhashaCore retrieve information?',
      hi: 'RAG क्या है और भाषाकोर जानकारी कैसे प्राप्त करता है?',
      te: 'RAG అంటే ఏమిటి మరియు భాషాకోర్ సమాచారాన్ని ఎలా శోధిస్తుంది?',
      ta: 'RAG என்றால் என்ன, பாஷாகோர் தகவல்களை எவ்வாறு மீட்டெடுக்கிறது?',
      kn: 'RAG ಎಂದರೇನು ಮತ್ತು ಭಾಷಾಕೋರ್ ಮಾಹಿತಿಯನ್ನು ಹೇಗೆ ಪಡೆಯುತ್ತದೆ?',
      ml: 'എന്താണ് RAG, ഭാഷാകോർ വിവരങ്ങൾ എങ്ങനെയാണ് വീണ്ടെടുക്കുന്നത്?',
    },
    answer: {
      en: 'RAG (Retrieval-Augmented Generation) combines document search with AI generation. Instead of guessing, BhashaCore first searches thousands of verified civic passages from IndicQA and IndicCorp v2 using script-aware BM25. It passes the top 5 relevant passages to Sarvam 105B with strict instructions to answer only using those verified facts.',
      hi: 'RAG (रिट्रीवल-ऑगमेंटेड जेनरेशन) खोज और AI को जोड़ता है। भाषाकोर पहले IndicQA और IndicCorp v2 के सत्यापित अनुच्छेदों में खोज करता है और फिर शीर्ष 5 संदर्भों के आधार पर Sarvam 105B से सटीक उत्तर तैयार करवाता है।',
      te: 'RAG డాక్యుమెంట్ సెర్చ్ మరియు AI జెనరేషన్‌ను కలుపుతుంది. ఊహించకుండా, భాషాకోర్ మొదట IndicQA మరియు IndicCorp v2 డాక్యుమెంట్లలో శోధించి, సంబంధిత ఆధారాలను Sarvam 105B మోడల్‌కు అందించి ఖచ్చితమైన సమాధానం ఇస్తుంది.',
      ta: 'RAG என்பது ஆவணத் தேடலையும் AI-யையும் இணைக்கும் தொழில்நுட்பம். பாஷாகோர் முதலில் சரிபார்க்கப்பட்ட தகவல்களைத் தேடி, அதன் அடிப்படையில் மட்டுமே Sarvam 105B மூலம் பதிலளிக்கிறது.',
      kn: 'RAG ತಂತ್ರಜ್ಞಾನವು ಡಾಕ್ಯುಮೆಂಟ್ ಹುಡುಕಾಟ ಮತ್ತು AI ಅನ್ನು ಸಂಯೋಜಿಸುತ್ತದೆ. ದೃಢೀಕರಿಸಿದ ದಾಖಲೆಗಳನ್ನು ಆಧರಿಸಿ ಮಾತ್ರ ನಿಖರ ಉತ್ತರ ನೀಡಲಾಗುತ್ತದೆ.',
      ml: 'RAG സാങ്കേതികവിദ്യ രേഖാ തിരച്ചിലും AI ജനറേഷനും സംയോജിപ്പിക്കുന്നു. വിശ്വസനീയമായ രേഖകൾ അടിസ്ഥാനമാക്കി മാത്രമാണ് മറുപടി നൽകുന്നത്.',
    },
    keywords: ['rag', 'retrieval', 'bm25', 'how it works', 'indicqa', 'indiccorp', 'खोज', 'శోధన', 'மீட்டெடுப்பு', 'ಹುಡುಕಾಟ'],
    action: {
      type: 'navigate',
      target: 'about',
      label: {
        en: 'Read Research Methodology',
        hi: 'अनुसंधान पद्धति पढ़ें',
        te: 'పరిశోధన పద్ధతిని చదవండి',
        ta: 'ஆராய்ச்சி முறையைப் படிக்கவும்',
        kn: 'ಸಂಶೋಧನಾ ವಿಧಾನವನ್ನು ಓದಿ',
        ml: 'ഗവേഷണ രീതി വായിക്കുക',
      },
    },
  },
  {
    id: 'citations_evidence',
    category: 'rag_citations',
    title: {
      en: 'Viewing Citations & Source Evidence',
      hi: 'उद्धरण और स्रोत साक्ष्य देखना',
      te: 'ఆధారాలు మరియు మూల సూచనలను చూడటం',
      ta: 'மேற்கோள்கள் மற்றும் மூல ஆதாரங்களைக் காண்பது',
      kn: 'ಮೂಲ ಉಲ್ಲೇಖಗಳು ಮತ್ತು ಪುರಾವೆಗಳನ್ನು ವೀಕ್ಷಿಸುವುದು',
      ml: 'അവലംബങ്ങളും ഉറവിട തെളിവുകളും കാണുന്നത്',
    },
    question: {
      en: 'How do I see where the answer came from and check citations?',
      hi: 'मुझे कैसे पता चलेगा कि उत्तर कहाँ से आया और मैं उद्धरण कैसे देखूँ?',
      te: 'సమాధానం ఎక్కడి నుండి వచ్చిందో ఎలా తెలుసుకోవాలి మరియు సైటేషన్లను ఎలా చూడాలి?',
      ta: 'பதில் எங்கிருந்து வந்தது என்பதை எவ்வாறு அறிந்து கொள்வது?',
      kn: 'ಉತ್ತರ ಎಲ್ಲಿಂದ ಬಂದಿದೆ ಎಂದು ತಿಳಿಯುವುದು ಮತ್ತು ಉಲ್ಲೇಖಗಳನ್ನು ನೋಡುವುದು ಹೇಗೆ?',
      ml: 'ഉത്തരം എവിടെ നിന്നാണ് വന്നതെന്നും അവലംബങ്ങൾ എങ്ങനെ കാണാമെന്നും അറിയുന്നത് എങ്ങനെ?',
    },
    answer: {
      en: 'Every grounded response includes interactive citation pills directly underneath the message. Click on any pill (e.g. "[1] Source Name") to expand the drawer showing the exact text passage, document title, and lexical support score (percentage of answer supported by that text).',
      hi: 'प्रत्येक उत्तर के नीचे इंटरैक्टिव उद्धरण बटन होते हैं। सटीक अनुच्छेद, दस्तावेज़ शीर्षक और समर्थन स्कोर देखने के लिए किसी भी बटन (जैसे "[1] स्रोत") पर क्लिक करें।',
      te: 'ప్రతి సమాధానం క్రింద మూల ఆధారాల బటన్లు ఉంటాయి. సంబంధిత సమాచార శకలం, డాక్యుమెంట్ శీర్షిక మరియు సపోర్ట్ స్కోర్ చూడటానికి ఏదైనా బటన్ (ఉదా. "[1] మూలం") పై క్లిక్ చేయండి.',
      ta: 'ஒவ்வொரு பதிலின் கீழும் மேற்கோள் பொத்தான்கள் உள்ளன. மூல உரை மற்றும் ஆதரவு மதிப்பெண்ணைக் காண ஏதேனும் பொத்தானைக் கிளிக் செய்யவும்.',
      kn: 'ಪ್ರತಿಯೊಂದು ಉತ್ತರದ ಕೆಳಗೆ ಉಲ್ಲೇಖ ಬಟನ್‌ಗಳಿರುತ್ತವೆ. ಮೂಲ ಮಾಹಿತಿ ಮತ್ತು ಡಾಕ್ಯುಮೆಂಟ್ ನೋಡಲು ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.',
      ml: 'ഓരോ മറുപടിയുടെയും താഴെ അവലംബ ബട്ടണുകൾ ഉണ്ട്. ഉറവിട രേഖ കാണാൻ ആ ബട്ടണുകളിൽ ക്ലിക്ക് ചെയ്യുക.',
    },
    keywords: ['citations', 'sources', 'evidence', 'proof', 'support score', 'drawer', 'उद्धरण', 'ఆధారాలు', 'மேற்கோள்கள்', 'ಉಲ್ಲೇಖಗಳು'],
    action: {
      type: 'navigate',
      target: 'chat',
      label: {
        en: 'See Citations in Chat',
        hi: 'चैट में उद्धरण देखें',
        te: 'చాట్‌లో ఆధారాలు చూడండి',
        ta: 'அரட்டையில் மேற்கோள்களைப் பார்க்கவும்',
        kn: 'ಚಾಟ್‌ನಲ್ಲಿ ಉಲ್ಲೇಖಗಳನ್ನು ನೋಡಿ',
        ml: 'ചാറ്റിൽ അവലംബങ്ങൾ കാണുക',
      },
    },
  },
  {
    id: 'guest_trial',
    category: 'trial_accounts',
    title: {
      en: 'Guest Access & 3-Message Trial',
      hi: 'अतिथि पहुंच और 3-संदेश परीक्षण',
      te: 'గెస్ట్ యాక్సెస్ మరియు 3-సందేశాల ట్రయల్',
      ta: 'விருந்தினர் அணுகல் மற்றும் 3-செய்தி சோதனை',
      kn: 'ಅತಿಥಿ ಪ್ರವೇಶ ಮತ್ತು 3-ಸಂದೇಶ ಪ್ರಯೋಗ',
      ml: 'ഗസ്റ്റ് ആക്‌സസും 3-സന്ദേശ ട്രയലും',
    },
    question: {
      en: 'How does the free guest trial work?',
      hi: 'मुफ़्त अतिथि परीक्षण कैसे काम करता है?',
      te: 'ఉచిత గెస్ట్ ట్రయల్ ఎలా పనిచేస్తుంది?',
      ta: 'இலவச விருந்தினர் சோதனை எவ்வாறு செயல்படுகிறது?',
      kn: 'ಉಚಿತ ಅತಿಥಿ ಪ್ರಯೋಗ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ?',
      ml: 'സൗജന്യ ഗസ്റ്റ് ട്രയൽ എങ്ങനെ പ്രവർത്തിക്കുന്നു?',
    },
    answer: {
      en: 'First-time visitors can ask 3 free questions without signing up. The quota (e.g. 1/3, 2/3, 3/3) is strictly tracked on our backend database with row-level locks, so refreshing the page or switching tabs never resets it. Failed or stopped requests never consume your quota. Once you reach 3/3, simply sign in for unlimited access.',
      hi: 'नए उपयोगकर्ता बिना साइन इन किए 3 मुफ़्त प्रश्न पूछ सकते हैं। यह कोटा (1/3, 2/3, 3/3) सर्वर डेटाबेस द्वारा सुरक्षित रूप से ट्रैक किया जाता है। विफल अनुरोध कोटा नहीं घटाते। 3/3 के बाद, असीमित पहुंच के लिए साइन इन करें।',
      te: 'కొత్త సందర్శకులు సైన్ ఇన్ చేయకుండానే 3 ఉచిత ప్రశ్నలను అడగవచ్చు. ఈ కోటా (1/3, 2/3, 3/3) సర్వర్‌లో సురక్షితంగా లెక్కించబడుతుంది. విఫలమైన ప్రశ్నలకు కోటా తగ్గదు. 3/3 ముగిసిన తర్వాత ఉచితంగా సైన్ ఇన్ చేయండి.',
      ta: 'புதிய பயனர்கள் பதிவு செய்யாமல் 3 இலவசக் கேள்விகளைக் கேட்கலாம். 3/3 முடிந்ததும், வரம்பற்ற பயன்பாட்டிற்கு உள்நுழையவும்.',
      kn: 'ಹೊಸ ಬಳಕೆದಾರರು ಸೈನ್ ಇನ್ ಮಾಡದೆಯೇ 3 ಉಚಿತ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಹುದು. 3/3 ನಂತರ ಅನ್‌ಲಿಮಿಟೆಡ್ ಚಾಟ್‌ಗಾಗಿ ಸೈನ್ ಇನ್ ಮಾಡಿ.',
      ml: 'പുതിയ ഉപയോക്താക്കൾക്ക് ലോഗിൻ ചെയ്യാതെ 3 സൗജന്യ ചോദ്യങ്ങൾ ചോദിക്കാം. 3/3 കഴിഞ്ഞാൽ അൺലിമിറ്റഡ് ആക്‌സസിനായി സൈൻ ഇൻ ചെയ്യുക.',
    },
    keywords: ['guest', 'trial', '3 messages', 'quota', 'free trial', 'limit', 'परीक्षण', 'ట్రయల్', 'சோதனை', 'ಪ್ರಯೋಗ', 'ട്രയൽ'],
    action: {
      type: 'open_auth',
      target: 'auth',
      label: {
        en: 'Sign In / Register',
        hi: 'साइन इन / रजिस्टर करें',
        te: 'సైన్ ఇన్ / రిజిస్టర్ చేసుకోండి',
        ta: 'உள்நுழைக / பதிவு செய்க',
        kn: 'ಸೈನ್ ಇನ್ / ನೋಂದಾಯಿಸಿ',
        ml: 'സൈൻ ഇൻ / രജിസ്റ്റർ ചെയ്യുക',
      },
    },
  },
  {
    id: 'signin_history',
    category: 'trial_accounts',
    title: {
      en: 'User Accounts & Persistent History',
      hi: 'उपयोगकर्ता खाते और स्थायी इतिहास',
      te: 'వినియోగదారు ఖాతాలు మరియు హిస్టరీ',
      ta: 'பயனர் கணக்குகள் & வரலாற்று சேமிப்பு',
      kn: 'ಬಳಕೆದಾರರ ಖಾತೆಗಳು ಮತ್ತು ಇತಿಹಾಸ',
      ml: 'ഉപയോക്തൃ അക്കൗണ്ടുകളും ഹിസ്റ്ററിയും',
    },
    question: {
      en: 'How do I save my chat history and get unlimited messages?',
      hi: 'मैं अपनी चैट हिस्ट्री कैसे सहेजूं और असीमित संदेश कैसे प्राप्त करूं?',
      te: 'నా చాట్ హిస్టరీని ఎలా సేవ్ చేసుకోవాలి మరియు అపరిమిత సందేశాలను ఎలా పొందాలి?',
      ta: 'எனது அரட்டை வரலாற்றைச் சேமிப்பது மற்றும் வரம்பற்ற செய்திகளைப் பெறுவது எப்படி?',
      kn: 'ನನ್ನ ಚಾಟ್ ಇತಿಹಾಸವನ್ನು ಉಳಿಸುವುದು ಮತ್ತು ಅನಿಯಮಿತ ಸಂದೇಶಗಳನ್ನು ಪಡೆಯುವುದು ಹೇಗೆ?',
      ml: 'എന്റെ ചാറ്റ് ഹിസ്റ്ററി എങ്ങനെ സംരക്ഷിക്കാം?',
    },
    answer: {
      en: 'Click "Sign In" in the top navigation bar or sidebar to create a free account or log in. Authenticated users enjoy unlimited AI chat completions, secure password hashing, and permanent cloud-synced conversation history across all devices with search and delete capabilities.',
      hi: 'मुफ़्त खाता बनाने के लिए शीर्ष नेविगेशन बार में "Sign In" पर क्लिक करें। प्रमाणित उपयोगकर्ताओं को असीमित चैट, स्थायी क्लाउड इतिहास और पूर्ण सुरक्षा मिलती है।',
      te: 'ఉచిత ఖాతాను సృష్టించడానికి పైభాగంలో ఉన్న "Sign In" పై క్లిక్ చేయండి. లాగిన్ అయిన వినియోగదారులకు అపరిమిత చాట్ మరియు శాశ్వత క్లౌడ్ హిస్టరీ లభిస్తుంది.',
      ta: 'இலவச கணக்கை உருவாக்க மேலே உள்ள "Sign In" என்பதைக் கிளிக் செய்யவும். உள்நுழைந்த பயனர்களுக்கு வரம்பற்ற உரையாடல்கள் மற்றும் வரலாற்றுச் சேமிப்பு கிடைக்கும்.',
      kn: 'ಉಚಿತ ಖಾತೆಯನ್ನು ರಚಿಸಲು "Sign In" ಕ್ಲಿಕ್ ಮಾಡಿ. ಲಾಗಿನ್ ಆದ ಬಳಕೆದಾರರಿಗೆ ಅನಿಯಮಿತ ಚಾಟ್ ಸೌಲಭ್ಯ ದೊರೆಯುತ್ತದೆ.',
      ml: 'സൗജന്യ അക്കൗണ്ട് സൃഷ്ടിക്കാൻ "Sign In" ക്ലിക്ക് ചെയ്യുക. ലോഗിൻ ചെയ്ത ഉപയോക്താക്കൾക്ക് അൺലിമിറ്റഡ് ചാറ്റ് ലഭ്യമാണ്.',
    },
    keywords: ['sign in', 'login', 'signup', 'register', 'history', 'save conversations', 'account', 'खाता', 'ఖాతా', 'கணக்கு', 'ಖಾತೆ', 'അക്കൗണ്ട്'],
    action: {
      type: 'open_auth',
      target: 'auth',
      label: {
        en: 'Sign In Now',
        hi: 'अभी साइन इन करें',
        te: 'ఇప్పుడే సైన్ ఇన్ చేయండి',
        ta: 'இப்போது உள்நுழைக',
        kn: 'ಈಗಲೇ ಸೈನ್ ಇನ್ ಮಾಡಿ',
        ml: 'ഇപ്പോൾ സൈൻ ഇൻ ചെയ്യുക',
      },
    },
  },
  {
    id: 'research_dashboard',
    category: 'research',
    title: {
      en: 'Using the Research Dashboard',
      hi: 'अनुसंधान डैशबोर्ड का उपयोग',
      te: 'రీసెర్చ్ డ్యాష్‌బోర్డ్ వినియోగం',
      ta: 'ஆராய்ச்சி டாஷ்போர்டைப் பயன்படுத்துதல்',
      kn: 'ಸಂಶೋಧನಾ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಬಳಕೆ',
      ml: 'ഗവേഷണ ഡാഷ്‌ബോർഡ് ഉപയോഗിക്കുന്നത്',
    },
    question: {
      en: 'What can I explore in the Research section?',
      hi: 'मैं अनुसंधान अनुभाग में क्या देख सकता हूँ?',
      te: 'రీసెర్చ్ విభాగంలో నేను ఏమి పరిశీలించగలను?',
      ta: 'ஆராய்ச்சி பிரிவில் நான் எதை ஆராயலாம்?',
      kn: 'ಸಂಶೋಧನಾ ವಿಭಾಗದಲ್ಲಿ ನಾನು ಏನನ್ನು ಅನ್ವೇಷಿಸಬಹುದು?',
      ml: 'ഗവേഷണ വിഭാഗത്തിൽ എനിക്ക് എന്തൊക്കെ കണ്ടെത്താനാകും?',
    },
    answer: {
      en: 'Click "Research" in the top navigation to access our scientific evaluation suite: 1) Dashboard: Overall evaluation counts and accuracy scores. 2) Language Comparison: The cross-language quality waterfall decomposing retrieval and comprehension gaps. 3) Failure Analysis: Breakdown of 530+ empirical failure cases into retrieval misses, refusals, and hallucinations.',
      hi: 'शीर्ष मेनू में "Research" पर क्लिक करें: 1) Dashboard: समग्र सटीकता मेट्रिक्स। 2) Language Comparison: भाषाओं के बीच तुलनात्मक विश्लेषण। 3) Failure Analysis: 530 से अधिक विफलता मामलों का श्रेणीवार वर्गीकरण।',
      te: 'పై మెనూలో "Research" పై క్లిక్ చేయండి: 1) Dashboard: మొత్తం ఖచ్చితత్వ గణాంకాలు. 2) Language Comparison: భాషల మధ్య నాణ్యతా విశ్లేషణ. 3) Failure Analysis: 530కి పైగా వైఫల్య కేసుల వర్గీకరణ.',
      ta: 'மேல் மெனுவில் "Research" என்பதைக் கிளிக் செய்யவும்: 1) Dashboard: ஒட்டுமொத்த மதிப்பீடுகள். 2) Language Comparison: மொழி ஒப்பீடு. 3) Failure Analysis: 530+ தோல்வி பகுப்பாய்வு.',
      kn: 'ಮೇಲಿನ ಮೆನುವಿನಲ್ಲಿ "Research" ಕ್ಲಿಕ್ ಮಾಡಿ: 1) Dashboard: ಒಟ್ಟಾರೆ ನಿಖರತೆ. 2) Language Comparison: ಭಾಷಾ ಹೋಲಿಕೆ. 3) Failure Analysis: ವೈಫಲ್ಯಗಳ ವಿಶ್ಲೇಷಣೆ.',
      ml: 'മുകളിലെ മെനുവിൽ "Research" ക്ലിക്ക് ചെയ്യുക: 1) Dashboard: കൃത്യത കണക്കുകൾ. 2) Language Comparison: ഭാഷാ താരതമ്യം. 3) Failure Analysis: പരാജയ വിശകലനം.',
    },
    keywords: ['research', 'dashboard', 'comparison', 'failures', 'benchmark', 'waterfall', 'metrics', 'अनुसंधान', 'పరిశోధన', 'ஆராய்ச்சி', 'ಸಂಶೋಧನೆ', 'ഗവേഷണം'],
    action: {
      type: 'navigate',
      target: 'dashboard',
      label: {
        en: 'Open Research Hub',
        hi: 'अनुसंधान केंद्र खोलें',
        te: 'రీసెర్చ్ హబ్ తెరవండి',
        ta: 'ஆராய்ச்சி மையத்தைத் திறக்கவும்',
        kn: 'ಸಂಶೋಧನಾ ಹಬ್ ತೆರೆಯಿರಿ',
        ml: 'ഗവേഷണ ഹബ് തുറക്കുക',
      },
    },
  },
  {
    id: 'capabilities_limitations',
    category: 'limitations',
    title: {
      en: 'Capabilities & Known Limitations',
      hi: 'क्षमताएं और ज्ञात सीमाएं',
      te: 'సామర్థ్యాలు మరియు తెలిసిన పరిమితులు',
      ta: 'திறன்கள் மற்றும் அறியப்பட்ட வரம்புகள்',
      kn: 'ಸಾಮರ್ಥ್ಯಗಳು ಮತ್ತು ತಿಳಿದಿರುವ ಮಿತಿಗಳು',
      ml: 'ശേഷികളും പരിമിതികളും',
    },
    question: {
      en: 'What can BhashaCore do, and what are its limitations?',
      hi: 'भाषाकोर क्या कर सकता है, और इसकी सीमाएं क्या हैं?',
      te: 'భాషాకోర్ ఏమి చేయగలదు మరియు దాని పరిమితులు ఏమిటి?',
      ta: 'பாஷாகோரால் என்ன செய்ய முடியும், அதன் வரம்புகள் யாவை?',
      kn: 'ಭಾಷಾಕೋರ್ ಏನು ಮಾಡಬಲ್ಲದು ಮತ್ತು ಅದರ ಮಿತಿಗಳೇನು?',
      ml: 'ഭാഷാകോറിന് എന്തൊക്കെ ചെയ്യാനാകും, എന്തൊക്കെയാണ് പരിമിതികൾ?',
    },
    answer: {
      en: 'BhashaCore excels at answering factual questions grounded in verified civic and Indian-language knowledge with strict citation provenance. Known limitations: 1) BM25 keyword retrieval experiences drops on agglutinative Dravidian languages (Tamil/Kannada). 2) Highly informal SMS slang can occasionally evade transliteration. 3) Offline knowledge is currently focused on IndicQA/IndicCorp datasets.',
      hi: 'भाषाकोर सत्यापित संदर्भों और उद्धरणों के साथ सटीक उत्तर देने में उत्कृष्ट है। ज्ञात सीमाएं: तमिल/कन्नड़ में संधि-प्रत्यय के कारण कीवर्ड मिलान कभी-कभी छूट सकता है, और अत्यधिक अनौपचारिक स्लैंग कभी-कभी समझ से बाहर हो सकता है।',
      te: 'భాషాకోర్ అధికారిక పత్రాల ఆధారంగా నిరూపితమైన సమాధానాలను ఇవ్వడంలో ఉత్తమమైనది. పరిమితులు: తమిళం/కన్నడ వంటి ద్రావిడ భాషల్లో ప్రత్యయాల వల్ల కీవర్డ్ శోధనలో కొన్నిసార్లు తగ్గుదల ఉండవచ్చు.',
      ta: 'பாஷாகோர் சரிபார்க்கப்பட்ட ஆதாரங்களுடன் பதிலளிப்பதில் சிறந்தது. திராவிட மொழிகளில் வேர்ச்சொல் மாற்றங்களால் சில நேரங்களில் தேடல் விடுபடலாம்.',
      kn: 'ಭಾಷಾಕೋರ್ ದೃಢೀಕರಿಸಿದ ದಾಖಲೆಗಳೊಂದಿಗೆ ಉತ್ತರಿಸಲು ಸಮರ್ಥವಾಗಿದೆ. ವ್ಯಾಕರಣ ಸಂಯೋಜನೆಗಳ ಕಾರಣದಿಂದ ಕೆಲವು ಕೀವರ್ಡ್ ಹುಡುಕಾಟ ಮಿತಿಗಳಿವೆ.',
      ml: 'വിശ്വസനീയമായ രേഖകളോടെ ഉത്തരം നൽകാൻ ഭാഷാകോർ മികച്ചതാണ്. ചില ഭാഷാപരമായ തിരച്ചിൽ പരിമിതികൾ നിലവിലുണ്ട്.',
    },
    keywords: ['limitations', 'capabilities', 'what it does', 'accuracy', 'boundaries', 'कमियां', 'పరిమితులు', 'வரம்புகள்', 'ಮಿತಿಗಳು', 'പരിമിതികൾ'],
    action: {
      type: 'navigate',
      target: 'about',
      label: {
        en: 'Learn More in About',
        hi: 'About पेज में और जानें',
        te: 'About పేజీలో మరింత తెలుసుకోండి',
        ta: 'About பக்கத்தில் மேலும் அறிக',
        kn: 'About ಪುಟದಲ್ಲಿ ಇನ್ನಷ್ಟು ತಿಳಿಯಿರಿ',
        ml: 'About പേജിൽ കൂടുതൽ അറിയുക',
      },
    },
  },
];

export const GUIDE_CATEGORIES: { id: GuideCategory; label: Record<LanguageCode, string> }[] = [
  {
    id: 'getting_started',
    label: {
      en: 'Getting Started',
      hi: 'शुरुआत करें',
      te: 'ప్రారంభం',
      ta: 'தொடங்குதல்',
      kn: 'ಪ್ರಾರಂಭಿಸಿ',
      ml: 'ആരംഭിക്കുക',
    },
  },
  {
    id: 'languages',
    label: {
      en: 'Languages & Prompts',
      hi: 'भाषाएं और प्रॉम्प्ट',
      te: 'భాషలు & ప్రాంప్ట్‌లు',
      ta: 'மொழிகள் & கட்டளைகள்',
      kn: 'ಭಾಷೆಗಳು & ಪ್ರಾಮ್ಪ್ಟ್‌ಗಳು',
      ml: 'ഭാഷകളും പ്രോംപ്റ്റുകളും',
    },
  },
  {
    id: 'rag_citations',
    label: {
      en: 'RAG & Citations',
      hi: 'RAG और उद्धरण',
      te: 'RAG & ఆధారాలు',
      ta: 'RAG & மேற்கோள்கள்',
      kn: 'RAG & ಉಲ್ಲೇಖಗಳು',
      ml: 'RAG & അവലംബങ്ങൾ',
    },
  },
  {
    id: 'trial_accounts',
    label: {
      en: 'Guest Trial & Accounts',
      hi: 'परीक्षण और खाते',
      te: 'ట్రయల్ & ఖాతాలు',
      ta: 'சோதனை & கணக்குகள்',
      kn: 'ಪ್ರಯೋಗ & ಖಾತೆಗಳು',
      ml: 'ട്രയലും അക്കൗണ്ടുകളും',
    },
  },
  {
    id: 'research',
    label: {
      en: 'Research Hub',
      hi: 'अनुसंधान केंद्र',
      te: 'రీసెర్చ్ హబ్',
      ta: 'ஆராய்ச்சி மையம்',
      kn: 'ಸಂಶೋಧನಾ ಕೇಂದ್ರ',
      ml: 'ഗവേഷണ ഹബ്',
    },
  },
  {
    id: 'limitations',
    label: {
      en: 'Capabilities & Limits',
      hi: 'क्षमताएं और सीमाएं',
      te: 'సామర్థ్యాలు & పరిమితులు',
      ta: 'திறன்கள் & வரம்புகள்',
      kn: 'ಸಾಮರ್ಥ್ಯ & ಮಿತಿಗಳು',
      ml: 'ശേഷികളും പരിമിതികളും',
    },
  },
];

/**
 * Intelligent deterministic search and intent matching for Guide queries.
 */
export function findGuideAnswer(
  query: string,
  currentLang: LanguageCode
): { topic: GuideTopic | null; replyText: string; action?: GuideTopic['action'] } {
  const cleaned = query.trim().toLowerCase();
  if (!cleaned) {
    return {
      topic: null,
      replyText: getLocalizedGreeting(currentLang),
    };
  }

  // Detect if query explicitly asks for a language (e.g. "in hindi", "telugu lo")
  let targetLang = currentLang;
  if (/hindi|हिंदी|हिन्दी|me do|mein/i.test(cleaned)) targetLang = 'hi';
  else if (/telugu|తెలుగు|lo cheppu|ivvandi/i.test(cleaned)) targetLang = 'te';
  else if (/tamil|தமிழ்|la sollu|sollunga/i.test(cleaned)) targetLang = 'ta';
  else if (/kannada|ಕನ್ನಡ|alli heli/i.test(cleaned)) targetLang = 'kn';
  else if (/malayalam|മലയാളം|thil parayu/i.test(cleaned)) targetLang = 'ml';
  else if (/english|aangilam|angrezi/i.test(cleaned)) targetLang = 'en';

  const tokens = cleaned.split(/\s+/);
  let bestTopic: GuideTopic | null = null;
  let highestScore = 0;

  for (const topic of GUIDE_TOPICS) {
    let score = 0;
    // Check keyword matches
    for (const kw of topic.keywords) {
      if (cleaned.includes(kw.toLowerCase())) {
        score += 3;
      }
      for (const tok of tokens) {
        if (tok.length >= 3 && kw.toLowerCase().includes(tok)) {
          score += 1;
        }
      }
    }
    // Check title/question overlap
    const localizedTitle = (topic.title[targetLang] || topic.title.en).toLowerCase();
    const localizedQ = (topic.question[targetLang] || topic.question.en).toLowerCase();
    for (const tok of tokens) {
      if (tok.length >= 3) {
        if (localizedTitle.includes(tok)) score += 2;
        if (localizedQ.includes(tok)) score += 2;
      }
    }

    if (score > highestScore) {
      highestScore = score;
      bestTopic = topic;
    }
  }

  if (bestTopic && highestScore >= 2) {
    return {
      topic: bestTopic,
      replyText: bestTopic.answer[targetLang] || bestTopic.answer.en,
      action: bestTopic.action,
    };
  }

  // Fallback helpful guidance
  const fallbackReplies: Record<LanguageCode, string> = {
    en: "I'm BhashaCore Guide! I can help you with starting chats, asking in six Indian languages, language selection, RAG citations, guest trial limits, signing in, and exploring our Research Dashboard. Please select a topic below or ask a specific question!",
    hi: "मैं भाषाकोर गाइड हूँ! मैं नई चैट शुरू करने, छह भाषाओं में प्रश्न पूछने, भाषा चयन, RAG उद्धरण, अतिथि परीक्षण और अनुसंधान डैशबोर्ड में आपकी सहायता कर सकता हूँ। कृपया नीचे दिए गए विषयों में से चुनें!",
    te: "నేను భాషాకోర్ గైడ్‌ని! కొత్త చాట్ ప్రారంభించడం, ఆరు భాషల్లో అడగడం, భాషా ఎంపిక, RAG ఆధారాలు, గెస్ట్ ట్రయల్ మరియు రీసెర్చ్ డ్యాష్‌బోర్డ్ గురించి నేను మీకు వివరించగలను. దయచేసి క్రింది అంశాలలో ఒకదాన్ని ఎంచుకోండి!",
    ta: "நான் பாஷாகோர் வழிகாட்டி! புதிய உரையாடல், ஆறு மொழிகள், மொழி தேர்வு, RAG மேற்கோள்கள், விருந்தினர் சோதனை மற்றும் ஆராய்ச்சி மையம் குறித்து உங்களுக்கு உதவ முடியும். கீழே உள்ள தலைப்புகளில் ஒன்றைத் தேர்ந்தெடுக்கவும்!",
    kn: "ನಾನು ಭಾಷಾಕೋರ್ ಗೈಡ್! ಹೊಸ ಚಾಟ್, ಆರು ಭಾಷೆಗಳು, RAG ಉಲ್ಲೇಖಗಳು, ಅತಿಥಿ ಪ್ರಯೋಗ ಮತ್ತು ಸಂಶೋಧನಾ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಬಗ್ಗೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ಕೆಳಗಿನ ವಿಷಯಗಳಲ್ಲಿ ಒಂದನ್ನು ಆಯ್ಕೆಮಾಡಿ!",
    ml: "ഞാൻ ഭാഷാകോർ ഗൈഡ് ആണ്! പുതിയ ചാറ്റ്, ആറ് ഭാഷകൾ, RAG അവലംബങ്ങൾ, ഗസ്റ്റ് ട്രയൽ, റിസർച്ച് ഡാഷ്‌ബോർഡ് എന്നിവയിൽ സഹായിക്കാൻ ഞാൻ തയ്യാറാണ്. താഴെ നൽകിയിരിക്കുന്ന വിഷയങ്ങളിൽ ഒന്ന് തിരഞ്ഞെടുക്കുക!",
  };

  return {
    topic: null,
    replyText: fallbackReplies[targetLang] || fallbackReplies.en,
  };
}

export function getLocalizedGreeting(lang: LanguageCode): string {
  const greetings: Record<LanguageCode, string> = {
    en: "👋 Hi! I'm your BhashaCore Application Guide. How can I help you navigate and explore BhashaCore today?",
    hi: "👋 नमस्ते! मैं आपका भाषाकोर एप्लीकेशन गाइड हूँ। आज भाषाकोर को समझने में मैं आपकी क्या मदद कर सकता हूँ?",
    te: "👋 నమస్కారం! నేను మీ భాషాకోర్ అప్లికేషన్ గైడ్‌ని. భాషాకోర్‌ను అన్వేషించడంలో నేను మీకు ఎలా సహాయపడగలను?",
    ta: "👋 வணக்கம்! நான் உங்கள் பாஷாகோர் வழிகாட்டி. பாஷாகோரைப் பயன்படுத்த நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
    kn: "👋 ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಭಾಷಾಕೋರ್ ಅಪ್ಲಿಕೇಶನ್ ಗೈಡ್. ಭಾಷಾಕೋರ್ ಅನ್ನು ಅನ್ವೇಷಿಸಲು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
    ml: "👋 നമസ്കാരം! ഞാൻ നിങ്ങളുടെ ഭാഷാകോർ ആപ്ലിക്കേഷൻ ഗൈഡ് ആണ്. ഭാഷാകോർ ഉപയോഗിക്കാൻ ഞാൻ എങ്ങനെ സഹായിക്കണം?",
  };
  return greetings[lang] || greetings.en;
}
