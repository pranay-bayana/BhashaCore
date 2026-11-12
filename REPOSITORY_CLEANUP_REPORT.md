# Repository cleanup report — 2026-11-04

## Audit scope

- Inspected **181 tracked files**, the active untracked implementation files,
  Python/Node manifests, Flask routes, frontend imports, migrations, tests,
  documentation references, and repository disk usage.
- The repository was reduced from approximately **769 MB** to **107 MB** before
  recreating local verification environments. The removed size was generated
  local tooling and build output, never research data.

## Removed

### Generated local artifacts

- `.venv/`, `frontend/node_modules/`, `frontend/dist/`, Python/pytest caches,
  Playwright/tool workspaces, generated browser screenshots, and local QA
  preview images.
- These directories are ignored and can be recreated with the documented setup
  commands. They are not source artifacts.

### Superseded status records and run snapshots

- Dated final-verification reports, duplicated provider/NVIDIA investigation
  reports, progress snapshots, old handoff notes, and dated audit/run folders.
- The authoritative current records are `PRODUCTION_READINESS_REPORT.md`,
  `SECURITY_AUDIT_REPORT.md`, `E2E_TEST_REPORT.md`, `DEPLOYMENT.md`, and this
  report.

### One-off diagnostics and duplicate checks

- Numbered `debug_nim*` probes, `smoke_nim.py`, duplicate pool/state checks,
  one-off browser QA copies, and an invalid `check_pools.py` experiment.
- Several removed NVIDIA probes read a user-home credential file directly;
  supported provider diagnostics now use environment-based configuration.

## Preserved

- Flask and React application source, templates, translations, migrations,
  deployment configuration, environment example, and test suites.
- All `data/`, `results/`, `report/`, and `report/figures/` research evidence.
- Reproducible ingestion, retrieval, held-out evaluation, citation, and
  provider diagnostic utilities that are referenced by the root documentation
  or research reports.
- `frontend/package-lock.json` and all runtime dependency manifests.

## Dependency changes

- Removed direct production pins for `sacrebleu`, `tqdm`, `numpy`, and
  `pyarrow`: none is imported directly by application or retained scripts.
  Transitive requirements remain resolved by the packages that need them.
- Added `requirements-dev.txt` for pytest and Playwright, keeping production
  requirements separate from verification tooling.
- `npm audit --omit=dev` reported **0 production vulnerabilities**. The npm
  install output reports two development dependency advisories; no automated
  breaking upgrade was applied.

## Verification

- Clean Python environment: `pip install -r requirements-dev.txt` passed.
- Clean frontend install: `npm ci` passed.
- TypeScript check and production build passed.
- Full backend suite: **143 passed**.
- Clean Alembic migration reached `7a4f4fe9e7d2`.
- Production Gunicorn configuration check passed.
- `.env`, cookie exports, virtual environments, Node modules, and frontend
  builds are ignored by Git.

## Deliberately retained candidates

- Legacy Jinja templates and static files remain because Flask can explicitly
  serve them through legacy/fallback routes and authentication pages.
- Evaluation/ingestion scripts that are not imported at runtime remain because
  they reproduce checked-in research data and figures.

## Remaining external blockers

- Apply the current migration to managed PostgreSQL after a normal backup.
- Verify Redis-backed rate limits, email delivery, HTTPS hosting, and backup
  recovery in the selected deployment environment.
