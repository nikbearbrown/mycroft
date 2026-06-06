import pandas as pd
import numpy as np
from models import AgentFindings


# ── Helpers ──────────────────────────────────────────────────────────────────

def _sells(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["action"] == "SELL") & df["pnl"].notna()].copy()

def _win_rate(s: pd.Series) -> float:
    if len(s) == 0: return 0.0
    return round(s.sum() / len(s) * 100, 1)

def _edge_score(win_rate: float, n: int, baseline: float = 50.0) -> float:
    """
    Simple edge score: normalized deviation from 50% baseline, dampened by sample size.
    Returns value in [-1, 1].
    """
    if n < 5: return 0.0
    raw = (win_rate - baseline) / 50.0
    confidence = min(1.0, n / 30)
    return round(raw * confidence, 3)


# ── Agent 1: Behavioral patterns ────────────────────────────────────────────

def behavior_agent(df: pd.DataFrame) -> AgentFindings:
    sells = _sells(df)
    insights = []
    metrics = {}

    # Averaging down: BUY after stock dropped (proxy: multiple buys in same ticker)
    avg_down_tickers = []
    for ticker, grp in df[df["action"] == "BUY"].groupby("ticker"):
        grp = grp.sort_values("date")
        if len(grp) > 1:
            prices = grp["price"].tolist()
            if any(prices[i] < prices[i-1] for i in range(1, len(prices))):
                avg_down_tickers.append(ticker)

    avg_down_rate = round(len(avg_down_tickers) / max(df["ticker"].nunique(), 1) * 100, 1)
    metrics["avg_down_rate_pct"] = avg_down_rate

    # Check if averaging down actually helps
    avg_down_pnl = sells[sells["ticker"].isin(avg_down_tickers)]["pnl"].sum()
    non_avg_pnl  = sells[~sells["ticker"].isin(avg_down_tickers)]["pnl"].sum()
    metrics["avg_down_pnl_total"]     = round(avg_down_pnl, 2)
    metrics["non_avg_down_pnl_total"] = round(non_avg_pnl, 2)

    if avg_down_rate > 30:
        verdict = "helped" if avg_down_pnl > 0 else "hurt"
        insights.append(f"You average down on {avg_down_rate}% of positions — this has {verdict} your P&L overall.")

    # Early exits: sold within 7 days
    short_sells = sells[sells["days_held"].notna() & (sells["days_held"] <= 7)]
    short_win_rate = _win_rate(short_sells["is_winner"]) if len(short_sells) > 0 else None
    metrics["short_hold_trades"]    = len(short_sells)
    metrics["short_hold_win_rate"]  = short_win_rate
    if short_win_rate is not None:
        insights.append(f"Trades held ≤7 days: {len(short_sells)} trades, {short_win_rate}% win rate.")

    # Panic selling: sold at a loss after holding <14 days
    panic = sells[(sells["days_held"].notna()) & (sells["days_held"] < 14) & (sells["pnl"] < 0)]
    metrics["panic_sell_count"] = len(panic)
    metrics["panic_sell_pnl"]   = round(panic["pnl"].sum(), 2)
    if len(panic) > 3:
        insights.append(f"Potential panic sells: {len(panic)} trades exited at a loss in under 2 weeks (total loss: ${abs(metrics['panic_sell_pnl']):,.0f}).")

    # Winner sell speed vs loser sell speed
    winner_avg_hold = sells[sells["is_winner"] == True]["days_held"].mean()
    loser_avg_hold  = sells[sells["is_winner"] == False]["days_held"].mean()
    metrics["winner_avg_hold_days"] = round(winner_avg_hold, 1) if not pd.isna(winner_avg_hold) else None
    metrics["loser_avg_hold_days"]  = round(loser_avg_hold, 1) if not pd.isna(loser_avg_hold) else None

    if metrics["winner_avg_hold_days"] and metrics["loser_avg_hold_days"]:
        if winner_avg_hold < loser_avg_hold:
            insights.append(
                f"Classic disposition effect: you sell winners after {metrics['winner_avg_hold_days']} days avg "
                f"but hold losers for {metrics['loser_avg_hold_days']} days avg."
            )
        else:
            insights.append(
                f"Good discipline: you let winners run ({metrics['winner_avg_hold_days']}d avg) "
                f"and cut losers faster ({metrics['loser_avg_hold_days']}d avg)."
            )

    overall_wr = _win_rate(sells["is_winner"])
    return AgentFindings(
        agent_name="behavior",
        summary="Analyzes trading behaviors: averaging down, early exits, panic selling, disposition effect.",
        metrics=metrics,
        insights=insights,
        edge_score=_edge_score(overall_wr, len(sells)),
    )


