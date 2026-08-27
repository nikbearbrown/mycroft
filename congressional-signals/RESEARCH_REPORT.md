# Do Congressional Stock Trades Predict Returns? An Event-Study Backtest of Cluster Signals in Post–STOCK Act Disclosures

**Ameya Deshmukh**
Northeastern University · Humanitarians AI (Mycroft Project)
deshmukh.amey@northeastern.edu

**Working paper — July 2026**

---

## Abstract

We build an open, reproducible pipeline that collects U.S. congressional stock-trade disclosures, enriches each trade with market prices, and evaluates whether these public filings constitute a tradeable signal for retail investors. Using **13,877 trades from 108 members of Congress (May 2023 – June 2026)**, of which **10,183 had complete post-disclosure price data**, we compute per-trade abnormal returns against the S&P 500 (SPY) over matched 30-day windows and run an event-study backtest in which trades are tiered *only* by information available at entry. We find that **congressional buying in aggregate does not beat the market** (mean abnormal return +0.13%, win rate 47.1%), consistent with Eggers & Hainmueller (2013). However, a **cluster signal** — two or more members independently buying the same ticker within a 30-day window — separates modestly but consistently from noise: clustered buys earn positive abnormal returns (+0.23% to +0.54%) and win ~50% of the time, versus negative abnormal returns (−0.05%) and ~45% for non-clustered trades. The effect is small in magnitude and, critically, our conviction-weighted `signal_score` does not rank cleanly *within* clusters — indicating that **cluster membership, not conviction weighting, is the source of the edge**. We document a methodological caution: on a 64-member subset the effect appeared inverted, a small-sample artifact that stabilized only at scale. We release the full pipeline, an MCP server exposing the data as queryable tools, and all code.

---

## 1. Introduction

The Stop Trading on Congressional Knowledge (STOCK) Act (2012) requires members of Congress to publicly disclose personal securities transactions within 45 days. A regime designed to deter insider advantage inadvertently produced a **public dataset** of the trades of individuals with privileged access to legislative, regulatory, and briefing information. If those trades systematically earn abnormal returns *and* the returns persist past the disclosure date, retail investors with timely access to filings would gain a replicable edge.

This paper asks a deliberately narrow, testable question: **if a retail investor mechanically followed congressional buy disclosures, would they beat the market?** We answer with an event-study backtest that is careful to avoid look-ahead bias and that reports its negative and positive results with equal weight.

Contributions:
1. An open, end-to-end pipeline (scrape → price-enrich → market-adjust → cluster → score → backtest) released as reproducible code.
2. A per-trade market-adjustment methodology stricter than the aggregate benchmarking used in prior literature.
3. An honest event-study backtest that isolates a small but directionally-consistent cluster signal and openly reports where the signal fails.
4. An MCP (Model Context Protocol) server exposing the analysis as natural-language-queryable tools.

---

## 2. Data

Congressional disclosures were scraped from Capitol Trades (capitoltrades.com), the largest public aggregator of STOCK Act filings, using a Selenium pipeline with checkpoint/resume. Each record contains politician, ticker, trade type (BUY/SELL), transaction date, disclosure date, and a reported amount range.

| Metric | Value |
|--------|-------|
| Politicians | 108 |
| Total trades | 13,877 |
| Trades with complete post-disclosure pricing | 10,183 (73%) |
| Priced BUY events (backtest sample) | 5,162 |
| Date range | May 2023 – June 2026 |

Price data was obtained from Yahoo Finance. Roughly 27% of trades are unpriceable — non-equity instruments (bonds, options), delisted tickers, or recent disclosures whose 30-day forward window has not yet closed — and are excluded rather than imputed.

---

## 3. Methodology

### 3.1 Returns measured from the disclosure date

For each trade we measure the equity's return over the **30 calendar days following the disclosure date** — not the transaction date. This is the earliest point at which a retail investor could act on public information, and it eliminates look-ahead bias in strategy construction.

### 3.2 Per-trade market adjustment

For every trade we subtract SPY's return over the *identical* 30-day window:

> abnormal return (α) = trade 30-day return − SPY 30-day return (matched window)

This is stricter than the annualized, portfolio-level benchmarking of prior literature: it controls for market beta trade-by-trade, so a stock that merely rose with the index shows no alpha.

### 3.3 Cluster detection

A **cluster** is defined as **≥ 2 distinct politicians** executing BUY transactions in the same ticker within a **30-day rolling window**. Cluster size is the count of distinct participants (not trade rows).

### 3.4 Signal score and tiering (no look-ahead)

For each politician we compute a **Buy-Conviction Ratio**, BCR = BUYs ÷ (BUYs + SELLs), over their full history. The entry-time signal score is:

> signal_score = cluster_size × max(BCR of cluster members)

Trades are tiered **solely by this entry-time score** — the realized return is never used to assign a tier, avoiding the circularity that inflates naive "top cluster" statistics:

- **STRONG:** score ≥ 2.0 · **WATCH:** 1.0 ≤ score < 2.0 · **SKIP:** cluster but score < 1.0 · **SOLO:** no cluster.

---

## 4. Results

### 4.1 Aggregate: Congress rides the market

| Trade type | n | Raw 30d | SPY | **Abnormal (α)** |
|-----------|---|---------|-----|------------------|
| BUY | 5,162 | +2.23% | +2.10% | **+0.13%** |
| SELL | 4,972 | +2.01% | +2.02% | **−0.01%** |

