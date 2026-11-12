# BhashaCore six-language localization audit

Date: 2026-11-12

## Fixed root cause

**PASS — homepage demonstration.** `frontend/src/pages/HomePage.tsx` contained a literal Hindi question, response, status and citation regardless of the active React interface language. It now reads from an explicit six-language, illustrative `HOME_DEMO` data set keyed by the existing `LanguageContext` language. The preview is labelled illustrative and is not represented as a live API response.

## Other changes

- **PASS — auth placeholders.** Name, email, password and confirmation inputs now use existing localization catalog values instead of English literals.
- **PASS — research page heading/subtitle.** The Research hub uses existing translated catalog entries instead of fixed English strings.
- **PASS — CSRF retained.** Interface-language changes continue to update through the protected same-origin API request; no CSRF exemption was reintroduced.
- **PASS — regression protection.** `tests/test_localization_audit.py` now ensures the homepage demo includes every supported interface language and is bound to the selected language.

## Browser verification

The actual built application was tested with Playwright using the sequence:

`English → Hindi → Telugu → Tamil → Kannada → Malayalam → English`

| Interface | Demo question changed | HTML language | Result |
|---|---:|---:|---|
| English | Yes | `en` | PASS |
| Hindi | Yes | `hi` | PASS |
| Telugu | Yes | `te` | PASS |
| Tamil | Yes | `ta` | PASS |
| Kannada | Yes | `kn` | PASS |
| Malayalam | Yes | `ml` | PASS |

The selected language persisted after refresh. Desktop and 390px mobile home/chat rendering succeeded with no observed browser console errors or failed requests in the completed smoke checks. Theme toggled dark → light without changing the selected interface language.

## AI and API verification

**PASS — genuine Sarvam responses.** Authenticated requests through local Gunicorn completed successfully for English, Hindi, Telugu, Tamil, Kannada and Malayalam. Each returned a terminal NDJSON `done` event, non-empty generated text and retrieved citations. This used the live configured provider, not mocked answers.

**PASS — API regression.** `/api/history`, `/api/guest-status`, `/api/load-chat`, and `/health` returned successful local responses. The existing authenticated stream persistence fix remained verified.

## Automated verification

- Backend suite: **147 passed**.
- TypeScript: **PASS**.
- Production Vite build: **PASS**. The only output is Vite’s non-fatal bundle-size warning.
- Python compilation: **PASS**.
- Localization catalogs: **PASS** — all six frontend catalogs contain 453 matching keys.

## Remaining deployment condition

The UI/localization work is ready locally. Public deployment remains blocked only by the already documented Supabase connection identity rejection (`tenant/user … not found`), not by localization or AI generation. Obtain the fresh connection string from the correct Supabase project and verify migrations before deploying.
