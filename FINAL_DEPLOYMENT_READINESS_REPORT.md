# BhashaCore final deployment readiness report

Date: 2026-11-12

## Verdict

**READY WITH ONE EXTERNAL DEPLOYMENT BLOCKER.** The application is working end-to-end locally with its production build, Gunicorn, SQLite development database, genuine Sarvam generation, and all six supported languages. It must not be deployed using the currently configured Supabase URL: that remote service rejects the database identity before a query can run.

## Root causes fixed

1. **`/api/history`, `/api/guest-status`, and `/api/load-chat` returned HTTP 500.** They all create/read server-side persistence. The configured Supabase Transaction Pooler returned `FATAL: tenant/user … not found`; the failure happened before SQLAlchemy could execute `SELECT 1`.
2. **Completed chat streams were cut off.** Gunicorn consumed the NDJSON generator after Flask had released the request context. The assistant answer reached the browser, then the final database persistence raised `RuntimeError: Working outside of application context`, terminating the HTTP chunked response.
3. **Interface-language persistence endpoint was CSRF-exempt.** This was inconsistent with the rest of the application’s protected state-changing API contract.

## Fixes implemented

- Added a SQLAlchemy error handler returning a safe `503 database_unavailable` JSON response instead of an unexplained 500. It does not fall back to local storage in production.
- Made `/health` perform a bounded `SELECT 1`, so a load balancer will not declare an application healthy while its required persistence backend is unavailable.
- Changed the stream’s final authenticated-message write to execute in an explicit application context. This preserves a complete NDJSON response and conversation persistence under Gunicorn without retaining request context beyond its lifetime.
- Added a regression test for the stream completion/persistence sequence.
- Removed CSRF exemption from `/api/set-interface-lang`; the React localization provider now fetches and sends the CSRF token with same-origin credentials.
- Updated `scripts/dev_start.sh` so local SQLite is an explicit opt-in (`BHASHACORE_USE_LOCAL_DB=true`). A configured remote `DATABASE_URL` is never silently replaced.

Changed files in this stabilization pass:

- `src/app.py`
- `frontend/src/localization/LanguageContext.tsx`
- `scripts/dev_start.sh`
- `tests/test_auth.py`

## Actual verification

| Check | Result |
|---|---|
| `/health`, `/api/guest-status`, `/api/history`, `/api/load-chat` on local Gunicorn | PASS — all returned correct responses; history and loaded conversation were persisted |
| Authenticated signup and session persistence | PASS — real HTTP session used |
| Sarvam streaming through Flask/Gunicorn | PASS — completed real responses, not mocks |
| English, Hindi, Telugu, Tamil, Kannada, Malayalam | PASS — each produced an HTTP 200 terminal `done` event, non-empty answer, and citations |
| Browser desktop check | PASS — language change and refresh persisted; chat view rendered; zero console errors and request failures |
| Browser mobile check | PASS — chat composer rendered at 390×844 |
| Rendered localization audit | PASS — all six languages rendered their catalog title and chat navigation; no checked raw localization keys or console errors |
| Language-change CSRF | PASS — missing token returned `400 csrf_invalid`; valid same-session token returned 200 and persisted Telugu |
| Alembic local migration state | PASS — `7a4f4fe9e7d2 (head)` |
| Backend deterministic suite | PASS — 146 passed |
| Frontend TypeScript check | PASS |
| Production frontend build | PASS — only Vite’s non-fatal large-chunk warning |
| Python compilation | PASS |
| Production required-secret guard | PASS — startup refuses production without `FLASK_SECRET_KEY` |
| Production database outage behavior | PASS — health correctly returns `503 database_unavailable` for an unreachable configured PostgreSQL host |

## Remote PostgreSQL / Supabase status

**BLOCKED — external configuration.** TLS/DNS connectivity reaches the Supabase pooler, but both configured ports 5432 and 6543 reject the supplied identity with `tenant/user … not found`. This is not a migration, application-query, prepared-statement, or Flask issue. No remote migration, stamp, drop, truncation, or schema change was performed.

Before deployment, copy a fresh connection string from the intended Supabase project’s **Connect** panel into the hosting platform’s `DATABASE_URL`, then run:

```bash
flask --app wsgi db current
flask --app wsgi db upgrade
```

Only run the upgrade after `flask db current` identifies the actual remote revision. Never use `stamp` or destructive schema commands to work around this error.

## Deployment checklist

Set the following only in the hosting provider’s secret/environment configuration:

- `APP_ENV=production`
- a strong unique `FLASK_SECRET_KEY`
- the corrected PostgreSQL `DATABASE_URL`
- a reachable `REDIS_URL`
- `SESSION_COOKIE_SECURE=true`
- `TRUSTED_HOSTS` containing the real public hostname(s)
- `GENERATION_PROVIDER=sarvam`, `SARVAM_API_KEY`, and `SARVAM_MODEL=sarvam-105b-conversations`
- `APP_BASE_URL` set to the public HTTPS URL
- email-provider values when password-reset delivery is enabled

Deploy with:

```bash
gunicorn --config gunicorn.conf.py wsgi:app
```

Terminate TLS at the hosting platform/reverse proxy and route its health check to `/health`. In production anonymous chat is intentionally disabled; users must authenticate so conversations remain attributable and durable.

## Remaining blocker

The sole current blocker is the rejected Supabase database identity. Until a valid remote PostgreSQL URL is configured and migrations are verified there, public deployment is **not yet safe** despite the working local application.
