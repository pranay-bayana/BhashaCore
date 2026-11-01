# Security audit — 2026-11-01

## PASS

- Passwords use Werkzeug hashes; reset tokens are random, hashed at rest,
  expire after one hour, and are single-use.
- CSRF protects state-changing forms and same-origin AJAX requests.
- Authorization queries scope conversations to the authenticated owner.
- Account deletion requires password reauthentication and cascades owned data.
- Security headers, path validation, secure session defaults, and rate limits
  are covered by deterministic tests.
- Production startup fails closed without a secret, a PostgreSQL `DATABASE_URL`,
  Redis, `TRUSTED_HOSTS`, or `SESSION_COOKIE_SECURE=true`; anonymous chat is disabled there.
- `.env` and common secret-file formats are Git-ignored, while `.env.example`
  remains tracked with placeholders. Alembic redacts database passwords from
  offline configuration state.

## PARTIAL

- Resend password-reset delivery is implemented and mock-tested. No real email
  delivery has been performed.

## BLOCKED

- The Supabase password described as previously exposed must be rotated before
  any database authentication, migration, or persistence test. Production
  Redis, TLS/proxy policy, and external penetration testing need deployed
  infrastructure.

## NOT IMPLEMENTED

- None of the application-level security controls identified in this release
  loop are intentionally absent. Dependency scanning is a release-pipeline
  task and has not been run here.