# ── Agent 2: Entry / exit timing ────────────────────────────────────────────

def timing_agent(df: pd.DataFrame) -> AgentFindings:
    sells = _sells(df)
    insights = []
    metrics = {}

    # Earnings proximity
    earn_trades = sells[sells["earnings_trade"] == True]
    non_earn    = sells[sells["earnings_trade"] == False]
    earn_wr     = _win_rate(earn_trades["is_winner"]) if len(earn_trades) > 0 else None
    non_earn_wr = _win_rate(non_earn["is_winner"])    if len(non_earn) > 0 else None

    metrics["earnings_trades_count"]   = len(earn_trades)
    metrics["earnings_win_rate"]       = earn_wr
    metrics["non_earnings_win_rate"]   = non_earn_wr

    if earn_wr is not None and non_earn_wr is not None:
        diff = earn_wr - non_earn_wr
        if abs(diff) > 10:
            direction = "better" if diff > 0 else "worse"
            insights.append(
                f"You perform {direction} around earnings ({earn_wr}% win rate) "
                f"vs non-earnings trades ({non_earn_wr}% win rate)."
            )

    # Day of week bias
    df_copy = df.copy()
    df_copy["dow"] = pd.to_datetime(df_copy["date"]).dt.day_name()
    sells_dow = sells.copy()
    sells_dow["dow"] = pd.to_datetime(sells_dow["date"]).dt.day_name()

    dow_wr = sells_dow.groupby("dow")["is_winner"].apply(_win_rate)
    metrics["win_rate_by_dow"] = dow_wr.to_dict()
    best_dow  = dow_wr.idxmax() if len(dow_wr) > 0 else None
    worst_dow = dow_wr.idxmin() if len(dow_wr) > 0 else None
    if best_dow and worst_dow and best_dow != worst_dow:
        insights.append(f"Best day to exit: {best_dow} ({dow_wr[best_dow]}% win rate). Worst: {worst_dow} ({dow_wr[worst_dow]}%).")

    # Entry quality: did price go up after buy?
    # Proxy: average pnl_pct on sells — positive means entries were generally at good prices
    avg_pnl_pct = sells["pnl_pct"].mean()
    metrics["avg_pnl_pct"] = round(avg_pnl_pct, 2) if not pd.isna(avg_pnl_pct) else None

    # Hold duration sweet spot
    duration_buckets = pd.cut(
        sells["days_held"].dropna(),
        bins=[0, 7, 30, 90, 180, 365, 99999],
        labels=["≤7d", "8-30d", "31-90d", "91-180d", "181-365d", ">1y"]
    )
    wr_by_duration = sells.groupby(duration_buckets)["is_winner"].apply(_win_rate)
    metrics["win_rate_by_hold_duration"] = wr_by_duration.to_dict()
    best_duration = wr_by_duration.idxmax() if len(wr_by_duration) > 0 else None
    if best_duration:
        insights.append(f"Your highest win rate by hold duration is in the {best_duration} range ({wr_by_duration[best_duration]}%).")

    overall_wr = _win_rate(sells["is_winner"])
    return AgentFindings(
        agent_name="timing",
        summary="Analyzes entry/exit timing: earnings proximity, day-of-week, hold duration sweet spot.",
        metrics=metrics,
        insights=insights,
        edge_score=_edge_score(overall_wr, len(sells)),
    )


