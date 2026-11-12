import React from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { ResearchDashboardView } from '@/components/research/ResearchDashboardView';
import { LanguageComparisonView } from '@/components/research/LanguageComparisonView';
import { FailureAnalysisView } from '@/components/research/FailureAnalysisView';
import { LayoutDashboard, GitCompare, AlertTriangle } from 'lucide-react';

interface ResearchPageProps {
  subRoute: 'dashboard' | 'comparison' | 'failures';
  onNavigateSubRoute: (subRoute: 'dashboard' | 'comparison' | 'failures') => void;
}

export const ResearchPage: React.FC<ResearchPageProps> = ({
  subRoute,
  onNavigateSubRoute,
}) => {
  const { t } = useLanguage();

  return (
    <div className="research-content-container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-300">
      {/* Sub-Navigation Tabs Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {t('research_hub_title') || 'Research Evaluation Workspace'}
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            {t('comparison_subtitle') || 'Empirical multilingual benchmarking on IndicQA and IndicCorp v2 corpus.'}
          </p>
        </div>

        {/* Tab Switcher Pills */}
        <div className="flex items-center gap-1.5 p-1 rounded-2xl glass-subtle border border-white/10 self-start sm:self-auto">
          <button
            onClick={() => onNavigateSubRoute('dashboard')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              subRoute === 'dashboard'
                ? 'bg-accent-lime/20 text-accent-lime border border-accent-lime/30 shadow-[0_0_12px_rgba(183,255,114,0.15)]'
                : 'text-text-secondary hover:text-white hover:bg-white/05'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>{t('nav_dashboard') || 'Dashboard'}</span>
          </button>

          <button
            onClick={() => onNavigateSubRoute('comparison')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              subRoute === 'comparison'
                ? 'bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30 shadow-[0_0_12px_rgba(54,214,154,0.15)]'
                : 'text-text-secondary hover:text-white hover:bg-white/05'
            }`}
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>{t('nav_comparison') || 'Language Comparison'}</span>
          </button>

          <button
            onClick={() => onNavigateSubRoute('failures')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              subRoute === 'failures'
                ? 'bg-amber-400/20 text-amber-300 border border-amber-400/30 shadow-[0_0_12px_rgba(251,191,36,0.15)]'
                : 'text-text-secondary hover:text-white hover:bg-white/05'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{t('nav_failures') || 'Failure Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      <main>
        {subRoute === 'dashboard' && <ResearchDashboardView />}
        {subRoute === 'comparison' && <LanguageComparisonView />}
        {subRoute === 'failures' && <FailureAnalysisView />}
      </main>
    </div>
  );
};
