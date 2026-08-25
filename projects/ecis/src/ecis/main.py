from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ecis")


def cmd_init_db() -> None:
    """Initialise all SQLite databases."""
    from ecis.db.init_db import init_all, insert_default_weights

    print("Initialising ECIS databases…")
    init_all()
    insert_default_weights()
    print("Done.")


def cmd_ingest(tickers: list[str], source: str) -> None:
    """Fetch transcripts for given tickers."""
    from ecis.config.settings import settings

    settings.ensure_dirs()

    if source in ("edgar", "both"):
        from ecis.ingestion.edgar_fetcher import fetch_transcripts as fetch_edgar

        paths = fetch_edgar(tickers)
        print(f"EDGAR: downloaded {len(paths)} files")

    if source in ("fmp", "both"):
        from ecis.ingestion.fmp_fetcher import fetch_transcripts as fetch_fmp

        paths = fetch_fmp(tickers)
        print(f"FMP: downloaded {len(paths)} files")

    from ecis.db.ticker_registry import refresh_transcript_counts, upsert_ticker

    for t in tickers:
        upsert_ticker(t)
        refresh_transcript_counts(t)


def cmd_preprocess(tickers: list[str]) -> None:
    """Clean, normalise, chunk, and embed transcripts."""
    from ecis.preprocessing.cleaner import clean_all
    from ecis.preprocessing.normaliser import normalise_all
    from ecis.preprocessing.chunker import chunk_all
    from ecis.embedding.embedder import embed_and_store_from_file

    for ticker in tickers:
        print(f"\n--- Processing {ticker} ---")
        cleaned = clean_all(ticker)
        print(f"  Cleaned: {len(cleaned)} files")

        normalised = normalise_all(ticker)
        print(f"  Normalised: {len(normalised)} files")

        chunk_files = chunk_all(ticker)
        print(f"  Chunked: {len(chunk_files)} files")

        total_embedded = 0
        for cf in chunk_files:
            n = embed_and_store_from_file(cf)
            total_embedded += n
        print(f"  Embedded: {total_embedded} chunks")


def cmd_extract(ticker: str, transcript_path: str, llm_model: str | None = None) -> None:
    """Run the full extraction pipeline on a single transcript."""
    from ecis.graphs.pipeline_graph import run_pipeline

    print(f"Running extraction pipeline for {ticker} on {transcript_path}…")
    if llm_model:
        print(f"  LLM: {llm_model}")
    signals = run_pipeline(ticker, transcript_path, llm_model=llm_model)
    print(f"\nExtracted {len(signals)} signals:")
    for s in signals:
        model_tag = f" [{s.llm_model}]" if s.llm_model else ""
        print(
            f"  [{s.direction.value:>10}] conf={s.confidence_raw:.2f} "
            f"chunk={s.chunk_index}{model_tag} | {s.supporting_quote[:80]}…"
        )


def cmd_extract_all(tickers: list[str], llm_models: list[str] | None = None) -> None:
    """Run extraction on all raw files for given tickers."""
    from ecis.config.settings import settings
    from ecis.db.ticker_registry import list_ticker_symbols, mark_extraction, upsert_ticker
    from ecis.graphs.pipeline_graph import run_pipeline

    if not tickers:
        tickers = list_ticker_symbols()
        if not tickers:
            print("No tickers in registry. Run --migrate-tickers or pass --ticker.")
            return

    models = llm_models or [settings.llm_model]
    total_signals = 0
    for ticker in tickers:
        upsert_ticker(ticker)
        raw_dirs = [settings.raw_edgar_dir / ticker, settings.raw_fmp_dir / ticker]
        files = []
        for raw_dir in raw_dirs:
            if raw_dir.exists():
                files.extend(sorted(f for f in raw_dir.iterdir() if f.is_file()))
        if not files:
            print(f"No raw files for {ticker}, skipping")
            mark_extraction(ticker, "no_files")
            continue

        print(f"\n{'='*60}")
        print(f"Extracting {ticker}: {len(files)} files × {len(models)} model(s)")
        print(f"{'='*60}")

        ticker_signals = 0
        for model in models:
            for i, raw_file in enumerate(files, 1):
                print(f"\n  [{i}/{len(files)}] {raw_file.name}  ({model})")
                try:
                    signals = run_pipeline(ticker, str(raw_file), llm_model=model)
                    ticker_signals += len(signals)
                    print(f"    → {len(signals)} signals")
                except Exception as exc:
                    print(f"    → ERROR: {exc}")

        mark_extraction(ticker, "complete")
        print(f"\n  {ticker} total: {ticker_signals} signals")
        total_signals += ticker_signals

    print(f"\n{'='*60}")
    print(f"Grand total: {total_signals} signals across {len(tickers)} tickers")
    print(f"{'='*60}")


