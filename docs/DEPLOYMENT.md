# BhashaCore Deployment & Production Operations Guide

This guide details the complete deployment process for BhashaCore across local development, staging environments, and production hosting on **Render** with **Supabase PostgreSQL**, **Upstash Redis**, and **Sarvam AI**.

---

## 1. System Requirements & Prerequisites

| Component | Minimum Version | Recommended / Production |
|---|---|---|
| **Python** | 3.12.0 | 3.12.11 (Managed via `.python-version`) |
| **Node.js** | 20.0.0 | 22.14.0 (Managed via `package.json` / Render blueprint) |
| **npm** | 10.0.0 | 10.9.0+ |
| **PostgreSQL** | 15.0 | Supabase Managed PostgreSQL (pg15+) |
| **Redis** | 6.0 | Upstash Redis (TLS enabled) |
| **Memory** | 512 MB | 512 MB (Render Free Web Service limit) |
| **Disk** | 1 GB | 1 GB free space for BM25 pools and runtime assets |

---

## 2. Local Development Setup

### 2.1 Automated Setup

The repository provides an idempotent bootstrap script:

```bash
# Clone the repository
git clone https://github.com/pranay-bayana/BhashaCore.git
cd BhashaCore

# Run automated development setup
chmod +x scripts/dev_setup.sh scripts/dev_start.sh
./scripts/dev_setup.sh
```

### 2.2 Manual Step-by-Step Setup

If setting up manually without shell scripts:

```bash
# 1. Create and activate a Python 3.12 virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip and install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install frontend dependencies and build assets
cd frontend
npm ci
npm run build
cd ..

# 4. Configure local environment variables
cp .env.example .env
# Edit .env and supply your FLASK_SECRET_KEY, DATABASE_URL, and SARVAM_API_KEY

# 5. Initialize or upgrade database schema
flask --app wsgi db upgrade

# 6. Verify runtime RAG assets
python scripts/verify_runtime_assets.py
```

### 2.3 Starting Local Development Servers

#### Option A: Unified Full-Stack Server (Recommended)
Runs Flask serving both API endpoints and the built frontend on port `8001`:

```bash
./scripts/dev_start.sh
# Accessible at http://127.0.0.1:8001
```

#### Option B: Split Development (Frontend Hot Reloading)
For rapid frontend UI iteration with Vite Hot Module Replacement (HMR):

```bash
# Terminal 1: Start Flask Backend API
source .venv/bin/activate
python src/app.py --port 8001

# Terminal 2: Start Vite Dev Server
cd frontend
npm run dev
# Accessible at http://127.0.0.1:5173 (proxies /api to localhost:8001)
```

---

## 3. Database Configuration & Migrations

### 3.1 Supabase PostgreSQL Configuration

For cloud deployments on Supabase, configure the connection URL using the **Transaction Pooler** endpoint on port `6543`:

```text
DATABASE_URL=postgresql+psycopg://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:6543/postgres?sslmode=require
```

#### Pooler Safety Guidelines:
- **Use the Transaction Pooler (Port 6543):** Required for serverless and auto-scaling web workers.
- **Disabled Server-Side Prepared Statements:** SQLAlchemy is configured with `prepare_threshold=None` in `psycopg` to prevent prepared-statement collision across pooled connection handoffs.
- **Transaction Cleanliness:** All database sessions commit or rollback cleanly within request teardown handlers.

### 3.2 Executing Migrations

Schema lifecycle is managed via Flask-Migrate and Alembic:

```bash
export FLASK_APP=wsgi:app

# Inspect current database revision
flask db current

# Apply all pending migrations non-destructively
flask db upgrade

# Verify migration status
flask db current
```

> [!CAUTION]
> Never execute `flask db stamp`, `db.drop_all()`, or `flask db init` against a remote production database. All schema changes must follow the committed Alembic migration chain in `migrations/versions/`.

---

## 4. Production Deployment on Render

BhashaCore is configured for continuous deployment on **Render** via `render.yaml`.

### 4.1 Render Blueprint Architecture

```yaml
services:
  - type: web
    name: bhashacore
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt && npm ci --prefix frontend && npm run build --prefix frontend
    startCommand: flask --app wsgi db upgrade && gunicorn --config gunicorn.conf.py wsgi:app
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: APP_ENV
        value: production
      - key: PYTHON_VERSION
        value: 3.12.11
      - key: NODE_VERSION
        value: 22.14.0
      - key: WEB_CONCURRENCY
        value: "1"
      - key: GENERATION_PROVIDER
        value: sarvam
      - key: SARVAM_MODEL
        value: sarvam-105b-conversations
      - key: SESSION_COOKIE_SECURE
        value: "true"
      - key: FLASK_SECRET_KEY
        generateValue: true
```

### 4.2 Handling Render Free Tier Constraints

1. **512 MB RAM Ceiling (`WEB_CONCURRENCY=1`):**
   Render Free instances provide 512 MB of RAM. To prevent Out-Of-Memory (OOM) termination during concurrent requests, `WEB_CONCURRENCY` is pinned to `1` in `render.yaml`. Gunicorn runs 1 worker with multiple asynchronous event threads.
2. **Embedded Migrations in `startCommand`:**
   Render Free instances do not support separate `preDeployCommand` hooks. BhashaCore embeds non-destructive Alembic migrations directly in the service startup command:
   ```bash
   flask --app wsgi db upgrade && gunicorn --config gunicorn.conf.py wsgi:app
   ```
3. **Cold-Start Latency:**
   Render Free services spin down after 15 minutes of inactivity. When a new request arrives, service wake-up requires 30–60 seconds. The frontend displays graceful connection spinners and retries automatically.
4. **Health Check Route (`/health`):**
   Render polls `/health` to confirm deployment readiness. The health check executes a database ping (`SELECT 1`) and verifies that all 6 BM25 language pools are loaded into memory.

---

## 5. Redis Setup (Upstash)

In production, multi-worker rate limiting requires a centralized Redis instance:

1. Create a free Redis database at [Upstash](https://upstash.com).
2. Copy the TLS Redis connection string (`rediss://...`).
3. Set the `REDIS_URL` environment variable in Render.
4. Flask-Limiter uses Redis to enforce per-IP throttling:
   - User Sign-Up: 5 per hour
   - User Sign-In: 10 per hour
   - Chat Generation: 20 per hour

---

## 6. Pre-Flight Verification & Health Checks

Before promoting any release to production, run the verification suite:

```bash
# 1. Verify runtime RAG assets
python scripts/verify_runtime_assets.py

# 2. Run backend test suite
pytest -q

# 3. Verify frontend build and TypeScript compilation
cd frontend && npm run lint && npm run build && cd ..

# 4. Check live deployment health
curl -fsS https://bhashacore.onrender.com/health
```

Expected output from `/health`:
```json
{
  "status": "ok",
  "environment": "production",
  "database": "connected",
  "provider": "sarvam",
  "model": "sarvam-105b-conversations",
  "pools_verified": ["en", "hi", "ta", "te", "kn", "ml"]
}
```
