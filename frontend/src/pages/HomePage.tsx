import React from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { LanguageCode, SUPPORTED_LANGUAGES } from '@/types/api';
import {
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Database,
  BarChart3,
  MessageSquare,
  Layers,
  CheckCircle2
} from 'lucide-react';

interface HomePageProps {
  onNavigate: (route: string) => void;
}

// This is explicitly a static product illustration, never an API result.
// Keeping one example per interface language prevents the old Hindi-only
// preview from implying that changing the interface had not taken effect.
const HOME_DEMO: Record<LanguageCode, { question: string; answer: string; status: string; citation: string }> = {
  en: {
    question: 'Where is the Taj Mahal located?',
    answer: 'The Taj Mahal is in Agra, Uttar Pradesh, India. It was commissioned by Mughal emperor Shah Jahan in memory of Mumtaz Mahal.',
    status: 'Illustrative grounded-answer preview',
    citation: 'Illustrative citation · IndicQA context',
  },
  hi: {
    question: 'ताजमहल कहाँ स्थित है?',
    answer: 'ताजमहल भारत के उत्तर प्रदेश के आगरा शहर में स्थित है। इसे मुगल सम्राट शाहजहाँ ने मुमताज महल की स्मृति में बनवाया था।',
    status: 'आधारित उत्तर का उदाहरण',
    citation: 'उदाहरणात्मक संदर्भ · IndicQA प्रसंग',
  },
  te: {
    question: 'తాజ్ మహల్ ఎక్కడ ఉంది?',
    answer: 'తాజ్ మహల్ భారతదేశంలోని ఉత్తరప్రదేశ్ రాష్ట్రం ఆగ్రా నగరంలో ఉంది. దీనిని షాజహాన్ ముంతాజ్ మహల్ జ్ఞాపకార్థం నిర్మించారు.',
    status: 'ఆధారిత సమాధాన ఉదాహరణ',
    citation: 'ఉదాహరణ సూచన · IndicQA సందర్భం',
  },
  ta: {
    question: 'தாஜ்மஹால் எங்கு அமைந்துள்ளது?',
    answer: 'தாஜ்மஹால் இந்தியாவின் உத்தரப் பிரதேச மாநிலத்தில் உள்ள ஆக்ராவில் அமைந்துள்ளது. அதை ஷாஜகான் மும்தாஜ் மகாலின் நினைவாகக் கட்டினார்.',
    status: 'ஆதாரமுள்ள பதில் எடுத்துக்காட்டு',
    citation: 'விளக்கக் குறிப்பு · IndicQA சூழல்',
  },
  kn: {
    question: 'ತಾಜ್ ಮಹಲ್ ಎಲ್ಲಿದೆ?',
    answer: 'ತಾಜ್ ಮಹಲ್ ಭಾರತದ ಉತ್ತರ ಪ್ರದೇಶದ ಆಗ್ರಾದಲ್ಲಿದೆ. ಇದನ್ನು ಷಹಜಹಾನ್ ಮಮ್ತಾಜ್ ಮಹಲ್ ಅವರ ಸ್ಮರಣಾರ್ಥ ನಿರ್ಮಿಸಿದರು.',
    status: 'ಆಧಾರಿತ ಉತ್ತರದ ಉದಾಹರಣೆ',
    citation: 'ಉದಾಹರಣೆಯ ಉಲ್ಲೇಖ · IndicQA ಸಂದರ್ಭ',
  },
  ml: {
    question: 'താജ്മഹൽ എവിടെയാണ് സ്ഥിതി ചെയ്യുന്നത്?',
    answer: 'താജ്മഹൽ ഇന്ത്യയിലെ ഉത്തർപ്രദേശ് സംസ്ഥാനത്തെ ആഗ്രയിലാണ് സ്ഥിതി ചെയ്യുന്നത്. മുംതാസ് മഹലിന്റെ സ്മരണയ്ക്കായി ഷാജഹാൻ ഇത് നിർമിച്ചു.',
    status: 'ആധാരിത ഉത്തരത്തിന്റെ ഉദാഹരണം',
    citation: 'ഉദാഹരണ അവലംബം · IndicQA സന്ദർഭം',
  },
};

