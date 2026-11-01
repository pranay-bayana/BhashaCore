"""Answer metrics: script-aware EM/F1, script purity / language detection, failure flags.

Design notes
------------
* Tokenization: NFC-normalize, drop punctuation (incl. danda), drop format chars
  (ZWJ/ZWNJ/zero-width space), lowercase, whitespace split. English articles are
  removed for every language (standard SQuAD behaviour; Indic languages lack
  articles so this is a no-op for them).
* Script purity: fraction of alphabetic characters that fall in the expected
  Unicode block of the response language. Low purity => code-mixing or the model
  answered in the wrong language.
"""
import re
import unicodedata
from collections import Counter

_SCRIPT_RANGES = {
    "Latin": [(0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x024F)],
    "Devanagari": [(0x0900, 0x097F)],
    "Tamil": [(0x0B80, 0x0BFF)],
    "Telugu": [(0x0C00, 0x0C7F)],
    "Kannada": [(0x0C80, 0x0CFF)],
    "Malayalam": [(0x0D00, 0x0D7F)],
}

_ARTICLES = {"a", "an", "the"}


def _normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("P") or cat.startswith("C"):
            out.append(" ")
        else:
            out.append(ch)
    text = "".join(out).lower()
    return " ".join(text.split())


def _tokens(text: str) -> list:
    return [t for t in _normalize(text).split() if t not in _ARTICLES]


def exact_match(pred: str, golds: list) -> float:
    p = _normalize(pred)
    return float(any(p == _normalize(g) for g in golds)) if golds else 0.0


def f1_score(pred: str, gold: str) -> float:
    pt, gt = _tokens(pred), _tokens(gold)
    if not pt or not gt:
        return float(pt == gt)
    common = Counter(pt) & Counter(gt)
    nsame = sum(common.values())
    if nsame == 0:
        return 0.0
    precision = nsame / len(pt)
    recall = nsame / len(gt)
    return 2 * precision * recall / (precision + recall)


def best_scores(pred: str, golds: list) -> tuple:
    """(EM, best-F1) against the best-matching gold answer."""
    if not golds:
        return 0.0, 0.0
    em = exact_match(pred, golds)
    f1 = max((f1_score(pred, g) for g in golds), default=0.0)
    return em, f1


def script_purity(text: str, script: str) -> float:
    letters = [ch for ch in text or "" if unicodedata.category(ch).startswith("L")]
    if not letters:
        return 0.0
    ranges = _SCRIPT_RANGES.get(script, [])
    n = sum(1 for ch in letters if any(lo <= ord(ch) <= hi for lo, hi in ranges))
    return n / len(letters)


def detect_script(text: str) -> str:
    scores = {s: script_purity(text, s) for s in _SCRIPT_RANGES}
    return max(scores, key=scores.get)


_REFUSAL_PATTERNS = [
    "don't know", "do not know", "cannot answer", "can't answer",
    "no information", "not available", "unable to answer",
    "माफ़", "जानकारी नहीं", "तथ्य नहीं",  # Hindi
    "तिमीलाई थाहा छैन",  # (nepali — harmless)
]


def looks_like_refusal(answer: str) -> bool:
    a = _normalize(answer)
    return any(p in a for p in _REFUSAL_PATTERNS)


def failure_flags(row: dict) -> list:
    """Combine local signals + judge output into a failure taxonomy.

    row keys used: mode, expected_script, answer, retrieved_hit (bool|None),
    judge (dict|None with correctness, faithfulness, issues), em, f1.
    """
    tags = []
    mode = row.get("mode", "")
    answer = row.get("answer") or ""
    judge = row.get("judge") or {}
    purity = script_purity(answer, row.get("expected_script", "Latin"))

    if mode in ("rag", "rag_translit") and row.get("retrieved_hit") is False:
        tags.append("retrieval_miss")
    if purity < 0.5 and answer.strip():
        tags.append("wrong_language_or_codemixed")
    if looks_like_refusal(answer):
        tags.append("refusal_like")
    faith = judge.get("faithfulness")
    if mode in ("gold_context", "rag", "rag_translit") and isinstance(faith, (int, float)) and faith <= 2:
        tags.append("unfaithful_to_context")
    issues = judge.get("issues") or []
    for it in issues:
        if it not in tags:
            tags.append(it)
    if not tags and (judge.get("correctness") is not None and judge["correctness"] <= 2):
        tags.append("wrong_answer")
    return tags
