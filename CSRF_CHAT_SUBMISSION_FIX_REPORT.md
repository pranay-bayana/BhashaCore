# CSRF chat-submission repair report

Date: 2026-11-04

## Root cause

Flask correctly rotates the signed session on login/logout. The frontend then
called `clearCsrfToken()`, but its next token lookup read the `<meta>` token
embedded in the pre-login page. That token was signed for the old session, so
the first streaming `/api/chat` request after authentication was rejected by
Flask-WTF with a 400 CSRF error.

## Changes

- `frontend/src/services/api.ts`
  - Tracks session-rotation state separately from the cached token.
  - Fetches `/api/csrf-token` with same-origin credentials after any rotation,
    bypassing both cache and page metadata.
  - Streaming chat retries once only when the server reports `csrf_invalid`.
    This is safe: CSRF validation happens before chat persistence, quota
    reservation, retrieval, or provider generation.
- `frontend/src/pages/AuthModal.tsx`
  - Fetches and stores a fresh token from the new session before it reports a
    successful sign-in/sign-up to the rest of the app.
- `src/app.py`
  - API CSRF failures now return structured JSON:
    `{"error":"csrf_invalid", "message": ...}`. HTML endpoints retain their
    normal CSRF page response.

CSRF remains enabled for chat, authentication, history mutations, settings,
and account actions. No API endpoint was exempted to mask the error.

## Verification

| Check | Result |
| --- | --- |
| CSRF backend/auth/guest regression | PASS — 20 passed |
| Full deterministic backend suite | PASS — 145 passed |
| Python compilation | PASS |
| TypeScript check | PASS |
| Production frontend build | PASS |
| Real browser JSON sign-in endpoint | PASS — HTTP 200 verified in Playwright |
| Browser refresh session check | PASS — authenticated `/api/auth/me` response after network idle |
| CSRF error response format | PASS — JSON code/message returned for `/api/*` mutations |

The browser’s first mutation after a session transition now gets a freshly
issued token. If a tab races a session transition, it receives at most one
pre-provider CSRF retry; no duplicate provider call, guest reservation, or
message persistence can occur.
