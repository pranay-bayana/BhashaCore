import React, { useState, useMemo } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { ChatHistoryItem } from '@/types/api';
import {
  Plus,
  Search,
  MessageSquare,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  TrendingUp,
  Settings,
  LogIn,
  ShieldCheck,
  Sparkles
} from 'lucide-react';

interface ChatSidebarProps {
  conversations: ChatHistoryItem[];
  activeSessionId: string | null;
  onSelectConversation: (sessionId: string) => void;
  onNewChat: () => void;
  onRenameConversation: (id: string, newTitle: string) => Promise<void>;
  onDeleteConversation: (id: string) => Promise<void>;
  collapsed: boolean;
  onToggleCollapse: () => void;
  isMobileOpen: boolean;
  onCloseMobile: () => void;
  user?: { name: string; email: string } | null;
  onOpenResearch?: () => void;
  onOpenSettings?: () => void;
  onOpenAuthModal?: () => void;
  guestCount?: number;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  conversations,
  activeSessionId,
  onSelectConversation,
  onNewChat,
  onRenameConversation,
  onDeleteConversation,
  collapsed,
  onToggleCollapse,
  isMobileOpen,
  onCloseMobile,
  user,
  onOpenResearch,
  onOpenSettings,
  onOpenAuthModal,
  guestCount = 0,
}) => {
  const { t } = useLanguage();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Filter conversations based on search
  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    const q = searchQuery.toLowerCase();
    return conversations.filter(c => c.title && c.title.toLowerCase().includes(q));
  }, [conversations, searchQuery]);

  // Group by date for authenticated users
  const groups = useMemo(() => {
    const today: ChatHistoryItem[] = [];
    const yesterday: ChatHistoryItem[] = [];
    const previous: ChatHistoryItem[] = [];

    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;

    filtered.forEach(c => {
      const ts = (c.created > 1e11 ? c.created : c.created * 1000);
      const diff = now - ts;
      if (diff < oneDay) {
        today.push(c);
      } else if (diff < 2 * oneDay) {
        yesterday.push(c);
      } else {
        previous.push(c);
      }
    });

    return { today, yesterday, previous };
  }, [filtered]);

  const handleStartRename = (e: React.MouseEvent, c: ChatHistoryItem) => {
    e.stopPropagation();
    setEditingId(c.id);
    setEditTitle(c.title);
  };

  const handleSaveRename = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      await onRenameConversation(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm(t('auth_delete_confirm') || 'Delete this conversation permanently?')) {
      await onDeleteConversation(id);
    }
  };

  const renderGroup = (titleKey: string, defaultTitle: string, items: ChatHistoryItem[]) => {
    if (items.length === 0) return null;
    return (
      <div className="mb-4">
        <div className="px-3 py-1.5 text-[10px] font-bold text-text-muted uppercase tracking-wider">
          {t(titleKey) || defaultTitle}
        </div>
        <div className="space-y-1">
          {items.map((c) => {
            const isActive = c.session_id === activeSessionId;
            return (
              <div
                key={c.id}
                onClick={() => {
                  onSelectConversation(c.session_id);
                  if (isMobileOpen) onCloseMobile();
                }}
                className={`group relative flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium cursor-pointer transition-all duration-150 ${
                  isActive
                    ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-sm'
                    : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/[0.04]'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate flex-1 min-w-0 pr-2">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-accent-lime' : 'text-text-muted'}`} />
                  {editingId === c.id ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveRename(e as any, c.id);
                        if (e.key === 'Escape') handleCancelRename(e as any);
                      }}
                      className="bg-black/10 dark:bg-black/30 border border-accent-lime/40 rounded px-1.5 py-0.5 text-xs text-text-primary outline-none w-full"
                      autoFocus
                    />
                  ) : (
                    <span className="truncate">{c.title}</span>
                  )}
                </div>

                {/* Edit & Delete Actions (Visible on hover or active) */}
                {editingId === c.id ? (
                  <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={(e) => handleSaveRename(e, c.id)}
                      className="p-1 rounded text-accent-lime hover:bg-accent-lime/10"
                      title="Save"
                    >
                      <Check className="w-3 h-3" />
                    </button>
                    <button
                      onClick={handleCancelRename}
                      className="p-1 rounded text-text-muted hover:bg-black/10 dark:hover:bg-white/10"
                      title="Cancel"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ) : (
                  <div className="opacity-0 group-hover:opacity-100 flex items-center gap-0.5 shrink-0 transition-opacity">
                    <button
                      onClick={(e) => handleStartRename(e, c)}
                      className="p-1 rounded text-text-muted hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/10"
                      title="Rename"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => handleDelete(e, c.id)}
                      className="p-1 rounded text-text-muted hover:text-red-500 hover:bg-red-500/10"
                      title="Delete"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-bg-deep/85 backdrop-blur-2xl text-text-primary select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-border-subtle flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-[#B7FF72] to-[#36D69A] flex items-center justify-center text-[#050706] font-extrabold text-sm shadow-sm">
            B
          </div>
          <div>
            <div className="font-bold text-sm text-text-primary tracking-tight">BhashaCore</div>
            <div className="text-[10px] text-text-muted tracking-wide uppercase font-medium">multilingual RAG</div>
          </div>
        </div>

        <button
          id="chatSidebarCollapseBtn"
          onClick={onToggleCollapse}
          className="hidden md:flex p-1.5 rounded-xl glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-text-secondary hover:text-accent-lime hover:border-accent-lime/40 cursor-pointer active:scale-95 transition-all border border-border-subtle"
          title="Collapse sidebar"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          id="newChatBtn"
          onClick={() => {
            onNewChat();
            if (isMobileOpen) onCloseMobile();
          }}
          className="w-full btn-lime-glass py-2.5 px-4 rounded-xl text-xs font-semibold flex items-center justify-between group shadow-sm"
        >
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            <span>{t('nav_new_chat') || 'New chat'}</span>
          </div>
          <span className="text-[10px] bg-black/15 dark:bg-black/30 font-mono px-1.5 py-0.5 rounded font-bold">
            ⌘K
          </span>
        </button>
      </div>

      {/* Guest Trial Status Banner (Compact for Guest Users) */}
      {!user && (
        <div className="px-3 pb-2">
          <div className="glass-panel p-3 rounded-xl border border-border-subtle space-y-2">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/30 tracking-wide uppercase">
                {t('guest_trial_badge') || 'Guest Trial'}
              </span>
              <span className="text-xs font-mono font-semibold text-text-primary">
                {Math.min(guestCount, 3)}/3 messages used
              </span>
            </div>

            {/* 3-step mini progress track */}
            <div className="grid grid-cols-3 gap-1.5 pt-0.5">
              {[1, 2, 3].map((step) => {
                const isFilled = guestCount >= step;
                return (
                  <div
                    key={step}
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      isFilled
                        ? 'bg-accent-lime shadow-[0_0_8px_rgba(183,255,114,0.4)]'
                        : 'bg-white/10 dark:bg-white/[0.06]'
                    }`}
                  />
                );
              })}
            </div>

            {onOpenAuthModal && (
              <button
                type="button"
                onClick={onOpenAuthModal}
                className="w-full btn-ghost-glass py-1 px-2.5 rounded-lg text-[11px] font-semibold flex items-center justify-center gap-1.5 text-accent-lime hover:border-accent-lime/40 transition-colors"
              >
                <LogIn className="w-3 h-3" />
                <span>{t('auth_sign_in') || 'Sign In to Save'}</span>
              </button>
            )}

            <p className="text-[10px] text-text-muted leading-tight pt-0.5 text-center">
              {t('guest_sidebar_save_hint') || 'Conversations are kept in temporary memory. Sign in to save and organize your conversation history.'}
            </p>
          </div>
        </div>
      )}

      {/* Search Input for All Users */}
      <div className="px-3 pb-2">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            id="historySearchInput"
            type="text"
            placeholder={t('chat_history_search') || 'Search conversations…'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/05 dark:bg-white/[0.04] border border-border-subtle rounded-xl pl-9 pr-3 py-1.5 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-lime transition-colors"
          />
        </div>
      </div>

      {/* Conversation List (Today, Yesterday, Previous) */}
      <div id="chatHistoryList" className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        {filtered.length === 0 ? (
          <div className="text-center py-8 text-xs text-text-muted">
            {searchQuery ? 'No matching conversations' : (t('auth_no_history') || 'No conversations yet')}
          </div>
        ) : (
          <>
            {renderGroup('chat_history_today', 'Today', groups.today)}
            {renderGroup('chat_history_yesterday', 'Yesterday', groups.yesterday)}
            {renderGroup('chat_history_previous_7', 'Previous 7 Days', groups.previous)}
          </>
        )}
      </div>

      {/* Bottom Pinned Research Goal Card */}
      <div className="p-3 border-t border-border-subtle space-y-2 mt-auto">
        <div
          onClick={onOpenResearch}
          className="glass-subtle p-3 rounded-xl border border-border-subtle hover:border-accent-lime/40 transition-colors cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-accent-lime">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>{t('goal_title') || 'Research Goal'}</span>
            </div>
            <ChevronRight className="w-3.5 h-3.5 text-text-muted group-hover:text-accent-lime transition-transform group-hover:translate-x-0.5" />
          </div>
          <p className="text-[11px] text-text-secondary leading-tight">
            {t('goal_desc') || 'Analyze how answer quality varies across Indian languages.'}
          </p>
        </div>

        {/* User Status Bar */}
        <div className="flex items-center justify-between pt-1 text-xs text-text-secondary">
          <div className="flex items-center gap-2 truncate">
            <div className="w-6 h-6 rounded-full bg-black/10 dark:bg-white/10 flex items-center justify-center font-bold text-accent-lime text-[11px]">
              {user ? user.name.charAt(0).toUpperCase() : 'G'}
            </div>
            <span className="truncate font-medium text-text-primary">
              {user ? user.name : 'Guest Researcher'}
            </span>
          </div>

          {user && onOpenSettings ? (
            <button
              onClick={onOpenSettings}
              className="p-1 rounded-lg hover:bg-black/05 dark:hover:bg-white/10 text-text-muted hover:text-text-primary transition-colors"
              title="Settings"
            >
              <Settings className="w-3.5 h-3.5" />
            </button>
          ) : (
            onOpenAuthModal && (
              <button
                onClick={onOpenAuthModal}
                className="text-[11px] font-semibold text-accent-lime hover:underline"
              >
                {t('auth_sign_in') || 'Sign In'}
              </button>
            )
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        id="chatHistorySidebar"
        className={`hidden md:block h-[calc(100vh-4rem)] border-r border-border-subtle bg-bg-deep/85 backdrop-blur-2xl transition-all duration-300 z-30 shrink-0 ${
          collapsed ? 'w-0 overflow-hidden border-none opacity-0' : 'w-72 opacity-100'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Floating Toggle button when collapsed on desktop */}
      {collapsed && (
        <button
          id="chatSidebarReopenBtn"
          onClick={onToggleCollapse}
          className="hidden md:flex fixed top-20 left-4 z-40 p-2.5 rounded-xl glass-elevated border border-border-subtle hover:border-accent-lime/50 text-accent-lime shadow-glass-md hover:scale-105 active:scale-95 cursor-pointer transition-all"
          title="Open conversations sidebar"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      )}

      {/* Mobile Drawer Overlay */}
      {isMobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
          />
          <div className="relative w-72 max-w-[85vw] h-full bg-bg-deep border-r border-border-subtle shadow-2xl flex flex-col z-10">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
