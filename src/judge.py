"""LLM-as-judge evaluation: translate-then-judge in English (avoids Indic judge bias).

The judge sees the question, gold answers, the context the chatbot was actually
given, and the chatbot's answer — all in the original language. It silently
translates to English and returns structured JSON (correctness 0-5,
faithfulness 1-5 or null, response language, issue tags, English glosses).

EM / F1 / script purity are computed locally and stored alongside.
"""
import asyncio
import json
import re

from src.config import LANGS, MAX_OUT_TOKENS, judge_results_path, proc_path
from src.generate import _context_for, load_jsonl
from src.metrics import best_scores, script_purity
from src.nim import NimClient

JUDGE_SYSTEM = (
    "You are an expert evaluator for a study of Indian-language government chatbots. "
    "You read Hindi, Tamil, Telugu, Kannada, Malayalam and English fluently. "
    "Respond ONLY with a single valid JSON object. No markdown, no extra text."
)

JUDGE_TMPL = """Language of the interaction: {lang_name}

[Question]
{question}

[Reference correct answers]
{golds}

[Context passages that were provided to the chatbot]
{context}

[Chatbot answer]
{answer}

Evaluate the chatbot answer (mentally translate everything to English first):
1. "correctness": 0 = refusal or no answer, 1 = completely wrong, 2 = mostly wrong, 3 = partially correct, 4 = mostly correct with minor omissions, 5 = fully correct. Judge against the reference answers.
2. "faithfulness": how well the answer is supported by the provided context (5 = fully supported, 1 = contradicts the context). If the context is NONE, use null.
3. "response_language": the language the chatbot answered in (e.g. "Hindi", "English", "Hindi-English mix").
4. "issues": list from ["wrong_answer", "incomplete", "hallucinated", "wrong_language", "refusal", "off_topic", "other"] that apply; empty list if the answer is good.
5. "gloss_question": English translation of the question.
6. "gloss_reference": English translation of the reference answers.
7. "gloss_answer": English translation of the chatbot answer.

Return ONLY this JSON object:
{{"correctness": <int 0-5>, "faithfulness": <int 1-5 or null>, "response_language": "...", "issues": [], "gloss_question": "...", "gloss_reference": "...", "gloss_answer": "..."}}"""


def extract_json(text: str):
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    break
    # fallback: regex for the essential fields
    def grab(field):
        m = re.search(rf'"{field}"\s*:\s*("?[^",]*"?)', text)
        return m.group(1).strip('"') if m else None
    corr = re.search(r'"correctness"\s*:\s*(\d)', text)
    if not corr:
        return None
    return {
        "correctness": int(corr.group(1)),
        "faithfulness": None,
        "response_language": grab("response_language") or "",
        "issues": re.findall(r'"(wrong_answer|incomplete|hallucinated|wrong_language|refusal|off_topic|other)"', text),
        "gloss_question": grab("gloss_question") or "",
        "gloss_reference": grab("gloss_reference") or "",
        "gloss_answer": grab("gloss_answer") or "",
    }


def judge_messages(question, golds, context, answer, lang):
    meta = LANGS[lang]
    if isinstance(golds, list):
        golds_txt = " | ".join(str(g) for g in golds)
    else:
        golds_txt = str(golds)
    ctx_txt = context if context else "NONE (the chatbot answered from its own knowledge)"
    return [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": JUDGE_TMPL.format(
            lang_name=meta["name"], question=question, golds=golds_txt,
            context=ctx_txt, answer=answer or "(empty)",
        )},
    ]


