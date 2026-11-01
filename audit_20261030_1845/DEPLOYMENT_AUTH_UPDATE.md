# Deployment-ready persistence and authentication update

## Implemented

- SQLAlchemy models for `users`, `conversations`, and `messages`.
- PostgreSQL-ready `DATABASE_URL` configuration with `psycopg`, connection
  pre-ping, foreign keys, unique user emails, and ownership indexes.
- Alembic/Flask-Migrate initial migration:
  `migrations/versions/ac522193ac45_initial_users_conversations_messages.py`.
- Werkzeug password hashing, sign-up, sign-in, sign-out, protected `/chat` and
  `/settings` routes, and secure session-cookie defaults.
- Authenticated conversation persistence and ownership checks on chat loading.
- Regression test that a second user receives 404 when trying to load the
  first user's conversation.
- Gunicorn entry point, environment template, and deployment instructions.

## Verified

- `flask db upgrade` succeeds against a clean SQLite development database.
- Production app import succeeds after migration.
- Authentication and ownership tests: 3 passed.
- Validation, session safety, and language utility regression selection: 10
  passed.

## Still required before public deployment

- Supply managed PostgreSQL through `DATABASE_URL` and run the existing
  migration there.
- Set a persistent high-entropy `FLASK_SECRET_KEY` and enable secure cookies
  behind HTTPS.
- Add an email delivery provider before advertising verification or password
  reset.
- Complete CSRF tokens and rate limiting before exposing login endpoints to
  the public internet.
- Complete six-language localization for the newly added landing, auth, and
  settings pages; existing translated application pages remain intact.
- Verify NVIDIA NIM live inference separately; the current provider remains
  configured but unverified due to slow/hanging calls.