Mean congressional buying returns are almost entirely explained by market beta. The average member does not beat a passive index — consistent with Eggers & Hainmueller (2013).

### 4.2 Backtest by signal tier

Event-study backtest, 30-day hold, tiers assigned at entry:

| Tier | n | Return | SPY | **Alpha** | Win% |
|------|---|--------|-----|-----------|------|
| STRONG (cluster) | 815 | +2.47% | +2.24% | **+0.23%** | **50.3%** |
| WATCH (cluster) | 1,212 | +3.14% | +2.61% | **+0.54%** | **50.6%** |
| SKIP | 132 | +1.96% | +2.00% | −0.04% | 44.7% |
| SOLO (no cluster) | 3,003 | +1.81% | +1.86% | −0.05% | 44.9% |
| ALL BUYS | 5,162 | +2.23% | +2.10% | +0.13% | 47.1% |

**The cluster signal separates from noise.** Clustered buys (STRONG + WATCH) earn positive abnormal returns and win ~50% of the time; non-clustered trades (SOLO + SKIP) earn negative abnormal returns and win ~45%. The ~5-percentage-point win-rate gap across 5,162 events is the most robust result in the study.

A $10,000 equal-weighted allocation across STRONG signals returns **$10,247**, versus **$10,224** for the same capital in SPY.

### 4.3 The conviction score does not rank within clusters

WATCH (+0.54%) outperforms STRONG (+0.23%), so the signal score is **not monotone**. Because we use the *maximum* BCR in a cluster, and popular tickers almost always contain at least one near-pure buyer, the conviction term saturates near 1.0 and the score collapses toward raw cluster size. **Cluster membership carries the edge; the conviction weighting adds no ranking power as currently formulated.**

### 4.4 Sample-size caution

On an earlier 64-member subset (67 STRONG events), the STRONG tier showed *negative* abnormal return (−2.63%) — an apparent inversion. Expanding to 108 members (815 STRONG events) stabilized the effect to a small positive edge. This is a direct illustration of small-sample fragility: the signal is only interpretable at scale.

---

## 5. Discussion

The results support a nuanced thesis. The popular narrative that "Congress beats the market" does not hold in aggregate under strict per-trade market adjustment. But the data are not uninformative: **independent convergence** — multiple members buying the same equity in a tight window — is associated with a small, directionally-consistent improvement in forward odds. This is consistent with (though not proof of) shared access to sector-level information during periods of active legislation. The signal is weak enough that it is best understood as a **filter that removes noise** rather than a profit engine: its value is in the ~95% of trades it declines to flag.

---

## 6. Limitations

1. **Magnitude.** The edge is small (+0.23% abnormal return over 30 days); after realistic transaction costs and slippage it may not be economically exploitable.
2. **No significance testing yet.** We report point estimates and win rates; formal t-tests / bootstrap confidence intervals on the tier differences remain future work.
3. **In-sample.** All tiers are evaluated on the same period; no train/test split.
4. **Position sizing.** Disclosures report amount ranges, not exact values, so returns are unweighted by capital deployed.
5. **Causation.** We measure correlation between convergence and returns; we cannot establish that members traded on privileged information rather than public analysis.
6. **Coverage.** 108 of ~194 members; expansion was paused by source-side rate limiting on the listing endpoint.

---

## 7. Conclusion

Using 13,877 disclosures from 108 members of Congress with strict per-trade market adjustment, we find that congressional buying in aggregate does not beat the market, but that **cluster buys — two or more members converging on the same ticker within 30 days — carry a small, consistent edge** (~50% vs ~45% win rate; positive vs negative abnormal return). Our conviction-weighted score does not add ranking power within clusters, and the effect is small and not yet significance-tested. The honest conclusion is that most congressional trading is noise, and the informative residual is narrow — isolating it, and reporting where the signal fails, is the contribution of this work.

---

## Appendix — System

The pipeline is released as an open, Mycroft-framework-compliant module: a Selenium scraper (INGEST), a resumable price enricher and per-trade SPY market-adjuster (GIGO), and cluster/scoring/backtest tools plus a five-tool FastMCP server (TOOL) that exposes the verified data for natural-language querying. A LangGraph state machine orchestrates conformance → cluster → scorer → research → report with a hard data-quality gate. Code: `github.com/Ameya-Deshmukh26/multi-agent-rag`.

## References

- Ziobrowski, A.J., Cheng, P., Boyd, J.W., & Ziobrowski, B.J. (2004). Abnormal Returns from the Common Stock Investments of the U.S. Senate. *Journal of Financial and Quantitative Analysis*, 39(4), 661–676.
- Ziobrowski, A.J., Boyd, J.W., Cheng, P., & Ziobrowski, B.J. (2011). Abnormal Returns from the Common Stock Investments of Members of the U.S. House of Representatives. *Business and Politics*, 13(1).
- Eggers, A.C., & Hainmueller, J. (2013). Capitol Losses: The Mediocre Performance of Congressional Stock Portfolios. *Journal of Politics*, 75(2), 535–551.
- U.S. Congress (2012). Stop Trading on Congressional Knowledge Act (STOCK Act). Public Law 112-105.

*This report is for research and educational purposes only and does not constitute financial advice. No trades were placed.*
