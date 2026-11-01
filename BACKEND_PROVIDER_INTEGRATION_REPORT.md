# Backend provider integration — 2026-11-01

## PASS

### CSRF

- Flask-WTF CSRF protection remains enabled for forms and state-changing API
  endpoints. No endpoint was globally exempted to suppress errors.
- Backend reproduction proved that a rendered page token is accepted for
  signup, authenticated new-chat, rename, delete, and account deletion.
  Missing API headers correctly return HTTP 400.
- A read-only browser proof loaded the real chat page, issued a normal
  JavaScript `fetch`, confirmed `X-CSRFToken` was attached, and received HTTP
  200 from `/api/new-chat`.
- The reported 400 is therefore not a backend token-generation or
  session-cookie failure. It occurs when a caller sends a state-changing
  request without the current rendered token, such as a stale page/session or
  a caller that bypasses the shared fetch wrapper. The protected request path
  works with the current page token.
- Authenticated new-chat now persists a newly created `Conversation` before
  returning success. Rename and delete no longer fail with 404 before the
  first message is sent. Existing cross-user ID protection is retained.

### Sarvam live provider

- `SARVAM_API_KEY` is read from the ignored environment file only; it is never
  logged, reported, or committed.
- Authenticated provider model discovery returned `sarvam-105b` and
  `sarvam-105b-conversations`.
- `sarvam-105b-conversations` returned genuine completed content through
  `https://api.sarvam.ai/v1/chat/completions`:
  - Non-streaming completion: 0.471 s.
  - Streaming completion: first token 0.215 s; completed 0.224 s.
- A dedicated `SarvamGenerationProvider` now uses completion-verified SSE,
  required `[DONE]`, safe HTTP/timeout/transport normalization, usage metrics,
  reasoning metrics, latency, and no duplicate retry after ambiguity.
- The active backend selects Sarvam with
  `GENERATION_PROVIDER=sarvam` and `SARVAM_MODEL=sarvam-105b-conversations`.
  NVIDIA remains selectable with `GENERATION_PROVIDER=nvidia`.
- A real Flask route proof passed: rendered CSRF token → `/api/chat` →
  retrieval → Sarvam streamed completion → NDJSON done event → citation
  provenance. The result was `answered`, used the Sarvam model label, and
  returned five citation records with pid, source, rank, support, and used
  fields.

### Six-language generation

All probes used real completed Sarvam streaming responses with a 64-token cap:

| Input | Result | Script | Latency |
| --- | --- | --- | ---: |
| English | PASS | Latin | 230 ms |
| Hindi | PASS | Devanagari | 226 ms |
| Telugu | PASS | Telugu | 207 ms |
| Tamil | PASS | Tamil | 234 ms |
| Kannada | PASS | Kannada | 193 ms |
| Malayalam | PASS | Malayalam | 204 ms |
| Romanized Hindi | PASS | Devanagari | 185 ms |

The probe asked for each native script explicitly. This verifies completed
generation and script compliance; it is not a substitute for a full quality
evaluation on held-out data.

### Tests and security

- Full deterministic backend regression: **73 passed, 7 NVIDIA live-model
  contracts deselected**.
- Sarvam adapter, CSRF, authentication, persistence, retrieval, language, and
  citation regressions pass.
- Python compilation passes. `.env` remains Git-ignored.

## PARTIAL

- The current six-language check verifies short generated responses and script
  correctness. A held-out quality evaluation remains to be run with Sarvam
  completed responses before publishing language-quality metrics.

## BLOCKED

- None for the active Sarvam chat path.

## NOT VERIFIED

- Real Redis multi-worker rate-limit verification and real password-reset
  email delivery remain outside this provider integration run.

## NVIDIA status

NVIDIA remains available as a configuration option but is not selected locally.
The configured Minimax model previously timed out after request acceptance;
two catalog-visible alternatives returned HTTP 404 for chat inference. No
NVIDIA model is claimed as a working generator.

## Backend files changed

- `src/app.py`: provider selection, Sarvam live generation path, and durable
  authenticated new-chat creation.
- `src/generation_provider.py`: Sarvam adapter and provider factory.
- `scripts/diagnose_sarvam.py`: bounded six-language live diagnostic.
- `tests/test_generation_provider.py`: Sarvam SSE completion coverage.
- `tests/test_csrf_backend.py`: rendered-token regression coverage.
- `.env.example`: provider configuration placeholders only.
