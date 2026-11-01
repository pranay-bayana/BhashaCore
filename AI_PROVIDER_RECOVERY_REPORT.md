# AI provider recovery — 2026-11-01

## NVIDIA findings

### PASS

- The authenticated NVIDIA catalog returned 85 model identifiers.
- DNS, authentication, request serialization, and model listing work.
- The configured model `minimaxai/minimax-m3.1-flash` accepted both a tiny
  streaming and non-streaming request, then reached `ReadTimeout` before
  returning content.
- The backend now verifies SSE completion and sends no duplicate request after
  an ambiguous timeout or interrupted stream.
- Two catalog-visible instruction models,
  `nvidia/mistral-nemo-minitron-8b-8k-instruct` and
  `mistralai/mistral-7b-instruct-v0.3`, returned HTTP 404 from
  `/chat/completions` for both bounded probes.

### PARTIAL

- Catalog visibility proves authentication and discovery only. The 404 results
  prove it does not establish inference entitlement for a model and API key.
- The configured Minimax model is reachable but does not complete a minimal
  request within the bounded read timeout. Its provider-side availability or
  latency must be resolved before it can be used as a live generator.

### NOT VERIFIED

- A completed NVIDIA response, first token, or six-language live generation.
- NVIDIA account-specific model entitlement details. The Build documentation
  could not be fetched from this execution host, and the model API does not
  expose entitlement metadata beyond response status.

## Provider-neutral backend seam

`src/generation_provider.py` provides a Flask-independent generation contract:

- `GenerationRequest` preserves model, messages, token limit, temperature, and
  streaming intent.
- `GenerationResult` normalizes completion, provider/model identity, latency,
  token usage, status, reasoning metrics, and safe error codes.
- `NvidiaGenerationProvider` wraps the current completion-verified NVIDIA
  streaming client.

The active Flask path was deliberately not changed because `src/app.py` is
being concurrently edited by the frontend workstream. A later backend-only
integration can replace direct `NimClient` construction with this adapter
without changing retrieval, citations, persistence, or the frontend API.

## Alternative providers to evaluate

These are recommendations, not verified integrations. No credentials were
added or requested.

1. **Sarvam AI**: prioritize for its Indian-language focus and potential fit
   for Hindi, Telugu, Tamil, Kannada, Malayalam, and English. Verify its
   current chat API, streaming behavior, model availability, and account
   limits with a one-request adapter diagnostic before production use.
2. **Google Gemini API / Vertex AI**: prioritize for broad multilingual
   instruction capability and mature streaming SDK/API support. It is a
   separate API contract, so an adapter should be implemented only after a
   configured account returns one completed response in each required language.

Neither provider is asserted to meet BhashaCore requirements until its adapter
passes completion, timeout, citation-pipeline, and six-language tests.

## Regression

- Provider adapter tests, NVIDIA parser tests, retrieval/language/citation
  regressions: 56 passed, 7 live-model contracts deselected.
- The full deterministic backend suite must be used as the release check after
  the concurrent frontend workstream is stable.

## Exact next action

Use NVIDIA Build or NVIDIA account support to enable a model with
`/chat/completions` inference entitlement for the active key, or select one of
the two alternative providers and configure it in the server environment.
Then implement only that provider's adapter and require a completed bounded
response before changing the active generator.
