import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { AppNotification } from '@/types/api';
import { Bell, CheckCheck, Trash2, Cpu, Database, Award, X } from 'lucide-react';

interface NotificationPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  onUnreadCountChange?: (count: number) => void;
}

const DEFAULT_NOTIFICATIONS: AppNotification[] = [
  {
    id: 'notif-1',
    type: 'system',
    title: 'IndicCorp v2 Index Active',
    message: 'BM25 multi-language retrieval pool is active across Hindi, Telugu, Tamil, Kannada, Malayalam, and English.',
    timestamp: 'Just now',
    read: false,
  },
  {
    id: 'notif-2',
    type: 'research',
    title: 'Sarvam AI 105B Connected',
    message: 'Primary generative model is active for grounded multilingual inference with RAG citations.',
    timestamp: '10m ago',
    read: false,
  },
  {
    id: 'notif-3',
    type: 'info',
    title: 'IndicQA Evaluation Corpus',
    message: 'Comprehensive cross-lingual QA dataset loaded with 530+ analyzed failure cases.',
    timestamp: '1h ago',
    read: false,
  },
];

export const NotificationPopover: React.FC<NotificationPopoverProps> = ({
  isOpen,
  onClose,
  onUnreadCountChange,
}) => {
  const { t } = useLanguage();
  const popoverRef = useRef<HTMLDivElement>(null);

  const [notifications, setNotifications] = useState<AppNotification[]>(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('bhashacore_notifications');
        if (saved) {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed)) return parsed;
        }
      } catch (_) {}
    }
    return DEFAULT_NOTIFICATIONS;
  });

  const unreadCount = notifications.filter((n) => !n.read).length;

  useEffect(() => {
    if (onUnreadCountChange) {
      onUnreadCountChange(unreadCount);
    }
    try {
      localStorage.setItem('bhashacore_notifications', JSON.stringify(notifications));
    } catch (_) {}
  }, [notifications, unreadCount, onUnreadCountChange]);

  // Click outside and Escape key to close
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  const handleMarkAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleClearAll = () => {
    setNotifications([]);
  };

  if (!isOpen) return null;

  return (
    <div
      ref={popoverRef}
      role="dialog"
      aria-label={t('notifications_title') || 'Notifications'}
      aria-modal="true"
      className="absolute right-0 top-full mt-2 w-80 sm:w-96 glass-elevated rounded-2xl shadow-glass-xl border border-border-subtle z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      {/* Popover Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-black/05 dark:bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-text-primary">
            {t('notifications_title') || 'Notifications'}
          </span>
          {unreadCount > 0 && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-accent-lime/20 text-accent-lime border border-accent-lime/40">
              {unreadCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className="p-1.5 rounded-lg hover:bg-black/05 dark:hover:bg-white/10 text-text-secondary hover:text-text-primary transition-colors text-xs flex items-center gap-1"
              title={t('notifications_mark_all_read') || 'Mark all as read'}
            >
              <CheckCheck className="w-3.5 h-3.5" />
            </button>
          )}
          {notifications.length > 0 && (
            <button
              onClick={handleClearAll}
              className="p-1.5 rounded-lg hover:bg-black/05 dark:hover:bg-white/10 text-text-secondary hover:text-red-400 transition-colors text-xs"
              title={t('notifications_clear') || 'Clear all'}
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-black/05 dark:hover:bg-white/10 text-text-muted hover:text-text-primary transition-colors"
            title="Close"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Notifications Body */}
      <div className="max-h-80 overflow-y-auto divide-y divide-border-subtle">
        {notifications.length === 0 ? (
          <div className="px-6 py-10 text-center flex flex-col items-center justify-center space-y-2">
            <div className="w-10 h-10 rounded-full glass-subtle flex items-center justify-center text-text-muted mb-1">
              <Bell className="w-5 h-5 opacity-40" />
            </div>
            <div className="font-medium text-xs text-text-primary">
              {t('notifications_empty_title') || 'All caught up'}
            </div>
            <p className="text-[11px] text-text-muted max-w-[200px]">
              {t('notifications_empty_desc') || 'You have no new notifications right now.'}
            </p>
          </div>
        ) : (
          notifications.map((n) => {
            return (
              <div
                key={n.id}
                onClick={() => handleMarkAsRead(n.id)}
                className={`p-3.5 transition-colors cursor-pointer flex gap-3 text-left ${
                  n.read
                    ? 'opacity-70 hover:opacity-100 hover:bg-black/05 dark:hover:bg-white/[0.03]'
                    : 'bg-accent-lime/[0.04] hover:bg-accent-lime/[0.08]'
                }`}
              >
                <div className="shrink-0 mt-0.5">
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs ${
                    n.type === 'system'
                      ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
                      : n.type === 'research'
                      ? 'bg-accent-lime/15 text-accent-lime border border-accent-lime/30'
                      : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  }`}>
                    {n.type === 'system' ? (
                      <Database className="w-3.5 h-3.5" />
                    ) : n.type === 'research' ? (
                      <Cpu className="w-3.5 h-3.5" />
                    ) : (
                      <Award className="w-3.5 h-3.5" />
                    )}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1 mb-0.5">
                    <span className="font-semibold text-xs text-text-primary truncate">
                      {n.title}
                    </span>
                    <span className="text-[10px] text-text-muted shrink-0">
                      {n.timestamp}
                    </span>
                  </div>
                  <p className="text-[11px] text-text-secondary leading-snug line-clamp-2">
                    {n.message}
                  </p>
                </div>

                {!n.read && (
                  <div className="shrink-0 self-center">
                    <span className="block w-2 h-2 rounded-full bg-accent-lime shadow-[0_0_8px_rgba(183,255,114,0.6)]" />
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
