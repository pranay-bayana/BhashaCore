# Deployment

## Required configuration

Set `FLASK_SECRET_KEY` to a unique high-entropy value and set `DATABASE_URL`
to a managed PostgreSQL database using the `postgresql+psycopg://` SQLAlchemy
scheme. Do not use the SQLite fallback for deployed user data. Configure
`NVIDIA_API_KEY` only in the server environment.

## Database migration

The initial migrations are already present in source control. On a new or
existing environment, inspect and apply them without creating a duplicate
initial migration:

```sh
export FLASK_APP=src.app:app
flask db current
flask db upgrade
flask db current
```

For Supabase Session Pooler configuration, connection safety, and the required
credential-rotation procedure, see `SUPABASE_SETUP.md`.

Run `flask db upgrade` before starting the application in every environment. The models define unique
email addresses, foreign keys, conversation ownership indexes, and cascading
deletion. Back up PostgreSQL and configure durable storage for knowledge assets
and any future uploads; the application filesystem is not user-data storage.

## Start and health checks

```sh
gunicorn --config gunicorn.conf.py wsgi:app
curl -fsS http://127.0.0.1:8001/health
```

Terminate TLS at the load balancer, redirect HTTP to HTTPS, set
`SESSION_COOKIE_SECURE=true`, and set `TRUSTED_HOSTS` to the public hostnames
(comma-separated). Restrict trusted proxy headers at the hosting platform, and
use an application firewall or reverse-proxy rate limit. Password
reset delivery requires a configured transactional email provider. Email
verification is deliberately not part of this application.

Password reset token generation is implemented. Configure `EMAIL_PROVIDER`,
`EMAIL_API_KEY`, `EMAIL_FROM`, and `APP_BASE_URL`. The existing delivery
adapter supports `EMAIL_PROVIDER=resend`; verify a controlled delivery before
enabling public reset-email traffic.

Set `REDIS_URL` in production. Flask-Limiter uses it for shared rate-limit
state across Gunicorn workers. Current application limits are 5 sign-ups/hour,
10 sign-ins/hour, and 20 chat generations/hour per client IP; adjust them for
your traffic and provider budget.