async def run_judge(judge_model: str, gen_model: str, modes: list, langs: list, limit: int = None):
    client = NimClient(judge_model)
    try:
        for lang in langs:
            evals = {e["qid"]: e for e in load_jsonl(proc_path(f"eval_{lang}"))}
            pool_by_pid = {r["pid"]: r for r in load_jsonl(proc_path(f"pool_{lang}"))}
            retrieval_by_qid = {}
            for rkey in ("retrieval", "retrieval_translit"):
                p = proc_path(f"{rkey}_{lang}")
                if p.exists():
                    for r in load_jsonl(p):
                        retrieval_by_qid[(rkey, r["qid"])] = r

            for mode in modes:
                from src.config import gen_results_path
                gen_path = gen_results_path(gen_model, mode, lang)
                if mode == "rag_translit" and lang == "en":
                    continue
                if not gen_path.exists():
                    print(f"[judge:{lang}:{mode}] no generations yet, skipping")
                    continue
                gens = load_jsonl(gen_path)
                out_path = judge_results_path(gen_model, mode, lang)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                done = set()
                if out_path.exists():
                    done = {r["qid"] for r in load_jsonl(out_path) if r.get("correctness") is not None}
                keep = {e["qid"] for e in list(evals.values())[:limit]} if limit else None
                todo = [g for g in gens if g["qid"] not in done and g.get("answer")
                        and (keep is None or g["qid"] in keep)]
                if not todo:
                    print(f"[judge:{lang}:{mode}] complete/skipped ({len(done)} existing)")
                    continue

                async def one(g):
                    item = evals[g["qid"]]
                    passages, hit = _context_for(item, pool_by_pid, retrieval_by_qid, mode)
                    if mode == "gold_context":
                        ctx = passages[0] if passages else None
                    elif mode in ("rag", "rag_translit"):
                        ctx = "\n\n".join(f"[{i+1}] {p}" for i, p in enumerate(passages)) or None
                    else:
                        ctx = None
                    resp = await client.chat(judge_messages(
                        item["question"], item["answers"], ctx, g["answer"], lang
                    ), max_tokens=MAX_OUT_TOKENS)
                    return g, item, resp

                n_ok = 0
                with open(out_path, "a", encoding="utf-8") as f:
                    for coro in asyncio.as_completed([one(g) for g in todo]):
                        g, item, resp = await coro
                        parsed = extract_json(resp.get("content") or "")
                        if parsed is None:
                            parsed = {"correctness": None, "faithfulness": None,
                                      "response_language": None, "issues": ["judge_parse_error"],
                                      "gloss_question": "", "gloss_reference": "", "gloss_answer": "",
                                      "judge_error": (resp.get("error") or resp.get("content") or "")[:200]}
                        n_ok += 1 if parsed.get("correctness") is not None else 0
                        em, f1 = best_scores(g.get("answer") or "", item["answers"])
                        f.write(json.dumps({
                            "qid": g["qid"], "lang": lang, "mode": mode,
                            "gen_model": gen_model, "judge_model": judge_model,
                            "em": em, "f1": round(f1, 4),
                            "purity": round(script_purity(g.get("answer") or "", LANGS[lang]["script"]), 4),
                            "retrieved_hit": g.get("retrieved_hit"),
                            "correctness": parsed.get("correctness"),
                            "faithfulness": parsed.get("faithfulness"),
                            "response_language": parsed.get("response_language"),
                            "issues": parsed.get("issues", []),
                            "gloss_question": parsed.get("gloss_question", ""),
                            "gloss_reference": parsed.get("gloss_reference", ""),
                            "gloss_answer": parsed.get("gloss_answer", ""),
                            "answer": g.get("answer"),
                        }, ensure_ascii=False) + "\n")
                        f.flush()
                print(f"[judge:{lang}:{mode}] {n_ok}/{len(todo)} judged")
    finally:
        await client.aclose()


if __name__ == "__main__":
    import argparse
    from src.config import ALL_LANGS, JUDGE_MODEL, MODES, PRIMARY_GENERATOR

    ap = argparse.ArgumentParser()
    ap.add_argument("--gen-model", default=PRIMARY_GENERATOR)
    ap.add_argument("--judge-model", default=JUDGE_MODEL)
    ap.add_argument("--modes", default=",".join(MODES))
    ap.add_argument("--langs", default=",".join(ALL_LANGS))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    asyncio.run(run_judge(args.judge_model, args.gen_model, args.modes.split(","), args.langs.split(","), args.limit))
