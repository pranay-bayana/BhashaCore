# BhashaCore Environment Configuration Reference

This document provides a complete reference for all environment variables supported and required by BhashaCore across development, testing, and production environments.

> [!IMPORTANT]
> Never commit actual credentials, API tokens, database passwords, or secret keys to source control. Use `.env` only for local development (which is excluded by `.gitignore`) and use the hosting provider's secrets manager (e.g., Render Environment Variables, Supabase Settings) in production.

---

## 1. Environment Variable Reference Table

| Variable Name | Required in Prod? | Default Value (Local) | Purpose & Description |
|---|---|---|---|
| `FLASK_SECRET_KEY` | **Yes** | Auto-generated in test | Cryptographic key used to sign session cookies, CSRF tokens, and flash messages. In Render, generated automatically via `generateValue: true`. |
| `APP_ENV` | **Yes** | `development` | Operating environment (`development`, `testing`, `production`). In production, enables TLS-aware cookies and proxy headers. |
| `DATABASE_URL` | **Yes** | `sqlite:///instance/...` | SQLAlchemy connection URL. In production, must be a managed PostgreSQL URL (e.g., Supabase Transaction Pooler: `postgresql+psycopg://...`). |
| `REDIS_URL` | **Yes** | `memory://` | Redis connection URL for distributed rate limiting across Gunicorn workers (e.g., `redis://...` or `rediss://...` for Upstash). |
| `SESSION_COOKIE_SECURE` | **Yes** | `false` | When `true`, enforces that session cookies are only transmitted over HTTPS connections. |
| `TRUSTED_HOSTS` | **Yes** | `127.0.0.1,localhost` | Comma-separated list of allowed hostnames (e.g., `bhashacore.onrender.com`). Rejects unauthorized `Host` header tampering. |
| `GENERATION_PROVIDER` | **Yes** | `sarvam` | Active LLM provider for live generation (`sarvam` or `nvidia`). |
| `SARVAM_API_KEY` | **Yes** | — | Secret API key for Sarvam AI. Obtainable from the [Sarvam AI Dashboard](https://dashboard.sarvam.ai). |
| `SARVAM_BASE_URL` | No | `https://api.sarvam.ai/v1` | Base endpoint URL for the Sarvam AI OpenAI-compatible chat API. |
| `SARVAM_MODEL` | No | `sarvam-105b-conversations` | Target generation model for chat responses. |
| `BHASHACORE_LLM_TIMEOUT` | No | `300.0` | Maximum timeout in seconds for generation provider API requests. |
| `BHASHACORE_MAX_TOKENS` | No | `1024` | Maximum token completion limit for assistant responses. |
| `APP_BASE_URL` | No | `http://127.0.0.1:8001` | Canonical public URL used when constructing password-reset links (e.g., `https://bhashacore.onrender.com`). |
| `EMAIL_PROVIDER` | No | `none` | Transactional email provider for password reset delivery (`resend` or `none`). |
| `EMAIL_API_KEY` | No | — | API key for the transactional email provider (e.g., Resend API key). |
| `EMAIL_FROM` | No | — | Sender email address for outgoing system emails (e.g., `noreply@bhashacore.com`). |
| `WEB_CONCURRENCY` | No | `1` | Number of Gunicorn worker processes. Pinned to `1` on Render Free tier to remain within 512 MB memory limit. |
| `PYTHON_VERSION` | No | `3.12.11` | Pinned Python runtime version for platform builders. |
| `NODE_VERSION` | No | `22.14.0` | Pinned Node.js runtime version for frontend build step. |
| `NVIDIA_API_KEY` | No | — | API key for NVIDIA NIM endpoints. Used only when running the offline research evaluation pipeline. |
| `NVIDIA_BASE_URL` | No | `https://integrate.api.nvidia.com/v1` | Endpoint URL for NVIDIA NIM evaluation models. |

---

## 2. Configuration Profiles

### 2.1 Local Development Profile (`.env`)

For local testing on your development machine:

```bash
# Core Application Settings
APP_ENV=development
FLASK_SECRET_KEY=local-dev-secret-key-replace-with-random-uuid
APP_BASE_URL=http://127.0.0.1:8001
TRUSTED_HOSTS=127.0.0.1,localhost

# Local Storage (SQLite is permitted only for local dev)
DATABASE_URL=sqlite:///instance/bhashacore_dev.sqlite3
REDIS_URL=memory://
SESSION_COOKIE_SECURE=false

# Live AI Provider (Sarvam AI)
GENERATION_PROVIDER=sarvam
SARVAM_API_KEY=your_actual_sarvam_api_key_here
SARVAM_MODEL=sarvam-105b-conversations
BHASHACORE_LLM_TIMEOUT=60
```

### 2.2 Production Cloud Profile (Render + Supabase + Upstash)

Configured securely within Render's Environment Variables dashboard:

```bash
# Core Environment
APP_ENV=production
PYTHON_VERSION=3.12.11
NODE_VERSION=22.14.0
WEB_CONCURRENCY=1
SESSION_COOKIE_SECURE=true
TRUSTED_HOSTS=bhashacore.onrender.com
APP_BASE_URL=https://bhashacore.onrender.com

# Persistence (Supabase Transaction Pooler, Port 6543)
DATABASE_URL=postgresql+psycopg://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require

# Distributed Rate Limiting (Upstash Redis)
REDIS_URL=rediss://default:YOUR_UPSTASH_TOKEN@YOUR_ENDPOINT.upstash.io:6379

# Production AI Provider (Sarvam AI)
GENERATION_PROVIDER=sarvam
SARVAM_API_KEY=your_production_sarvam_key
SARVAM_MODEL=sarvam-105b-conversations
SARVAM_BASE_URL=https://api.sarvam.ai/v1
```

---

## 3. How to Acquire External Service Credentials

### 3.1 Sarvam AI API Key
1. Navigate to the [Sarvam AI Platform](https://dashboard.sarvam.ai).
2. Sign in or create an account.
3. Access **API Keys** in the navigation menu.
4. Generate a new API key and set it as `SARVAM_API_KEY`.

### 3.2 Supabase PostgreSQL Database URL
1. Create a project at [Supabase](https://supabase.com).
2. Go to **Project Settings** $\rightarrow$ **Database** $\rightarrow$ **Connection Pooling**.
3. Select **Transaction Pooler** (Port `6543`).
4. Select the connection mode for `psycopg3` (`postgresql+psycopg://...`).
5. Replace `[YOUR-PASSWORD]` with your actual database password and assign to `DATABASE_URL`.

### 3.3 Upstash Redis URL
1. Sign in to [Upstash Console](https://console.upstash.com).
2. Create a Serverless Redis database in your closest region.
3. In the database details, copy the `rediss://...` connection string under **REST / Connection Strings**.
4. Assign to `REDIS_URL`.
