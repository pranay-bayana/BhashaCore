import React, { useEffect, useState } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { FailureItem } from '@/types/api';
import { fetchFailures } from '@/services/api';
import {
  AlertTriangle,
  Filter,
  Loader2,
  CheckCircle2,
  XCircle,
  Search,
  FileQuestion,
  Sparkles,
  ShieldAlert
} from 'lucide-react';

export const FailureAnalysisView: React.FC = () => {
  const { t } = useLanguage();
  const [failures, setFailures] = useState<FailureItem[]>([]);
  const [totalMatching, setTotalMatching] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedLang, setSelectedLang] = useState<string>('all');
  const [selectedMode, setSelectedMode] = useState<string>('all');
  const [filterQuery, setFilterQuery] = useState('');

  const loadFailures = async () => {
    setLoading(true);
    const result = await fetchFailures(selectedLang, selectedMode, 100);
    if (result) {
      setFailures(result.failures || []);
      setTotalMatching(result.total_matching || 0);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadFailures();
  }, [selectedLang, selectedMode]);

  const filteredFailures = failures.filter(f => {
    if (!filterQuery.trim()) return true;
    const q = filterQuery.toLowerCase();
    return (
      (f.question && f.question.toLowerCase().includes(q)) ||
      (f.gloss_question && f.gloss_question.toLowerCase().includes(q)) ||
      (f.answer && f.answer.toLowerCase().includes(q)) ||
      (f.qid && f.qid.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-text-primary tracking-tight flex items-center gap-2.5">
            <AlertTriangle className="w-6 h-6 text-amber-500" />
            <span>{t('failure_heading') || 'Empirical Failure Analysis'}</span>
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary mt-1 max-w-2xl">
            {t('failure_subheading') || 'Analyzing instances where generation correctness scored ≤ 3 due to hallucinations, retrieval misses, or script drift.'}
          </p>
        </div>

        <div className="text-xs text-text-muted font-medium self-start sm:self-auto bg-black/05 dark:bg-white/05 px-3 py-1.5 rounded-xl border border-border-subtle">
          {t('failure_showing_count', { filtered: filteredFailures.length, total: totalMatching }) ||
            `Showing ${filteredFailures.length} of ${totalMatching} failure cases`}
        </div>
      </div>

      {/* 2. Filter Controls Bar */}
      <div className="glass-panel p-4 sm:p-5 rounded-3xl border border-border-subtle flex flex-wrap items-center justify-between gap-4 shadow-glass-sm">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-text-muted mr-1 font-semibold">
            <Filter className="w-3.5 h-3.5" />
            <span>{t('failure_filter_label') || 'Filter:'}</span>
          </div>

          {/* Hidden select element for legacy test automation compatibility */}
          <select
            id="langFilter"
            aria-label="Filter language"
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            className="sr-only"
          >
            <option value="all">all</option>
            <option value="hi">hi</option>
            <option value="te">te</option>
            <option value="ta">ta</option>
            <option value="kn">kn</option>
            <option value="ml">ml</option>
            <option value="en">en</option>
          </select>

          {/* Language selector buttons */}
          {['all', 'hi', 'te', 'ta', 'kn', 'ml', 'en'].map(l => (
            <button
              key={l}
              onClick={() => setSelectedLang(l)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors ${
                selectedLang === l
                  ? 'bg-accent-lime-surface border-accent-lime/40 text-accent-lime font-bold shadow-sm'
                  : 'glass-subtle border-border-subtle text-text-secondary hover:text-text-primary'
              }`}
            >
              {l === 'all' ? (t('failure_all_languages') || 'All Languages') : l.toUpperCase()}
            </button>
          ))}

          {/* Mode selector buttons */}
          <div className="h-4 w-px bg-border-subtle mx-1 hidden sm:block" />
          {['all', 'rag', 'closed_book', 'gold_context', 'rag_translit'].map(m => (
            <button
              key={m}
              onClick={() => setSelectedMode(m)}
              className={`px-2.5 py-1.5 rounded-xl text-xs font-mono transition-colors ${
                selectedMode === m
                  ? 'bg-accent-emerald-surface border border-accent-emerald/40 text-accent-emerald font-bold'
                  : 'glass-subtle border border-border-subtle text-text-muted hover:text-text-primary'
              }`}
            >
              {m === 'all' ? (t('failure_all_modes') || 'All Modes') : m}
            </button>
          ))}
        </div>

        {/* Search query input */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            placeholder={t('failure_search_placeholder') || 'Search questions or keywords…'}
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="w-full bg-black/05 dark:bg-white/[0.04] border border-border-subtle rounded-xl pl-9 pr-3 py-1.5 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-lime transition-colors"
          />
        </div>
      </div>

      {/* 3. Failure Cases Feed */}
      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-3 text-text-muted">
          <Loader2 className="w-8 h-8 animate-spin text-accent-lime" />
          <span className="text-sm">{t('loading') || 'Retrieving failure cases…'}</span>
        </div>
      ) : filteredFailures.length === 0 ? (
        <div className="glass-panel rounded-3xl p-12 text-center text-text-muted space-y-2 border border-border-subtle">
          <CheckCircle2 className="w-8 h-8 text-accent-emerald mx-auto" />
          <p className="text-sm">{t('failure_no_matches') || 'No failure cases match the selected filter criteria.'}</p>
        </div>
      ) : (
        <div id="results" className="grid grid-cols-1 gap-4">
          {filteredFailures.map((item, idx) => (
            <div
              key={item.qid || idx}
              className="failure-item-card glass-panel rounded-3xl p-5 sm:p-6 border border-border-subtle hover:border-accent-lime/30 transition-all space-y-4 shadow-glass-sm"
            >
              {/* Card Top Metadata Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle pb-3">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-accent-lime-surface border border-accent-lime/30 text-[11px] font-bold text-accent-lime">
                    {item.lang ? item.lang.toUpperCase() : 'UNKNOWN'}
                  </span>
                  <span className="text-xs font-mono text-text-muted">
                    Mode: <strong className="text-text-primary font-medium">{item.mode}</strong>
                  </span>
                  <span className="text-xs font-mono text-text-muted">
                    QID: {item.qid}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="text-text-muted">{t('failure_score_label') || 'Correctness'}:</span>
                    <span className={`px-2 py-0.5 rounded-md font-mono font-bold text-xs ${
                      item.correctness <= 1
                        ? 'bg-red-500/10 text-red-500 border border-red-500/20'
                        : item.correctness <= 2
                        ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                        : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                    }`}>
                      {item.correctness} / 5
                    </span>
                  </div>

                  {item.retrieved_hit !== undefined && (
                    <div className="flex items-center gap-1 text-[11px] font-medium">
                      {item.retrieved_hit ? (
                        <span className="text-accent-emerald flex items-center gap-0.5">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Hit
                        </span>
                      ) : (
                        <span className="text-red-500 flex items-center gap-0.5">
                          <XCircle className="w-3.5 h-3.5" /> Miss
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Question & Gloss */}
              <div className="space-y-1">
                <div className="text-[10px] font-semibold text-text-muted uppercase tracking-wider">
                  {t('failure_q_label') || 'Question'}
                </div>
                <div className="text-sm font-semibold text-text-primary break-words">
                  {item.question}
                </div>
                {item.gloss_question && (
                  <div className="text-xs text-text-muted italic break-words">
                    {t('failure_gloss_label') || 'English Translation'}: {item.gloss_question}
                  </div>
                )}
              </div>

              {/* Model Generated Output vs Expected Gold Reference */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                {/* Generated response */}
                <div className="bg-red-500/05 dark:bg-red-500/10 p-4 rounded-2xl border border-red-500/20 space-y-1.5">
                  <div className="text-[10px] font-bold text-red-500 uppercase tracking-wider flex items-center gap-1">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>{t('failure_model_ans_label') || 'Model Response (Failed)'}</span>
                  </div>
                  <div className="text-xs text-text-secondary leading-relaxed break-words">
                    {item.answer || '—'}
                  </div>
                  {item.gloss_answer && (
                    <div className="text-[11px] text-text-muted italic pt-1 border-t border-red-500/15 break-words">
                      {t('failure_gloss_label') || 'Gloss'}: {item.gloss_answer}
                    </div>
                  )}
                </div>

                {/* Expected reference */}
                <div className="bg-accent-emerald-surface p-4 rounded-2xl border border-accent-emerald/20 space-y-1.5">
                  <div className="text-[10px] font-bold text-accent-emerald uppercase tracking-wider flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{t('failure_gold_ref_label') || 'Expected Reference'}</span>
                  </div>
                  <div className="text-xs text-text-secondary leading-relaxed break-words">
                    {item.gloss_reference || item.reference || '—'}
                  </div>
                </div>
              </div>

              {/* Failure Root Causes Tags */}
              {item.issues && item.issues.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-[10px] text-text-muted font-medium mr-1">
                    {t('failure_category_label') || 'Failure Mode'}:
                  </span>
                  {item.issues.map((iss, ii) => (
                    <span
                      key={ii}
                      className="px-2.5 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-semibold"
                    >
                      {iss}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
