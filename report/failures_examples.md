# Failure examples (auto-selected raw material)


## HI (Hindi)

### [gold_context comprehension] `491`
- **Question:** चंडीगढ़ शहर से नई दिल्ली की दुरी कितनी है ?
- **Gloss (Q):** How far is Chandigarh city from New Delhi?
- **Gold answer:** 229 meters | original: 229 मी
- **Bot answer:** चंडीगढ़ नई दिल्ली से लगभग 260 किलोमीटर (162 मील) उत्तर में स्थित है।
- **Gloss (A):** Chandigarh is located about 260 kilometers (162 miles) north of New Delhi.
- **Flags:** wrong_answer | correctness=1.0 purity=1.0

### [gold_context comprehension] `1506`
- **Question:** हैदराबाद किस उद्योग के लिए प्रमुख रूप से जाना जाता है?
- **Gloss (Q):** For which industry is Hyderabad primarily known?
- **Gold answer:** Pharmaceutical industry | original: औषधीय उद्योग
- **Bot answer:** हैदराबाद सेवा उद्योग के लिए प्रमुख रूप से जाना जाता है, जो इसके आर्थिक विकास का मुख्य अंशदाता है; यह औषधीय उद्योग का भी एक प्रमुख केंद्र है।
- **Gloss (A):** Hyderabad is primarily known for the service industry, which is the main contributor to its economic development; it is also a major centre of the pharmaceutical industry.
- **Flags:** wrong_answer | correctness=3.0 purity=1.0

### [RAG failed despite successful retrieval] `1506`
- **Question:** हैदराबाद किस उद्योग के लिए प्रमुख रूप से जाना जाता है?
- **Gloss (Q):** For which industry is Hyderabad primarily known?
- **Gold answer:** Pharmaceutical industry | original: औषधीय उद्योग
- **Bot answer:** हैदराबाद सूचना
- **Gloss (A):** Hyderabad information
- **Flags:** unfaithful_to_context, wrong_answer, incomplete | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `491`
- **Question:** चंडीगढ़ शहर से नई दिल्ली की दुरी कितनी है ?
- **Gloss (Q):** How far is Chandigarh city from New Delhi?
- **Gold answer:** 229 meters | original: 229 मी
- **Bot answer:** चंडीगढ़ नई दिल्ली से लगभग 260 किलोमीटर (162 मील) उत्तर में स्थित है।
- **Gloss (A):** Chandigarh is located approximately 260 kilometers (162 miles) north of New Delhi.
- **Flags:** wrong_answer | correctness=1.0 purity=1.0


## TA (Tamil)

### [gold_context comprehension] `1378`
- **Question:** சப்பாத்தி எதனால் ஆனது?
- **Gloss (Q):** What is chapati made of?
- **Gold answer:** with | original: கொண்டு
- **Bot answer:** கொடுக்கப்பட்ட தகவல்களில் சப்பாத்தி எதனால் ஆனது என்பது குறிப்பிடப்படவில்லை; எனவே அதைத் தெரிவிக்க முடியாது.
- **Gloss (A):** Chapati what is made of is not mentioned in the given information; therefore it cannot be stated.
- **Flags:** refusal | correctness=0.0 purity=1.0

### [gold_context comprehension] `1123`
- **Question:** டோப்பை அடைக்கலம் கொடுத்தது யார்?
- **Gloss (Q):** Who gave shelter to Topé?
- **Gold answer:** Queen of Jhansi | original: ஜான்சியின் ராணி
- **Bot answer:** வழங்கப்பட்ட தகவலில், டோப்பை அடைக்கலம் கொடுத்தவர் யார் என்பது குறிப்பிடப்படவில்லை.
- **Gloss (A):** In the provided information, who gave shelter to Top is not mentioned.
- **Flags:** unfaithful_to_context, refusal, wrong_answer | correctness=0.0 purity=1.0