# ── Agent 3: Macro regime ────────────────────────────────────────────────────

def regime_agent(df: pd.DataFrame) -> AgentFindings:
    sells = _sells(df)
    insights = []
    metrics = {}

    # Win rate by VIX regime
    vix_wr = sells.groupby("vix_regime")["is_winner"].apply(_win_rate)
    metrics["win_rate_by_vix_regime"] = vix_wr.to_dict()
    if len(vix_wr) > 1:
        best  = vix_wr.idxmax()
        worst = vix_wr.idxmin()
        insights.append(f"You perform best in {best} VIX environments ({vix_wr[best]}% win rate) and worst in {worst} ({vix_wr[worst]}%).")

    # Win rate by market regime
    mkt_wr = sells.groupby("market_regime")["is_winner"].apply(_win_rate)
    metrics["win_rate_by_market_regime"] = mkt_wr.to_dict()
    if len(mkt_wr) > 1:
        best  = mkt_wr.idxmax()
        worst = mkt_wr.idxmin()
        insights.append(f"Market regime edge: {best} markets suit you best ({mkt_wr[best]}% win rate); {worst} markets hurt ({mkt_wr[worst]}%).")

    # Recession trades
    rec_sells     = sells[sells["in_recession"] == True]
    non_rec_sells = sells[sells["in_recession"] == False]
    rec_wr     = _win_rate(rec_sells["is_winner"])     if len(rec_sells) > 0 else None
    non_rec_wr = _win_rate(non_rec_sells["is_winner"]) if len(non_rec_sells) > 0 else None
    metrics["recession_win_rate"]     = rec_wr
    metrics["non_recession_win_rate"] = non_rec_wr

    # P&L by regime
    pnl_by_regime = sells.groupby("market_regime")["pnl"].sum().round(2).to_dict()
    metrics["pnl_by_market_regime"] = pnl_by_regime

    # Trade frequency in different regimes (over-trading in volatile markets?)
    vol_trades = df[df["vix_regime"].isin(["high", "extreme"])]
    calm_trades = df[df["vix_regime"].isin(["low", "elevated"])]
    metrics["trades_in_high_vol"] = len(vol_trades)
    metrics["trades_in_low_vol"]  = len(calm_trades)
    if len(vol_trades) > len(calm_trades) * 0.6:
        insights.append("You trade more frequently during high-volatility periods — check if this is intentional or reactive.")

    overall_wr = _win_rate(sells["is_winner"])
    return AgentFindings(
        agent_name="regime",
        summary="Win rate and P&L broken down by VIX regime, market trend, and recession periods.",
        metrics=metrics,
        insights=insights,
        edge_score=_edge_score(overall_wr, len(sells)),
    )


# ── Agent 4: Sector / market cap ────────────────────────────────────────────

