import React, { useEffect, useState } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { DashboardData } from '@/types/api';
import { fetchDashboard } from '@/services/api';
import {
  BarChart3,
  CheckCircle2,
  AlertOctagon,
  Layers,
  Database,
  Cpu,
  Loader2,
  RefreshCw,
  Info
} from 'lucide-react';

export const ResearchDashboardView: React.FC = () => {
  const { t } = useLanguage();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    const result = await fetchDashboard();
    setData(result);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3 text-text-muted">
        <Loader2 className="w-8 h-8 animate-spin text-accent-lime" />
        <span className="text-sm">{t('dashboard_loading') || 'Loading empirical evaluation metrics…'}</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center max-w-lg mx-auto space-y-4">
        <AlertOctagon className="w-10 h-10 text-amber-500 mx-auto" />
        <h3 className="text-lg font-bold text-text-primary">{t('dashboard_unavailable') || 'Evaluation Data Unavailable'}</h3>
        <p className="text-sm text-text-secondary">
          {t('dashboard_error_desc') || 'Could not load the research benchmark dataset from the backend service.'}
        </p>
        <button onClick={loadData} className="btn-ghost-glass px-4 py-2 text-xs rounded-xl">
          {t('retry') || 'Retry'}
        </button>
      </div>
    );
  }

  const counts = data.counts || { judged: 0, failures: 0, languages: 0, retrieval_rows: 0 };
  const languagesList = Object.keys(data.by_language || {});

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      {/* 1. Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-text-primary tracking-tight flex items-center gap-2.5">
            <BarChart3 className="w-6 h-6 text-accent-lime" />
            <span>{t('nav_dashboard') || 'Multilingual Benchmark Dashboard'}</span>
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary mt-1 max-w-2xl">
            {t('dashboard_eyebrow') || 'Empirical accuracy, faithfulness, and hallucination rates evaluated across IndicQA contexts.'}
          </p>
        </div>

        <button
          onClick={loadData}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-xs font-medium text-text-secondary hover:text-text-primary transition-colors self-start sm:self-auto border border-border-subtle"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>{t('refresh') || 'Refresh'}</span>
        </button>
      </div>

      {/* 2. Structured KPI Overview: Refined Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl space-y-2 border border-border-subtle shadow-glass-sm">
          <div className="flex items-center justify-between text-text-muted">
            <span className="text-xs font-medium uppercase tracking-wider">{t('stat_judged_queries') || 'Judged Queries'}</span>
            <CheckCircle2 className="w-4 h-4 text-accent-emerald" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">{counts.judged}</div>
          <div className="text-[11px] text-text-muted">{t('stat_judged_desc') || 'Multi-turn evaluation samples'}</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-2 border border-border-subtle shadow-glass-sm">
          <div className="flex items-center justify-between text-text-muted">
            <span className="text-xs font-medium uppercase tracking-wider">{t('stat_failures') || 'Identified Failures'}</span>
            <AlertOctagon className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-500 tracking-tight">{counts.failures}</div>
          <div className="text-[11px] text-text-muted">{t('stat_failures_desc') || 'Score ≤ 3 (hallucination / retrieval gap)'}</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-2 border border-border-subtle shadow-glass-sm">
          <div className="flex items-center justify-between text-text-muted">
            <span className="text-xs font-medium uppercase tracking-wider">{t('stat_indian_languages') || 'Languages'}</span>
            <Layers className="w-4 h-4 text-accent-lime" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-accent-lime tracking-tight">{counts.languages || 6}</div>
          <div className="text-[11px] text-text-muted">EN, HI, TE, TA, KN, ML</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-2 border border-border-subtle shadow-glass-sm">
          <div className="flex items-center justify-between text-text-muted">
            <span className="text-xs font-medium uppercase tracking-wider">{t('stat_corpus') || 'Retrieval Corpus'}</span>
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-cyan-500 tracking-tight">IndicCorp v2</div>
          <div className="text-[11px] text-text-muted">{t('stat_corpus_desc') || 'BM25 index across 6 languages'}</div>
        </div>
      </div>

      {/* 3. Models & Benchmark Provenance Metadata */}
      <div className="glass-panel p-4 rounded-2xl border border-border-subtle flex flex-wrap items-center justify-between gap-4 text-xs shadow-glass-sm">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-accent-lime shrink-0" />
          <span className="text-text-muted font-medium">{t('label_generator') || 'Active Generator'}:</span>
          <span className="font-mono font-semibold text-text-primary">{data.generator_active || data.generator}</span>
        </div>
        {data.judge_model && (
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-accent-emerald shrink-0" />
            <span className="text-text-muted font-medium">{t('label_judge') || 'Judge Evaluator'}:</span>
            <span className="font-mono font-semibold text-text-primary">{data.judge_model}</span>
          </div>
        )}
      </div>

      {/* 4. Detailed Results Matrix: Mode Performance by Language */}
      <div className="glass-panel rounded-3xl border border-border-subtle overflow-hidden shadow-glass-md">
        <div className="p-5 border-b border-border-subtle bg-black/[0.01] dark:bg-white/[0.01]">
          <h3 className="text-sm font-bold text-text-primary tracking-tight">
            {t('dashboard_mode_performance_title') || 'Mode Performance by Language'}
          </h3>
          <p className="text-xs text-text-muted mt-0.5">
            {t('dashboard_mode_performance_desc') || 'Correctness (1–5 scale), Faithfulness (1–5 scale), Script Purity, and F1 Token Overlap.'}
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border-subtle text-text-muted uppercase tracking-wider bg-black/[0.01] dark:bg-white/[0.01] font-semibold">
                <th className="py-3.5 px-4">{t('table_col_lang') || 'Language'}</th>
                <th className="py-3.5 px-4">{t('table_col_mode') || 'Mode'}</th>
                <th className="py-3.5 px-4">{t('table_col_samples') || 'Samples (N)'}</th>
                <th className="py-3.5 px-4">{t('table_col_correctness') || 'Correctness (/5)'}</th>
                <th className="py-3.5 px-4">{t('table_col_faithfulness') || 'Faithfulness (/5)'}</th>
                <th className="py-3.5 px-4">{t('table_col_purity') || 'Purity'}</th>
                <th className="py-3.5 px-4">{t('table_col_f1') || 'F1 Score'}</th>
                <th className="py-3.5 px-4">{t('table_col_em') || 'Exact Match'}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {languagesList.map((lang) => {
                const modes = data.by_language[lang] || {};
                return Object.entries(modes).map(([mode, metrics], mi) => (
                  <tr key={`${lang}-${mode}`} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors">
                    {mi === 0 ? (
                      <td
                        rowSpan={Object.keys(modes).length}
                        className="py-3 px-4 font-bold text-accent-lime border-r border-border-subtle align-top bg-black/[0.01] dark:bg-white/[0.01]"
                      >
                        {lang.toUpperCase()}
                      </td>
                    ) : null}
                    <td className="py-3 px-4 font-mono text-text-secondary">{mode}</td>
                    <td className="py-3 px-4 text-text-muted font-mono">{metrics.n}</td>
                    <td className="py-3 px-4 font-semibold font-mono">
                      {metrics.correctness !== null ? (
                        <span className={metrics.correctness >= 4 ? 'text-accent-emerald font-bold' : metrics.correctness >= 3 ? 'text-accent-lime font-bold' : 'text-amber-500 font-bold'}>
                          {metrics.correctness.toFixed(2)}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-mono">
                      {metrics.faithfulness !== null ? metrics.faithfulness.toFixed(2) : '—'}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-mono">
                      {metrics.purity !== null ? `${(metrics.purity * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-mono">
                      {metrics.f1 !== null ? (metrics.f1).toFixed(3) : '—'}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-mono">
                      {metrics.em !== null ? (metrics.em).toFixed(3) : '—'}
                    </td>
                  </tr>
                ));
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