// Script identifiers are kept in the script in which they are normally
// written; the surrounding "Script" label is localized through the catalog.
const SCRIPT_NATIVE_NAMES: Record<LanguageCode, string> = {
  en: 'Latin', hi: 'देवनागरी', te: 'తెలుగు', ta: 'தமிழ்', kn: 'ಕನ್ನಡ', ml: 'മലയാളം',
};

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const { t, language } = useLanguage();
  const demo = HOME_DEMO[language];

  return (
    <div className="space-y-20 sm:space-y-28 py-8 sm:py-16 animate-in fade-in duration-300">
      {/* 1. HERO SECTION */}
      <section className="relative text-center max-w-4xl mx-auto px-4 space-y-6 sm:space-y-8">
        {/* Subtle pill tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-elevated border border-accent-lime/30 text-xs font-semibold text-accent-lime shadow-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-lime animate-pulse" />
          <span>{t('landing_eyebrow') || 'Research-grounded multilingual AI'}</span>
        </div>

        {/* Main Headline - Fully localized across all 6 languages */}
        <h1 className="home-hero-headline text-3xl sm:text-5xl lg:text-6xl font-extrabold text-text-primary tracking-tight leading-[1.12] selection:bg-accent-lime/20 max-w-3xl mx-auto">
          {t('landing_title') || 'Intelligence Without Language Barriers.'}
        </h1>

        {/* Description */}
        <p className="text-sm sm:text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed font-normal">
          {t('landing_copy') || 'Explore how AI understands, retrieves, and responds across India’s diverse languages.'}
        </p>

        {/* Primary CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2">
          <button
            onClick={() => onNavigate('chat')}
            className="btn-start-chat w-full sm:w-auto btn-lime-glass px-8 py-3.5 rounded-2xl text-sm font-bold flex items-center justify-center gap-2.5 shadow-lime-glow group"
          >
            <MessageSquare className="w-4 h-4" />
            <span>{t('cta_start_chatting') || t('landing_start') || 'Start Chatting'}</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>

          <button
            onClick={() => onNavigate('dashboard')}
            className="w-full sm:w-auto btn-ghost-glass px-7 py-3.5 rounded-2xl text-sm font-semibold flex items-center justify-center gap-2"
          >
            <BarChart3 className="w-4 h-4 text-accent-emerald" />
            <span>{t('cta_explore_research') || t('landing_cta_research') || 'Explore Research'}</span>
          </button>
        </div>

        {/* Quick Search Capsule Preview */}
        <div
          onClick={() => onNavigate('chat')}
          className="max-w-xl mx-auto mt-6 glass-panel p-2 rounded-full border border-border-subtle flex items-center justify-between cursor-pointer hover:border-accent-lime/40 transition-all shadow-glass-md group"
        >
          <div className="flex items-center gap-3 pl-4 text-text-muted text-xs sm:text-sm truncate">
            <Sparkles className="w-4 h-4 text-accent-lime shrink-0" />
            <span className="truncate">{t('chat_input_placeholder') || 'Type your question here… (e.g. What is photosynthesis?)'}</span>
          </div>
          <div className="w-9 h-9 rounded-full btn-lime-glass flex items-center justify-center shrink-0">
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </div>
        </div>
      </section>

      {/* 2. REALISTIC PRODUCT PREVIEW */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="glass-elevated rounded-3xl border border-border-subtle p-5 sm:p-6 shadow-glass-lg relative overflow-hidden">
          {/* Mock Window Controls */}
          <div className="flex items-center justify-between border-b border-border-subtle pb-4 mb-5">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500/50" />
              <span className="w-3 h-3 rounded-full bg-amber-500/50" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/50" />
              <span className="text-xs font-mono text-text-muted ml-3 hidden sm:inline">
                BhashaCore RAG Grounded · IndicQA + IndicCorp v2
              </span>
            </div>
            <span className="text-[11px] font-mono text-accent-lime bg-accent-lime-surface px-2.5 py-0.5 rounded-full border border-accent-lime/20 font-medium">
              sarvam-105b-conversations
            </span>
          </div>

          {/* Conversation Preview Messages */}
          <div className="space-y-4">
            {/* User message */}
            <div className="flex justify-end">
              <div className="bg-accent-lime-surface border border-accent-lime/20 rounded-2xl rounded-tr-sm px-4 py-2.5 text-xs text-text-primary max-w-md font-medium">
                {demo.question}
              </div>
            </div>

            {/* Assistant message */}
            <div className="flex justify-start items-start gap-3">
              <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-[#B7FF72] to-[#36D69A] flex items-center justify-center text-[#050706] font-bold text-xs shrink-0 mt-1 shadow-sm">
                B
              </div>
              <div className="glass-panel rounded-2xl rounded-tl-sm p-4 text-xs text-text-primary max-w-lg space-y-2 border border-border-subtle">
                <div className="text-[11px] font-medium text-accent-lime flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald" />
                  <span>{demo.status}</span>
                </div>
                <p className="leading-relaxed">
                  {demo.answer}
                </p>
                <div className="pt-1.5 border-t border-border-subtle flex items-center gap-2 text-[10px] text-text-muted font-mono">
                  <span className="px-1.5 py-0.5 rounded bg-black/10 dark:bg-white/05 border border-border-subtle">
                    {demo.citation}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. SIX-LANGUAGE SHOWCASE */}
      <section className="max-w-6xl mx-auto px-4 space-y-8">
        <div className="text-center space-y-2 max-w-xl mx-auto">
          <div className="text-xs font-semibold text-accent-lime uppercase tracking-wider">
            {t('landing_sec_languages') || 'Supported Languages'}
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
            {t('home_languages_title') || 'Six Supported Indian Languages'}
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary">
            {t('landing_sec_languages_desc') || 'Six Indian languages with script-aware tokenization, Romanized query bridging, and independent knowledge pools.'}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {SUPPORTED_LANGUAGES.map((l) => (
            <div
              key={l.code}
              onClick={() => onNavigate('chat')}
              className="glass-panel rounded-2xl p-5 border border-border-subtle hover:border-accent-lime/40 transition-all duration-200 hover:-translate-y-1 cursor-pointer group space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-text-primary group-hover:text-accent-lime transition-colors">
                  {l.nativeName}
                </span>
                <span className="text-xs font-mono text-text-muted bg-black/05 dark:bg-white/05 px-2 py-0.5 rounded-md border border-border-subtle font-semibold">
                  {l.code.toUpperCase()}
                </span>
              </div>

              <div className="text-xs text-text-secondary">
                <span className="text-text-muted font-medium">{t('meta_script') || 'Script'}:</span> {SCRIPT_NATIVE_NAMES[l.code]}
              </div>

              <div className="bg-black/05 dark:bg-white/[0.03] rounded-xl p-2.5 text-xs text-text-secondary group-hover:text-text-primary transition-colors border border-border-subtle">
                <div className="text-[10px] text-accent-lime font-semibold mb-0.5">
                  {t('sample_query_label') || 'Sample Query'}
                </div>
                "{l.sampleQuestion}"
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. RESEARCH OBJECTIVES & EVIDENCE */}
      <section className="max-w-6xl mx-auto px-4 space-y-8">
        <div className="text-center space-y-2 max-w-xl mx-auto">
          <div className="text-xs font-semibold text-accent-emerald uppercase tracking-wider">
            {t('home_research_eyebrow') || 'Rigorous Empirical Research'}
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
            {t('landing_sec_comp') || 'Research & Cross-Lingual Evaluation'}
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary">
            {t('landing_sec_comp_desc') || 'Systematic evaluation measuring performance drops between English and regional Indic languages across closed-book and RAG settings.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-panel rounded-2xl p-6 border border-border-subtle space-y-3">
            <div className="w-10 h-10 rounded-xl bg-accent-lime-surface border border-accent-lime/30 flex items-center justify-center text-accent-lime">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-text-primary">
              {t('landing_evidence') || 'IndicCorp v2 Integration'}
            </h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('landing_evidence_copy') || 'Grounds LLM responses in curated articles from AI4Bharat IndicCorp v2 and IndicQA context datasets, mitigating low-resource hallucinations.'}
            </p>
          </div>

          <div className="glass-panel rounded-2xl p-6 border border-border-subtle space-y-3">
            <div className="w-10 h-10 rounded-xl bg-accent-emerald-surface border border-accent-emerald/30 flex items-center justify-center text-accent-emerald">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-text-primary">
              {t('landing_sec_eval') || 'Empirical Evaluation'}
            </h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('landing_sec_eval_desc') || 'Measures answer correctness and faithfulness using an automated LLM judge across closed-book, gold-context, and retrieval-augmented modes.'}
            </p>
          </div>

          <div className="glass-panel rounded-2xl p-6 border border-border-subtle space-y-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-500">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-text-primary">
              {t('home_translit_title') || 'Romanized Transliteration'}
            </h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('home_translit_desc') || 'Bridges spoken colloquial Romanized Indic queries into native script representations for high-recall corpus matching.'}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
