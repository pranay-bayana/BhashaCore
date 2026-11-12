# Production readiness report — 2026-11-03

## PASS

- Flask, Gunicorn, SQLAlchemy, Flask-Migrate, CSRF, secure-cookie guards, trusted-host guards, security headers, password hashing, password reset token lifecycle, account deletion, and conversation ownership enforcement are implemented and covered by deterministic tests.
- The Sarvam provider is selected through environment configuration and was exercised through the real local Flask/Gunicorn chat pipeline during guest browser verification.
- Guest sessions are server-managed and expiry-bound. Guest conversations are stored separately from account conversations, survive refresh/navigation, migrate into the account on sign-in/sign-up, and are protected by a three-successful-response server-side limit.
- Guest quota reservations use row locks and request fingerprints, preventing concurrent tabs/workers from issuing more than three reserved responses and preventing duplicate request consumption. Provider failures release the reservation without consuming quota.
- Migration `7a4f4fe9e7d2` adds `guest_sessions` and its expiry index. A fresh migration run reached this revision successfully.
- Full deterministic regression: **143 passed**. Frontend `npm run build` and `npm run lint` pass. Gunicorn production configuration check passes.

## BLOCKED

- Managed PostgreSQL has not been upgraded with the new guest-session migration in this execution. Apply `flask --app wsgi db upgrade` against the deployment database after taking the normal backup.
- Redis-backed rate limiting has not been verified against a live Redis service with multiple production workers.
- Real password-reset email delivery is not verified without configured email provider credentials.
- Public HTTPS hosting, backups, and managed-service recovery checks require the selected hosting environment.

## NOT VERIFIED

- A complete external security scan and penetration test.
- Full held-out multilingual quality scoring for the current Sarvam model.

## Local production-style commands

```sh
set -a; source .env; set +a
export APP_ENV=production
export SESSION_COOKIE_SECURE=true
export REDIS_URL='redis://HOST:6379/0'
export TRUSTED_HOSTS='app.example.com'
flask --app wsgi db upgrade
gunicorn --config gunicorn.conf.py wsgi:app
```

## Verdict

**READY WITH EXTERNAL BLOCKERS.** The application code and local production checks pass. A public launch still requires the listed managed infrastructure verification and deployment configuration.
