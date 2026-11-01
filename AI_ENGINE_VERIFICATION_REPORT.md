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
- The authenticated NVIDIA catalog lists 85 model identifiers. Provider model
  discovery is therefore distinct from inference entitlement and was not used
  as proof that a model can generate.

## PARTIAL

- The diagnostic script `scripts/diagnose_nim.py` provides bounded DNS, model
  listing, non-streaming, streaming, first-token, completion, and latency
  checks without logging credentials.
- Existing language detection, Romanized-query retrieval, retrieval pools, and
  citation provenance are covered by deterministic tests. Live six-language
  generation cannot be credited without a completed provider response.
- The diagnostic supports an explicit model argument, so a provider-approved
  replacement can be tested without changing production configuration.

## BLOCKED

- A tiny non-streaming request and a tiny streaming request to
  `minimaxai/minimax-m3.1-flash` both reached a `ReadTimeout` after model
  discovery and authentication succeeded. This is provider response latency or
  availability after request acceptance, not DNS, TLS, credentials, model
  discovery, request serialization, or the SSE parser.
- Two alternative catalog-visible instruction models,
  `nvidia/mistral-nemo-minitron-8b-8k-instruct` and
  `mistralai/mistral-7b-instruct-v0.3`, both returned HTTP 404 from
  `/chat/completions` for streaming and non-streaming probes. The catalog
  therefore includes models unavailable to this key or endpoint for inference.
  No unverified model was configured as a replacement.
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

## Provider recovery action

Use the NVIDIA Build catalog or account support to enable a chat-completions
model for this API key and endpoint, or resolve the configured Minimax model's
inference availability. Re-run `python -u scripts/diagnose_nim.py --model
MODEL_ID` and require completed streaming and non-streaming output before
changing `PRIMARY_GENERATOR`.

No frontend templates, styles, scripts, translation catalogs, or design assets
were modified.
