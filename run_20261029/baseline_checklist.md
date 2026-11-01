# BhashaCore Engineering Checkpoint - Phase 1 Complete

## Date: Oct 30, 2026
## Project: /Users/pranaybayana/Desktop/Supervised project
## Run Dir: /Users/pranaybayana/Desktop/Supervised project/run_20261029/

## Fix Applied
- Changed `_llm_available()` to `_llm_configured()` in src/app.py
- Removed import-time network probe (httpx GET /models) that failed transiently
- Now only checks if API key exists; network reachability verified per-request
- HAS_LLM=True in both running app and pytest context

## Test Results - test_app.py (ALL 25 PASSED)
1. test_health
2. test_languages_api
3. test_modes_api
4. test_examples_real_grounded
5. test_chat_validation
6. test_stop_endpoint
7. test_pages_render (6 routes)
8. test_chat_page_contains_real_examples
9. test_chat_grounded_all_languages[en, hi, ta, te, kn, ml] - all 6 PASS
10. test_chat_grounded_hindi_citation_integrity PASS
11. test_chat_insufficient_evidence PASS
12. test_chat_provider_failure_returns_provider_unavailable PASS
13. test_eval_mode_uses_dataset_gold_on_provider_failure PASS
14. test_new_chat_history_roundtrip PASS
15. test_dashboard_matches_saved_results PASS
16. test_comparison_matches_saved_results PASS
17. test_failures_api_filters PASS

## LLM Verification
- Direct inference: "What is 2+2?" → "2 + 2 = 4." (5.6s warm start)
- Direct inference: "What is the capital of Japan?" → "The capital of Japan is Tokyo." (150.5s cold start)
- Model-only answers work correctly with is_model_only=True

## App Status
- Flask app running on port 8001
- HAS_LLM=True
- GENERATOR_LABEL=minimaxai/minimax-m3.1-flash
- Retrieval pools: en=3174, hi=3287, kn=3310, ml=3270, ta=3290, te=3279
- Total Wikidata knowledge passages: 248

## Remaining Test Files to Run
- tests/test_langkit.py
- tests/test_multilingual.py
- tests/test_correctness.py
- tests/browser_e2e.py (Playwright)

## Next Steps
1. Run remaining test files
2. Phase 3: Expand knowledge coverage (Wikidata already has 248 passages, need more sources)
3. Phase 4: Improve multilingual retrieval
4. Phase 5: Build broader evaluation suite
5. Phase 6: Verify citations and answer quality
6. Phase 7: Verify browser application
7. Create final timestamped report