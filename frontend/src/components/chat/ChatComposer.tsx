import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { LanguageCode, SUPPORTED_LANGUAGES } from '@/types/api';
import {
  Send,
  Square,
  Paperclip,
  Mic,
  RotateCcw,
  Sparkles,
  ChevronDown
} from 'lucide-react';

interface ChatComposerProps {
  onSendMessage: (
    question: string,
    options: { inputLang: string; inputStyle: string; answerLang: string | null; answerScript: string }
  ) => void;
  onStop: () => void;
  onRetry?: () => void;
  isStreaming: boolean;
  disabled?: boolean;
  isGuestQuotaReached?: boolean;
  onOpenAuthModal?: () => void;
  activeSessionId?: string;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
  onSendMessage,
  onStop,
  onRetry,
  isStreaming,
  disabled = false,
  isGuestQuotaReached = false,
  onOpenAuthModal,
  activeSessionId,
}) => {
  const { t } = useLanguage();
  const [question, setQuestion] = useState('');
  const [inputLang, setInputLang] = useState<string>('auto');
  const [inputStyle, setInputStyle] = useState<string>('auto');
  const [answerLang, setAnswerLang] = useState<string>('auto');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isEffectivelyDisabled = disabled || isGuestQuotaReached;

  // Clear draft and auto-focus textarea when active conversation changes or new chat starts
  useEffect(() => {
    setQuestion('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '40px';
      if (!isEffectivelyDisabled) {
        textareaRef.current.focus();
      }
    }
  }, [activeSessionId, isEffectivelyDisabled]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(Math.max(scrollHeight, 40), 160)}px`;
    }
  }, [question]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!question.trim() || isStreaming || isEffectivelyDisabled) return;

    onSendMessage(question.trim(), {
      inputLang,
      inputStyle,
      answerLang: answerLang === 'auto' ? (inputLang === 'auto' ? null : inputLang) : answerLang,
      answerScript: 'native',
    });

    setQuestion('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '40px';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4">
      {/* Single Consolidated Language & Input Controls Bar */}
      <div className="flex items-center justify-between gap-2 px-1 mb-2 text-xs flex-wrap">
        {/* Horizontal Language Selection Pills */}
        <div className="horizontal-lang-bar flex items-center gap-1.5 flex-wrap overflow-x-auto py-0.5">
          <button
            type="button"
            data-lang="auto"
            aria-pressed={inputLang === 'auto' ? 'true' : 'false'}
            onClick={() => setInputLang('auto')}
            className={`lang-btn px-2.5 py-1 rounded-xl text-xs font-medium border transition-all flex items-center gap-1 shrink-0 cursor-pointer active:scale-95 ${
              inputLang === 'auto'
                ? 'bg-accent-lime-surface border-accent-lime/60 text-accent-lime font-semibold shadow-[0_0_12px_rgba(183,255,114,0.25)] ring-1 ring-accent-lime/40'
                : 'glass-subtle border-border-subtle text-text-secondary hover:text-text-primary hover:border-accent-lime/40'
            }`}
          >
            <Sparkles className="w-3 h-3 text-accent-lime" />
            <span>{t('auto_detect_label') || 'Auto-detect'}</span>
          </button>
          {SUPPORTED_LANGUAGES.map((l) => (
            <button
              key={l.code}
              type="button"
              data-lang={l.code}
              aria-pressed={inputLang === l.code ? 'true' : 'false'}
              onClick={() => setInputLang(l.code)}
              className={`lang-btn px-2.5 py-1 rounded-xl text-xs font-medium border transition-all flex items-center gap-1 shrink-0 cursor-pointer active:scale-95 ${
                inputLang === l.code
                  ? 'bg-accent-lime-surface border-accent-lime/60 text-accent-lime font-semibold shadow-[0_0_12px_rgba(183,255,114,0.25)] ring-1 ring-accent-lime/40'
                  : 'glass-subtle border-border-subtle text-text-secondary hover:text-text-primary hover:border-accent-lime/40'
              }`}
            >
              <span>{l.nativeName}</span>
              <span className="lang-sub-code font-mono text-[9px] text-text-muted font-bold opacity-80">
                {l.code.toUpperCase()}
              </span>
            </button>
          ))}
        </div>

        {/* Script Style Selector & Retry */}
        <div className="flex items-center gap-2 shrink-0 ml-auto">
          <div className="inline-flex rounded-xl glass-subtle border border-border-subtle p-0.5 text-[11px]">
            <button
              type="button"
              onClick={() => setInputStyle('auto')}
              className={`px-2 py-0.5 rounded-lg transition-all cursor-pointer active:scale-95 ${
                inputStyle === 'auto'
                  ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-xs'
                  : 'text-text-muted hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
              }`}
            >
              Auto
            </button>
            <button
              type="button"
              onClick={() => setInputStyle('native')}
              className={`px-2 py-0.5 rounded-lg transition-all cursor-pointer active:scale-95 ${
                inputStyle === 'native'
                  ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-xs'
                  : 'text-text-muted hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
              }`}
            >
              Native
            </button>
            <button
              type="button"
              onClick={() => setInputStyle('romanized')}
              className={`px-2 py-0.5 rounded-lg transition-all cursor-pointer active:scale-95 ${
                inputStyle === 'romanized'
                  ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-xs'
                  : 'text-text-muted hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
              }`}
            >
              Romanized
            </button>
          </div>

          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="p-1.5 rounded-xl glass-subtle border border-border-subtle text-text-muted hover:text-text-primary hover:border-accent-lime/40 cursor-pointer active:scale-95 transition-all"
              title="Retry last question"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Guest Trial Limit Banner */}
      {isGuestQuotaReached && (
        <div className="flex items-center justify-between px-4 py-2 rounded-2xl glass-elevated border border-accent-lime/40 text-xs text-text-primary mb-2 shadow-sm animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent-lime shrink-0" />
            <span className="font-medium text-text-secondary">
              {t('guest_limit_composer_placeholder') || 'Trial limit reached (3/3) · Sign in to continue asking questions'}
            </span>
          </div>
          {onOpenAuthModal && (
            <button
              type="button"
              id="composerGuestSignInBtn"
              onClick={onOpenAuthModal}
              className="font-bold text-accent-lime hover:underline ml-2 shrink-0 flex items-center gap-1"
            >
              <span>{t('auth_sign_in') || 'Sign In'}</span>
              <span>→</span>
            </button>
          )}
        </div>
      )}

      {/* Main Composer Capsule */}
      <div className={`composer-capsule relative glass-panel rounded-3xl border border-border-subtle p-2 shadow-glass-lg ${
        isEffectivelyDisabled
          ? 'opacity-80'
          : 'focus-within:border-accent-lime/60 focus-within:ring-2 focus-within:ring-accent-lime/25 shadow-glass-elevated'
      } transition-all duration-200`}>
        <form onSubmit={handleSubmit} className="flex items-end gap-2">
          {/* Attachment Icon */}
          <button
            type="button"
            disabled={isEffectivelyDisabled}
            className="p-2.5 rounded-2xl glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-text-muted hover:text-text-primary hover:border-accent-lime/30 cursor-pointer active:scale-95 transition-all shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Attach document (Corpus RAG)"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          {/* Multiline Textarea */}
          <textarea
            id="questionInput"
            ref={textareaRef}
            rows={1}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isEffectivelyDisabled}
            placeholder={
              isGuestQuotaReached
                ? (t('guest_limit_composer_placeholder') || 'Trial limit reached (3/3) · Sign in to continue asking questions')
                : (t('chat_input_placeholder') || 'Type your question here...')
            }
            className="flex-1 bg-transparent border-none outline-none resize-none py-2 px-1 text-sm text-text-primary placeholder:text-text-muted leading-relaxed max-h-40 overflow-y-auto disabled:cursor-not-allowed"
          />

          {/* Microphone Icon */}
          <button
            type="button"
            disabled={isEffectivelyDisabled}
            className="p-2.5 rounded-2xl glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-text-muted hover:text-text-primary hover:border-accent-lime/30 cursor-pointer active:scale-95 transition-all shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>

          {/* Stop / Send Button */}
          {isStreaming ? (
            <button
              id="stopBtn"
              type="button"
              onClick={onStop}
              className="w-10 h-10 rounded-2xl bg-red-500/20 border border-red-500/40 text-red-500 hover:bg-red-500/30 cursor-pointer active:scale-95 flex items-center justify-center transition-all shrink-0"
              title="Stop generation"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          ) : null}

          {/* Permanent Send Button */}
          <button
            id="sendBtn"
            type="submit"
            disabled={isStreaming || isEffectivelyDisabled}
            style={isStreaming ? { display: 'none' } : undefined}
            className="w-10 h-10 rounded-2xl btn-lime-glass flex items-center justify-center transition-all cursor-pointer active:scale-95 hover:scale-105 disabled:opacity-40 disabled:cursor-not-allowed shrink-0 shadow-sm"
            title="Send message (Enter)"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Sub-composer Hint */}
      <div className="text-center mt-2 text-[11px] text-text-muted">
        {t('chat_hint') || 'Enter sends · Shift+Enter adds a newline · grounded in IndicQA + IndicCorp v2 corpus'}
      </div>
    </div>
  );
};
