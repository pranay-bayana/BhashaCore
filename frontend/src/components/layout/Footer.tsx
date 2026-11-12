import React from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { Database, ShieldCheck, Cpu, Code2 } from 'lucide-react';

export const Footer: React.FC = () => {
  const { t } = useLanguage();

  return (
    <footer className="w-full border-t border-border-subtle bg-bg/90 backdrop-blur-md py-12 px-4 sm:px-6 lg:px-8 mt-auto transition-colors duration-200">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col items-center md:items-start gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[#B7FF72] to-[#36D69A] flex items-center justify-center text-[#050706] font-bold text-xs">
              B
            </div>
            <span className="font-bold text-sm text-text-primary tracking-tight">
              BhashaCore
            </span>
            <span className="text-xs text-text-muted">·</span>
            <span className="text-xs text-text-muted">
              {t('tagline') || 'multilingual RAG · research'}
            </span>
          </div>
          <p className="text-xs text-text-secondary text-center md:text-left max-w-md">
            {t('chat_disclaimer') || 'BhashaCore is a multilingual research chatbot. Answers are grounded in IndicQA + IndicCorp v2.'}
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-text-secondary">
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-accent-lime" />
            <span>{t('about_corpus_title') || 'IndicCorp v2 (AI4Bharat)'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-accent-emerald" />
            <span>{t('about_retrieval') || 'BM25 + RAG Grounding'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-accent-lime" />
            <span>{t('about_generator_evaluated') || 'Sarvam 105B'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Code2 className="w-3.5 h-3.5 text-text-muted" />
            <span>{t('about_run_it') || 'MIT Research Open License'}</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
