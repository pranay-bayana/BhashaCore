# AI engine verification — 2026-11-01

## PASS

- Backend-only NVIDIA diagnostic confirms DNS resolution, API authentication,
  and availability of `minimaxai/minimax-m3.1-flash`.
- The PostgreSQL persistence path, retrieval path, language detection, and
  citation regression tests pass in the isolated backend suite.
- NVIDIA SSE parsing now requires the protocol completion marker (`[DONE]`).
  A truncated stream can no longer be reported as a completed answer.
- NVIDIA request timeouts and transport failures now return after one request.
  This prevents duplicate prompts and duplicate provider cost after an
  ambiguous timeout.
- Parser completion, truncated stream, and single-request timeout behavior are
  covered by backend tests.
- Isolated deterministic backend regression: 63 passed; 7 live-model
  contracts deselected because they require verified provider generation.
- Backend compilation and production Gunicorn configuration passed.

## PARTIAL

- The diagnostic script `scripts/diagnose_nim.py` provides bounded DNS, model
  listing, non-streaming, streaming, first-token, completion, and latency
  checks without logging credentials.
- Existing language detection, Romanized-query retrieval, retrieval pools, and
  citation provenance are covered by deterministic tests. Live six-language
  generation cannot be credited without a completed provider response.

## BLOCKED

- A tiny non-streaming request and a tiny streaming request to the configured
  NVIDIA model both reached a `ReadTimeout` after model discovery and
  authentication succeeded. This is provider response latency or availability
  after request acceptance, not DNS, TLS, credentials, model discovery,
  request serialization, or the SSE parser.
- No real generated content, first token, completion latency, six-language
  live generation, Flask live-model response, or held-out live evaluation was
  recorded. No fabricated result is reported.

## NOT VERIFIED

- A provider-completed NVIDIA response for the configured model.
- Live six-language answer quality and held-out live-model metrics.

## Backend files changed

- `src/nim.py`: completion verification and safe no-retry handling for
  ambiguous timeout or transport failure.
- `scripts/diagnose_nim.py`: bounded credential-safe NVIDIA diagnostics.
- `tests/test_nim.py`: SSE completion and no-duplicate timeout regressions.

No frontend templates, styles, scripts, translation catalogs, or design assets
were modified.
