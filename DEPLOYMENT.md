# Deployment

## Required configuration

Set `APP_ENV=production`, `FLASK_SECRET_KEY` to a unique high-entropy value and set `DATABASE_URL`
to a managed PostgreSQL database using the `postgresql+psycopg://` SQLAlchemy
scheme. Do not use the SQLite fallback for deployed user data. Configure
provider credentials only in the server environment. BhashaCore's production
configuration uses `GENERATION_PROVIDER=sarvam`, `SARVAM_API_KEY`, and
`SARVAM_MODEL=sarvam-105b-conversations`.

## Render

The repository contains `render.yaml`. Create a Render Blueprint from the
repository, enter the values marked `sync: false` in Render's secret UI, and
keep them out of Git. Render builds the React application into `frontend/dist`,
applies any pending Alembic migrations at service boot, then starts Gunicorn.

Render uses the committed `.python-version` (and matching Blueprint
`PYTHON_VERSION`) to avoid an unexpected platform-default Python upgrade.

```sh
# Render build command
pip install -r requirements.txt && npm ci --prefix frontend && npm run build --prefix frontend

# Render start command (includes non-destructive migration before Gunicorn boot)
flask --app wsgi db upgrade && gunicorn --config gunicorn.conf.py wsgi:app
```

Render's health check is `/health`. It performs a database ping and loads all
six BM25 pools, so a 200 response means both persistence and RAG assets are
available. Do not point the health check at a route that bypasses either.

### Runtime RAG assets

The deployment includes only `data/processed/pool_<lang>.jsonl` and
`data/processed/eval_<lang>.jsonl` for `en`, `hi`, `te`, `ta`, `kn`, and `ml`,
plus the compact optional `pool_<lang>_knowledge.jsonl` files. Raw source
corpora remain ignored. Production startup explicitly fails with an actionable
error if any required pool or evaluation map is missing or empty.

Check these assets locally before pushing:

```sh
python scripts/verify_runtime_assets.py
```

For Supabase, use the Transaction Pooler endpoint on port `6543`. The
application requires TLS and disables psycopg server-side prepared statements
so requests remain safe when the pooler assigns different backend sessions.

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

For the Render Free plan (which does not support `preDeployCommand`), database
migration is embedded directly in the start command:

```sh
flask --app wsgi db upgrade && gunicorn --config gunicorn.conf.py wsgi:app
```

`WEB_CONCURRENCY=1` is configured to keep memory consumption safely within the
512 MB free instance limit. The migration is non-destructive and uses the existing
Alembic revision chain. Inspect `flask --app wsgi db current` against Supabase
before the first deployment; never use `stamp`, `drop_all`, or `db init` against
the remote database.
