"""CLI orchestrator for the BhashaCore pipeline."""
import argparse
import asyncio


def main():
    ap = argparse.ArgumentParser(description="BhashaCore pipeline")
    ap.add_argument("--stage", required=True,
                    choices=["data", "retrieve", "generate", "judge", "analyze"])
    ap.add_argument("--model", default=None, help="generator model (generate stage)")
    ap.add_argument("--gen-model", default=None, help="generator model (judge stage)")
    ap.add_argument("--judge-model", default=None, help="judge model")
    ap.add_argument("--modes", default=None)
    ap.add_argument("--langs", default=None)
    ap.add_argument("--limit", type=str, default=None,
                    help="comma-separated per-language limit (e.g. en=50,hi=30); overrides config RUN_LIMIT")
    args = ap.parse_args()

    from src.config import ALL_LANGS, JUDGE_MODEL, MODES, PRIMARY_GENERATOR

    # Support per-language RUN_LIMIT via --limit en=50,hi=30
    if args.limit:
        per_lang = {}
        for item in args.limit.split(","):
            k, v = item.split("=")
            per_lang[k.strip()] = int(v.strip())
        RUN_LIMIT = {lang: per_lang.get(lang, RUN_LIMIT[lang]) for lang in ALL_LANGS}

    langs = args.langs.split(",") if args.langs else ALL_LANGS
    modes = args.modes.split(",") if args.modes else MODES
    limit = RUN_LIMIT  # per-language dict

    if args.stage == "data":
        from src.data import build_all
        build_all()

    elif args.stage == "retrieve":
        from src.retrieval import run_retrieval, run_translit_retrieval
        for lang in langs:
            run_retrieval(lang)
            if lang != "en":
                run_translit_retrieval(lang)

    elif args.stage == "generate":
        from src.generate import run_generation
        model = args.model or PRIMARY_GENERATOR
        asyncio.run(run_generation(model, modes, langs, limit))

    elif args.stage == "judge":
        from src.judge import run_judge
        gen_model = args.gen_model or PRIMARY_GENERATOR
        judge_model = args.judge_model or JUDGE_MODEL
        asyncio.run(run_judge(judge_model, gen_model, modes, langs, limit))

    elif args.stage == "analyze":
        from src.analyze import main as analyze_main
        analyze_main()


if __name__ == "__main__":
    main()
