# BhashaCore Web Translator

An installable Chrome Manifest V3 extension that translates visible webpage text through BhashaCore's server-side Sarvam integration. It supports English, हिन्दी, తెలుగు, தமிழ், ಕನ್ನಡ, and മലയാളം.

## What it does

- Translates visible headings, paragraphs, navigation labels, buttons, tables, title attributes, accessible labels, and safe placeholders.
- Preserves text-node and attribute originals in the current page only; **Restore Original** returns the page to its prior state.
- Batches at most 40 segments / 12,000 source characters per backend request; it never sends a full HTML document.
- Watches controlled dynamic DOM additions while translated, with debouncing and loop prevention.
- Does not translate scripts, styles, code blocks, hidden elements, input values, password fields, contenteditable regions, or elements marked `data-bhashacore-translate-exclude`.
- Has an optional auto-translate setting and an optional isolated Shadow-DOM floating control.

## Architecture and privacy

`popup → MV3 service worker → injected content script → POST /api/translate → Sarvam AI`

The extension has no Sarvam, database, or BhashaCore secret. The backend receives short text segments only after an explicit Translate action, unless the user opts into auto-translate. Originals stay in memory in the page and are discarded when the page unloads. The translation endpoint does not use RAG, conversations, or the chat guest quota; it rate-limits translation separately.

The extension requests only `activeTab`, `scripting`, and `storage` by default. Enabling auto-translate triggers Chrome's optional site-access permission prompt, because translating future pages requires injection permission beyond the currently active tab. Its network access is limited to the production BhashaCore origin and documented local-development origins. It does not read browsing history or transmit analytics.

## Install locally

1. Deploy the backend version containing `POST /api/translate`. For local-only testing, set the extension's `apiBaseUrl` in its service-worker console to `http://127.0.0.1:8001`; the extension accepts only this documented local URL or the BhashaCore production URL.
2. Open Chrome and visit `chrome://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select this `browser-extension` directory.
6. Pin **BhashaCore Web Translator**.
7. Open a normal HTTP(S) website (Chrome internal pages are intentionally unavailable).
8. Select a target language and click **Translate Page**.
9. Click **Restore Original** to restore the website text.

## Development checks

```bash
cd browser-extension
npm test
npm run check
```

## Status meanings

- **Original:** no tracked page translation is active.
- **Translating:** batches are in flight.
- **Translated:** every submitted batch returned a validated, complete mapping.
- **Partially translated:** at least one batch safely failed; originals remain available.
- **Failed:** no batch completed. Retry manually after checking the displayed error.

## Troubleshooting and limitations

- The extension cannot run on `chrome://`, the Chrome Web Store, PDFs, or other browser-restricted pages.
- Some sites render text inside closed shadow roots, canvases, or cross-origin frames; those areas cannot be safely translated by a content script.
- The backend must be deployed with a valid `SARVAM_API_KEY`; a provider failure results in a visible retryable error and does not alter original text.
- Auto-translate sends visible page text to BhashaCore on each loaded eligible page. Keep it disabled if that is not desired.
- This project is not published to the Chrome Web Store.