### [gold_context comprehension] `170`
- **Question:** மும்பையின் மக்கள் தொகை அடர்த்தி என்ன?
- **Gloss (Q):** What is the population density of Mumbai?
- **Gold answer:** 11,914,398 | original: 11,914,398
- **Bot answer:** மும்பையின் மக்கள்தொகை அடர்த்தி ஒரு சதுர கிலோமீட்டருக்கு சுமார் 22,000 பேராகும்.
- **Gloss (A):** The population density of Mumbai is about 22,000 people per square kilometer.
- **Flags:** wrong_answer | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `170`
- **Question:** மும்பையின் மக்கள் தொகை அடர்த்தி என்ன?
- **Gloss (Q):** What is the population density of Mumbai?
- **Gold answer:** 11,914,398 | original: 11,914,398
- **Bot answer:** மும்பையின் மக்கள்தொகை அடர்த்தி ஒரு சதுர கிலோமீட்டருக்கு சுமார் **22,000 பேர்** ஆகும்.
- **Gloss (A):** The population density of Mumbai is about 22,000 people per square kilometer.
- **Flags:** wrong_answer | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `1288`
- **Question:** வெறுமை கொள்கையை ஏற்றுக்கொண்டவர் யார்?
- **Gloss (Q):** Who accepted the doctrine of emptiness?
- **Gold answer:** Nagarjuna | original: நாகார்ஜூனா
- **Bot answer:** வெறுமை நிலைக் கொள்கையை ஏற்றுக்கொண்டவர் நாகார்ஜூனாவின் படைப்பான **சூன்யதா** ஆகும்.
- **Gloss (A):** The one who accepted the emptiness state doctrine is Nagarjuna's work Sunyata.
- **Flags:** wrong_answer | correctness=2.0 purity=1.0

### [RAG failed despite successful retrieval] `1273`
- **Question:** பாகிஸ்தான் பஞ்சாபிகள் எங்கே வாழ்கிறார்கள்?
- **Gloss (Q):** Where do Pakistani Punjabis live?
- **Gold answer:** In North Punjab | original: வடக்கு பஞ்சாபில்
- **Bot answer:** பாகிஸ்தானின் பஞ்சாப் பகுதியில், ஐந்து முக்கிய நதிகளில் நான்கினால் வளம் கொழிக்கும் பிராந்தியங்களில் பாகிஸ்தானிய பஞ்சாபியர்கள் பெரும்பாலும் வாழ்கிறார்கள்.
- **Gloss (A):** In Pakistan's Punjab area, in the fertile regions nourished by four of the five major rivers, Pakistani Punjabis mostly live.
- **Flags:** incomplete | correctness=3.0 purity=1.0


## TE (Telugu)

### [gold_context comprehension] `1556`
- **Question:** భూభాగాలను పరిపాలించి సామ్రాజ్యానికి కప్ప కూల్చడానికి ఎన్ని రకాల ఆర్మీ దళాలు ఉన్నాయి?
- **Gloss (Q):** How many types of army forces are there to govern territories and pay tribute to the empire?
- **Gold answer:** Keladi, Madurai | original: కెలాడి, మదురై
- **Bot answer:** ఈ సమాచారంలో భూభాగాలను పరిపాలించి సామ్రాజ్యానికి కప్ప కూల్చే ఆర్మీ దళాల రకాల సంఖ్య గురించి వివరాలు లేవు. అందువల్ల ఈ ప్రశ్నకు అందుబాటులో ఉన్న సమాచారం ఆధారంగా సమాధానం ఇవ్వలేను.
- **Gloss (A):** This information does not contain details about the number of types of army forces that govern territories and pay tribute to the empire. Therefore I cannot answer this question based on the available information.
- **Flags:** refusal | correctness=0.0 purity=1.0