def sector_agent(df: pd.DataFrame) -> AgentFindings:
    sells = _sells(df)
    insights = []
    metrics = {}

    # Win rate by sector
    sector_wr  = sells.groupby("sector")["is_winner"].apply(_win_rate)
    sector_pnl = sells.groupby("sector")["pnl"].sum().round(2)
    metrics["win_rate_by_sector"] = sector_wr.to_dict()
    metrics["pnl_by_sector"]      = sector_pnl.to_dict()

    if len(sector_wr) > 0:
        best_s  = sector_wr.idxmax()
        worst_s = sector_wr.idxmin()
        insights.append(
            f"Best sector: {best_s} ({sector_wr[best_s]}% win rate, ${sector_pnl.get(best_s, 0):,.0f} P&L). "
            f"Worst: {worst_s} ({sector_wr[worst_s]}% win rate)."
        )

    # Win rate by market cap
    cap_wr  = sells.groupby("market_cap")["is_winner"].apply(_win_rate)
    cap_pnl = sells.groupby("market_cap")["pnl"].sum().round(2)
    metrics["win_rate_by_market_cap"] = cap_wr.to_dict()
    metrics["pnl_by_market_cap"]      = cap_pnl.to_dict()

    if len(cap_wr) > 0:
        best_cap = cap_wr.idxmax()
        insights.append(f"Market cap edge: you have the best win rate in {best_cap}-cap stocks ({cap_wr[best_cap]}%).")

    # Concentration risk: what % of trades are in top 3 tickers
    ticker_counts = df["ticker"].value_counts()
    top3_pct = ticker_counts.head(3).sum() / len(df) * 100
    metrics["top3_ticker_concentration_pct"] = round(top3_pct, 1)
    metrics["top_tickers"] = ticker_counts.head(5).to_dict()
    if top3_pct > 50:
        insights.append(f"High concentration: {top3_pct}% of all trades are in your top 3 tickers.")

    # Diversification across sectors
    n_sectors = sells["sector"].nunique()
    metrics["unique_sectors_traded"] = int(n_sectors)

    overall_wr = _win_rate(sells["is_winner"])
    return AgentFindings(
        agent_name="sector",
        summary="Win rate and P&L by sector and market cap bucket. Concentration analysis.",
        metrics=metrics,
        insights=insights,
        edge_score=_edge_score(overall_wr, len(sells)),
    )


# ── Agent 5: Hold duration / conviction ─────────────────────────────────────

def hold_duration_agent(df: pd.DataFrame) -> AgentFindings:
    sells = _sells(df)
    insights = []
    metrics = {}

    sells = sells[sells["days_held"].notna()].copy()
    if len(sells) == 0:
        return AgentFindings(agent_name="hold_duration", summary="No closed trades found.", metrics={}, insights=[], edge_score=None)

    avg_hold  = sells["days_held"].mean()
    med_hold  = sells["days_held"].median()
    metrics["avg_hold_days"]    = round(avg_hold, 1)
    metrics["median_hold_days"] = round(med_hold, 1)

    # Optimal hold window: find the duration bucket with best win rate
    sells["hold_bucket"] = pd.cut(
        sells["days_held"],
        bins=[0, 7, 14, 30, 60, 90, 180, 365, 99999],
        labels=["≤7d","8-14d","15-30d","31-60d","61-90d","91-180d","181-365d",">1y"]
    )
    wr_by_bucket  = sells.groupby("hold_bucket", observed=True)["is_winner"].apply(_win_rate)
    pnl_by_bucket = sells.groupby("hold_bucket", observed=True)["pnl"].sum().round(2)
    metrics["win_rate_by_hold_bucket"] = wr_by_bucket.to_dict()
    metrics["pnl_by_hold_bucket"]      = pnl_by_bucket.to_dict()

    best_bucket = wr_by_bucket.idxmax() if len(wr_by_bucket) > 0 else None
    if best_bucket:
        insights.append(f"Your optimal hold window is {best_bucket} ({wr_by_bucket[best_bucket]}% win rate, ${pnl_by_bucket.get(best_bucket, 0):,.0f} total P&L).")

    # Churn: how many positions were opened and closed within 7 days?
    churn = len(sells[sells["days_held"] <= 7])
    churn_pct = round(churn / len(sells) * 100, 1)
    metrics["churn_rate_pct"] = churn_pct
    if churn_pct > 40:
        insights.append(f"High churn rate: {churn_pct}% of positions closed within 7 days — this may be eating into returns via transaction friction.")

    # Long conviction: positions held >90d
    conviction = sells[sells["days_held"] > 90]
    conv_wr = _win_rate(conviction["is_winner"]) if len(conviction) > 0 else None
    metrics["high_conviction_count"]    = len(conviction)
    metrics["high_conviction_win_rate"] = conv_wr
    if conv_wr is not None:
        insights.append(f"Long-conviction trades (>90d): {len(conviction)} positions, {conv_wr}% win rate.")

    overall_wr = _win_rate(sells["is_winner"])
    return AgentFindings(
        agent_name="hold_duration",
        summary="Optimal hold window, churn rate, and conviction trade analysis.",
        metrics=metrics,
        insights=insights,
        edge_score=_edge_score(overall_wr, len(sells)),
    )


