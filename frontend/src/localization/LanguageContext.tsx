import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { LanguageCode } from '@/types/api';
import { getCsrfToken } from '@/services/api';

import en from './catalogs/en.json';
import hi from './catalogs/hi.json';
import te from './catalogs/te.json';
import ta from './catalogs/ta.json';
import kn from './catalogs/kn.json';
import ml from './catalogs/ml.json';

const CATALOGS: Record<LanguageCode, Record<string, string>> = {
  en,
  hi,
  te,
  ta,
  kn,
  ml,
};

export const LANGUAGE_DISPLAY_NAMES: Record<LanguageCode, { name: string; native: string }> = {
  en: { name: 'English', native: 'English (EN)' },
  hi: { name: 'Hindi', native: 'हिन्दी (HI)' },
  te: { name: 'Telugu', native: 'తెలుగు (TE)' },
  ta: { name: 'Tamil', native: 'தமிழ் (TA)' },
  kn: { name: 'Kannada', native: 'ಕನ್ನಡ (KN)' },
  ml: { name: 'Malayalam', native: 'മലയാളം (ML)' },
};

interface LanguageContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  availableLanguages: LanguageCode[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

function getInitialLanguage(): LanguageCode {
  if (typeof window === 'undefined') return 'en';
  // 1. URL parameter ?lang=
  const urlParams = new URLSearchParams(window.location.search);
  const urlLang = urlParams.get('lang') as LanguageCode;
  if (urlLang && ['en', 'hi', 'te', 'ta', 'kn', 'ml'].includes(urlLang)) {
    return urlLang;
  }
  // 2. Cookie bhashacore-ui-lang
  const match = document.cookie.match(/(?:^|;\s*)bhashacore-ui-lang=([^;]+)/);
  if (match && ['en', 'hi', 'te', 'ta', 'kn', 'ml'].includes(match[1])) {
    return match[1] as LanguageCode;
  }
  // 3. LocalStorage
  const stored = localStorage.getItem('bhashacore_ui_lang') as LanguageCode;
  if (stored && ['en', 'hi', 'te', 'ta', 'kn', 'ml'].includes(stored)) {
    return stored;
  }
  return 'en';
}

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<LanguageCode>(getInitialLanguage);

  const setLanguage = useCallback((lang: LanguageCode) => {
    setLanguageState(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('bhashacore_ui_lang', lang);
      document.cookie = `bhashacore-ui-lang=${lang};path=/;max-age=${365 * 24 * 3600};SameSite=Lax`;
      document.cookie = `bhashacore-lang=${lang};path=/;max-age=${365 * 24 * 3600};SameSite=Lax`;
      document.documentElement.lang = lang;
      // Sync with Flask backend session asynchronously
      // This mutates the server-side session, so it follows the same CSRF
      // contract as chat and account requests.
      void getCsrfToken().then((csrfToken) => fetch('/api/set-interface-lang', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ lang }),
      })).catch(() => {});
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const t = useCallback((key: string, params?: Record<string, string | number>): string => {
    const catalog = CATALOGS[language];
    let template = catalog ? catalog[key] : undefined;

    if (!template) {
      // Fallback to English
      template = CATALOGS.en[key];
      if (!template) {
        console.warn(`[Localization] Missing key: "${key}" in language "${language}"`);
        return key;
      }
    }

    if (!params) return template;

    let result = template;
    for (const [paramKey, paramVal] of Object.entries(params)) {
      result = result.replaceAll(`{${paramKey}}`, String(paramVal));
    }
    return result;
  }, [language]);

  return (
    <LanguageContext.Provider value={{
      language,
      setLanguage,
      t,
      availableLanguages: ['en', 'hi', 'te', 'ta', 'kn', 'ml'],
    }}>
      {children}
    </LanguageContext.Provider>
  );
};

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