### [gold_context comprehension] `1622`
- **Question:** భగత్ సింగ్, రాజ్‌గురు, సుఖ్‌దేవ్, ఉదమ్‌సింగ్‌ల ఏ శిక్షలకు వ్యతిరేకంగా నిరసన చేయలేదని కొన్ని వర్గాలు నిందించాయి?
- **Gloss (Q):** Against which punishments of Bhagat Singh, Rajguru, Sukhdev and Udham Singh did some groups accuse [him] of not protesting?
- **Gold answer:** to the death sentences / death penalty | original: ఉరిశిక్షలకు
- **Bot answer:** భగత్ సింగ్, రాజ్‌గురు, సుఖ్‌దేవ్, ఉదమ్‌సింగ్‌ల **హింసా శిక్షలకు** వ్యతిరేకంగా నిరసన చేయలేదని కొన్ని వర్గాలు నిందించాయి; హింసా
- **Gloss (A):** Some groups criticized that [he] did not protest against the violent punishments of Bhagat Singh, Rajguru, Sukhdev, Udham Singh; violent
- **Flags:** unfaithful_to_context, wrong_answer, hallucinated | correctness=1.0 purity=1.0

### [gold_context comprehension] `364`
- **Question:** చాణక్యుడు వికారమైన భౌతిక రూపంతో నందుడు ఏ రాజును అవమానించాడు?
- **Gloss (Q):** Which king, Nanda, insulted Chanakya for his deformed physical form?
- **Gold answer:** Pataliputra king | original: పాటలీపుత్ర రాజు
- **Bot answer:** చాణక్యుడు పాటలీపుత్ర రాజు **రాజు ధననందను** తన వికారమైన శారీరక రూపానికి అవమానించాడు.
- **Gloss (A):** Chanakya insulted Pataliputra king Raja Dhana Nanda for his deformed physical form.
- **Flags:** unfaithful_to_context, wrong_answer | correctness=3.0 purity=1.0

### [RAG failed despite successful retrieval] `1556`
- **Question:** భూభాగాలను పరిపాలించి సామ్రాజ్యానికి కప్ప కూల్చడానికి ఎన్ని రకాల ఆర్మీ దళాలు ఉన్నాయి?
- **Gloss (Q):** How many types of army forces were there to govern territories and pay tribute to the empire?
- **Gold answer:** Keladi, Madurai | original: కెలాడి, మదురై
- **Bot answer:** ప్రదత్త సమాచారంలో ఆర్మీ దళాల రకాల సంఖ్య గురించి ప్రస్తావన లేదు. రాజు కమాండర్లు యుద్ధభూమిలో దళాలను నడిపించారని మాత్రమే తెలుపబడింది.
- **Gloss (A):** There is no mention about the number of types of army forces in the provided information. It is only mentioned that the king's commanders led the forces in the battlefield.
- **Flags:** wrong_answer, incomplete | correctness=1.0 purity=1.0

### [Answer not in target script] `727`
- **Question:** సెంట్రల్ హిందూ కాలేజ్ 1916 వ సంవత్సరం నుండి ఏ విశ్వవిద్యాలయంగా మారింది?
- **Gloss (Q):** Since the year 1916, into which university did Central Hindu College become?
- **Gold answer:** Benaras Hindu University | original: " బెనారస్ హిందూ విశ్వవిద్యాలయం "
- **Bot answer:** సెంట్రల్ హిందూ కాలేజ్ 1916 నుండి **బెనారస్ హిందూ విశ్వవిద్యాలయం** (Banaras Hindu University) గా మారింది.
- **Gloss (A):** Central Hindu College became Benaras Hindu University (Banaras Hindu University) from 1916.
- **Flags:** none | correctness=5.0 purity=0.5686


## KN (Kannada)

### [gold_context comprehension] `103`
- **Question:** ಅರೆ-ಅಧ್ಯಕ್ಷೀಯ ವ್ಯವಸ್ಥೆಯು ಯಾವಾಗ ಚರ್ಚೆ ನಡೆಸಿತು?
- **Gloss (Q):** When was the semi-presidential system discussed?
- **Gold answer:** Rahman | original: ರಹಮಾನ್
- **Bot answer:** ಅರೆ-ಅಧ್ಯಕ್ಷೀಯ ವ್ಯವಸ್ಥೆಯನ್ನು ಯಾವಾಗ ಚರ್ಚೆ ಮಾಡಲಾಗಿತು ಎಂಬುದು ಲಭ್ಯವಿರುವ ಮಾಹಿತಿಯಲ್ಲಿ ಇಲ್ಲ.
- **Gloss (A):** The information about when the semi-presidential system was discussed is not available in the available information.
- **Flags:** refusal | correctness=0.0 purity=1.0

