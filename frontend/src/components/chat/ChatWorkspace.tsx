import React, { useRef, useEffect, useState } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { ChatMessage, SUPPORTED_LANGUAGES } from '@/types/api';
import {
  Globe,
  Sparkles,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  BookOpen,
  MessageSquare,
  Cpu,
  Layers,
  Database,
  Plus
} from 'lucide-react';

interface ChatWorkspaceProps {
  messages: ChatMessage[];
  title: string;
  isStreaming: boolean;
  onSelectPromptStarter: (question: string, langCode: string) => void;
  onNewChat?: () => void;
  onToggleSidebar?: () => void;
  sidebarCollapsed?: boolean;
  isGuestQuotaReached?: boolean;
  onOpenAuthModal?: () => void;
  user?: { name: string; email: string } | null;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  messages,
  title,
  isStreaming,
  onSelectPromptStarter,
  onNewChat,
  onToggleSidebar,
  sidebarCollapsed,
  isGuestQuotaReached = false,
  onOpenAuthModal,
  user,
}) => {
  const { t } = useLanguage();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  // Auto-scroll on new messages, streaming chunks, or guest limit card appearance
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages, isStreaming, isGuestQuotaReached]);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleSources = (msgIndex: number) => {
    setExpandedSources(prev => ({
      ...prev,
      [msgIndex]: !prev[msgIndex],
    }));
  };

  const starterQuestions = [
    { text: t('chat_sample_q1') || 'What is photosynthesis?', lang: 'auto', label: '1' },
    { text: t('chat_sample_q2') || 'List major government schemes in India', lang: 'auto', label: '2' },
    { text: t('chat_sample_q3') || 'How to maintain a healthy lifestyle?', lang: 'auto', label: '3' },
    { text: t('chat_sample_q4') || 'Explain climate change in simple terms', lang: 'auto', label: '4' },
  ];

  const isEmpty = messages.length === 0;

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
      {/* Top Workspace Toolbar */}
      <div className="h-12 border-b border-border-subtle bg-bg/70 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-3 truncate">
          {onToggleSidebar && (
            <button
              id="chatSidebarToggleBtn"
              onClick={onToggleSidebar}
              className="p-1.5 rounded-lg glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-text-secondary hover:text-text-primary transition-colors border border-border-subtle"
              title="Toggle conversation sidebar"
            >
              <MessageSquare className="w-4 h-4 text-accent-lime" />
            </button>
          )}

          {/* Active conversation title capsule */}
          <div id="currentChatTitleBadge" className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-subtle border border-border-subtle text-xs font-medium text-text-primary truncate max-w-sm">
            <span className="w-2 h-2 rounded-full bg-accent-lime shadow-sm shrink-0" />
            <span id="currentChatTitle" className="truncate font-semibold">{title || t('nav_new_chat') || 'New chat'}</span>
          </div>

          {/* Model Status Badge */}
          <div className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/05 dark:bg-white/[0.03] border border-border-subtle text-[11px] text-text-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald shrink-0" />
            <span>RAG GROUNDED · sarvam-105b-conversations</span>
          </div>
        </div>

        {/* Action Controls on Toolbar Right */}
        <div className="flex items-center gap-2">
          {onNewChat && (
            <button
              id="toolbarNewChatBtn"
              type="button"
              onClick={onNewChat}
              className="px-2.5 py-1 rounded-xl btn-lime-glass flex items-center gap-1.5 text-xs font-semibold shadow-xs"
              title="New chat (⌘K)"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{t('nav_new_chat') || 'New chat'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Messages & Empty State Viewport */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 py-6 md:px-8 space-y-6"
      >
        {isEmpty ? (
          /* Empty Chat Hero State */
          <div className="max-w-3xl lg:max-w-4xl mx-auto w-full flex flex-col items-center justify-center min-h-[65vh] text-center space-y-7 animate-in fade-in duration-300">
            {/* 3D Floating Language Emblem */}
            <div className="relative group">
              <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-accent-lime/20 to-accent-emerald/10 border border-accent-lime/40 flex items-center justify-center shadow-lg backdrop-blur-md">
                <Globe className="w-8 h-8 text-accent-lime animate-pulse-subtle" />
              </div>
              <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-bg border border-border-subtle flex items-center justify-center text-[10px] font-bold text-accent-emerald shadow-sm">
                अ
              </div>
            </div>

            {/* Headline & Subtitle */}
            <div className="space-y-2 max-w-xl">
              <h1 className="hero-headline-center text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
                {t('chat_hero_headline_plain') || 'Ask anything in your language'}
              </h1>
              <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
                {t('chat_hero_subheadline') || 'A multilingual, research-backed chatbot for Indian languages'}
              </p>
            </div>

            {/* 6 Supported Language Chips */}
            <div className="flex flex-wrap items-center justify-center gap-2 max-w-2xl">
              {SUPPORTED_LANGUAGES.map((l) => (
                <button
                  key={l.code}
                  onClick={() => onSelectPromptStarter(l.sampleQuestion, l.code)}
                  className="px-3.5 py-1.5 rounded-2xl glass-subtle hover:glass-elevated border border-border-subtle hover:border-accent-lime/50 text-xs text-text-secondary hover:text-text-primary active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <span className="font-semibold text-accent-lime">{l.nativeName}</span>
                  <span className="text-[10px] text-text-muted">({l.code.toUpperCase()})</span>
                </button>
              ))}
            </div>

            {/* "Try asking" Prompt Starter Cards */}
            <div className="w-full space-y-3">
              <div className="try-asking-header flex items-center justify-center gap-1.5 text-xs font-semibold text-text-muted uppercase tracking-wider">
                <span><Sparkles className="w-3.5 h-3.5 text-accent-lime inline" /></span>
                <span>{t('chat_try_asking') || 'Try asking'}</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                {starterQuestions.map((sq, i) => (
                  <button
                    key={i}
                    id={`heroPromptCard${i + 1}`}
                    onClick={() => onSelectPromptStarter(sq.text, sq.lang)}
                    className="interactive-glass-card p-4 rounded-2xl glass-subtle border border-border-subtle hover:border-accent-lime/50 transition-all text-xs group flex items-start justify-between gap-3 shadow-glass-sm cursor-pointer"
                  >
                    <div>
                      <div className="text-[10px] font-bold text-accent-lime uppercase tracking-wider mb-1 flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-accent-lime" />
                        <span>Prompt {i + 1}</span>
                      </div>
                      <div className="card-text text-text-primary font-medium leading-snug group-hover:text-accent-lime transition-colors">
                        {sq.text}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent-lime transition-transform group-hover:translate-x-1 shrink-0 mt-0.5" />
                  </button>
                ))}
              </div>
            </div>

            {/* Metrics Glass Banner */}
            <div className="w-full glass-panel rounded-2xl p-4 border border-border-subtle grid grid-cols-2 sm:grid-cols-4 gap-4 text-center shadow-glass-sm">
              <div>
                <div className="text-base font-bold text-accent-lime">6</div>
                <div className="text-[11px] text-text-secondary">{t('stat_indian_languages') || 'Indian Languages'}</div>
              </div>
              <div>
                <div className="text-base font-bold text-accent-lime">IndicCorp</div>
                <div className="text-[11px] text-text-secondary">(AI4Bharat)</div>
              </div>
              <div>
                <div className="text-base font-bold text-accent-lime">{t('stat_research_backed') || 'Research-Backed'}</div>
                <div className="text-[11px] text-text-secondary">{t('stat_answers') || 'Answers'}</div>
              </div>
              <div>
                <div className="text-base font-bold text-accent-lime">{t('stat_lang_quality') || 'Language Quality'}</div>
                <div className="text-[11px] text-text-secondary">{t('stat_comparison') || 'Comparison'}</div>
              </div>
            </div>
          </div>
        ) : (
          /* Active Messages Thread */
          <div className="max-w-3xl lg:max-w-4xl mx-auto w-full space-y-6 pb-6">
            {messages.map((msg, index) => {
              const isUser = msg.role === 'user';
              const citations = msg.citations || [];
              const hasCitations = citations.length > 0;
              const isSourcesExpanded = expandedSources[index] || false;

              if (isUser) {
                return (
                  <div key={index} className="msg user flex justify-end">
                    <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-sm bg-accent-lime-surface border border-accent-lime/30 text-text-primary px-4 py-3 text-sm leading-relaxed shadow-sm">
                      <div className="text-xs text-text-secondary font-medium mb-1">You</div>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                );
              }

              /* Cohesive Assistant Response Card */
              return (
                <div key={index} className="msg bot w-full">
                  <div className="glass-panel rounded-2xl border border-white/10 dark:border-white/[0.08] p-5 shadow-glass-md transition-all">
                    {/* Card Header: Identity & Status */}
                    <div className="flex items-center justify-between gap-2 pb-3 mb-3 border-b border-border-subtle text-xs">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[#B7FF72] to-[#36D69A] flex items-center justify-center text-[#050706] font-extrabold text-[11px] shadow-sm">
                          B
                        </div>
                        <span className="font-semibold text-text-primary tracking-tight">BhashaCore</span>
                        <span className="hidden sm:inline-block text-[10px] px-2 py-0.5 rounded-full bg-accent-lime/10 text-accent-lime font-mono font-medium border border-accent-lime/20">
                          sarvam-105b
                        </span>
                      </div>

                      {msg.status && (
                        <div className="flex items-center gap-1.5 text-[11px] font-medium text-accent-lime">
                          <span className="w-1.5 h-1.5 rounded-full bg-accent-lime animate-pulse" />
                          <span className="truncate max-w-[220px] sm:max-w-none">{msg.status}</span>
                        </div>
                      )}
                    </div>

                    {/* Answer Text Body */}
                    <div className="answer-text text-sm leading-relaxed text-text-primary whitespace-pre-wrap font-sans">
                      {msg.content}
                      {isStreaming && index === messages.length - 1 && (
                        <span className="inline-block w-1.5 h-4 bg-accent-lime ml-1 animate-pulse align-middle" />
                      )}
                    </div>

                    {/* Integrated Sources / Citations Accordion */}
                    {hasCitations && (
                      <div className="mt-4 pt-3 border-t border-border-subtle">
                        <button
                          type="button"
                          onClick={() => toggleSources(index)}
                          className="sources-btn inline-flex items-center justify-between w-full px-3 py-2 rounded-xl glass-subtle hover:bg-black/05 dark:hover:bg-white/[0.05] text-xs font-semibold text-text-secondary hover:text-text-primary transition-all border border-border-subtle"
                        >
                          <div className="flex items-center gap-2">
                            <BookOpen className="w-3.5 h-3.5 text-accent-lime" />
                            <span>
                              {(t('citations_heading') && t('citations_heading') !== 'citations_heading' ? t('citations_heading') : 'Sources & Evidence')} ({citations.length})
                            </span>
                          </div>
                          <ChevronDown
                            className={`w-3.5 h-3.5 text-text-muted transition-transform duration-200 ${isSourcesExpanded ? 'rotate-180 text-accent-lime' : ''}`}
                          />
                        </button>

                        {isSourcesExpanded && (
                          <div className="sources-list mt-2.5 space-y-2 animate-in fade-in duration-150">
                            {citations.map((c, ci) => (
                              <div
                                key={ci}
                                className="source-card p-3 rounded-xl bg-black/10 dark:bg-white/[0.02] border border-border-subtle text-xs space-y-1.5"
                              >
                                <div className="flex items-center justify-between text-text-muted font-mono text-[10px]">
                                  <span className="text-accent-lime font-bold">[{ci + 1}] {c.pid || c.id || `doc_${ci + 1}`}</span>
                                  {c.score !== undefined && (
                                    <span className="text-text-secondary">
                                      BM25: {typeof c.score === 'number' ? c.score.toFixed(2) : c.score}
                                    </span>
                                  )}
                                </div>
                                <p className="text-text-secondary text-xs leading-relaxed">
                                  {c.text}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Integrated Footer: Provenance & Copy Action */}
                    {msg.content && (
                      <div className="flex items-center justify-between pt-3 mt-3 border-t border-border-subtle text-[11px] text-text-muted">
                        <span className="text-[10px] text-text-muted">
                          Grounded in IndicQA + IndicCorp v2
                        </span>

                        <button
                          type="button"
                          onClick={() => handleCopy(msg.content, `msg-${index}`)}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg hover:bg-black/05 dark:hover:bg-white/[0.06] hover:text-text-primary transition-colors text-xs"
                          title="Copy answer"
                        >
                          {copiedId === `msg-${index}` ? (
                            <>
                              <Check className="w-3 h-3 text-accent-emerald" />
                              <span className="text-accent-emerald font-medium">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Compact Glassmorphic Guest Trial Limit Card */}
            {!user && isGuestQuotaReached && (
              <div
                id="guestLimitCard"
                className="glass-panel p-5 rounded-2xl border border-accent-lime/30 shadow-glass-lg space-y-3 animate-in fade-in duration-200"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/30 uppercase tracking-wide">
                        {t('guest_trial_badge') || 'Guest Trial'}
                      </span>
                      <span className="text-xs font-mono text-text-muted">
                        3/3 messages used
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-text-primary">
                      {t('guest_limit_title') || "You've reached the 3-question trial limit"}
                    </h3>
                    <p className="text-xs text-text-secondary leading-relaxed max-w-xl">
                      {t('guest_limit_desc') || "Create a free account or sign in to continue chatting, unlock unlimited questions, and save your conversation history."}
                    </p>
                  </div>

                  <div className="flex items-center gap-2.5 shrink-0">
                    <button
                      id="guestLimitSignInBtn"
                      onClick={onOpenAuthModal}
                      className="btn-lime-glass px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-sm"
                    >
                      <span>{t('guest_signin_btn') || 'Sign In'}</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                    <button
                      id="guestLimitSignUpBtn"
                      onClick={onOpenAuthModal}
                      className="btn-ghost-glass px-3.5 py-2 rounded-xl text-xs font-semibold text-text-primary hover:border-accent-lime/40 transition-colors"
                    >
                      {t('guest_create_account_btn') || 'Create Account'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
