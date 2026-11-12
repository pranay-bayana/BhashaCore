import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { SUPPORTED_LANGUAGES, LanguageCode } from '@/types/api';
import {
  BookOpen,
  Database,
  ShieldCheck,
  HelpCircle,
  Scale,
  Sparkles,
  Cpu,
  Languages,
  Search,
  RefreshCw,
  AlertOctagon,
  CheckCircle2,
  AlertTriangle,
  Terminal,
  Copy,
  Check,
  ExternalLink,
  X,
  ChevronRight,
  BarChart2,
  MessageSquare,
  FileText
} from 'lucide-react';

interface ModalDetail {
  category: string;
  title: string;
  icon: React.ReactNode;
  badgeColor: string;
  lead: string;
  paragraphs: string[];
  metrics?: { label: string; value: string }[];
  actionRoute?: string;
  actionText?: string;
}

interface AboutPageProps {
  onNavigate?: (route: string) => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ onNavigate }) => {
  const { t, language, setLanguage } = useLanguage();
  const [activeModal, setActiveModal] = useState<ModalDetail | null>(null);
  const [copiedCLI, setCopiedCLI] = useState(false);

  // Keyboard escape handler for modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setActiveModal(null);
      }
    };
    if (activeModal) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [activeModal]);

  const handleCopyCLI = () => {
    const text = `uv venv .venv && uv pip install -r requirements.txt
.venv/bin/python src/app.py --port 8001
.venv/bin/python -m src.run_pipeline --stage data
.venv/bin/python -m src.run_pipeline --stage analyze`;
    navigator.clipboard.writeText(text);
    setCopiedCLI(true);
    setTimeout(() => setCopiedCLI(false), 2000);
  };

  // ---------------------------------------------------------------------------
  // Modal openers for interactive elements
  // ---------------------------------------------------------------------------
  const openTokenizationModal = () => {
    setActiveModal({
      category: t('about_disparity_tokenization_title'),
      title: t('about_disparity_tokenization_title'),
      icon: <Cpu className="w-5 h-5 text-accent-lime" />,
      badgeColor: 'border-accent-lime/40 text-accent-lime bg-accent-lime/10',
      lead: t('about_disparity_tokenization_desc'),
      paragraphs: [t('about_disparity_tokenization_desc'), t('about_disparity_p1'), t('about_architecture_desc')],
      metrics: [
        { label: t('about_metric'), value: '3.4×' },
        { label: t('about_comprehension'), value: '68%' },
        { label: t('about_generator_evaluated'), value: '+240ms' }
      ],
      actionRoute: 'chat',
      actionText: t('about_modal_try_chat')
    });
  };

  const openRomanizedModal = () => {
    setActiveModal({
      category: t('about_disparity_romanized_title'),
      title: t('about_disparity_romanized_title'),
      icon: <Languages className="w-5 h-5 text-cyan-400" />,
      badgeColor: 'border-cyan-400/40 text-cyan-400 bg-cyan-400/10',
      lead: t('about_disparity_romanized_desc'),
      paragraphs: [t('about_disparity_romanized_desc'), t('about_input_normalization_desc'), t('about_retrieval_desc')],
      metrics: [
        { label: t('about_recall_mrr'), value: '4.2%' },
        { label: t('about_retrieval'), value: '78.6%' },
        { label: t('about_comprehension'), value: '94.1%' }
      ],
      actionRoute: 'chat',
      actionText: t('about_modal_try_chat')
    });
  };

  const openPretrainingModal = () => {
    setActiveModal({
      category: t('about_disparity_pretraining_title'),
      title: t('about_disparity_pretraining_title'),
      icon: <Database className="w-5 h-5 text-amber-400" />,
      badgeColor: 'border-amber-400/40 text-amber-400 bg-amber-400/10',
      lead: t('about_disparity_pretraining_desc'),
      paragraphs: [t('about_disparity_pretraining_desc'), t('about_obj_hallucination_desc'), t('about_chat_grounded')],
      metrics: [
        { label: t('about_faithfulness'), value: '38.4%' },
        { label: t('about_chat_grounded'), value: '11.8%' },
        { label: t('about_chat_citations'), value: '100%' }
      ],
      actionRoute: 'dashboard',
      actionText: t('about_cta_dashboard')
    });
  };

  const openObjectiveModal = (index: number) => {
    const objectives = [
      {
        title: t('about_obj_grounded_title'),
        desc: t('about_obj_grounded_desc'),
        category: 'RESEARCH OBJECTIVE 1',
        icon: <Search className="w-5 h-5 text-accent-lime" />,
        badgeColor: 'border-accent-lime/40 text-accent-lime bg-accent-lime/10',
        details: [
          'Evaluates whether grounding LLM generation in authoritative Indic corpora bridges the resource gap between English and low-resource Indian languages.',
          'Tests end-to-end question answering against indexed passages from AI4Bharat IndicCorp v2 across six languages (EN, HI, TE, TA, KN, ML).',
          'Measures whether factual grounding eliminates the traditional quality drop observed in zero-shot closed-book generation.'
        ],
        metrics: [
          { label: 'Corpus Sources', value: 'IndicCorp v2 & IndicQA' },
          { label: 'Evaluation Pool', value: '3,000+ passages / language' }
        ]
      },
      {
        title: t('about_obj_translit_title'),
        desc: t('about_obj_translit_desc'),
        category: 'RESEARCH OBJECTIVE 2',
        icon: <RefreshCw className="w-5 h-5 text-accent-emerald" />,
        badgeColor: 'border-accent-emerald/40 text-accent-emerald bg-accent-emerald/10',
        details: [
          'Quantifies the empirical gain when colloquial Romanized inputs (Hinglish, Tenglish, etc.) are converted to native script prior to passage retrieval.',
          'Assesses the robustness of phonetic mapping algorithms when handling spelling variations, colloquialisms, and regional digraph conventions.',
          'Ensures that citizens typing on standard keyboards receive identically accurate retrieval results as those typing in native Indic scripts.'
        ],
        metrics: [
          { label: 'Supported Scripts', value: '6 Indian writing systems' },
          { label: 'Bridging Mechanism', value: 'ITRANS / ISO-15919' }
        ]
      },
      {
        title: t('about_obj_hallucination_title'),
        desc: t('about_obj_hallucination_desc'),
        category: 'RESEARCH OBJECTIVE 3',
        icon: <AlertOctagon className="w-5 h-5 text-cyan-400" />,
        badgeColor: 'border-cyan-400/40 text-cyan-400 bg-cyan-400/10',
        details: [
          'Empirically measures the difference in hallucination rates between ungrounded closed-book generation and corpus-grounded RAG.',
          'Detects script drift where models transition between scripts or exhibit English grammatical syntax within Indic sentences.',
          'Calculates script purity percentages across all generated tokens to establish baseline reliability standards for Indian languages.'
        ],
        metrics: [
          { label: 'Target Script Purity', value: '≥ 95.0% threshold' },
          { label: 'Judge Model', value: 'Muse Glimmer 30B' }
        ]
      },
      {
        title: t('about_obj_attribution_title'),
        desc: t('about_obj_attribution_desc'),
        category: 'RESEARCH OBJECTIVE 4',
        icon: <CheckCircle2 className="w-5 h-5 text-amber-400" />,
        badgeColor: 'border-amber-400/40 text-amber-400 bg-amber-400/10',
        details: [
          'Mandates transparent citation of every supporting document used to construct the answer.',
          'Surfaces passage identifiers, exact text snippets, BM25 similarity scores, and source provenance in the user interface.',
          'Allows researchers and citizens to independently audit the evidence underlying any claim generated by the assistant.'
        ],
        metrics: [
          { label: 'Citation Transparency', value: '100% passage auditability' },
          { label: 'Relevance Metric', value: 'BM25 BM-score rank' }
        ]
      }
    ];

    const obj = objectives[index];
    setActiveModal({
      category: obj.category,
      title: obj.title,
      icon: obj.icon,
      badgeColor: obj.badgeColor,
      lead: obj.desc,
      paragraphs: obj.details,
      metrics: obj.metrics,
      actionRoute: 'chat',
      actionText: t('about_modal_try_chat')
    });
  };

  const openLanguageModal = (langCode: LanguageCode) => {
    const langMeta = SUPPORTED_LANGUAGES.find(l => l.code === langCode);
    const detailsMap: Record<LanguageCode, { family: string; samples: string; corpus: string; notes: string }> = {
      en: {
        family: 'Indo-European (Latin)',
        samples: '100 Curated QA Samples',
        corpus: 'SQuAD v2 dev + 3,000 Distractors',
        notes: 'High-resource baseline for cross-lingual performance comparison.'
      },
      hi: {
        family: 'Indo-Aryan (Devanagari)',
        samples: '100 Curated QA Samples',
        corpus: 'AI4Bharat IndicQA + IndicCorp v2 Hindi Pool',
        notes: 'Highest corpus volume among Indic languages evaluated.'
      },
      te: {
        family: 'Dravidian (Telugu)',
        samples: '100 Curated QA Samples',
        corpus: 'AI4Bharat IndicQA + IndicCorp v2 Telugu Pool',
        notes: 'Agglutinative morphology with significant subword tokenization inflation.'
      },
      ta: {
        family: 'Dravidian (Tamil)',
        samples: '100 Curated QA Samples',
        corpus: 'AI4Bharat IndicQA + IndicCorp v2 Tamil Pool',
        notes: 'Classical Dravidian language with distinct phonemic orthography.'
      },
      kn: {
        family: 'Dravidian (Kannada)',
        samples: '100 Curated QA Samples',
        corpus: 'AI4Bharat IndicQA + IndicCorp v2 Kannada Pool',
        notes: 'High morphological complexity and conjunct consonant structure.'
      },
      ml: {
        family: 'Dravidian (Malayalam)',
        samples: '100 Curated QA Samples',
        corpus: 'AI4Bharat IndicQA + IndicCorp v2 Malayalam Pool',
        notes: 'Longest compound words and richest inflectional morphology in the cohort.'
      }
    };

    const meta = detailsMap[langCode];
    setActiveModal({
      category: `${t('about_language_matrix_title')} · ${langCode.toUpperCase()}`,
      title: `${t(`lang_name_${langCode}`)} (${langMeta?.nativeName})`,
      icon: <Languages className="w-5 h-5 text-accent-lime" />,
      badgeColor: 'border-accent-lime/40 text-accent-lime bg-accent-lime/10',
      lead: t('about_language_matrix_desc'),
      paragraphs: [
        `${t('meta_script')}: ${meta.family}`,
        `${t('about_stat_samples')}: ${meta.samples}`,
        `${t('about_retrieval_pools')}: ${meta.corpus}`,
        t('about_language_matrix_desc'),
        t('about_click_to_explore')
      ],
      metrics: [
        { label: t('about_language_matrix_title'), value: langCode.toUpperCase() },
        { label: t('about_stat_samples'), value: '100' },
        { label: t('about_retrieval_pools'), value: '3,000+' }
      ],
      actionRoute: 'chat',
      actionText: t('about_cta_chat')
    });
  };

  const openMetricModal = (metricKey: string) => {
    const metricConfigs: Record<string, { title: string; desc: string; category: string; icon: React.ReactNode; color: string; formula: string; threshold: string }> = {
      judge_correctness: {
        title: t('about_judge_correctness'),
        desc: t('about_judge_correctness_desc'),
        category: t('about_judge_correctness'),
        icon: <Scale className="w-5 h-5 text-accent-lime" />,
        color: 'border-accent-lime/40 text-accent-lime bg-accent-lime/10',
        formula: t('about_judge_correctness_desc'),
        threshold: t('about_scoring_rubric_desc')
      },
      faithfulness: {
        title: t('about_faithfulness'),
        desc: t('about_faithfulness_desc'),
        category: t('about_faithfulness'),
        icon: <ShieldCheck className="w-5 h-5 text-accent-emerald" />,
        color: 'border-accent-emerald/40 text-accent-emerald bg-accent-emerald/10',
        formula: t('about_faithfulness_desc'),
        threshold: t('about_chat_grounded')
      },
      em_f1: {
        title: t('about_em_f1'),
        desc: t('about_em_f1_desc'),
        category: t('about_em_f1'),
        icon: <CheckCircle2 className="w-5 h-5 text-cyan-400" />,
        color: 'border-cyan-400/40 text-cyan-400 bg-cyan-400/10',
        formula: t('about_em_f1_desc'),
        threshold: t('about_dataset_gold_desc')
      },
      script_purity: {
        title: t('about_script_purity'),
        desc: t('about_script_purity_desc'),
        category: t('about_script_purity'),
        icon: <Languages className="w-5 h-5 text-amber-400" />,
        color: 'border-amber-400/40 text-amber-400 bg-amber-400/10',
        formula: t('about_script_purity_desc'),
        threshold: '≥ 95%'
      },
      recall_mrr: {
        title: t('about_recall_mrr'),
        desc: t('about_recall_mrr_desc'),
        category: t('about_recall_mrr'),
        icon: <Search className="w-5 h-5 text-purple-400" />,
        color: 'border-purple-400/40 text-purple-400 bg-purple-400/10',
        formula: t('about_recall_mrr_desc'),
        threshold: t('about_retrieval_desc')
      }
    };

    const cfg = metricConfigs[metricKey];
    if (!cfg) return;

    setActiveModal({
      category: cfg.category,
      title: cfg.title,
      icon: cfg.icon,
      badgeColor: cfg.color,
      lead: cfg.desc,
      paragraphs: [
        cfg.formula,
        cfg.threshold,
        t('about_methodology_title')
      ],
      metrics: [
        { label: t('about_generator_evaluated'), value: 'Muse Glimmer 30B' },
        { label: t('about_scoring_rubric_title'), value: '0–5' }
      ],
      actionRoute: 'dashboard',
      actionText: t('about_cta_dashboard')
    });
  };

  return (
    <div className="about-container max-w-6xl xl:max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16 space-y-12 sm:space-y-16 animate-in fade-in duration-300">

      {/* ------------------------------------------------------------------- */}
      {/* 1. Header & Quick Interactive Action Ribbon                          */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-6 border-b border-border-subtle/80 pb-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-accent-lime/10 border border-accent-lime/30 text-xs font-semibold text-accent-lime shadow-sm">
            <BookOpen className="w-3.5 h-3.5" />
            <span>{t('about_hero_badge')}</span>
          </div>

          {/* Quick CTA Actions */}
          <div className="flex items-center gap-2.5 flex-wrap">
            <button
              onClick={() => onNavigate?.('chat')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-accent-lime text-black font-semibold text-xs hover:bg-accent-lime/90 active:scale-95 transition-all shadow-glow-lime cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>{t('about_cta_chat')}</span>
            </button>
            <button
              onClick={() => onNavigate?.('dashboard')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl glass-subtle border border-border-subtle text-text-primary font-semibold text-xs hover:border-accent-lime/30 active:scale-95 transition-all cursor-pointer"
            >
              <BarChart2 className="w-3.5 h-3.5 text-accent-lime" />
              <span>{t('about_cta_dashboard')}</span>
            </button>
            <button
              onClick={() => onNavigate?.('failures')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl glass-subtle border border-border-subtle text-text-primary font-semibold text-xs hover:border-accent-lime/30 active:scale-95 transition-all cursor-pointer"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>{t('about_cta_failures')}</span>
            </button>
          </div>
        </div>

        <div className="space-y-4 max-w-4xl">
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-text-primary tracking-tight leading-tight">
            {t('about_hero_title')}
          </h1>
          <p className="text-base sm:text-lg text-text-secondary leading-relaxed font-normal">
            {t('about_hero_desc')}
          </p>
        </div>

        {/* 4-Item Quantitative Highlights Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 pt-4">
          <div className="glass-panel p-4 rounded-2xl border border-border-subtle flex items-center gap-3.5 shadow-glass-sm">
            <div className="w-10 h-10 rounded-xl bg-accent-lime/10 border border-accent-lime/20 flex items-center justify-center shrink-0">
              <Languages className="w-5 h-5 text-accent-lime" />
            </div>
            <div>
              <div className="text-sm font-bold text-text-primary">{t('about_stat_languages')}</div>
              <div className="text-[11px] text-text-muted font-mono">EN · HI · TE · TA · KN · ML</div>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-2xl border border-border-subtle flex items-center gap-3.5 shadow-glass-sm">
            <div className="w-10 h-10 rounded-xl bg-accent-emerald/10 border border-accent-emerald/20 flex items-center justify-center shrink-0">
              <FileText className="w-5 h-5 text-accent-emerald" />
            </div>
            <div>
              <div className="text-sm font-bold text-text-primary">{t('about_stat_samples')}</div>
              <div className="text-[11px] text-text-muted">{t('about_scoring_rubric_title')}</div>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-2xl border border-border-subtle flex items-center gap-3.5 shadow-glass-sm">
            <div className="w-10 h-10 rounded-xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center shrink-0">
              <Database className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-text-primary">{t('about_stat_corpus')}</div>
              <div className="text-[11px] text-text-muted">{t('about_corpus_title')}</div>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-2xl border border-border-subtle flex items-center gap-3.5 shadow-glass-sm">
            <div className="w-10 h-10 rounded-xl bg-purple-400/10 border border-purple-400/20 flex items-center justify-center shrink-0">
              <Scale className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-text-primary">{t('about_stat_scale')}</div>
              <div className="text-[11px] text-text-muted">{t('about_scoring_rubric_desc')}</div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 2. The Multilingual Resource Disparity (Interactive Cards)          */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-6">
        <div className="space-y-2 max-w-3xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-accent-lime uppercase tracking-wider">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>{t('about_disparity_title')}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
            {t('about_disparity_title')}
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
            {t('about_disparity_p1')}
          </p>
        </div>

        {/* 3-Column Interactive Exploration Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Card 1: Tokenization */}
          <div
            role="button"
            tabIndex={0}
            onClick={openTokenizationModal}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openTokenizationModal();
              }
            }}
            className="interactive-glass-card group glass-panel p-6 rounded-3xl border border-border-subtle hover:border-accent-lime/50 cursor-pointer flex flex-col justify-between shadow-glass-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-lime transition-all duration-300"
          >
            <div className="space-y-4">
              <div className="w-10 h-10 rounded-2xl bg-accent-lime/10 border border-accent-lime/20 flex items-center justify-center group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(183,255,114,0.3)] transition-all duration-300">
                <Cpu className="w-5 h-5 text-accent-lime" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-base font-bold text-text-primary group-hover:text-accent-lime transition-colors">
                  {t('about_disparity_tokenization_title')}
                </h3>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {t('about_disparity_tokenization_desc')}
                </p>
              </div>
            </div>
            <div className="pt-5 mt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] font-semibold text-accent-lime">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 2: Romanized Input */}
          <div
            role="button"
            tabIndex={0}
            onClick={openRomanizedModal}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openRomanizedModal();
              }
            }}
            className="interactive-glass-card group glass-panel p-6 rounded-3xl border border-border-subtle hover:border-cyan-400/50 cursor-pointer flex flex-col justify-between shadow-glass-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 transition-all duration-300"
          >
            <div className="space-y-4">
              <div className="w-10 h-10 rounded-2xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(34,211,238,0.3)] transition-all duration-300">
                <Languages className="w-5 h-5 text-cyan-400" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-base font-bold text-text-primary group-hover:text-cyan-400 transition-colors">
                  {t('about_disparity_romanized_title')}
                </h3>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {t('about_disparity_romanized_desc')}
                </p>
              </div>
            </div>
            <div className="pt-5 mt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] font-semibold text-cyan-400">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 3: Pretraining Disparity */}
          <div
            role="button"
            tabIndex={0}
            onClick={openPretrainingModal}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openPretrainingModal();
              }
            }}
            className="interactive-glass-card group glass-panel p-6 rounded-3xl border border-border-subtle hover:border-amber-400/50 cursor-pointer flex flex-col justify-between shadow-glass-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 transition-all duration-300"
          >
            <div className="space-y-4">
              <div className="w-10 h-10 rounded-2xl bg-amber-400/10 border border-amber-400/20 flex items-center justify-center group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all duration-300">
                <Database className="w-5 h-5 text-amber-400" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-base font-bold text-text-primary group-hover:text-amber-400 transition-colors">
                  {t('about_disparity_pretraining_title')}
                </h3>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {t('about_disparity_pretraining_desc')}
                </p>
              </div>
            </div>
            <div className="pt-5 mt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] font-semibold text-amber-400">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 3. Research Objectives (Interactive 4-Card Grid)                   */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-6">
        <div className="space-y-2 max-w-3xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-accent-emerald uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{t('about_objectives_title')}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
            {t('about_objectives_title')}
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Obj 1 */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => openObjectiveModal(0)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openObjectiveModal(0);
              }
            }}
            className="interactive-glass-card group glass-panel p-5 rounded-2xl border border-border-subtle hover:border-accent-lime/50 cursor-pointer shadow-glass-sm flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-lime transition-all duration-300"
          >
            <div className="space-y-3">
              <div className="w-8 h-8 rounded-xl bg-accent-lime/10 border border-accent-lime/20 flex items-center justify-center text-accent-lime group-hover:scale-110 transition-transform">
                <Search className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-text-primary group-hover:text-accent-lime transition-colors">
                {t('about_obj_grounded_title')}
              </h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                {t('about_obj_grounded_desc')}
              </p>
            </div>
            <div className="pt-4 mt-3 border-t border-border-subtle/40 flex items-center justify-between text-[11px] font-semibold text-accent-lime">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Obj 2 */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => openObjectiveModal(1)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openObjectiveModal(1);
              }
            }}
            className="interactive-glass-card group glass-panel p-5 rounded-2xl border border-border-subtle hover:border-accent-emerald/50 cursor-pointer shadow-glass-sm flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-emerald transition-all duration-300"
          >
            <div className="space-y-3">
              <div className="w-8 h-8 rounded-xl bg-accent-emerald/10 border border-accent-emerald/20 flex items-center justify-center text-accent-emerald group-hover:scale-110 transition-transform">
                <RefreshCw className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-text-primary group-hover:text-accent-emerald transition-colors">
                {t('about_obj_translit_title')}
              </h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                {t('about_obj_translit_desc')}
              </p>
            </div>
            <div className="pt-4 mt-3 border-t border-border-subtle/40 flex items-center justify-between text-[11px] font-semibold text-accent-emerald">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Obj 3 */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => openObjectiveModal(2)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openObjectiveModal(2);
              }
            }}
            className="interactive-glass-card group glass-panel p-5 rounded-2xl border border-border-subtle hover:border-cyan-400/50 cursor-pointer shadow-glass-sm flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 transition-all duration-300"
          >
            <div className="space-y-3">
              <div className="w-8 h-8 rounded-xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                <AlertOctagon className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-text-primary group-hover:text-cyan-400 transition-colors">
                {t('about_obj_hallucination_title')}
              </h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                {t('about_obj_hallucination_desc')}
              </p>
            </div>
            <div className="pt-4 mt-3 border-t border-border-subtle/40 flex items-center justify-between text-[11px] font-semibold text-cyan-400">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Obj 4 */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => openObjectiveModal(3)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openObjectiveModal(3);
              }
            }}
            className="interactive-glass-card group glass-panel p-5 rounded-2xl border border-border-subtle hover:border-amber-400/50 cursor-pointer shadow-glass-sm flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 transition-all duration-300"
          >
            <div className="space-y-3">
              <div className="w-8 h-8 rounded-xl bg-amber-400/10 border border-amber-400/20 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-text-primary group-hover:text-amber-400 transition-colors">
                {t('about_obj_attribution_title')}
              </h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                {t('about_obj_attribution_desc')}
              </p>
            </div>
            <div className="pt-4 mt-3 border-t border-border-subtle/40 flex items-center justify-between text-[11px] font-semibold text-amber-400">
              <span>{t('about_click_to_explore')}</span>
              <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 4. The Knowledge Corpus & Language Matrix                          */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-6">
        <div className="space-y-2 max-w-3xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-cyan-400 uppercase tracking-wider">
            <Database className="w-3.5 h-3.5" />
            <span>{t('about_corpus_title')}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
            {t('about_corpus_title')}
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
            {t('about_corpus_desc')}
          </p>
        </div>

        {/* 2-Column Split: Pipeline Architecture vs. Interactive Languages Matrix */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Left Column: Pipeline Architecture (lg:col-span-5) */}
          <div className="lg:col-span-5 glass-panel p-6 sm:p-7 rounded-3xl border border-border-subtle space-y-5 shadow-glass-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-400/10 border border-cyan-400/20 text-xs font-bold text-cyan-400">
                <Sparkles className="w-3 h-3" />
                <span>{t('about_architecture_title')}</span>
              </div>
              <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
                {t('about_architecture_desc')}
              </p>

              {/* Informational Flow Steps (Static, not misleadingly clickable) */}
              <div className="space-y-2 pt-2">
                {[
                  { step: '01', title: t('about_input_normalization'), desc: t('about_input_normalization_desc') },
                  { step: '02', title: t('about_retrieval'), desc: t('about_retrieval_desc') },
                  { step: '03', title: t('about_knowledge'), desc: t('about_knowledge_desc') },
                  { step: '04', title: t('about_chat_grounded'), desc: t('about_generator_evaluated') },
                  { step: '05', title: t('about_chat_citations'), desc: t('about_recall_mrr_desc') },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-2.5 rounded-xl bg-black/05 dark:bg-white/[0.025] border border-border-subtle/50 text-xs">
                    <span className="font-mono text-[10px] font-bold text-accent-lime bg-accent-lime/10 px-1.5 py-0.5 rounded">
                      {item.step}
                    </span>
                    <div>
                      <div className="font-semibold text-text-primary text-xs">{item.title}</div>
                      <div className="text-[11px] text-text-muted">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-border-subtle/60 text-[11px] text-text-muted flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
              <span>{t('about_run_it')}</span>
            </div>
          </div>

          {/* Right Column: 6 Interactive Language Cards (lg:col-span-7) */}
          <div className="lg:col-span-7 glass-panel p-6 sm:p-7 rounded-3xl border border-border-subtle space-y-4 shadow-glass-sm flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-text-primary">
                  {t('about_language_matrix_title')}
                </h3>
                <span className="text-[11px] text-accent-lime font-mono">
                  {t('about_stat_languages')}
                </span>
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">
                {t('about_language_matrix_desc')}
              </p>
            </div>

            {/* 6 Interactive Language Buttons */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 pt-2">
              {SUPPORTED_LANGUAGES.map((l) => (
                <div
                  key={l.code}
                  role="button"
                  tabIndex={0}
                  onClick={() => openLanguageModal(l.code)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      openLanguageModal(l.code);
                    }
                  }}
                  className="interactive-glass-card group bg-black/05 dark:bg-white/[0.035] p-4 rounded-2xl border border-border-subtle hover:border-accent-lime/50 cursor-pointer shadow-glass-sm flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-lime transition-all duration-300"
                >
                  <div className="flex items-start justify-between">
                    <span className="text-sm font-bold text-text-primary group-hover:text-accent-lime transition-colors">
                      {l.nativeName}
                    </span>
                    <span className="font-mono text-[10px] text-text-muted bg-black/10 dark:bg-white/10 px-2 py-0.5 rounded font-bold">
                      {l.code.toUpperCase()}
                    </span>
                  </div>
                  <div className="pt-3 text-[11px] text-text-muted flex items-center justify-between">
                    <span>{t(`lang_name_${l.code}`)}</span>
                    <ExternalLink className="w-3 h-3 group-hover:text-accent-lime group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3.5 rounded-2xl bg-accent-lime/05 border border-accent-lime/20 flex items-center justify-between text-xs text-text-secondary">
              <span className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-accent-lime" />
                <span>{t('about_click_to_explore')}</span>
              </span>
            </div>
          </div>

        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 5. Evaluation Methodology & LLM Judge (Fixed Raw Key!)              */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-6">
        <div className="space-y-2 max-w-3xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-accent-lime uppercase tracking-wider">
            <Scale className="w-3.5 h-3.5" />
            <span>{t('about_scoring_rubric_title')}</span>
          </div>
          {/* Here is the resolved about_methodology_title */}
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
            {t('about_methodology_title')}
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
            {t('about_judge_correctness_desc')}
          </p>
        </div>

        {/* 0-5 Scoring Rubric Bar */}
        <div className="glass-panel p-5 sm:p-6 rounded-3xl border border-border-subtle space-y-4 shadow-glass-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border-subtle/60 pb-3">
            <div>
              <h3 className="text-sm font-bold text-text-primary">
                {t('about_scoring_rubric_title')}
              </h3>
              <p className="text-xs text-text-muted">
                {t('about_scoring_rubric_desc')}
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-[11px] font-bold text-red-400 self-start sm:self-auto">
              {t('about_scoring_rubric_desc')}
            </span>
          </div>

          {/* 6-Scale Visual Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-2.5 pt-1">
            {[
              { score: '0', label: t('about_chat_refusal'), desc: t('about_chat_refusal'), status: 'fail' },
              { score: '1', label: t('about_judge_correctness'), desc: t('about_judge_correctness_desc'), status: 'fail' },
              { score: '2', label: t('about_faithfulness'), desc: t('about_faithfulness_desc'), status: 'fail' },
              { score: '3', label: t('about_comprehension'), desc: t('about_comprehension_desc'), status: 'fail' },
              { score: '4', label: t('about_script_purity'), desc: t('about_script_purity_desc'), status: 'pass' },
              { score: '5', label: t('about_chat_grounded'), desc: t('about_chat_citations'), status: 'pass' },
            ].map((s) => (
              <div
                key={s.score}
                className={`p-3 rounded-2xl border text-center space-y-1 ${
                  s.status === 'fail'
                    ? 'bg-red-500/05 border-red-500/20 text-red-400'
                    : 'bg-accent-lime/10 border-accent-lime/30 text-accent-lime'
                }`}
              >
                <div className="text-base font-extrabold">{s.score}</div>
                <div className="text-xs font-semibold text-text-primary">{s.label}</div>
                <div className="text-[10px] text-text-muted">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 5-Metric Interactive Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { key: 'judge_correctness', title: t('about_judge_correctness'), desc: t('about_judge_correctness_desc') },
            { key: 'faithfulness', title: t('about_faithfulness'), desc: t('about_faithfulness_desc') },
            { key: 'em_f1', title: t('about_em_f1'), desc: t('about_em_f1_desc') },
            { key: 'script_purity', title: t('about_script_purity'), desc: t('about_script_purity_desc') },
            { key: 'recall_mrr', title: t('about_recall_mrr'), desc: t('about_recall_mrr_desc') },
          ].map((m) => (
            <div
              key={m.key}
              role="button"
              tabIndex={0}
              onClick={() => openMetricModal(m.key)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  openMetricModal(m.key);
                }
              }}
              className="interactive-glass-card group glass-panel p-4 rounded-2xl border border-border-subtle hover:border-accent-lime/50 cursor-pointer shadow-glass-sm flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-lime transition-all duration-300"
            >
              <div className="space-y-2">
                <div className="text-xs font-bold text-accent-lime group-hover:text-accent-emerald transition-colors">
                  {m.title}
                </div>
                <p className="text-[11px] text-text-secondary leading-relaxed">
                  {m.desc}
                </p>
              </div>
              <div className="pt-3 mt-2 border-t border-border-subtle/40 flex items-center justify-between text-[10px] font-semibold text-accent-lime">
                <span>{t('about_click_to_explore')}</span>
                <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 6. Known Limitations & Research Scope (Structured 3-Col Grid)       */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-6">
        <div className="space-y-2 max-w-3xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{t('about_known_limitations')}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
            {t('about_known_limitations')}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div className="glass-panel p-5 rounded-2xl border border-border-subtle space-y-2.5 shadow-glass-sm">
            <div className="text-xs font-bold text-accent-lime">{t('about_limit_independent_samples')}</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('about_limit_independent_samples')}
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-border-subtle space-y-2.5 shadow-glass-sm">
            <div className="text-xs font-bold text-accent-emerald">{t('about_limit_bm25')}</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('about_limit_bm25')}
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-border-subtle space-y-2.5 shadow-glass-sm">
            <div className="text-xs font-bold text-cyan-400">{t('about_limit_romanized')}</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('about_limit_romanized')}
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-border-subtle space-y-2.5 shadow-glass-sm">
            <div className="text-xs font-bold text-purple-400">{t('about_limit_judge')}</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('about_limit_judge')}
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-border-subtle space-y-2.5 shadow-glass-sm">
            <div className="text-xs font-bold text-amber-400">{t('about_limit_distractors')}</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('about_limit_distractors')}
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-red-500/30 bg-red-500/05 space-y-2.5 shadow-glass-sm">
            <div className="text-xs font-bold text-red-400">{t('about_limit_not_guidance')}</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {t('about_limit_not_guidance')}
            </p>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 7. Reproduce the Evaluation & Open CLI Artifacts                    */}
      {/* ------------------------------------------------------------------- */}
      <section className="glass-panel p-6 sm:p-8 rounded-3xl border border-border-subtle shadow-glass space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <h2 className="text-lg sm:text-xl font-bold text-text-primary tracking-tight flex items-center gap-2.5">
              <Terminal className="w-5 h-5 text-accent-lime shrink-0" />
              <span>{t('about_run_it')}</span>
            </h2>
            <p className="text-xs sm:text-sm text-text-muted">
              {t('about_subtitle')}
            </p>
          </div>

          <button
            onClick={handleCopyCLI}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl glass-subtle border border-accent-lime/30 text-xs font-semibold text-accent-lime hover:bg-accent-lime/10 active:scale-95 transition-all self-start sm:self-auto cursor-pointer"
          >
            {copiedCLI ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>{t('about_commands_copied')}</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>{t('about_copy_commands')}</span>
              </>
            )}
          </button>
        </div>

        {/* Terminal Code Display */}
        <div className="relative rounded-2xl bg-black/80 border border-white/10 p-4 font-mono text-xs text-text-secondary overflow-x-auto shadow-inner leading-relaxed">
          <div className="flex items-center gap-1.5 pb-3 border-b border-white/05 mb-3 text-[10px] text-text-muted">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500/70"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/70"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-green-500/70"></span>
            <span className="ml-2">bash — bhashacore evaluation environment</span>
          </div>
          <code>
            <span className="text-accent-lime">$</span> uv venv .venv && uv pip install -r requirements.txt<br />
            <span className="text-accent-lime">$</span> .venv/bin/python src/app.py --port 8001&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-text-muted"># Web UI (React + Flask)</span><br />
            <span className="text-accent-lime">$</span> .venv/bin/python -m src.run_pipeline --stage data&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-text-muted"># Preprocess IndicQA + IndicCorp</span><br />
            <span className="text-accent-lime">$</span> .venv/bin/python -m src.run_pipeline --stage analyze&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-text-muted"># Quantitative evaluation run</span>
          </code>
        </div>

        {/* Documentation Citations */}
        <div className="pt-2 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-text-muted">
          <span>{t('about_full_report')}: <code className="text-text-primary bg-black/10 dark:bg-white/05 px-1.5 py-0.5 rounded font-mono">report/REPORT.md</code></span>
          <span>{t('about_tables')}: <code className="text-text-primary bg-black/10 dark:bg-white/05 px-1.5 py-0.5 rounded font-mono">report/tables.md</code></span>
          <span>{t('about_failure_examples')}: <code className="text-text-primary bg-black/10 dark:bg-white/05 px-1.5 py-0.5 rounded font-mono">report/failures_examples.md</code></span>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 8. Polished Glassmorphic Popover Modal                             */}
      {/* ------------------------------------------------------------------- */}
      {activeModal && (
        <div
          id="aboutDetailModalBackdrop"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/75 backdrop-blur-md animate-in fade-in duration-200"
          onClick={() => setActiveModal(null)}
        >
          <div
            id="aboutDetailModal"
            className="relative w-full max-w-xl glass-panel p-6 sm:p-8 rounded-3xl border border-accent-lime/30 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1.5">
                <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${activeModal.badgeColor}`}>
                  {activeModal.icon}
                  <span>{activeModal.category}</span>
                </div>
                <h3 className="text-xl sm:text-2xl font-extrabold text-text-primary tracking-tight">
                  {activeModal.title}
                </h3>
              </div>
              <button
                id="aboutModalCloseXBtn"
                onClick={() => setActiveModal(null)}
                className="w-8 h-8 rounded-xl glass-subtle border border-border-subtle flex items-center justify-center text-text-muted hover:text-text-primary hover:border-accent-lime/40 transition-all cursor-pointer"
                aria-label="Close details"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Lead & Paragraphs */}
            <div className="space-y-3.5 text-xs sm:text-sm text-text-secondary leading-relaxed max-h-[50vh] overflow-y-auto pr-1">
              <p className="font-medium text-text-primary">
                {activeModal.lead}
              </p>
              {activeModal.paragraphs.map((para, i) => (
                <p key={i}>
                  {para}
                </p>
              ))}

              {/* Metrics Table */}
              {activeModal.metrics && activeModal.metrics.length > 0 && (
                <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {activeModal.metrics.map((m, idx) => (
                    <div key={idx} className="p-3 rounded-2xl bg-black/05 dark:bg-white/[0.03] border border-border-subtle/60">
                      <div className="text-[10px] uppercase font-bold text-text-muted">{m.label}</div>
                      <div className="text-xs font-bold text-accent-lime font-mono mt-0.5">{m.value}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Modal Footer Actions */}
            <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-end gap-3">
              <button
                id="aboutModalCloseBottomBtn"
                onClick={() => setActiveModal(null)}
                className="px-4 py-2 rounded-xl glass-subtle border border-border-subtle text-xs font-semibold text-text-secondary hover:text-text-primary cursor-pointer"
              >
                {t('about_modal_close')}
              </button>
              {activeModal.actionRoute && (
                <button
                  onClick={() => {
                    const route = activeModal.actionRoute!;
                    setActiveModal(null);
                    onNavigate?.(route);
                  }}
                  className="px-4 py-2 rounded-xl bg-accent-lime text-black font-semibold text-xs hover:bg-accent-lime/90 active:scale-95 transition-all shadow-glow-lime flex items-center gap-1.5 cursor-pointer"
                >
                  <span>{activeModal.actionText || 'Proceed'}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
