/* Shared, dependency-free translation helpers. Exposed for content script and Node tests. */
(function (root) {
  const EXCLUDED_TAGS = new Set([
    'SCRIPT', 'STYLE', 'NOSCRIPT', 'CODE', 'PRE', 'KBD', 'SAMP', 'TEXTAREA',
    'INPUT', 'SELECT', 'OPTION', 'SVG', 'CANVAS', 'TEMPLATE'
  ]);

  function isEligibleText(text, tagName, excluded) {
    return typeof text === 'string' && text.trim().length > 0 && text.trim().length <= 800 &&
      !EXCLUDED_TAGS.has(String(tagName || '').toUpperCase()) && !excluded;
  }

  function batch(items, maxItems, maxChars) {
    const groups = [];
    let current = [], chars = 0;
    for (const item of items) {
      const length = item.text.length;
      if (current.length && (current.length >= maxItems || chars + length > maxChars)) {
        groups.push(current); current = []; chars = 0;
      }
      current.push(item); chars += length;
    }
    if (current.length) groups.push(current);
    return groups;
  }

  function validateResponse(payload, expectedIds) {
    if (!payload || !Array.isArray(payload.translations) || payload.translations.length !== expectedIds.size) {
      throw new Error('Translation response is incomplete.');
    }
    const seen = new Set();
    const mapped = new Map();
    for (const value of payload.translations) {
      if (!value || typeof value.id !== 'string' || typeof value.text !== 'string' || !value.text.trim() ||
          !expectedIds.has(value.id) || seen.has(value.id)) {
        throw new Error('Translation response has an invalid segment mapping.');
      }
      seen.add(value.id); mapped.set(value.id, value.text);
    }
    if (seen.size !== expectedIds.size) throw new Error('Translation response is missing a segment.');
    return mapped;
  }

  const api = { EXCLUDED_TAGS, isEligibleText, batch, validateResponse };
  root.BhashaCoreTranslatorCore = api;
  if (typeof module !== 'undefined') module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : window);
