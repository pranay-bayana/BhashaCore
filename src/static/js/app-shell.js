/**
 * BhashaCore Application Shell JavaScript
 * Handles theme toggling, in-place language switching, mobile drawer, and CSRF fetch wrapping.
 */

(function () {
  'use strict';

  // 1. Language Names Catalog by Interface Locale
  const LANG_NAMES_BY_INTERFACE = {
    en: { en: 'English', hi: 'Hindi', ta: 'Tamil', te: 'Telugu', kn: 'Kannada', ml: 'Malayalam' },
    hi: { en: 'अंग्रेज़ी', hi: 'हिंदी', ta: 'तमिल', te: 'तेलुगु', kn: 'कन्नड़', ml: 'मलयालम' },
    ta: { en: 'ஆங்கிலம்', hi: 'இந்தி', ta: 'தமிழ்', te: 'தெலுங்கு', kn: 'கன்னடம்', ml: 'மலையாளம்' },
    te: { en: 'ఆంగ్లం', hi: 'హిందీ', ta: 'తమిళం', te: 'తెలుగు', kn: 'కన్నడ', ml: 'మలయాళం' },
    kn: { en: 'ಇಂಗ್ಲಿಷ್', hi: 'ಹಿಂದಿ', ta: 'ತಮಿಳು', te: 'ತೆಲುಗು', kn: 'ಕನ್ನಡ', ml: 'ಮಲಯಾಳಂ' },
    ml: { en: 'ഇംഗ്ലീഷ്', hi: 'ഹിന്ദി', ta: 'തമിഴ്', te: 'തെലുങ്ക്', kn: 'കന്നഡ', ml: 'മലയാളം' },
  };
  window.LANG_NAMES_BY_INTERFACE = LANG_NAMES_BY_INTERFACE;

  // Catalog cache for instant offline zero-latency switching
  window.__BHASHACORE_CATALOGS__ = window.__BHASHACORE_CATALOGS__ || {};

  // 2. Theme Management
  function initTheme() {
    const savedTheme = localStorage.getItem('bhashacore-theme') ||
      (document.cookie.match(/bhashacore-theme=([^;]+)/) || [])[1] ||
      'dark';

    applyTheme(savedTheme, false);
  }

  function applyTheme(theme, save = true) {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
    }

    if (save) {
      localStorage.setItem('bhashacore-theme', theme);
      document.cookie = `bhashacore-theme=${theme}; path=/; max-age=31536000; SameSite=Lax`;
    }

    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      themeBtn.setAttribute('aria-label', isLight ? 'Switch to dark mode' : 'Switch to light mode');
      themeBtn.innerHTML = isLight
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    }
  }

  window.toggleTheme = function () {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    applyTheme(isLight ? 'dark' : 'light', true);
  };

  // 3. CSRF & Fetch Wrapper
  function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
  }
  window.getCsrfToken = getCsrfToken;

  const nativeFetch = window.fetch.bind(window);
  window.fetch = function (input, init = {}) {
    const method = (init.method || 'GET').toUpperCase();
    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
      const token = getCsrfToken();
      if (token) {
        if (init.headers instanceof Headers) {
          if (!init.headers.has('X-CSRFToken')) init.headers.set('X-CSRFToken', token);
          if (!init.headers.has('X-CSRF-Token')) init.headers.set('X-CSRF-Token', token);
        } else if (Array.isArray(init.headers)) {
          if (!init.headers.some(([k]) => k.toLowerCase() === 'x-csrftoken')) {
            init.headers.push(['X-CSRFToken', token]);
          }
        } else {
          init.headers = {
            ...(init.headers || {}),
            'X-CSRFToken': token,
            'X-CSRF-Token': token,
          };
        }
      }
    }
    return nativeFetch(input, init);
  };

  // 4. In-Place DOM Localization Without Refresh
  function applyClientTranslations(lang, catalog) {
    if (!catalog || typeof catalog !== 'object') return;
    document.documentElement.lang = lang;

    // A. Update textContent for [data-i18n]
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (key && catalog[key] !== undefined) {
        el.textContent = catalog[key];
      }
    });

    // B. Update innerHTML for [data-i18n-html]
    document.querySelectorAll('[data-i18n-html]').forEach((el) => {
      const key = el.getAttribute('data-i18n-html');
      if (key && catalog[key] !== undefined) {
        el.innerHTML = catalog[key];
      }
    });

    // C. Update placeholders for [data-i18n-placeholder]
    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key && catalog[key] !== undefined) {
        el.placeholder = catalog[key];
      }
    });

    // D. Update titles for [data-i18n-title]
    document.querySelectorAll('[data-i18n-title]').forEach((el) => {
      const key = el.getAttribute('data-i18n-title');
      if (key && catalog[key] !== undefined) {
        el.title = catalog[key];
      }
    });

    // E. Update aria-labels for [data-i18n-aria]
    document.querySelectorAll('[data-i18n-aria]').forEach((el) => {
      const key = el.getAttribute('data-i18n-aria');
      if (key && catalog[key] !== undefined) {
        el.setAttribute('aria-label', catalog[key]);
      }
    });

    // F. Update interface language select elements and pill text
    const langNames = LANG_NAMES_BY_INTERFACE[lang] || LANG_NAMES_BY_INTERFACE.en;
    const selects = document.querySelectorAll('#interfaceLangSelect, .interface-lang-select');
    selects.forEach((sel) => {
      sel.value = lang;
      Array.from(sel.options).forEach((opt) => {
        const c = opt.value;
        if (langNames[c]) {
          opt.textContent = `${langNames[c]} (${c.toUpperCase()})`;
        }
      });
    });

    // Update floating header pill text: e.g. "Interface: Hindi" or "इंटरफ़ेस: हिंदी"
    const pillText = document.querySelector('.interface-pill-text');
    if (pillText) {
      const prefix = catalog.interface_label || 'Interface';
      const curName = langNames[lang] || lang;
      pillText.textContent = `${prefix}: ${curName}`;
    }

    // Update horizontal language buttons on chat hero stage to reflect localized language names
    const heroLangBtns = document.querySelectorAll('.horizontal-lang-bar .lang-btn');
    heroLangBtns.forEach((btn) => {
      const c = btn.getAttribute('data-lang');
      if (c && c !== 'auto') {
        const nameSpan = btn.querySelector('span:first-child');
        if (nameSpan && langNames[c]) {
          nameSpan.textContent = langNames[c];
        }
      }
    });

    // G. Dispatch custom event for page-specific components
    document.dispatchEvent(new CustomEvent('bhashacore:langchange', {
      detail: { lang: lang, translations: catalog, langNames: langNames }
    }));
  }
  window.applyClientTranslations = applyClientTranslations;

  // 5. Interface Language Switcher (Zero Refresh, Instant Update)
  window.setInterfaceLang = function (lang) {
    if (!lang) return;

    // Set cookies immediately for subsequent loads
    document.cookie = `bhashacore-ui-lang=${lang}; path=/; max-age=31536000; SameSite=Lax`;
    document.cookie = `bhashacore-lang=${lang}; path=/; max-age=31536000; SameSite=Lax`;

    // Persist to server in background
    nativeFetch('/api/set-interface-lang', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ lang: lang }),
    }).catch((err) => {
      console.warn('Background language persistence notice:', err);
    });

    // If translations are cached, update DOM instantly (0ms latency)
    if (window.__BHASHACORE_CATALOGS__[lang]) {
      applyClientTranslations(lang, window.__BHASHACORE_CATALOGS__[lang]);
      return;
    }

    // Otherwise fetch catalog from API and apply without reload
    nativeFetch(`/api/translations?lang=${lang}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load translations: ' + res.status);
        return res.json();
      })
      .then((data) => {
        window.__BHASHACORE_CATALOGS__[lang] = data.translations;
        applyClientTranslations(lang, data.translations);
      })
      .catch((err) => {
        console.error('Localization error:', err);
      });
  };

  // 6. Mobile Navigation Drawer
  window.toggleMobileNav = function () {
    const drawer = document.getElementById('mobileNavDrawer');
    if (!drawer) return;
    const isOpen = drawer.classList.contains('open');
    if (isOpen) {
      drawer.classList.remove('open');
      document.body.style.overflow = '';
    } else {
      drawer.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
  };

  // 7. Toast Notification System
  window.showToast = function (message, type = 'info', duration = 3000) {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(8px)';
      toast.style.transition = 'all 0.2s ease-out';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  };

  // Close mobile drawer on Escape key or outside click
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const drawer = document.getElementById('mobileNavDrawer');
      if (drawer && drawer.classList.contains('open')) {
        window.toggleMobileNav();
      }
    }
  });

  // Pre-load all translation catalogs in background on idle for instant switching
  function preloadCatalogs() {
    if (window.requestIdleCallback) {
      window.requestIdleCallback(fetchCatalogs);
    } else {
      setTimeout(fetchCatalogs, 200);
    }

    function fetchCatalogs() {
      nativeFetch('/api/translations/all')
        .then((res) => res.json())
        .then((data) => {
          if (data && data.catalogs) {
            Object.assign(window.__BHASHACORE_CATALOGS__, data.catalogs);
          }
        })
        .catch(() => {});
    }
  }

  // Run initializations on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initTheme();
      preloadCatalogs();
    });
  } else {
    initTheme();
    preloadCatalogs();
  }
})();
