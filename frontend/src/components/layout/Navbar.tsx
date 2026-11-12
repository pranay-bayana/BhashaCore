import React, { useState, useRef, useEffect } from 'react';
import { useLanguage, LANGUAGE_DISPLAY_NAMES } from '@/localization/LanguageContext';
import { useTheme } from '@/context/ThemeContext';
import { LanguageCode } from '@/types/api';
import { NotificationPopover } from '@/components/layout/NotificationPopover';
import {
  Globe,
  ChevronDown,
  Sun,
  Moon,
  Menu,
  X,
  Sparkles,
  LayoutDashboard,
  GitCompare,
  AlertTriangle,
  Bell
} from 'lucide-react';

interface NavbarProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
  onOpenAuthModal?: () => void;
  user?: { name: string; email: string } | null;
  onLogout?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRoute,
  onNavigate,
  onOpenAuthModal,
  user,
  onLogout,
}) => {
  const { language, setLanguage, t, availableLanguages } = useLanguage();
  const { isDark, toggleTheme } = useTheme();
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [researchDropdownOpen, setResearchDropdownOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [unreadNotifs, setUnreadNotifs] = useState(3);

  const langRef = useRef<HTMLDivElement>(null);
  const researchRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setLangDropdownOpen(false);
      }
      if (researchRef.current && !researchRef.current.contains(event.target as Node)) {
        setResearchDropdownOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isChatRoute = currentRoute === 'chat';
  const isResearchRoute = ['dashboard', 'comparison', 'failures'].includes(currentRoute);

  return (
    <header className="app-top-header sticky top-0 z-40 w-full backdrop-blur-deep bg-bg/85 border-b border-border-subtle transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand Logo (Only show on non-chat pages, or when chat sidebar is closed) */}
        <div className="flex items-center gap-6">
          {!isChatRoute && (
            <button
              onClick={() => onNavigate('home')}
              className="flex items-center gap-2.5 text-left group focus:outline-none"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#B7FF72] to-[#36D69A] flex items-center justify-center text-[#050706] font-extrabold text-base shadow-[0_0_16px_rgba(183,255,114,0.35)] transition-transform duration-200 group-hover:scale-105">
                B
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-base text-text-primary tracking-tight transition-colors">
                  BhashaCore
                </span>
                <span className="text-[10px] text-text-muted tracking-wider uppercase font-medium">
                  {t('home_badge') || 'Multilingual AI Research'}
                </span>
              </div>
            </button>
          )}

          {/* Desktop Navigation Links */}
          <nav className="top-horizontal-nav main-nav hidden md:flex items-center gap-1.5 ml-2">
            <a
              href="/"
              onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-150 ${
                currentRoute === 'home'
                  ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/[0.04]'
              }`}
            >
              {t('nav_home') || 'Home'}
            </a>

            <a
              href="/chat"
              onClick={(e) => { e.preventDefault(); onNavigate('chat'); }}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-150 ${
                currentRoute === 'chat'
                  ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/[0.04]'
              }`}
            >
              {t('nav_chat') || 'Chat'}
            </a>

            {/* Research Dropdown */}
            <div className="relative" ref={researchRef}>
              <button
                type="button"
                onClick={() => setResearchDropdownOpen(!researchDropdownOpen)}
                className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-150 ${
                  isResearchRoute
                    ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-sm'
                    : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/[0.04]'
                }`}
              >
                <span>{t('nav_research') || 'Research'}</span>
                <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-150 ${researchDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {researchDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-64 glass-elevated rounded-2xl p-2 shadow-glass-lg animate-in fade-in duration-150 z-50">
                  <a
                    href="/dashboard"
                    onClick={(e) => { e.preventDefault(); onNavigate('dashboard'); setResearchDropdownOpen(false); }}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors ${
                      currentRoute === 'dashboard' ? 'bg-accent-lime-surface text-accent-lime font-semibold' : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
                    }`}
                  >
                    <LayoutDashboard className="w-4 h-4 text-accent-lime shrink-0" />
                    <div className="text-left">
                      <div className="text-text-primary font-medium">{t('nav_dashboard') || 'Research Dashboard'}</div>
                      <div className="text-[10px] text-text-muted">{t('dashboard_eyebrow') || 'Metrics & evaluation overview'}</div>
                    </div>
                  </a>

                  <a
                    href="/language-comparison"
                    onClick={(e) => { e.preventDefault(); onNavigate('comparison'); setResearchDropdownOpen(false); }}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors ${
                      currentRoute === 'comparison' ? 'bg-accent-lime-surface text-accent-lime font-semibold' : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
                    }`}
                  >
                    <GitCompare className="w-4 h-4 text-accent-emerald shrink-0" />
                    <div className="text-left">
                      <div className="text-text-primary font-medium">{t('nav_comparison') || 'Language Comparison'}</div>
                      <div className="text-[10px] text-text-muted">{t('comparison_eyebrow') || '6-language accuracy breakdown'}</div>
                    </div>
                  </a>

                  <a
                    href="/failure-analysis"
                    onClick={(e) => { e.preventDefault(); onNavigate('failures'); setResearchDropdownOpen(false); }}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors ${
                      currentRoute === 'failures' ? 'bg-accent-lime-surface text-accent-lime font-semibold' : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
                    }`}
                  >
                    <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                    <div className="text-left">
                      <div className="text-text-primary font-medium">{t('nav_failures') || 'Failure Analysis'}</div>
                      <div className="text-[10px] text-text-muted">{t('failure_eyebrow') || 'Hallucination & retrieval logs'}</div>
                    </div>
                  </a>
                </div>
              )}
            </div>

            <a
              href="/about"
              onClick={(e) => { e.preventDefault(); onNavigate('about'); }}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-150 ${
                currentRoute === 'about'
                  ? 'bg-accent-lime-surface text-accent-lime font-semibold border border-accent-lime/30 shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/[0.04]'
              }`}
            >
              {t('nav_about') || 'About'}
            </a>
          </nav>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-3">
          {/* Interface Language Dropdown */}
          <div className="relative" ref={langRef}>
            <select
              id="interfaceLangSelect"
              aria-label="Interface Language Select"
              style={{ position: 'absolute', opacity: 0, pointerEvents: 'none', width: '1px', height: '1px' }}
              value={language}
              onChange={(e) => setLanguage(e.target.value as any)}
            >
              <option value="en">en</option>
              <option value="hi">hi</option>
              <option value="te">te</option>
              <option value="ta">ta</option>
              <option value="kn">kn</option>
              <option value="ml">ml</option>
            </select>
            <button
              onClick={() => setLangDropdownOpen(!langDropdownOpen)}
              className="inline-flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-full glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-xs font-medium text-text-primary transition-all duration-150 border border-border-subtle"
              aria-label="Select Interface Language"
            >
              <Globe className="w-3.5 h-3.5 text-accent-lime shrink-0" />
              <span className="hidden sm:inline">{LANGUAGE_DISPLAY_NAMES[language]?.native || language}</span>
              <span className="inline sm:hidden font-mono uppercase text-[10px] font-bold">{language}</span>
              <ChevronDown className={`w-3 h-3 text-text-secondary transition-transform ${langDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {langDropdownOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 glass-elevated rounded-2xl p-1.5 shadow-glass-lg z-50">
                <div className="px-2.5 py-1 text-[10px] font-semibold text-text-muted uppercase tracking-wider">
                  {t('select_interface_language') || 'Interface Language'}
                </div>
                {availableLanguages.map((code) => {
                  const meta = LANGUAGE_DISPLAY_NAMES[code];
                  const isSelected = code === language;
                  return (
                    <button
                      key={code}
                      onClick={() => {
                        setLanguage(code as LanguageCode);
                        setLangDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
                        isSelected
                          ? 'bg-accent-lime-surface text-accent-lime font-semibold'
                          : 'text-text-secondary hover:text-text-primary hover:bg-black/05 dark:hover:bg-white/05'
                      }`}
                    >
                      <span>{meta.native}</span>
                      {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-accent-lime" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Theme Toggle Button */}
          <button
            id="themeToggleBtn"
            onClick={toggleTheme}
            className="w-9 h-9 rounded-full glass-subtle hover:bg-black/05 dark:hover:bg-white/10 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors"
            title={isDark ? (t('theme_light') || 'Switch to Light Mode') : (t('theme_dark') || 'Switch to Dark Mode')}
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-slate-700" />}
          </button>

          {/* Notifications Button & Popover */}
          <div className="relative">
            <button
              id="notificationBellBtn"
              type="button"
              onClick={() => setNotifOpen(!notifOpen)}
              className="w-9 h-9 rounded-full glass-subtle hover:bg-black/05 dark:hover:bg-white/10 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors relative"
              title={t('notifications_title') || 'Notifications'}
              aria-label={t('notifications_title') || 'Notifications'}
              aria-expanded={notifOpen}
            >
              <Bell className="w-4 h-4" />
              {unreadNotifs > 0 && (
                <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-accent-lime shadow-[0_0_8px_rgba(183,255,114,0.8)]" />
              )}
            </button>

            <NotificationPopover
              isOpen={notifOpen}
              onClose={() => setNotifOpen(false)}
              onUnreadCountChange={setUnreadNotifs}
            />
          </div>

          {/* User Profile / Auth Button */}
          <div className="relative" ref={profileRef}>
            {user ? (
              <div>
                <button
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  className="w-9 h-9 rounded-full bg-gradient-to-br from-white/20 to-white/05 border border-border-subtle flex items-center justify-center text-accent-lime font-bold text-sm shadow-glass-sm hover:border-accent-lime/40 transition-colors"
                >
                  {user.name.charAt(0).toUpperCase()}
                </button>
                {profileDropdownOpen && (
                  <div className="absolute right-0 top-full mt-2 w-56 glass-elevated rounded-2xl p-2 shadow-glass-lg z-50">
                    <div className="px-3 py-2 border-b border-border-subtle mb-1">
                      <div className="text-xs font-semibold text-text-primary truncate">{user.name}</div>
                      <div className="text-[10px] text-text-muted truncate">{user.email}</div>
                    </div>
                    {onLogout && (
                      <button
                        onClick={() => {
                          onLogout();
                          setProfileDropdownOpen(false);
                        }}
                        className="w-full text-left px-3 py-2 rounded-xl text-xs font-medium text-red-500 hover:bg-red-500/10 transition-colors"
                      >
                        {t('auth_logout') || 'Sign out'}
                      </button>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onOpenAuthModal}
                className="hidden sm:inline-flex btn-lime-glass px-3.5 py-1.5 rounded-full text-xs font-semibold items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{t('auth_sign_in') || 'Sign In'}</span>
              </button>
            )}
          </div>

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden w-9 h-9 rounded-full glass-subtle hover:bg-black/05 dark:hover:bg-white/10 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors"
          >
            {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-elevated border-b border-border-subtle px-4 py-4 space-y-2 animate-in slide-in-from-top duration-200">
          <button
            onClick={() => { onNavigate('home'); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm font-medium text-text-primary hover:bg-black/05 dark:hover:bg-white/05"
          >
            {t('nav_home') || 'Home'}
          </button>
          <button
            onClick={() => { onNavigate('chat'); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm font-medium text-text-primary hover:bg-black/05 dark:hover:bg-white/05"
          >
            {t('nav_chat') || 'Chat'}
          </button>
          <div className="border-t border-border-subtle pt-2 pb-1 text-xs font-semibold text-text-muted px-3">
            {t('nav_research') || 'Research'}
          </div>
          <button
            onClick={() => { onNavigate('dashboard'); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm text-text-secondary hover:bg-black/05 dark:hover:bg-white/05 flex items-center gap-2"
          >
            <LayoutDashboard className="w-4 h-4 text-accent-lime" />
            <span>{t('nav_dashboard') || 'Dashboard'}</span>
          </button>
          <button
            onClick={() => { onNavigate('comparison'); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm text-text-secondary hover:bg-black/05 dark:hover:bg-white/05 flex items-center gap-2"
          >
            <GitCompare className="w-4 h-4 text-accent-emerald" />
            <span>{t('nav_comparison') || 'Language Comparison'}</span>
          </button>
          <button
            onClick={() => { onNavigate('failures'); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm text-text-secondary hover:bg-black/05 dark:hover:bg-white/05 flex items-center gap-2"
          >
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span>{t('nav_failures') || 'Failure Analysis'}</span>
          </button>
          <button
            onClick={() => { onNavigate('about'); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm font-medium text-text-primary hover:bg-black/05 dark:hover:bg-white/05"
          >
            {t('nav_about') || 'About'}
          </button>
          {!user && (
            <div className="pt-2 border-t border-border-subtle">
              <button
                onClick={() => { onOpenAuthModal?.(); setMobileMenuOpen(false); }}
                className="w-full btn-lime-glass px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-2"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{t('auth_sign_in') || 'Sign In'}</span>
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
};
