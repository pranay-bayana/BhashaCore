# Authentication and guest-quota repair report

Date: 2026-11-04

## Root cause

The Flask quota gate was already server-side and correctly skipped its guest
reservation path when `current_user()` returned an authenticated user. The
fault was in the React authentication modal:

1. It submitted credentials to the HTML `/signin` and `/signup` routes.
2. `fetch()` followed redirects and treated any final `200` HTML response as a
   successful sign-in, including an unchanged anonymous session.
3. The UI then displayed an account profile based on typed form values while
   `/api/chat` correctly treated the browser as a guest and returned
   `guest_quota_exceeded`.

There was also a race in `ChatPage`: a guest-status request started before
authentication resolved could finish later and re-apply its exhausted guest
state to an authenticated UI.

## Fixes

- `frontend/src/pages/AuthModal.tsx`
  - Uses `/api/auth/signin` and `/api/auth/signup` JSON endpoints.
  - Requires the returned authenticated `user` object before updating UI state.
  - Shows the server's safe error message instead of treating a redirect/page
    load as success.
- `frontend/src/services/api.ts`
  - Clears the cached CSRF token after session-changing login/logout actions.
- `frontend/src/pages/ChatPage.tsx`
  - Cancels stale guest-status updates when auth state changes.
  - Clears guest count/quota state for an authenticated user and reloads
    history when identity changes.
- `src/app.py`
  - Login/signup now discard the browser's guest reference rather than moving
    guest conversations into an account. Authenticated conversations therefore
    belong only to the authenticated account; guest history stays isolated.
  - Logout clears the session, so the next anonymous visit receives a fresh
    guest trial.
- `scripts/dev_setup.sh` and `scripts/dev_start.sh`
  - Reuse an existing `.venv`, preserve `.env`, databases and local data, and
    start the built Flask/React app on port 8001.

## Regression coverage

`tests/test_auth.py` and `tests/test_guest_session_continuity.py` now cover:

1. An exhausted guest signs in and is no longer quota limited.
2. The authenticated user completes five messages.
3. Guests are capped at three successful messages.
4. Failed generation releases its reservation and consumes no guest quota.
5. Login after quota exhaustion unlocks server-side chat immediately.
6. Auth status survives subsequent session checks/refresh.
7. Logout returns the browser to a new guest session with a 0/3 trial.
8. Guest conversations remain outside authenticated account history.

## Verification

| Check | Result |
| --- | --- |
| Focused auth + guest regression | PASS — 18 passed |
| Full deterministic backend suite | PASS — 145 passed |
| Python compilation | PASS |
| TypeScript check | PASS |
| Production frontend build | PASS |
| Browser JSON sign-in | PASS — `/api/auth/signin` returned HTTP 200 with an authenticated user |
| Browser refresh after sign-in | PASS — `/api/auth/me` remained authenticated after network idle |
| Browser mobile composer | PASS — visible at 390px |
| Flask startup on port 8001 | PASS — fresh Gunicorn pool health check passed |

## Local versus production readiness

The local setup is ready: `.venv`, `.env`, databases and local user data are
ignored by Git and are not removed by the supplied setup script. Production
still requires the documented external PostgreSQL, Redis, email, HTTPS,
trusted-host and Sarvam configuration; local success does not claim those
provider deployments are configured.