### [gold_context comprehension] `992`
- **Question:** ದುರ್ಯೋಧನನ ಆಪ್ತ ಸ್ನೇಹಿತ ಯಾರು?
- **Gloss (Q):** Who is Duryodhana's close friend?
- **Gold answer:** Karna | original: ಕರ್ಣ
- **Bot answer:** ಈ ಮಾಹಿತಿಯಲ್ಲಿ ದುರ್ಯೋಧನನ ಆಪ್ತ ಸ್ನೇಹಿತನ ಬಗ್ಗೆ ಯಾವುದೇ ಮಾಹಿತಿ ಇಲ್ಲದೆ, ಹಾಗಾಗಿ ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.
- **Gloss (A):** There is no information about Duryodhana's close friend in this information, so it cannot be answered.
- **Flags:** refusal | correctness=0.0 purity=1.0

### [gold_context comprehension] `893`
- **Question:** ಸಿಂಧೂ-ಸರಸ್ವತಿ ನಾಗರಿಕತೆ ಎಂಬ ಹೆಸರು ಬರಲು ಕಾರಣವಾದ ನದಿ ಯಾವುದು?
- **Gloss (Q):** Which river is the reason for the name Sindhu-Saraswati civilization?
- **Gold answer:** Sindhu | original: ಸಿಂಧೂ
- **Bot answer:** ಸಿಂಧೂ-ಸರಸ್ವತಿ ನಾಗರಿಕತೆ ಎಂಬ ಹೆಸರಿಗೆ ಕಾರಣವಾದ ನದಿಯೆ **ಸರಸ್ವತಿ ನದಿ**. ಈ ಪ್ರದೇಶದಲ್ಲಿ ಈಗ ಬತ್ತಿ ಹೋಗಿರುವ ಸರಸ್ವತಿ ನದಿಯನ್ನು ಸಂಶೋಧಕರು ಗುರುತಿಸಿದ್ದಾರೆ.
- **Gloss (A):** The river that is the reason for the name Sindhu-Saraswati civilization is the Saraswati River. Researchers have identified the Saraswati river which is now dried up in this region.
- **Flags:** unfaithful_to_context, wrong_answer, hallucinated | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `893`
- **Question:** ಸಿಂಧೂ-ಸರಸ್ವತಿ ನಾಗರಿಕತೆ ಎಂಬ ಹೆಸರು ಬರಲು ಕಾರಣವಾದ ನದಿ ಯಾವುದು?
- **Gloss (Q):** Which river is the reason for the name Sindhu-Saraswati civilization?
- **Gold answer:** Sindhu | original: ಸಿಂಧೂ
- **Bot answer:** ಸಿಂಧೂ-ಸರಸ್ವತಿ ನಾಗರಿಕತೆಯ ಹೆಸರಿನಲ್ಲಿ ಸಿಂಧೂ ಎಂದುವುದು ನದಿಗೆ ಸಂಸ್ಕೃತದಲ್ಲಿ ಬಳಸುವ ಪದವಾಗಿದ್ದು, ಸರಸ್ವತಿ ಎಂಬುದು ಆ ನದಿಯ ಹೆಸರು. ಈಗ ಬತ್ತಿ ಹೋಗಿರುವ ಸರಸ್ವತಿ ನದಿಯನ್ನು ಸಂಶೋಧಕರು ಈ ಪ್ರದೇಶದಲ್ಲಿ ಗುರುತಿಸಿದ್ದಾರೆ.
- **Gloss (A):** In the name Sindhu-Saraswati civilization, Sindhu is the word used in Sanskrit for river, Saraswati is the name of that river. Researchers have identified the now dried Saraswati river in this region.
- **Flags:** unfaithful_to_context, wrong_answer, hallucinated | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `899`
- **Question:** ಜೀವನದಲ್ಲಿ ಧ್ಯಾನಸ್ಥ ಸ್ಥಿತಿಯಲ್ಲಿರುವುದನ್ನು ಏನೆನ್ನುತ್ತಾರೆ?
- **Gloss (Q):** What is it called to be in a meditative state in life?
- **Gold answer:** absorption | original: ತನ್ಮಯತೆಯ
- **Bot answer:** ಜೀವನದಲ್ಲಿ ಧ್ಯಾನಸ್ಥ ಸ್ಥಿತಿಯನ್ನು **ಸಮಾಧಿ (ಸಾವಿನ)** ಎಂದು ಕರೆಯಲಾಗುತ್ತದೆ; ಪ್ರಾಚೀನ ಬೌದ್ಧ ಧರ್ಮವು ಈ ಸ್ಥಿತಿಗಳನ್ನು ಮೂರ್ತೀಕರಿಸಿತ್ತು. ಬುದ್ಧನ ಪ್ರಕಾರ ಧ್ಯಾನದ ಉನ್ನತ ಸ್ಥಿತಿಯೂ ಬಿಡುಗಡೆ ನೀಡುವುದಿಲ್ಲ.
- **Gloss (A):** The meditative state in life is called samadhi (
- **Flags:** wrong_answer, hallucinated | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `482`
- **Question:** ಯಾರು ಕ್ರಮ್ಸ್ ಎಂದು ಕರೆಯಲ್ಪಡುವ ವಂಶಾವಳಿಯ ಹೆಸರುಗಳನ್ನು ಹೊಂದಿದ್ದಾರೆ?
- **Gloss (Q):** Who has lineage names called Krams?
- **Gold answer:** Damar | original: ದಮಾರ‍್
- **Bot answer:** ಸೈಯಿದ್‌ಗಳು ಕ್ರಮ್‌ ಎಂದು ಕರೆಯಲ್ಪಡುವ ವಂಶನಾಮಗಳನ್ನು ಹೊಂದಿದ್ದಾರೆ; ಇವೆಯಲ್ಲ “ತಂತ್ರೆ”, “ಷೇಕ್”, “ಭಟ್”, “ಮಂಟು”, “ಗನಾಯ್”, “ದರ್”, “ದಮಾರ್”, “ಲೊನ್” ಇತ್ಯಾದಿಗಳೂ ಸೇರಿಕೊಂಡಿವೆ.
- **Gloss (A):** Sayyids have lineage names called Kram; these include 'Tantre', 'Sheikh', 'Bhat', 'Mantu', 'Ganai', 'Dar', 'Damar', 'Lon' etc.
- **Flags:** hallucinated, incomplete | correctness=3.0 purity=1.0


## ML (Malayalam)

### [gold_context comprehension] `1143`
- **Question:** ഇന്ത്യൻ പതാകയിൽ ഹിന്ദുമതത്തെ പ്രതിനിധീകരിക്കുന്ന നിറം ഏത് ?
- **Gloss (Q):** Which colour in the Indian flag represents Hinduism?
- **Gold answer:** Saffron | original: കാവിയും
- **Bot answer:** ഹിന്ദുമതത്തെ പ്രതിനിധീകരിക്കുന്നത് പട്ടയിലെ ഖക്കി (മാക്കി) നിറമാണ്.
- **Gloss (A):** The colour representing Hinduism is the khaki (maki) colour in the flag.
- **Flags:** unfaithful_to_context, wrong_answer | correctness=1.0 purity=1.0

### [gold_context comprehension] `1292`
- **Question:** സ്വതന്ത്രരായി അറിയപ്പെടുന്ന ബ്രിഗേഡുകൾ, ഡിവിഷനുകൾ, കോർപ്സ് എന്നിവ ആരുടെ നേരിട്ടുള്ള നിയന്ത്രണത്തിലാണ്.?
- **Gloss (Q):** Under whose direct control are the brigades, divisions and corps that are known as independent?
- **Gold answer:** Core Commander | original: കോർ കമാൻഡർ
- **Bot answer:** ബ്രിഗേഡ്, ഡിവിഷൻ, കോർ എന്നിവ അവതരുമാനവിന്റെ കമാൻഡറിന്റെ നേരിട്ടുള്ള നിയന്ത്രണത്തിലാണ്—ബ്രിഗേഡ് കമാൻഡർ, ഡിവിഷൻ കമാൻഡർ (മേജർ ജനറൽ), കോർ കമാൻഡർ എന്നിവരുടെ അധികാരത്തിലാണ്.
- **Gloss (A):** Brigade, division and corps are under the direct control of their respective commanders — under the authority of the brigade commander, the division commander (Major General), and the corps commander.
- **Flags:** wrong_answer | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `234`
- **Question:** ഭഗത് സിംഗ് നെ തൂക്കിക്കൊന്ന ദിവസം ഏത്?
- **Gloss (Q):** On which day was Bhagat Singh hanged?
- **Gold answer:** On 24 March 1931. | original: .1931 മാർച്ച് 24 ന്
- **Bot answer:** ഭഗത് സിംഗിനെ തൂക്കിക്കൊന്നത് **1931 മാർച്ച് 31ന്**. അന്ന് വധശിക്ഷ നടപ്പാക്കാനായിരുന്നു; ഗാന്ധിയും കോൺഗ്രസ്സ് നേതാക്കളും ശ്രമിച്ചതിനാല് വധശിക്ഷ പതിനൊന്നു മണിക്കൂറോളം മാറ്റിവയസ്സിച്ചിരുന്നു.
- **Gloss (A):** Bhagat Singh was hanged on 31 March 1931. The execution was to be carried out on that day; because Gandhi and Congress leaders tried, the execution was postponed by about eleven hours.
- **Flags:** unfaithful_to_context, wrong_answer, hallucinated | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `1292`
- **Question:** സ്വതന്ത്രരായി അറിയപ്പെടുന്ന ബ്രിഗേഡുകൾ, ഡിവിഷനുകൾ, കോർപ്സ് എന്നിവ ആരുടെ നേരിട്ടുള്ള നിയന്ത്രണത്തിലാണ്.?
- **Gloss (Q):** Under whose direct control are the brigades, divisions and corps that are known as independent?
- **Gold answer:** Core Commander | original: കോർ കമാൻഡർ
- **Bot answer:** ബ്രിഗേഡുകൾ, ഡിവിഷനുകൾ, കോർപ്സ് എന്നിവ ആർമി കമാൻഡിന്റെ (ആർമി കമാൻഡിന്റെ) നേരിട്ടുള്ള നിയന്ത്രണത്തിലാണ്. ആർമി കമാൻഡ് കരസേനയുടെ ഏറ്റവും ഉയർന്ന അധികാരിയാണ്.
- **Gloss (A):** Brigades, divisions and corps are under the direct control of Army Command. Army Command is the highest authority of the army.
- **Flags:** unfaithful_to_context, wrong_answer, hallucinated | correctness=1.0 purity=1.0

### [RAG failed despite successful retrieval] `1143`
- **Question:** ഇന്ത്യൻ പതാകയിൽ ഹിന്ദുമതത്തെ പ്രതിനിധീകരിക്കുന്ന നിറം ഏത് ?
- **Gloss (Q):** Which colour represents Hinduism in the Indian flag?
- **Gold answer:** Saffron | original: കാവിയും
- **Bot answer:** 1921-ൽ ഇന്ത്യൻ നാഷണൽ കോൺഗ്രസ് ഔദ്യോഗികപതാകയിൽ ഹിന്ദുമതത്തെ **ചുവപ്പ്** പ്രതിനിധീകരിച്ചിരുന്നു. 1931-ലെ പതാകയിൽ മതപരമായ പ്രതീകാത്മകത ഇല്ല.
- **Gloss (A):** In 1921 the official flag of the Indian National Congress represented Hinduism with red. The 1931 flag has no religious symbolism.
- **Flags:** wrong_answer | correctness=1.0 purity=1.0
