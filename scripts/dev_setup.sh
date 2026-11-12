#!/usr/bin/env bash
# Reproducible local setup. It deliberately reuses an existing virtualenv.
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt

if [[ -f frontend/package-lock.json ]]; then
  (cd frontend && npm ci)
else
  (cd frontend && npm install)
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example; add local credentials before live generation."
fi

echo "Setup complete. Existing .venv, .env, databases, and user data were preserved."
