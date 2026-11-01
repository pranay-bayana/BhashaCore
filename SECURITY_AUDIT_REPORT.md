# Security audit — 2026-11-01

## Remediated

- Path traversal in file-backed anonymous chat-session IDs.
- Malformed JSON and numeric pagination server errors.
- Production debug output from chat processing.
- Password storage using Werkzeug hashes.
- CSRF for forms and same-origin AJAX/API requests.
- Session cookie HTTP-only and SameSite flags; production requires secure cookies.
- Security headers: CSP, frame denial, MIME sniff prevention, referrer policy, permissions policy, and HSTS when HTTPS is detected.
- SQLAlchemy parameterized queries and conversation ownership checks.
- IP-based login/signup/chat rate limits; production requires Redis shared storage.
- One-time, hashed password-reset tokens with one-hour expiry and account-enumeration-safe request messaging.
- Password-reset delivery adapter supports Resend and was tested with a deterministic HTTP mock; real delivery requires configured provider credentials.
- Production startup rejects missing secrets, Redis, PostgreSQL URLs, trusted hosts, or a secure-cookie setting; it also disables anonymous chat.

## Required before public launch

- Set `FLASK_SECRET_KEY`, `SESSION_COOKIE_SECURE=true`, `TRUSTED_HOSTS`, managed PostgreSQL, and Redis in the deployment environment.
- Configure TLS termination and trusted-proxy policy at the hosting layer.
- Configure a Resend account using `EMAIL_API_KEY`, `EMAIL_FROM`, and HTTPS `APP_BASE_URL`; the adapter and token lifecycle are implemented.
- Run dependency vulnerability scanning and external penetration testing as part of the deployment release process.
