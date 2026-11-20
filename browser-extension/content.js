(() => {
  if (window.__bhashaCoreTranslatorLoaded) return;
  window.__bhashaCoreTranslatorLoaded = true;

  const Core = window.BhashaCoreTranslatorCore;
  const DEFAULT_API_BASE = 'https://bhashacore.onrender.com';
  const ALLOWED_API_BASES = new Set([DEFAULT_API_BASE, 'http://127.0.0.1:8001', 'http://localhost:8001']);
  const ATTRIBUTES = ['title', 'aria-label', 'placeholder'];
  const state = {
    status: 'original', targetLang: null, translating: null, observer: null, timer: null,
    originals: new Map(), attributeOriginals: new Map(), queued: new Set(), applying: false,
    floating: null, floatingEnabled: false,
  };

  const excludedElement = (element) => !element || element.closest(
    '[data-bhashacore-translator], [data-bhashacore-translate-exclude], script,style,noscript,code,pre,kbd,samp,textarea,input,select,option,svg,canvas,template,[contenteditable="true"]'
  );
  // Attribute text is safe on normal controls; only their user-entered values
  // are protected by the broader text-node exclusion above.
  const excludedAttributeElement = (element) => !element || element.closest(
    '[data-bhashacore-translator], [data-bhashacore-translate-exclude], script,style,noscript,code,pre,kbd,samp,textarea,select,option,svg,canvas,template,[contenteditable="true"]'
  );
  const visible = (element) => Boolean(element && element.isConnected && element.getClientRects().length);

  function emitStatus(error) {
    chrome.runtime.sendMessage({ type: 'translation-status', status: state.status, error: error || null }).catch(() => {});
  }

  function textSegments(root = document.body) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const segments = [];
    let node;
    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (visible(parent) && !excludedElement(parent) && Core.isEligibleText(node.nodeValue, parent.tagName, false)) {
        segments.push({ kind: 'text', node, text: node.nodeValue, id: `t${segments.length}` });
      }
    }
    return segments;
  }

  function attributeSegments(root = document.body, offset = 0) {
    const segments = [];
    for (const element of root.querySelectorAll('[title],[aria-label],[placeholder]')) {
      if (!visible(element) || excludedAttributeElement(element) || element.matches('input[type="password"]')) continue;
      for (const name of ATTRIBUTES) {
        const text = element.getAttribute(name);
        // Do not reuse the text-node predicate: it intentionally excludes all
        // INPUT elements to protect values, while their placeholder/ARIA text
        // is explicitly safe to translate here.
        if (typeof text === 'string' && text.trim() && text.trim().length <= 800) {
          segments.push({ kind: 'attribute', element, name, text, id: `a${offset + segments.length}` });
        }
      }
    }
    return segments;
  }

  function collect(root = document.body) {
    const texts = textSegments(root);
    return texts.concat(attributeSegments(root, texts.length));
  }

  async function fetchTranslations(items, targetLang) {
    // The local URL exists solely for documented development testing.  An
    // arbitrary persisted endpoint would turn a page translator into a page
    // content exfiltration switch, so reject anything outside this allowlist.
    const { apiBaseUrl } = await chrome.storage.local.get({ apiBaseUrl: DEFAULT_API_BASE });
    const apiBase = ALLOWED_API_BASES.has(apiBaseUrl) ? apiBaseUrl : DEFAULT_API_BASE;
    const response = await fetch(`${apiBase}/api/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-BhashaCore-Extension': '1' },
      body: JSON.stringify({ target_lang: targetLang, segments: items.map(({ id, text }) => ({ id, text })) }),
    });
    let payload = null;
    try { payload = await response.json(); } catch (_) { /* handled below */ }
    if (!response.ok) throw new Error(payload?.message || `Translation service returned ${response.status}.`);
    return Core.validateResponse(payload, new Set(items.map((item) => item.id)));
  }

  function apply(items, translated) {
    state.applying = true;
    try {
      for (const item of items) {
        const value = translated.get(item.id);
        if (!value) continue;
        if (item.kind === 'text' && item.node.isConnected) {
          if (!state.originals.has(item.node)) state.originals.set(item.node, item.node.nodeValue);
          item.node.nodeValue = value;
        } else if (item.kind === 'attribute' && item.element.isConnected) {
          if (!state.attributeOriginals.has(item.element)) state.attributeOriginals.set(item.element, new Map());
          const originals = state.attributeOriginals.get(item.element);
          if (!originals.has(item.name)) originals.set(item.name, item.element.getAttribute(item.name));
          item.element.setAttribute(item.name, value);
        }
      }
    } finally {
      state.applying = false;
      state.observer?.takeRecords();
    }
  }

  async function translateItems(items, targetLang) {
    let translatedCount = 0;
    let failed = 0;
    for (const group of Core.batch(items, 40, 12000)) {
      try {
        apply(group, await fetchTranslations(group, targetLang));
        translatedCount += group.length;
      } catch (error) {
        failed += group.length;
        console.warn('BhashaCore translator batch failed:', error.message);
      }
    }
    return { translatedCount, failed };
  }

  function startObserver() {
    state.observer?.disconnect();
    state.observer = new MutationObserver((mutations) => {
      if (state.applying || state.status !== 'translated') return;
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.TEXT_NODE) state.queued.add(node.parentElement || node);
          else if (node.nodeType === Node.ELEMENT_NODE && !excludedElement(node)) state.queued.add(node);
        }
      }
      clearTimeout(state.timer);
      state.timer = setTimeout(processDynamic, 600);
    });
    state.observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  async function processDynamic() {
    if (state.status !== 'translated' || !state.queued.size || state.translating) return;
    const roots = [...state.queued]; state.queued.clear();
    const seenTextNodes = new Set();
    const seenAttributes = new WeakMap();
    const items = roots.flatMap((root) => collect(root)).filter((item) => {
      if (item.kind === 'text') {
        if (seenTextNodes.has(item.node) || state.originals.has(item.node)) return false;
        seenTextNodes.add(item.node);
        return true;
      }
      const names = seenAttributes.get(item.element) || new Set();
      if (names.has(item.name)) return false;
      names.add(item.name); seenAttributes.set(item.element, names);
      return true;
    });
    if (items.length) {
      const outcome = await translateItems(items, state.targetLang);
      if (outcome.failed) {
        state.status = 'partial';
        emitStatus('Some newly added page text could not be translated.');
      }
    }
  }

  async function translate(targetLang) {
    if (state.translating) return state.translating;
    state.translating = (async () => {
      if (!targetLang) throw new Error('Choose a language first.');
      if (state.status !== 'original') restore();
      state.status = 'translating'; emitStatus();
      const outcome = await translateItems(collect(), targetLang);
      state.targetLang = targetLang;
      state.status = outcome.translatedCount && !outcome.failed ? 'translated' : outcome.translatedCount ? 'partial' : 'failed';
      if (state.status !== 'failed') startObserver();
      emitStatus(outcome.failed ? 'Some page text could not be translated.' : null);
      return { status: state.status, ...outcome };
    })();
    try { return await state.translating; } finally { state.translating = null; }
  }

  function restore() {
    state.observer?.disconnect(); state.observer = null; clearTimeout(state.timer); state.queued.clear();
    state.applying = true;
    try {
      for (const [node, original] of state.originals) if (node.isConnected) node.nodeValue = original;
      for (const [element, attrs] of state.attributeOriginals) if (element.isConnected) {
        for (const [name, original] of attrs) original === null ? element.removeAttribute(name) : element.setAttribute(name, original);
      }
      state.originals.clear(); state.attributeOriginals.clear(); state.status = 'original'; state.targetLang = null;
    } finally { state.applying = false; }
    emitStatus();
    return { status: state.status };
  }

  function floating(enabled) {
    state.floatingEnabled = enabled;
    state.floating?.remove(); state.floating = null;
    if (!enabled) return;
    const host = document.createElement('div'); host.dataset.bhashacoreTranslator = 'true';
    host.style.cssText = 'position:fixed;right:18px;bottom:18px;z-index:2147483647';
    const shadow = host.attachShadow({ mode: 'closed' });
    shadow.innerHTML = `<style>button,select{font:13px system-ui;color:#ecfdf5;background:#09251d;border:1px solid #35e897;border-radius:9px;padding:8px}button{cursor:pointer}#box{display:flex;gap:6px;align-items:center;padding:7px;background:#071812;border-radius:12px;box-shadow:0 8px 24px #0008}</style><div id="box"><select aria-label="Translation language"><option value="en">English</option><option value="hi">हिन्दी</option><option value="te">తెలుగు</option><option value="ta">தமிழ்</option><option value="kn">ಕನ್ನಡ</option><option value="ml">മലയാളം</option></select><button id="restore">Restore</button><button id="close" aria-label="Close translator">×</button></div>`;
    const select = shadow.querySelector('select'); select.value = state.targetLang || 'hi';
    select.addEventListener('change', () => translate(select.value));
    shadow.querySelector('#restore').addEventListener('click', restore);
    shadow.querySelector('#close').addEventListener('click', () => floating(false));
    // Drag only from the control's empty surface; buttons and the selector
    // retain their normal accessible click/touch behavior.
    const box = shadow.querySelector('#box');
    let drag = null;
    box.addEventListener('pointerdown', (event) => {
      if (event.target.closest('button,select')) return;
      drag = { x: event.clientX, y: event.clientY, right: parseInt(host.style.right, 10), bottom: parseInt(host.style.bottom, 10) };
      box.setPointerCapture(event.pointerId);
    });
    box.addEventListener('pointermove', (event) => {
      if (!drag) return;
      host.style.right = `${Math.max(0, drag.right - (event.clientX - drag.x))}px`;
      host.style.bottom = `${Math.max(0, drag.bottom - (event.clientY - drag.y))}px`;
    });
    box.addEventListener('pointerup', () => { drag = null; });
    document.documentElement.append(host); state.floating = host;
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === 'translate') translate(message.targetLang).then(sendResponse).catch((error) => sendResponse({ status: 'failed', error: error.message }));
    else if (message.type === 'restore') sendResponse(restore());
    else if (message.type === 'status') sendResponse({ status: state.status, targetLang: state.targetLang });
    else if (message.type === 'floating') { floating(Boolean(message.enabled)); sendResponse({ enabled: state.floatingEnabled }); }
    else return;
    return true;
  });
})();
