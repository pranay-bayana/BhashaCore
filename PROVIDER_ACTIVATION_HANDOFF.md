# Sarvam activation record

Sarvam live inference is verified with the active account using
`sarvam-105b-conversations` through `https://api.sarvam.ai/v1`.

The provider-neutral adapter is implemented in `src/generation_provider.py`
and the backend call sites in `src/app.py` now construct it through
`create_generation_provider()`. A result is accepted only when
`result.completed` is true. The existing provider-unavailable path remains
in effect for timeouts, transport failures, and incomplete streams.

This uses no schema migration, template change, JavaScript change, or API
contract change.

Set these server environment values after that change:

```sh
GENERATION_PROVIDER=sarvam
SARVAM_API_KEY=...
SARVAM_BASE_URL=https://api.sarvam.ai/v1
SARVAM_MODEL=sarvam-105b-conversations
```
