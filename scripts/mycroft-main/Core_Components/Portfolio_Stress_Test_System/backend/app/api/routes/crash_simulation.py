from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import uuid

from app.models.schemas import CrashSimulationRequest, CrashSimulationResponse, CrashResult
from app.services.data_fetcher import DataFetcher, DataFetchError
from app.services.crash_simulator import CrashSimulator
from app.services.loss_analyzer import LossAnalyzer
from app.services.crash_visualization import CrashVisualization
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("portfolio_analysis.crash_simulation_api")


def _resolve_crash_periods(request: CrashSimulationRequest) -> list[dict]:
    """
    Build the ordered list of crash windows to run.
    - Start with all predefined crashes (or the selected subset).
    - Append the custom window if provided.
    """
    predefined = settings.PREDEFINED_CRASHES

    if request.selected_crashes:
        unknown = [k for k in request.selected_crashes if k not in predefined]
        if unknown:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown crash keys: {unknown}. "
                       f"Valid options: {list(predefined.keys())}"
            )
        periods = [predefined[k] for k in request.selected_crashes]
    else:
        periods = list(predefined.values())

    if request.custom_crash:
        c = request.custom_crash
        periods.append({
            "key":              c.key,
            "name":             c.name,
            "start":            c.start,
            "end":              c.end,
            "benchmark_ticker": c.benchmark_ticker,
            "description":      c.description or "User-defined crash window"
        })

    return periods


@router.post("/crash-simulation", response_model=CrashSimulationResponse)
async def run_crash_simulation(request: CrashSimulationRequest):
    """
    Layer 2 endpoint — Historical crash simulation.

    For each crash window:
      1. Fetch price data (crash period + 5-day buffer)
      2. Compute portfolio + benchmark cumulative returns & drawdowns
      3. Decompose losses by holding
      4. Measure recovery time (post-crash fetch)
      5. Generate risk flags per crash

    Then roll up cross-crash summary + visualizations.
    """
    simulation_id = str(uuid.uuid4())
    tickers  = [h.ticker for h in request.portfolio]
    weights  = {h.ticker: h.weight for h in request.portfolio}

    logger.info(
        f"[{simulation_id}] Starting crash simulation for "
        f"{len(tickers)} holdings across selected crashes"
    )

    periods = _resolve_crash_periods(request)
    crash_results: list[CrashResult] = []

    for period in periods:
        key       = period["key"]
        name      = period["name"]
        start     = period["start"]
        end       = period["end"]
        bench     = period["benchmark_ticker"]
        desc      = period["description"]

        logger.info(f"[{simulation_id}] Running crash: {name} ({start} → {end})")

        try:
            # ── 1. Fetch crash window data ─────────────────────────
            price_data = DataFetcher.fetch_crash_period_data(
                tickers=tickers,
                start=start,
                end=end,
                benchmark_ticker=bench
            )

            # ── 2. Simulate ────────────────────────────────────────
            sim = CrashSimulator.simulate(
                price_data=price_data,
                start=start,
                end=end,
                weights=weights,
                benchmark_ticker=bench
            )

            # ── 3. Recovery ────────────────────────────────────────
            recovery_data = DataFetcher.fetch_recovery_data(
                tickers=tickers,
                crash_end=end,
                benchmark_ticker=bench
            )
            recovery_days = CrashSimulator.compute_recovery_days(
                recovery_price_data=recovery_data,
                weights=weights,
                crash_end=end,
                trough_value=sim["port_total_return"]
            )

            # ── 4. Build result ────────────────────────────────────
            result = LossAnalyzer.build_crash_result(
                key=key,
                name=name,
                description=desc,
                start=start,
                end=end,
                benchmark_ticker=bench,
                sim=sim,
                weights=weights,
                recovery_days=recovery_days
            )
            crash_results.append(result)
            logger.info(
                f"[{simulation_id}] {name} done — "
                f"port: {result.portfolio_total_return*100:+.1f}%, "
                f"bench: {result.benchmark_total_return*100:+.1f}%, "
                f"max_dd: {result.max_drawdown*100:.1f}%"
            )

        except DataFetchError as e:
            logger.warning(f"[{simulation_id}] Skipping {name}: data fetch failed — {e}")
            # Non-fatal: skip this crash period
            continue

        except Exception as e:
            logger.error(f"[{simulation_id}] Error in {name}: {e}", exc_info=True)
            continue

    if not crash_results:
        raise HTTPException(
            status_code=422,
            detail="All crash simulations failed. "
                   "Check that tickers are valid and data is available for the selected periods."
        )

    # ── 5. Cross-crash summary ─────────────────────────────────────────────
    overall_flags, recommendations = LossAnalyzer.generate_overall_flags_and_recommendations(
        crash_results
    )

    worst = min(crash_results, key=lambda r: r.max_drawdown)
    avg_dd  = float(sum(r.max_drawdown          for r in crash_results) / len(crash_results))
    avg_rel = float(sum(r.relative_performance  for r in crash_results) / len(crash_results))

    # ── 6. Visualizations ─────────────────────────────────────────────────
    visualizations = CrashVisualization.generate_all(crash_results)

    return CrashSimulationResponse(
        simulation_id=simulation_id,
        timestamp=datetime.now(),
        portfolio_summary={
            "num_holdings":  len(request.portfolio),
            "tickers":       tickers,
            "total_weight":  sum(weights.values()),
            "crashes_run":   len(crash_results),
        },
        crash_results=crash_results,
        worst_crash=worst.key,
        avg_max_drawdown=round(avg_dd,  4),
        avg_relative_performance=round(avg_rel, 4),
        overall_risk_flags=overall_flags,
        recommendations=recommendations,
        visualizations=visualizations
    )