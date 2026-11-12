# Sarvam generation error investigation

Date: 2026-11-04

## Root cause

The repeated user-facing sentence was caused by an application error-handling
bug: `answer_question()` caught every provider exception and converted it into
the text `Live model generation is unavailable at the moment...`. The route
then streamed that text as a successful `done` event. The browser therefore
rendered a fake assistant response instead of a real failure.

During live verification, a separate intermittent local network fault was also
observed. Some TLS connections to `api.sarvam.ai` were substituted with a
certificate issued by `Sophos SSL CA_*`; valid connections presented the Amazon
certificate for `api.sarvam.ai`. Certificate validation correctly rejected the
substituted certificate. This was confirmed with repeated TLS handshakes and
with Sarvam adapter diagnostics. No TLS verification was disabled.

## Changes

- `src/app.py`
  - Introduced `ProviderGenerationError` with a safe provider error code,
    HTTP status, and latency.
  - Failed generation no longer becomes assistant text or an NDJSON `done`
    event.
  - `/api/chat` releases a guest reservation on every provider failure and
    returns a classified JSON error: authentication, rate limit, timeout,
    transport/interrupted stream, or temporary provider error.
  - Technical diagnostics are logged server-side without prompts, response
    bodies, API keys, or other secrets.
- `src/generation_provider.py`
  - Preserves SSE completion verification: only `[DONE]` plus non-empty text
    is a completed response.
  - Logs safe timeout/transport diagnostics.
  - Makes at most one additional connection attempt only after `ConnectError`,
    before an HTTP request can be sent. It never retries a timeout, provider
    response, or incomplete SSE stream, so ambiguous requests are not
    duplicated.
- `frontend/src/services/api.ts`
  - Preserves API error code/message/retryability.
  - Treats a stream ending without a terminal `done` or `error` event as an
    incomplete-stream error.
- `frontend/src/pages/ChatPage.tsx` and `frontend/src/types/api.ts`
  - Replaces the loading bubble with the safe server message on every failure.
  - Allows exactly one manual retry for a retryable failure; no automatic retry
    is performed.
- Deterministic tests now mock external inference where they test retrieval,
  guest persistence, and localization semantics. Live inference is verified
  separately so transient external TLS routing cannot produce false local
  regression failures.

## Live verification

Active provider: `sarvam`; model: `sarvam-105b-conversations`.

- Direct Sarvam streaming completion succeeded with HTTP 200, a `[DONE]`
  marker, non-empty generated text, and usage metadata.
- Flask `/api/chat` was verified with real Sarvam output and NDJSON events.
- Grounded questions in English, Hindi, Tamil, Telugu, Kannada, and Malayalam
  each produced a real completed `meta` + `delta` + `done` stream. Each result
  included five retrieved citations and at least one used citation. Hindi
  succeeded on the bounded follow-up diagnostic after one local TLS
  interception failure.
- Browser verification on `/chat` recorded exactly one `/api/chat` request for
  one user submission. A successful real response rendered normally. On a
  deliberately encountered transport failure, the generic old sentence was
  absent and the UI showed a retryable state without resending automatically.

## Verification results

| Check | Status | Result |
| --- | --- | --- |
| Sarvam real streamed generation | PASS | HTTP 200, completion marker, non-empty response |
| Six-language grounded generation and citations | PASS | en, hi, ta, te, kn, ml verified |
| Flask → retrieval → Sarvam → NDJSON pipeline | PASS | Completed real route response verified |
| One submission / one provider request | PASS | Browser network check recorded one request |
| Failure does not consume guest quota | PASS | Covered by regression test and reservation release path |
| Incomplete stream handling | PASS | Adapter and frontend terminal-event regression coverage |
| Frontend TypeScript check | PASS | `npm run lint` |
| Frontend production build | PASS | `npm run build` |
| Backend deterministic regression | PASS | 144 passed |
| Browser console | PARTIAL | App generated no JavaScript error; an external Google Fonts request can log `ERR_CERT_AUTHORITY_INVALID` on this machine for the same Sophos TLS interception. It does not affect API calls. |

## Operational note

The application is working with genuine Sarvam output. For consistently
reliable calls from this particular computer/network, the network administrator
must either stop TLS interception for `api.sarvam.ai` or install its enterprise
root certificate in the operating system trust store. The application must
continue rejecting untrusted substituted certificates; accepting them or using
`verify=False` would weaken production security.
