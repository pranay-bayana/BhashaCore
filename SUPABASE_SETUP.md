# Supabase PostgreSQL setup

## Application support

The application loads `.env` at WSGI startup without overriding values supplied
by the hosting environment. PostgreSQL URLs using `postgresql+psycopg://` are
accepted. Managed PostgreSQL connections use TLS (`sslmode=require`), a
10-second connection timeout, pool pre-ping, a pool of five connections, up to
five overflow connections, and a 30-second pool checkout timeout.

Production startup requires a PostgreSQL URL and refuses SQLite. It also
requires `FLASK_SECRET_KEY`, `REDIS_URL`, `TRUSTED_HOSTS`, and
`SESSION_COOKIE_SECURE=true`.

## Required environment values

Use the Supabase Session Pooler URL with the `postgresql+psycopg://` scheme in
`DATABASE_URL`. Keep the actual URL only in the hosting environment or the
ignored `.env` file. Set `TRUSTED_HOSTS` to the public hostname or a
comma-separated hostname list.

## Safe migration procedure

After rotating any exposed database password, run:

```sh
export FLASK_APP=src.app:app
flask db current
flask db upgrade
flask db current
```

The repository migrations create `users`, `conversations`, `messages`, and
`password_reset_tokens`, together with ownership indexes, foreign keys, unique
email enforcement, and cascading user-data deletion. Do not run `flask db
stamp` or generate a new initial migration against an existing Supabase
database.

## Verification

Use an authenticated, non-destructive check after password rotation:

```sh
python -c 'from sqlalchemy import create_engine, text; from src.app import app; engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], **app.config["SQLALCHEMY_ENGINE_OPTIONS"]); print(engine.connect().execute(text("SELECT 1")).scalar())'
```

Do not place connection URLs, credentials, or command output containing them in
issue trackers, reports, or Git.

## Current verification status

On 2026-11-01, remote verification stopped before authentication because the
ignored `DATABASE_URL` still contained the literal placeholder host
`YOUR_POOLER_HOST`, which DNS cannot resolve. No remote migration, schema
inspection, or data mutation occurred. Replace that placeholder with the exact
Supabase Session Pooler hostname from the Supabase Connect panel while keeping
the rotated password URL out of Git. Then run the verification command above.
