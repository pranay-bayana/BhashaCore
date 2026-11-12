# BhashaCore

BhashaCore is a multilingual Indian-language research chatbot and evaluation platform. It supports English, Hindi, Telugu, Tamil, Kannada, and Malayalam with BM25 retrieval, citation provenance, Romanized Indic input handling, and Sarvam-backed live generation.

## Architecture

- **Flask** provides APIs, authentication, CSRF, rate limits, migrations, and the production web server entry point.
- **React + TypeScript + Vite** provides the single-page interface in `frontend/src`; Flask serves the production build from `frontend/dist`.
- **PostgreSQL + SQLAlchemy + Alembic** store accounts and authenticated conversations. Guest conversations are expiry-bound server-side sessions.
- **Redis** is required in production for shared rate limits.
- **BM25** retrieval uses the checked-in research corpus and results in `data/`, `results/`, and `report/`.

## Repository layout

```text
src/          Flask app, auth, retrieval, provider, translations
frontend/     React source and Vite configuration
migrations/   Alembic migration history
tests/        Automated backend and browser checks
scripts/      Reproducible ingestion and evaluation utilities
data/         Research datasets and processed knowledge pools
results/      Evaluation outputs
report/       Research report and supporting figures
```

## Setup

```sh
scripts/dev_setup.sh
```

Configure `.env` locally. It is ignored by Git. At minimum, configure the database URL, Flask secret, Sarvam credentials, and public base URL for the environment you are running.

## Development

```sh
scripts/dev_start.sh
```

This starts the combined Flask + built React application on port `8001` by
default. The setup script reuses an existing `.venv` and never deletes `.env`,
databases, local user data, or development configuration.

For frontend iteration, run `npm run dev` inside `frontend/`. The Vite server proxies API requests to the Flask server on port 8001.

## Testing

```sh
pytest -q
cd frontend && npm run lint && npm run build
```

Tests cover authentication, CSRF, conversation ownership, guest quotas, retrieval, citations, languages, migrations, and provider behavior. Browser verification results are recorded in [E2E_TEST_REPORT.md](E2E_TEST_REPORT.md).

## Production deployment

Set `APP_ENV=production` and configure all of the following outside source control:

```text
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://...
FLASK_SECRET_KEY=...
SESSION_COOKIE_SECURE=true
TRUSTED_HOSTS=app.example.com
GENERATION_PROVIDER=sarvam
SARVAM_API_KEY=...
SARVAM_MODEL=sarvam-105b-conversations
EMAIL_PROVIDER=resend
EMAIL_API_KEY=...
EMAIL_FROM=...
APP_BASE_URL=https://app.example.com
```

Build the frontend, then apply migrations before starting Gunicorn:

```sh
cd frontend && npm ci && npm run build && cd ..
flask --app wsgi db upgrade
gunicorn --config gunicorn.conf.py wsgi:app
```

See [DEPLOYMENT.md](DEPLOYMENT.md), [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md), and [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md) for verified status and remaining infrastructure work.

## Research reproducibility

The datasets, processed pools, results, and report figures are retained for reproducibility. Use `python -m src.run_pipeline --help` to inspect supported pipeline stages. Evaluation and ingestion utilities in `scripts/` are kept only where they reproduce research inputs or reported measurements.
