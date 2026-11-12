# Final localization audit

Date: 2026-11-12

## Root cause

The React application had complete catalog key parity but several presentation components bypassed `useLanguage()` with literal English data. The most visible cases were the Hindi-fixed homepage preview and hardcoded About methodology cards, scoring scale, pipeline labels, modal content, footer labels, and research heading.

## Changes

- `frontend/src/pages/HomePage.tsx`
  - Replaced the fixed Hindi preview with a clearly illustrative, language-keyed six-language preview.
  - Localized surrounding script labels while preserving native script identifiers.
- `frontend/src/pages/AboutPage.tsx`
  - Replaced visible hardcoded methodology, scoring, metric, pipeline, limitation, language-card and modal labels/descriptions with existing catalog-backed values.
- `frontend/src/pages/ResearchPage.tsx`
  - Localized the research workspace heading and description.
- `frontend/src/components/layout/Footer.tsx`
  - Localized the non-brand footer labels.
- `frontend/src/pages/AuthModal.tsx`
  - Localized name, email, password and confirmation placeholders.
- `tests/test_localization_audit.py`
  - Added a regression assertion that each supported interface language has a homepage preview and that the preview is bound to the current language.

## Verification

| Area | English | Hindi | Telugu | Tamil | Kannada | Malayalam |
|---|---|---|---|---|---|---|
| Catalog parity (453 keys per locale) | PASS | PASS | PASS | PASS | PASS | PASS |
| Homepage demonstration changes with interface | PASS | PASS | PASS | PASS | PASS | PASS |
| Navigation, chat input and common labels | PASS | PASS | PASS | PASS | PASS | PASS |
| About visible methodology/scoring/pipeline/disclaimer labels | PASS | PASS | PASS | PASS | PASS | PASS |
| Research headings and tabs | PASS | PASS | PASS | PASS | PASS | PASS |
| Refresh persistence | PASS | PASS | PASS | PASS | PASS | PASS |

The browser sequence was tested in this order: English → Hindi → Telugu → Tamil → Kannada → Malayalam → English. Hindi About was explicitly inspected after the fix: the prior visible literals `Quantitative Scoring`, `Failure when Score`, `Honest Research Disclaimers`, `Input Normalization`, `Lexical Retrieval`, and `Click any language card` were absent. Browser console errors: 0.

## Independent language settings

Interface language continues to be client-localized and persists independently of the chat input/answer language fields. No AI model, retrieval, authentication, CSRF, or response-language configuration was changed.

## Test results

- Full backend and localization suite: **147 passed**.
- Frontend TypeScript: **PASS**.
- Production Vite build: **PASS** (non-fatal bundle-size warning only).
- Genuine Sarvam six-language generation remains verified from the preceding stabilization run.

## Remaining deployment note

No localization blocker remains in the fixed visible UI paths. The previously documented external Supabase connection identity issue remains the only deployment blocker.
