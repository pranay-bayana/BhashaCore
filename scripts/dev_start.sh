#!/usr/bin/env bash
# Start the complete local application on the documented development port.
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ ! -x .venv/bin/gunicorn || ! -d frontend/node_modules ]]; then
  echo "Run scripts/dev_setup.sh first."
  exit 1
fi

(cd frontend && npm run build)

# A remote DATABASE_URL in .env is intentionally never replaced implicitly.
# Use this opt-in only when presenting or developing without a reachable
# PostgreSQL service: BHASHACORE_USE_LOCAL_DB=true scripts/dev_start.sh
if [[ "${BHASHACORE_USE_LOCAL_DB:-false}" == "true" ]]; then
  export DATABASE_URL="sqlite:///${project_root}/instance/bhashacore_dev_v2.sqlite3"
fi

.venv/bin/flask --app wsgi db upgrade
exec env PORT="${PORT:-8001}" .venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