# ── Agent 6: Luck vs recipe ───────────────────────────────────────────────────

def luck_vs_skill_agent(df: pd.DataFrame) -> AgentFindings:
    sells = _sells(df)
    insights = []
    metrics = {}

    if len(sells) == 0:
        return AgentFindings(agent_name="luck_vs_skill", summary="No closed trades.", metrics={}, insights=[], edge_score=None)

    total_pnl = sells["pnl"].sum()
    metrics["total_realized_pnl"] = round(total_pnl, 2)

    # Estimate SPY baseline return over same hold periods
    # Simple proxy: (SPY annual return / 252) * days_held * notional
    spy_annual = 0.10   # approximate 10% annualized
    sells["spy_expected"] = sells.apply(
        lambda r: r["quantity"] * r["price"] * spy_annual * (r["days_held"] or 0) / 365,
        axis=1
    )
    spy_baseline = sells["spy_expected"].sum()
    alpha = total_pnl - spy_baseline
    metrics["spy_baseline_pnl"] = round(spy_baseline, 2)
    metrics["estimated_alpha"]  = round(alpha, 2)

    if alpha > 0:
        insights.append(f"Estimated alpha vs SPY baseline: +${alpha:,.0f} — your stock selection has added value over passive holding.")
    else:
        insights.append(f"Estimated alpha vs SPY baseline: -${abs(alpha):,.0f} — a passive SPY position would have outperformed over the same periods.")

    # Consistency: win rate by year
    sells_copy = sells.copy()
    sells_copy["year"] = pd.to_datetime(sells_copy["date"]).dt.year
    wr_by_year  = sells_copy.groupby("year")["is_winner"].apply(_win_rate)
    pnl_by_year = sells_copy.groupby("year")["pnl"].sum().round(2)
    metrics["win_rate_by_year"] = wr_by_year.to_dict()
    metrics["pnl_by_year"]      = pnl_by_year.to_dict()

    # Consistency score: std dev of yearly win rates (lower = more consistent)
    if len(wr_by_year) > 1:
        consistency = 100 - round(wr_by_year.std(), 1)
        metrics["consistency_score"] = max(0, consistency)
        insights.append(f"Year-over-year consistency score: {metrics['consistency_score']}/100 (lower std dev = more consistent edge).")
    else:
        metrics["consistency_score"] = None

    # Biggest winner / loser
    best_trade  = sells.loc[sells["pnl"].idxmax()]
    worst_trade = sells.loc[sells["pnl"].idxmin()]
    metrics["best_trade"]  = {"ticker": best_trade["ticker"],  "pnl": round(best_trade["pnl"], 2)}
    metrics["worst_trade"] = {"ticker": worst_trade["ticker"], "pnl": round(worst_trade["pnl"], 2)}

    # Outsized winner dependency: what % of total P&L comes from top 3 trades?
    top3_pnl = sells.nlargest(3, "pnl")["pnl"].sum()
    top3_pct  = round(top3_pnl / total_pnl * 100, 1) if total_pnl > 0 else None
    metrics["top3_trades_pnl_pct"] = top3_pct
    if top3_pct and top3_pct > 60:
        insights.append(f"Warning: {top3_pct}% of your total P&L comes from just 3 trades — results may be luck-dependent.")

    overall_wr = _win_rate(sells["is_winner"])
    return AgentFindings(
        agent_name="luck_vs_skill",
        summary="Alpha vs SPY baseline, year-over-year consistency, and outsized winner dependency.",
        metrics=metrics,
        insights=insights,
        edge_score=_edge_score(overall_wr, len(sells)),
    )