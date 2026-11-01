# BhashaCore QA repair report — 2026-10-30

Project: `/Users/pranaybayana/Desktop/Supervised project`

## Scope and initial state

- Flask application with six language pools, saved evaluation artifacts, and an NVIDIA NIM configuration for `minimaxai/minimax-m3.1-flash`.
- The working directory has no usable Git repository metadata, so there is no baseline commit or Git diff.
- NVIDIA credentials are configured. They were not printed or recorded.

## Defects reproduced and fixed

1. **Chat history path traversal**: `session_id` was interpolated directly into `chat_history/<session_id>.json`. A request using `../escape` successfully created and loaded a file outside `chat_history`.
   - Fixed by accepting only 1–128 characters from `[A-Za-z0-9_-]`.
   - Applied to chat, stop, new-chat, and load-chat endpoints.
   - Added a regression test for all four endpoints.

2. **Malformed API input caused 500 responses**: non-object JSON and non-string chat questions could reach attribute access; `/api/failures?limit=nope` raised `ValueError`.
   - Fixed with JSON-object, question type, boolean `eval_mode`, and bounded integer `limit` validation.
   - Added regression tests for arrays, scalar JSON, non-string questions, invalid `eval_mode`, and invalid limits.

3. **Production debug output**: chat processing emitted raw request and bridge details to stderr.
   - Removed the `DEBUG:` prints.

## Files changed

- `src/app.py`
- `tests/test_app.py`

## Verification performed

| Category | Result | Evidence |
| --- | --- | --- |
| New validation/path-safety tests | PASS, 7 tests | `pytest -q tests/test_app.py -k 'validation or session_id_cannot or failures_api_rejects_invalid_limit or stop_endpoint'` |
| Language utilities | PASS, 30 tests | `pytest -q tests/test_langkit.py` |
| API, saved-result, page checks excluding live generation | PASS, 20 tests | `pytest -q tests/test_app.py -k 'not chat_grounded and not chat_insufficient and not eval_mode and not new_chat_history and not chat_provider_failure'` |
| Multilingual deterministic checks | PASS, 17 tests | `pytest -q tests/test_multilingual.py -k 'not auto_detect_latin and not translation_live_llm_smoke and not answer_language_malayalam_live_llm and not original_question_preserved'` |
| Correctness/retrieval integrity checks excluding live generation | PASS, 18 tests | `pytest -q tests/test_correctness.py -k 'not live_llm_contract and not used_citations_support_contract_all_languages'` |
| Compilation | PASS | `python -m compileall -q src tests` |
| Translation file keys | PASS | Six files each contain 181 nonempty keys; no missing or extra keys against English. |
| Page rendering | PASS | All five pages returned 200 with the correct HTML language tag for each of six UI languages. |
| Running application health | PASS | `/health` returned 200 with pools: en 3188, hi 3288, ta 3291, te 3280, kn 3311, ml 3271. |

## Browser verification

Headless Playwright loaded the chat, dashboard, comparison, failure-analysis, and about pages for English, Hindi, Tamil, Telugu, and Kannada; all requests returned 200 with the requested document language. Malayalam chat also returned 200. The temporary development server exited while continuing the remaining Malayalam browser requests, producing `ERR_CONNECTION_REFUSED`; this browser pass is incomplete and is not recorded as a full pass.

## Live-provider status

The NVIDIA key is configured, but live calls did not complete within several minutes during the full suite and the bounded probe. The full suite and individual live probes were stopped rather than allowed to continue indefinitely. No live generation, translation, or full browser-chat result is claimed as verified in this run.

The deterministic tests monkeypatch provider failures where stated. They verify honest provider-unavailable and dataset-evaluation fallback behavior; they do not prove current NVIDIA availability.

## Remaining blockers

- Re-run live provider tests only when the NIM endpoint responds within its configured timeout.
- Complete the browser workflow, including streaming, stop/retry, citations, and every responsive breakpoint, against a server kept alive for the whole test process.
- The 84-question held-out evaluation was not rerun because it uses external model calls; existing results were preserved.

## Reproduction commands

```sh
./.venv/bin/pytest -q tests/test_langkit.py
./.venv/bin/pytest -q tests/test_app.py -k 'validation or session_id_cannot or failures_api_rejects_invalid_limit or stop_endpoint'
./.venv/bin/python -m compileall -q src tests
./.venv/bin/python src/app.py --port 8001
```