def cmd_batch(tickers: list[str], llm_models: list[str] | None = None) -> None:
    """Run the full pipeline: ingest → preprocess → extract for all tickers."""
    from ecis.config.settings import settings
    from ecis.db.init_db import init_all, insert_default_weights
    from ecis.db.ticker_registry import refresh_transcript_counts, upsert_ticker

    init_all()
    insert_default_weights()

    cmd_ingest(tickers, source="both")
    for t in tickers:
        upsert_ticker(t)
        refresh_transcript_counts(t)
    cmd_preprocess(tickers)
    cmd_extract_all(tickers, llm_models=llm_models)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ECIS — Earnings Call Intelligence Signals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--init-db", action="store_true", help="Initialise databases")
    parser.add_argument("--ticker", type=str, help="Company ticker symbol(s), comma-separated")
    parser.add_argument("--file", type=str, help="Path to a specific transcript file")
    parser.add_argument("--ingest", action="store_true", help="Fetch transcripts from EDGAR/FMP")
    parser.add_argument("--preprocess", action="store_true", help="Clean, normalise, chunk, embed")
    parser.add_argument("--extract", action="store_true", help="Run extraction pipeline")
    parser.add_argument("--batch", action="store_true", help="Full pipeline: ingest → preprocess → extract")
    parser.add_argument("--source", choices=["edgar", "fmp", "both"], default="both",
                        help="Data source for ingestion (default: both)")
    parser.add_argument("--resolve-outcomes", action="store_true",
                        help="Resolve market outcomes for extracted signals")
    parser.add_argument("--score", action="store_true", help="Print scoring report")
    parser.add_argument("--recalibrate", choices=["platt", "isotonic"],
                        help="Recalibrate signal confidences")
    parser.add_argument("--watchdog", action="store_true",
                        help="Run calibration watchdog for all readers")
    parser.add_argument("--learn", action="store_true",
                        help="Run orchestration learning graph (tune escalation thresholds)")
    parser.add_argument("--vindicate", action="store_true",
                        help="Aggregate conflict vindications and update reader weights")
    parser.add_argument("--migrate-tickers", action="store_true",
                        help="Populate ticker registry from existing directories")
    parser.add_argument("--list-tickers", action="store_true",
                        help="Print the ticker registry")
    parser.add_argument("--approve", type=int, metavar="ID",
                        help="Approve a pending HITL proposal by id")
    parser.add_argument("--reject", type=int, metavar="ID",
                        help="Reject a pending HITL proposal by id")
    parser.add_argument("--model", type=str, default=None,
                        help="LLM for extraction: llama, mistral, qwen, both, all, or an Ollama tag")
    parser.add_argument("--force-resolve", action="store_true",
                        help="Re-fetch outcomes even if cached (splits / corrected dates)")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit dashboard")
    parser.add_argument("--api", action="store_true", help="Launch FastAPI server")
    parser.add_argument("--horizon", type=int, choices=[30, 90, 180],
                        help="Evaluation horizon in days (for --score)")

    args = parser.parse_args()

    if args.init_db:
        cmd_init_db()
        return

    if args.dashboard:
        import subprocess
        import sys
        dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_path)])
        return

    if args.api:
        import uvicorn
        uvicorn.run("ecis.api.app:app", host="0.0.0.0", port=8000, reload=True)
        return

    tickers = [t.strip().upper() for t in args.ticker.split(",")] if args.ticker else []
    from ecis.config.settings import settings as _settings
    llm_models = _settings.resolve_llm_models(args.model) if args.model else None

    if args.migrate_tickers:
        from ecis.db.ticker_registry import migrate_from_directories
        n = migrate_from_directories()
        print(f"Migrated {n} tickers into the registry")
        return

    if args.list_tickers:
        from ecis.db.ticker_registry import list_tickers as registry_list
        rows = registry_list()
        if not rows:
            print("Ticker registry is empty. Run --migrate-tickers.")
            return
        print(f"{'Ticker':<8} {'Company':<28} {'Transcripts':>11} {'Extract':<12} {'Outcomes':<12}")
        for r in rows:
            print(
                f"{r['ticker']:<8} {r['company_name']:<28} {r['total_transcripts']:>11} "
                f"{r['extraction_status']:<12} {r['outcome_resolution_status']:<12}"
            )
        return

    if args.approve is not None or args.reject is not None:
        from ecis.db.approvals import resolve_approval
        aid = args.approve if args.approve is not None else args.reject
        approved = args.approve is not None
        result = resolve_approval(aid, approved=approved)
        print(f"Approval #{aid} → {result['status']}")
        return

    if args.learn:
        from ecis.graphs.learning_graph import run_learning
        result = run_learning()
        print("Learning graph")
        print(f"  FN rate: {result.get('false_negative_rate', 0):.4f}")
        print(f"  Missed D: {result.get('missed_from_category_d', 0)}")
        print(f"  Adjustment: {result.get('adjustment_magnitude', 0):.2%}")
        print(f"  Applied: {result.get('adjustment_applied')}")
        print(f"  HITL: {result.get('requires_human_approval')}")
        if result.get("skip_reason"):
            print(f"  {result['skip_reason']}")
        return

    if args.vindicate:
        from ecis.extraction.vindication import aggregate_vindications
        result = aggregate_vindications()
        print("Vindication aggregation")
        print(f"  Conflicts: {result['total_conflicts']}")
        print(f"  Applied: {result['applied']}")
        print(f"  HITL: {result['requires_human_approval']}")
        print(f"  {result['reason']}")
        print(f"  Weights: {result['proposed_weights']}")
        return

    if args.batch:
        if not tickers:
            parser.error("--batch requires --ticker")
        cmd_batch(tickers, llm_models=llm_models)
        return

    if args.ingest:
        if not tickers:
            parser.error("--ingest requires --ticker")
        cmd_ingest(tickers, args.source)

    if args.preprocess:
        if not tickers:
            parser.error("--preprocess requires --ticker")
        cmd_preprocess(tickers)

    if args.extract:
        if args.file:
            if not tickers:
                parser.error("--extract --file requires --ticker")
            models = llm_models or [_settings.llm_model]
            for model in models:
                cmd_extract(tickers[0], args.file, llm_model=model)
        else:
            cmd_extract_all(tickers, llm_models=llm_models)

    if args.resolve_outcomes:
        from ecis.scoring.outcome_resolver import resolve_all, resolve_ticker
        if tickers:
            for t in tickers:
                n = resolve_ticker(t, force=args.force_resolve)
                print(f"{t}: resolved {n} outcomes")
                from ecis.db.ticker_registry import mark_outcomes
                mark_outcomes(t)
        else:
            n = resolve_all(force=args.force_resolve)
            print(f"Resolved {n} outcomes total")

    if args.score:
        from ecis.scoring.scorer import print_scorecard
        ticker = tickers[0] if tickers else None
        print_scorecard(ticker=ticker, horizon=args.horizon)

    if args.recalibrate:
        from ecis.scoring.recalibrator import recalibrate_signals
        method = args.recalibrate
        source = tickers[0].lower() if tickers else None
        n = recalibrate_signals(method=method, source_method=source)
        print(f"Recalibrated {n} signals using {method}")

    if args.watchdog:
        from ecis.graphs.watchdog_graph import run_watchdog
        for reader in ["keyword", "finbert", "llm", "triangulated"]:
            print(f"\nWatchdog: {reader}")
            result = run_watchdog(reader)
            action = result.get("action_type")
            if action:
                print(f"  Action: {action} — {result.get('action_details', {})}")
            else:
                print(f"  No action needed (ECE={result.get('rolling_ece', 0):.4f})")

    all_commands = [
        args.init_db, args.ingest, args.preprocess, args.extract,
        args.batch, args.resolve_outcomes, args.score, args.recalibrate,
        args.watchdog, args.learn, args.vindicate, args.migrate_tickers,
        args.list_tickers, args.dashboard, args.api,
        args.approve is not None, args.reject is not None,
    ]
    if not any(all_commands):
        parser.print_help()


if __name__ == "__main__":
    main()
