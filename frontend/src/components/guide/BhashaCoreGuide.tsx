import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { LanguageCode } from '@/types/api';
import { GuideMessage, GuideCategory, GuideTopic } from '@/types/guide';
import {
  GUIDE_TOPICS,
  GUIDE_CATEGORIES,
  findGuideAnswer,
  getLocalizedGreeting,
} from './guideData';
import {
  Sparkles,
  X,
  Send,
  HelpCircle,
  ArrowRight,
  RotateCcw,
  BookOpen,
  ChevronRight,
  MessageCircleQuestion,
} from 'lucide-react';

interface BhashaCoreGuideProps {
  onNavigate: (route: string) => void;
  onOpenAuthModal: () => void;
}

export const BhashaCoreGuide: React.FC<BhashaCoreGuideProps> = ({
  onNavigate,
  onOpenAuthModal,
}) => {
  const { language } = useLanguage();
  const currentLang = language as LanguageCode;

  const [isOpen, setIsOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState<GuideCategory>('getting_started');
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<GuideMessage[]>(() => [
    {
      id: 'initial-greeting',
      sender: 'guide',
      text: getLocalizedGreeting(currentLang),
      timestamp: Date.now(),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  // Update initial greeting if user switches language before asking anything
  useEffect(() => {
    if (messages.length === 1 && messages[0].id === 'initial-greeting') {
      setMessages([
        {
          id: 'initial-greeting',
          sender: 'guide',
          text: getLocalizedGreeting(currentLang),
          timestamp: Date.now(),
        },
      ]);
    }
  }, [currentLang]);

  const handleAsk = (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed) return;

    const userMsg: GuideMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: trimmed,
      timestamp: Date.now(),
    };

    const result = findGuideAnswer(trimmed, currentLang);

    const guideMsg: GuideMessage = {
      id: `guide-${Date.now() + 1}`,
      sender: 'guide',
      text: result.replyText,
      timestamp: Date.now() + 1,
      action: result.action
        ? {
            type: result.action.type,
            target: result.action.target,
            label: result.action.label[currentLang] || result.action.label.en,
          }
        : undefined,
    };

    setMessages((prev) => [...prev, userMsg, guideMsg]);
    setInputQuery('');
  };

  const handleSelectTopic = (topic: GuideTopic) => {
    const q = topic.question[currentLang] || topic.question.en;
    handleAsk(q);
  };

  const handleActionClick = (action: { type: string; target: string }) => {
    if (action.type === 'navigate') {
      onNavigate(action.target);
    } else if (action.type === 'open_auth') {
      onOpenAuthModal();
    }
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: `greeting-${Date.now()}`,
        sender: 'guide',
        text: getLocalizedGreeting(currentLang),
        timestamp: Date.now(),
      },
    ]);
  };

  const filteredTopics = GUIDE_TOPICS.filter((t) => t.category === activeCategory);

  return (
    <>
      {/* 1. FLOATING LAUNCHER BUTTON */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="fixed bottom-5 right-5 z-40 flex items-center gap-2.5 px-4 py-3 rounded-full bg-[#121619]/95 text-text-primary border border-accent-lime/40 shadow-[0_0_24px_rgba(183,255,114,0.25)] hover:border-accent-lime hover:scale-105 active:scale-95 transition-all group backdrop-blur-md cursor-pointer"
          title="Open BhashaCore Guide"
          aria-label="Open BhashaCore Application Guide"
        >
          <div className="relative flex items-center justify-center w-7 h-7 rounded-full bg-accent-lime/10 border border-accent-lime/50 text-accent-lime">
            <Sparkles className="w-4 h-4 animate-pulse text-accent-lime" />
          </div>
          <div className="flex flex-col text-left">
            <span className="text-xs font-bold tracking-tight text-white flex items-center gap-1">
              <span>BhashaCore Guide</span>
            </span>
            <span className="text-[10px] text-accent-lime font-medium">Need Help?</span>
          </div>
        </button>
      )}

      {/* 2. FLOATING ASSISTANT FLYOUT WINDOW */}
      {isOpen && (
        <div className="fixed bottom-5 right-4 sm:right-6 z-50 w-[calc(100vw-32px)] sm:w-[400px] h-[580px] max-h-[85vh] flex flex-col rounded-3xl bg-[#121619]/95 border border-accent-lime/30 shadow-[0_12px_48px_rgba(0,0,0,0.7)] backdrop-blur-xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3.5 border-b border-white/10 bg-white/[0.03]">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-accent-lime/20 border border-accent-lime/40 flex items-center justify-center text-accent-lime">
                <Sparkles className="w-4 h-4 text-accent-lime" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>BhashaCore Guide</span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-accent-lime/15 text-accent-lime border border-accent-lime/30">
                    AI Assistant
                  </span>
                </h3>
                <p className="text-[10px] text-text-secondary">App Navigation & Multilingual Help</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleResetChat}
                className="p-1.5 rounded-xl hover:bg-white/10 text-text-secondary hover:text-white transition-colors"
                title="Restart Guide Conversation"
                aria-label="Restart Guide"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-xl hover:bg-white/10 text-text-secondary hover:text-white transition-colors"
                title="Close Guide"
                aria-label="Close Guide"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Thread */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs leading-relaxed">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 shadow-sm ${
                    msg.sender === 'user'
                      ? 'bg-accent-lime text-black font-medium rounded-br-sm'
                      : 'bg-white/[0.06] border border-white/10 text-text-primary rounded-bl-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                </div>

                {/* Direct Action Link if present */}
                {msg.action && (
                  <button
                    type="button"
                    onClick={() => handleActionClick(msg.action!)}
                    className="mt-1.5 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-accent-lime/15 hover:bg-accent-lime/25 border border-accent-lime/40 text-accent-lime text-[11px] font-semibold transition-all cursor-pointer active:scale-95"
                  >
                    <span>{msg.action.label}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Category Selector */}
          <div className="px-3 pt-2 pb-1 border-t border-white/05 bg-black/20">
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1.5 no-scrollbar">
              {GUIDE_CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-2 py-1 rounded-lg text-[10px] font-medium whitespace-nowrap transition-all shrink-0 cursor-pointer ${
                    activeCategory === cat.id
                      ? 'bg-accent-lime/20 border border-accent-lime/40 text-accent-lime font-semibold'
                      : 'text-text-secondary hover:text-white bg-white/05 border border-transparent'
                  }`}
                >
                  {cat.label[currentLang] || cat.label.en}
                </button>
              ))}
            </div>

            {/* Topic Pills in Selected Category */}
            <div className="flex items-center gap-1.5 overflow-x-auto py-1 no-scrollbar">
              {filteredTopics.map((top) => (
                <button
                  key={top.id}
                  type="button"
                  onClick={() => handleSelectTopic(top)}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-normal text-text-primary bg-white/05 hover:bg-accent-lime/10 hover:border-accent-lime/30 border border-white/10 whitespace-nowrap transition-all shrink-0 cursor-pointer"
                >
                  <MessageCircleQuestion className="w-2.5 h-2.5 text-accent-lime" />
                  <span>{top.title[currentLang] || top.title.en}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Input Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAsk(inputQuery);
            }}
            className="p-3 border-t border-white/10 bg-white/[0.02] flex items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask anything about BhashaCore..."
              className="flex-1 bg-black/40 border border-white/15 focus:border-accent-lime/60 rounded-xl px-3 py-2 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent-lime/30 transition-all"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim()}
              className="p-2 rounded-xl bg-accent-lime hover:bg-accent-lime/90 disabled:opacity-30 disabled:cursor-not-allowed text-black transition-all cursor-pointer active:scale-95 shrink-0"
              title="Send guide question"
              aria-label="Send"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
