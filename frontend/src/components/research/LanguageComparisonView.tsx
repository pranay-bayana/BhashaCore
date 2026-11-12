import React, { useEffect, useState } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { ComparisonData, ComparisonLanguageRow } from '@/types/api';
import { fetchComparison } from '@/services/api';
import {
  GitCompare,
  Loader2,
  RefreshCw,
  AlertCircle,
  ArrowUpRight,
  Layers,
  Database,
  Info
} from 'lucide-react';

interface TooltipInfo {
  x: number;
  y: number;
  lang: string;
  langName: string;
  mode: string;
  score: number | null;
  delta?: string | null;
}

export const LanguageComparisonView: React.FC = () => {
  const { t } = useLanguage();
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTooltip, setActiveTooltip] = useState<TooltipInfo | null>(null);

  const loadData = async () => {
    setLoading(true);
    const result = await fetchComparison();
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
        <span className="text-sm">{t('comparison_loading') || 'Loading cross-lingual evaluation benchmarks…'}</span>
      </div>
    );
  }

  if (!data || !data.languages) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center max-w-lg mx-auto space-y-4">
        <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
        <h3 className="text-lg font-bold text-text-primary">{t('comparison_unavailable') || 'Comparison Data Unavailable'}</h3>
        <p className="text-sm text-text-secondary">
          {t('comparison_error_desc') || 'Could not fetch cross-language evaluation metrics from the API service.'}
        </p>
        <button onClick={loadData} className="btn-ghost-glass px-4 py-2 text-xs rounded-xl">
          {t('retry') || 'Retry'}
        </button>
      </div>
    );
  }

  const languages = data.languages;

  // Chart dimensions & calculations
  const maxScore = 5.0;
  const chartHeight = 220;
  const barWidth = 14;
  const groupSpacing = 72;

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      {/* 1. Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-text-primary tracking-tight flex items-center gap-2.5">
            <GitCompare className="w-6 h-6 text-accent-emerald" />
            <span>{t('chart_generation_modes_title') || 'Cross-Language Generation Mode Comparison'}</span>
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary mt-1 max-w-2xl">
            {t('chart_generation_modes_desc') || 'Evaluating Closed-Book vs. RAG Grounded vs. Gold Context correctness across 6 languages (/5.0)'}
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

      {/* 2. Professional Interactive Grouped Bar Chart */}
      <div className="glass-panel p-6 sm:p-7 rounded-3xl border border-border-subtle shadow-glass-md relative">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border-subtle pb-4 mb-6">
          <div>
            <h3 className="text-sm font-bold text-text-primary">
              {t('chart_generation_modes_title') || 'Cross-Language Generation Mode Comparison'}
            </h3>
            <p className="text-xs text-text-muted mt-0.5">
              Empirical LLM correctness scores on IndicQA benchmark (0.0 to 5.0 scale)
            </p>
          </div>

          {/* Chart Legend */}
          <div className="flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-slate-500/80" />
              <span className="text-text-secondary">{t('chart_legend_closed_book') || 'Closed Book'}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-accent-lime shadow-[0_0_8px_rgba(183,255,114,0.4)]" />
              <span className="text-text-primary font-medium">{t('chart_legend_rag') || 'RAG Grounded'}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-cyan-400" />
              <span className="text-text-secondary">{t('chart_legend_gold') || 'Gold Context'}</span>
            </div>
          </div>
        </div>

        {/* SVG Grouped Bar Visualization */}
        <div className="w-full overflow-x-auto pb-4">
          <div className="min-w-[620px] relative">
            <svg viewBox="0 0 620 280" className="w-full h-64 overflow-visible font-sans">
              {/* Y-Axis Grid Lines & Labels */}
              {[0, 1, 2, 3, 4, 5].map((tick) => {
                const y = chartHeight - (tick / maxScore) * chartHeight + 20;
                const isThreshold = tick === 3;
                return (
                  <g key={tick}>
                    <line
                      x1="45"
                      y1={y}
                      x2="600"
                      y2={y}
                      stroke="currentColor"
                      className={isThreshold ? 'text-accent-lime/40 stroke-dashed' : 'text-border-subtle opacity-40'}
                      strokeWidth={isThreshold ? '1.5' : '1'}
                      strokeDasharray={isThreshold ? '4,4' : undefined}
                    />
                    <text
                      x="35"
                      y={y + 4}
                      textAnchor="end"
                      className={`text-[10px] font-mono ${isThreshold ? 'fill-accent-lime font-bold' : 'fill-text-muted'}`}
                    >
                      {tick}.0
                    </text>
                    {isThreshold && (
                      <text x="605" y={y + 3} className="text-[9px] fill-accent-lime font-mono">
                        threshold (3.0)
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Grouped Bars per Language */}
              {languages.map((row, groupIndex) => {
                const groupX = 65 + groupIndex * (groupSpacing + 16);
                const closedScore = row.closed_book || 0;
                const ragScore = row.rag || 0;
                const goldScore = row.gold_context || 0;

                const closedHeight = (closedScore / maxScore) * chartHeight;
                const ragHeight = (ragScore / maxScore) * chartHeight;
                const goldHeight = (goldScore / maxScore) * chartHeight;

                const closedY = chartHeight - closedHeight + 20;
                const ragY = chartHeight - ragHeight + 20;
                const goldY = chartHeight - goldHeight + 20;

                const delta = row.rag && row.closed_book ? (row.rag - row.closed_book).toFixed(2) : null;

                return (
                  <g key={row.lang} className="transition-all">
                    {/* Closed Book Bar */}
                    <rect
                      x={groupX}
                      y={closedY}
                      width={barWidth}
                      height={closedHeight}
                      rx="3"
                      className="fill-slate-500/80 hover:fill-slate-400 cursor-pointer transition-colors"
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setActiveTooltip({
                          x: rect.left + rect.width / 2,
                          y: rect.top - 8,
                          lang: row.lang.toUpperCase(),
                          langName: row.name,
                          mode: t('chart_legend_closed_book') || 'Closed Book',
                          score: row.closed_book,
                        });
                      }}
                      onMouseLeave={() => setActiveTooltip(null)}
                    />

                    {/* RAG Grounded Bar (Highlighted) */}
                    <rect
                      x={groupX + barWidth + 3}
                      y={ragY}
                      width={barWidth}
                      height={ragHeight}
                      rx="3"
                      className="fill-accent-lime hover:opacity-90 cursor-pointer transition-colors filter drop-shadow-[0_0_6px_rgba(183,255,114,0.35)]"
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setActiveTooltip({
                          x: rect.left + rect.width / 2,
                          y: rect.top - 8,
                          lang: row.lang.toUpperCase(),
                          langName: row.name,
                          mode: t('chart_legend_rag') || 'RAG Grounded',
                          score: row.rag,
                          delta: delta ? `+${delta}` : null,
                        });
                      }}
                      onMouseLeave={() => setActiveTooltip(null)}
                    />

                    {/* Gold Context Bar */}
                    <rect
                      x={groupX + (barWidth + 3) * 2}
                      y={goldY}
                      width={barWidth}
                      height={goldHeight}
                      rx="3"
                      className="fill-cyan-400 hover:fill-cyan-300 cursor-pointer transition-colors"
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setActiveTooltip({
                          x: rect.left + rect.width / 2,
                          y: rect.top - 8,
                          lang: row.lang.toUpperCase(),
                          langName: row.name,
                          mode: t('chart_legend_gold') || 'Gold Context',
                          score: row.gold_context,
                        });
                      }}
                      onMouseLeave={() => setActiveTooltip(null)}
                    />

                    {/* Language Label under group */}
                    <text
                      x={groupX + barWidth * 1.5 + 3}
                      y={chartHeight + 42}
                      textAnchor="middle"
                      className="text-xs font-bold fill-text-primary"
                    >
                      {row.name}
                    </text>
                    <text
                      x={groupX + barWidth * 1.5 + 3}
                      y={chartHeight + 56}
                      textAnchor="middle"
                      className="text-[10px] font-mono fill-text-muted"
                    >
                      {row.lang.toUpperCase()}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </div>

        {/* Floating Tooltip */}
        {activeTooltip && (
          <div
            className="fixed z-50 pointer-events-none -translate-x-1/2 -translate-y-full glass-elevated px-3 py-2 rounded-xl border border-accent-lime/40 shadow-glass-lg text-xs"
            style={{ left: activeTooltip.x, top: activeTooltip.y }}
          >
            <div className="font-bold text-text-primary flex items-center gap-1.5">
              <span>{activeTooltip.langName}</span>
              <span className="text-[10px] text-accent-lime font-mono">({activeTooltip.lang})</span>
            </div>
            <div className="text-text-secondary text-[11px] mt-0.5">
              {activeTooltip.mode}: <span className="font-bold text-text-primary">{activeTooltip.score?.toFixed(2)}</span>
            </div>
            {activeTooltip.delta && (
              <div className="text-accent-emerald text-[10px] font-medium flex items-center gap-0.5 mt-0.5">
                <ArrowUpRight className="w-3 h-3" />
                <span>RAG Uplift: {activeTooltip.delta}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 3. Retrieval Recall & Transliteration Gap Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-3xl border border-border-subtle space-y-4 shadow-glass-md">
          <div>
            <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>{t('chart_retrieval_title') || 'Retrieval Performance & Transliteration Gap'}</span>
            </h3>
            <p className="text-xs text-text-muted mt-1">
              {t('chart_retrieval_desc') || 'Recall@5 comparing Native Script queries against Romanized inputs without bridging'}
            </p>
          </div>

          <div className="space-y-4 pt-2">
            {languages.map((row) => {
              const nativeVal = (row.recall_native || 0) * 100;
              const romanizedVal = row.recall_romanized !== null ? row.recall_romanized * 100 : null;

              return (
                <div key={row.lang} className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-text-primary flex items-center gap-1.5">
                      <span>{row.name}</span>
                      <span className="text-[10px] font-mono text-text-muted">({row.lang.toUpperCase()})</span>
                    </span>
                    <div className="flex items-center gap-3 text-xs font-mono">
                      <span className="text-cyan-400 font-bold" title="Native Script Recall@5">
                        Native: {nativeVal.toFixed(1)}%
                      </span>
                      {romanizedVal !== null ? (
                        <span className="text-amber-500 font-medium" title="Romanized Input Recall@5">
                          Romanized: {romanizedVal.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-text-muted text-[11px]">N/A (Latin script)</span>
                      )}
                    </div>
                  </div>

                  {/* Dual Bar (Native vs Romanized) */}
                  <div className="space-y-1">
                    <div className="w-full h-2 rounded-full bg-black/05 dark:bg-white/05 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-cyan-400 transition-all duration-500"
                        style={{ width: `${nativeVal}%` }}
                      />
                    </div>
                    {romanizedVal !== null && (
                      <div className="w-full h-1.5 rounded-full bg-black/05 dark:bg-white/05 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-amber-500 transition-all duration-500"
                          style={{ width: `${Math.max(romanizedVal, 1)}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-2 border-t border-border-subtle flex items-center gap-4 text-[11px] text-text-muted">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400" />
              <span>Native Script Recall@5</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-amber-500" />
              <span>Romanized Without Bridging</span>
            </div>
          </div>
        </div>

        {/* 4. Research Insight Card */}
        <div className="glass-panel p-6 rounded-3xl border border-border-subtle space-y-4 flex flex-col justify-between shadow-glass-md">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-accent-lime text-xs font-bold uppercase tracking-wider">
              <Info className="w-4 h-4" />
              <span>Key Empirical Findings</span>
            </div>
            <h3 className="text-base font-bold text-text-primary">
              Why Multilingual RAG is Essential for Indian Languages
            </h3>
            <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
              In closed-book mode, foundation models suffer significant accuracy drops across Dravidian and Indo-Aryan languages (scores as low as 2.10/5.0 in Tamil).
            </p>
            <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
              When grounded in <strong className="text-text-primary">IndicCorp v2</strong> via BM25, answer correctness increases by <strong className="text-accent-lime font-bold">+0.66 to +1.32 points</strong> across all evaluated Indian languages.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-accent-lime-surface border border-accent-lime/20 space-y-1.5">
            <div className="text-xs font-bold text-accent-lime">The Romanization Penalty</div>
            <p className="text-xs text-text-secondary leading-relaxed">
              Without algorithmic transliteration bridging, Romanized queries suffer near-total retrieval collapse (1.0% in Hindi), causing immediate hallucinations.
            </p>
          </div>
        </div>
      </div>

      {/* 5. Complete, Refined Data Table */}
      <div className="glass-panel rounded-3xl border border-border-subtle overflow-hidden shadow-glass-md">
        <div className="p-5 border-b border-border-subtle bg-black/[0.01] dark:bg-white/[0.01]">
          <h3 className="text-sm font-bold text-text-primary">
            {t('table_generation_comparison') || 'Generation Mode Comparison (Correctness / 5.0)'}
          </h3>
          <p className="text-xs text-text-muted mt-0.5">
            {t('table_generation_desc') || 'Demonstrates how RAG bridges the resource disparity across Indian languages.'}
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border-subtle text-text-muted uppercase tracking-wider font-semibold">
                <th className="py-3 px-4">{t('table_col_lang') || 'Language'}</th>
                <th className="py-3 px-4">{t('table_col_script') || 'Script'}</th>
                <th className="py-3 px-4">{t('table_col_closed_book') || 'Closed Book'}</th>
                <th className="py-3 px-4">{t('table_col_rag') || 'RAG Grounded'}</th>
                <th className="py-3 px-4">{t('table_col_gold') || 'Gold Context'}</th>
                <th className="py-3 px-4">{t('table_col_translit') || 'RAG Translit'}</th>
                <th className="py-3 px-4">{t('table_col_recall_native') || 'Recall@5 (Native)'}</th>
                <th className="py-3 px-4">{t('table_col_recall_romanized') || 'Recall@5 (Romanized)'}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {languages.map((row) => {
                const ragGain = row.rag && row.closed_book ? (row.rag - row.closed_book).toFixed(2) : null;

                return (
                  <tr key={row.lang} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-bold text-text-primary">
                      <span>{row.name}</span>
                      <span className="ml-1.5 text-[10px] text-accent-lime font-mono">({row.lang.toUpperCase()})</span>
                    </td>
                    <td className="py-3.5 px-4 text-text-secondary">{row.script}</td>
                    <td className="py-3.5 px-4 text-text-muted font-mono">
                      {row.closed_book !== null ? row.closed_book.toFixed(2) : '—'}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-accent-lime font-mono">
                      <div className="flex items-center gap-1.5">
                        <span>{row.rag !== null ? row.rag.toFixed(2) : '—'}</span>
                        {ragGain && parseFloat(ragGain) > 0 && (
                          <span className="text-[10px] text-accent-emerald flex items-center font-normal">
                            <ArrowUpRight className="w-3 h-3" />
                            +{ragGain}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-accent-emerald font-semibold font-mono">
                      {row.gold_context !== null ? row.gold_context.toFixed(2) : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-text-secondary font-mono">
                      {row.rag_translit !== null ? row.rag_translit.toFixed(2) : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-cyan-500 font-mono font-medium">
                      {row.recall_native !== null ? `${(row.recall_native * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-amber-500 font-mono font-medium">
                      {row.recall_romanized !== null ? `${(row.recall_romanized * 100).toFixed(1)}%` : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
