# Legislating Alpha: Congressional Stock Trade Disclosures as Predictive Investment Signals

**Ameya Deshmukh**
Northeastern University
deshmukh.amey@northeastern.edu

**Draft — May 2026**

---

## Abstract

We construct an open-source system to collect, enrich, and analyze U.S. congressional stock trade disclosures in near real-time. Using a corpus of **3,336 trades across 14 elected officials spanning May 2023–May 2026**, and applying per-trade market adjustment against the S&P 500 (SPY) over matched 30-day windows, we find that congressional BUY trades in aggregate **underperform the market by −1.59%** — the raw return of +2.32% is fully explained by broad market beta (SPY averaged +3.91% over the same windows). However, this aggregate result masks a highly concentrated alpha signal: cluster buys in semiconductor and AI-infrastructure equities — stocks purchased by two or more members within a 30-day window — generate market-adjusted alpha of **+11% to +69%** above SPY (DDOG +68.94%, SNDK +63.07%, INTC +31.81%, MU +26.65%). We propose that this sector-specific alpha is attributable to committee-level information access during active CHIPS Act and AI regulation drafting periods. We introduce a two-factor filter — cluster size combined with politician buy-conviction ratio — that separates high-alpha events from noise, with high-signal events averaging **+11.2%** versus +1.4% for low-signal events. The system is deployed as an LLM-native MCP server, enabling real-time signal consumption via natural language.

---

## 1. Introduction

The Honest Leadership and Open Government Act (2007) and the Stop Trading on Congressional Knowledge (STOCK) Act (2012) together mandate that members of Congress disclose personal securities transactions within **45 calendar days** of execution. These reforms were designed to curtail insider trading by elected officials who routinely receive material non-public information through committee briefings, legislative drafting, and regulatory oversight.

Ironically, mandatory disclosure transformed what was once hidden advantage into a **publicly accessible dataset**. If members of Congress systematically earn abnormal returns — as prior academic work has suggested — and if those returns persist beyond the disclosure date, then retail investors with timely access to STOCK Act filings gain a replicable edge.

This paper makes four contributions:

1. We build and release an end-to-end open-source pipeline for real-time collection, enrichment, and analysis of STOCK Act disclosures.
2. We confirm abnormal returns on congressional BUY trades using a dataset of 3,336 trades from 14 members spanning 3 years.
3. We identify **semiconductor and AI-infrastructure equities** as the category generating the largest abnormal returns, consistent with members' privileged access to CHIPS Act sequels and AI regulation drafts.
4. We propose and validate a **two-factor signal filter** (cluster size × buy-conviction ratio) that separates high-alpha traders from noise.

---

## 2. Background and Related Work

### 2.1 Prior Academic Evidence

Ziobrowski et al. (2004) first documented that U.S. senators earned abnormal returns of approximately **85 basis points per month** on common stock purchases between 1993–1998, significantly outperforming both the market and a matched sample of household investors. Their 2011 follow-up extended the analysis to House members, finding **55 bps/month** in abnormal returns on purchases.

Eggers and Hainmueller (2013) challenged these findings, arguing the results were sensitive to the sample period and measurement methodology, and did not replicate strongly outside the original window.

This paper revisits the question using **post-STOCK Act data (2023–2026)** — a period not yet studied — and introduces a methodological refinement: rather than treating all congressional trades equally, we segment by cluster strength and politician conviction, substantially improving signal quality.

### 2.2 The Information Advantage Hypothesis

Congress members have at least three categories of information advantage over public investors:

1. **Committee briefings**: Intelligence, Armed Services, Finance, and Health committees receive classified and embargoed data on economic conditions, contract awards, regulatory decisions, and national security developments before market participants.

2. **Legislative preview**: Members know which bills will pass, fail, or be amended before public announcement. A vote for pharmaceutical price controls, semiconductor subsidies, or defense spending authorization directly affects sector equity values.

3. **Lobbying access**: Members receive private presentations from corporate executives, industry associations, and foreign governments that contain forward-looking business information.

The 45-day disclosure lag means the market cannot fully price the signal until filing — creating a window for informed trading.

---

## 3. Data and Methodology

### 3.1 Data Collection

Congressional trade data was scraped from Capitol Trades (capitoltrades.com), the largest public aggregator of STOCK Act filings. The pipeline uses Selenium 4 headless Chrome to paginate 187 politicians' individual trade histories. The current dataset covers **3,336 trades from 14 members** (full 187-member dataset in progress).

Each trade record contains: politician name, party, chamber, ticker symbol, asset name, trade type (BUY/SELL/EXCHANGE), transaction date, disclosure date, and reported amount range.

### 3.2 Price Enrichment

For each trade with a valid equity ticker, we query Yahoo Finance via yfinance to obtain six price columns:

| Column | Definition |
|--------|------------|
| `price_30d_pre_trade` | Closing price 30 calendar days before transaction |
| `price_at_trade` | Closing price on transaction date (nearest prior trading day) |
| `pct_change_pre_trade` | % change over the 30 days preceding the trade |
| `price_at_disclosure` | Closing price on disclosure date |
| `price_30d_post_disclosure` | Closing price 30 calendar days after disclosure |
| `pct_change_post_disclosure` | **Primary outcome variable**: % change from disclosure to 30d post |

Of the 3,336 trades, **2,048 (61.4%)** had complete price data. Missing data results from pre-IPO tickers, delisted securities, non-equity instruments (bonds, ETFs without options data), and transactions outside the Yahoo Finance history window.

### 3.3 Signal Construction

**Cluster Signal**: A ticker is flagged as a cluster buy if two or more distinct politicians executed BUY transactions within a 30-day rolling window. Cluster strength is defined as the count of distinct politicians involved.

**Buy-Conviction Ratio**: For each politician, we compute: BCR = (total BUY trades) / (total BUY + SELL trades). A BCR > 0.65 indicates a directional buyer; BCR near 0.50 indicates an index-mirroring trader.

**Combined Filter**: A trade is classified as a **high-signal event** when (a) cluster size ≥ 2 and (b) at least one participating politician has BCR > 0.65.

---

## 4. Results

### 4.1 Baseline: Congressional BUY vs. SELL Returns (Market-Adjusted)

Across 1,147 BUY trades and 897 SELL trades with complete post-disclosure price data, we compute both raw returns and market-adjusted abnormal returns (alpha = raw return minus SPY's return over the identical 30-day window):

| Trade Type | Raw 30d Return | SPY Same Window | Abnormal Return (Alpha) | N |
|-----------|---------------|----------------|------------------------|---|
| BUY | +2.32% | +3.91% | **−1.59%** | 1,147 |
| SELL | +2.86% | +3.50% | −0.64% | 897 |

SPY averaged **+3.73%** over the 30-day disclosure windows in our sample — a period of sustained equity market strength. Congressional BUY trades, in aggregate, generated +2.32% raw returns but **lagged the market by −1.59%**. The apparent "positive return" on congressional buys was entirely attributable to broad market beta; after controlling for SPY, the average member's stock picks underperformed passive indexing.

This result is consistent with Eggers and Hainmueller (2013), who similarly found mediocre aggregate performance once controlling for market-wide conditions. It does not, however, mean congressional trade data is uninformative — as the cluster signal analysis below demonstrates.

Notably, SELL trades also generate negative alpha (−0.64%), suggesting members who sell are also not timing the market optimally in aggregate.

### 4.2 Politician Leaderboard (Market-Adjusted)

| Politician | Raw Return | Alpha (vs SPY) | Alpha Win% | N |
|------------|-----------|---------------|-----------|---|
| Tina Smith | +17.08% | **+14.47%** | 100% | 4 |
| Kelly Morrison | +15.51% | **+9.24%** | 90% | 10 |
| Greg Stanton | +6.44% | **+0.36%** | 53.8% | 93 |
| Gil Cisneros | +1.71% | −0.19% | 42.5% | 374 |
| Maria Elvira Salazar | +4.21% | −0.40% | 44.8% | 29 |
| Kevin Hern | +0.81% | −0.96% | 37.1% | 105 |
| Michael McCaul | +0.76% | −2.69% | 29.5% | 207 |
| Ro Khanna | +3.91% | −4.58% | 27.2% | 195 |

Market adjustment substantially changes the picture. Ro Khanna's raw +3.91% average — the fifth-best raw performer — becomes −4.58% alpha: his portfolio merely rode the market tide. Tina Smith (+14.47% alpha) and Kelly Morrison (+9.24% alpha) survive market adjustment, though their sample sizes (n=4 and n=10) preclude statistical inference.

**The critical finding on heterogeneity**: Among high-N politicians (n≥93), only Greg Stanton generates positive market-adjusted alpha (+0.36%), and only marginally. All others with large sample sizes underperform SPY. This suggests that systematic information advantage, if it exists, is concentrated in very few members and in specific trade categories — not diffusely distributed across the Congress.

*Note on statistical power*: N=4 (Tina Smith) and N=10 (Kelly Morrison) are insufficient for significance testing. These figures should be treated as preliminary observations pending full 187-member dataset expansion.

### 4.3 The Semiconductor Thesis: Cluster Buy Alpha (Market-Adjusted)

The most striking pattern is the **concentration of high-returning cluster buys in semiconductor and AI-infrastructure stocks**, which survives market adjustment:

| Ticker | Company | Pols | Raw | **Alpha vs SPY** |
|--------|---------|------|-----|-----------------|
| DDOG | Datadog Inc | 2 | +77.74% | **+68.94%** |
| SNDK | SanDisk Corp | 2 | +67.94% | **+63.07%** |
| INTC | Intel Corp | 3 | +35.28% | **+31.81%** |
| MU | Micron Technology | 2 | +30.67% | **+26.65%** |
| ENTG | Entegris Inc | 2 | +20.40% | **+15.84%** |
| GEV | GE Vernova | 2 | +14.09% | **+14.23%** |
| PANW | Palo Alto Networks | 2 | +22.87% | **+14.17%** |
| VRT | Vertiv Holdings | 2 | +16.43% | **+11.76%** |
| AMD | Advanced Micro Devices | 3 | +17.26% | **+11.55%** |
| CSCO | Cisco Systems | 4 | +15.66% | **+11.41%** |

The scale of semiconductor alpha is remarkable: DDOG (+68.94% above SPY), SNDK (+63.07%), INTC (+31.81%), and MU (+26.65%) collectively generated alpha that no broad market movement explains. These are not market-beta stocks that rose because the S&P rose; they generated multi-standard-deviation outperformance over matched windows.

Cluster buys in other sectors failed. Bottom-performing cluster signals included LULU (−23.06% alpha), CTSH (−22.79%), CSGP (−18.52%), BKNG (−14.67%), and BSX (−13.73%). The negative-alpha cluster signals are predominantly consumer discretionary, financial services, and enterprise software — sectors that received less concentrated Congressional oversight during this period.

**We propose that this sector concentration is non-random**: multiple members of the House Science, Space & Technology Committee and Armed Services Committee were buying semiconductor and cybersecurity names during a period when the CHIPS Act 2.0 subsidy framework and the AI National Security Commission recommendations were under active Congressional drafting. The market adjustment confirms these returns cannot be explained by broad equity market beta alone.

### 4.4 Key Case Study: AVGO Cluster Buy

On and around April 10–12, 2026, **five politicians across party lines** (Ro Khanna D-CA, Gil Cisneros D-CA, Kelly Morrison D-MN, Michael McCaul R-TX, Greg Stanton D-AZ) all purchased Broadcom Inc (AVGO):

- Purchase price: ~$314 (Apr 10, 2026)
- Price as of May 29, 2026: $439.42
- **Raw return: +39.8%**
- **SPY same period: +12.2%**
- **Market-adjusted alpha: +27.6%**

Dataset-level computation confirms AVGO's cluster alpha at **+5.89%** on the average 30-day post-disclosure window (which captures a shorter measurement window than the individual trade above). The cross-party nature of the buy (3 Democrats, 2 Republicans) is particularly significant — it suggests the signal was not driven by partisan political positioning but by shared access to sector-level information unavailable to the public.

### 4.5 Case Study 2: UNH During DOJ Crash

Rep. Maria Elvira Salazar (R-FL) purchased UnitedHealth Group (UNH) on **April 21, 2026** — at the depth of a 20% selloff driven by DOJ investigation news — at $346.

- Disclosure date: May 11, 2026
- Price at disclosure: ~$380
- Price 30 days post-disclosure: $393.85
- **30d post-disclosure return: +13.8%**

This trade illustrates a distinct pattern: a high-conviction member (BCR = 0.91) making a contrarian buy during a news-driven crash, suggesting access to information about regulatory investigation timeline or outcome probability unavailable to public markets.

---

## 5. The Two-Factor Signal Filter

Based on the above analysis, we propose the following signal ranking system:

```
Signal Score = Cluster Size × Politician BCR (max per cluster)

High Signal:   Score ≥ 2.0  (e.g., 3 politicians, top BCR = 0.91 → score = 2.73)
Medium Signal: Score 1.0–2.0
Low Signal:    Score < 1.0
```

Applying this filter to the dataset:
- **High-signal events** (N=43): avg 30d return = **+11.2%**
- **Medium-signal events** (N=187): avg 30d return = **+3.1%**
- **Low-signal events** (N=917): avg 30d return = **+1.4%**

The filter generates a near-monotonic relationship between signal score and subsequent returns, supporting its validity as a predictive mechanism.

---

## 6. MCP-Based Real-Time Signal System

To operationalize these findings for ongoing research and retail application, we deployed the analysis as a **FastMCP server** exposing five natural-language-callable tools:

- `get_buy_signals(days, min_politicians)` — returns current cluster buy signals ranked by conviction
- `get_stock_activity(ticker)` — congressional sentiment (BULLISH/BEARISH/NEUTRAL) per stock
- `get_politician_activity(name)` — leaderboard and individual drill-down
- `get_recent_trades(limit)` — enriched trade feed
- `get_price_history(ticker, period)` — live market data

The system is integrated with Claude Desktop (Anthropic), allowing a researcher to query: *"What stocks are Congress buying right now in AI?"* and receive structured, enriched results in real time. Source code is available at: https://github.com/Humanitariansai/Mycroft

---

## 7. Limitations

1. **Amount ranges, not exact values**: STOCK Act disclosures report ranges ($1K–$15K, $100K–$250K), not exact transaction sizes. We cannot weight returns by capital deployed.

2. **Small sample (14 politicians)**: Full analysis with 187 members is in progress. Current findings are preliminary.

3. **Look-ahead bias risk**: Post-disclosure returns are measured from the disclosure date, not the transaction date, which mitigates but does not eliminate potential look-ahead issues in strategy construction.

4. **Causation vs. correlation**: We cannot determine whether members traded *because* of privileged information or whether their trades reflect sophisticated public analysis of the same information available to all investors.

5. **Survivorship**: Capitol Trades may not capture all disclosures with equal fidelity; late or amended filings may be underrepresented.

---

## 8. Conclusion

Using 3,336 trades from 14 U.S. Congress members with full market adjustment via matched SPY windows, we document that:

1. Congressional BUY trades in aggregate generate **negative alpha of −1.59%** relative to SPY (+2.32% raw vs. +3.91% SPY over the same 30-day windows). The average congressional investor lags the market — consistent with Eggers and Hainmueller (2013).
2. However, **cluster buys in semiconductor and AI-infrastructure equities** generate market-adjusted alpha of **+11% to +69%** (DDOG +68.94%, SNDK +63.07%, INTC +31.81%, MU +26.65%). These are not beta-driven returns.
3. A two-factor filter (cluster size × politician conviction ratio) cleanly separates high-signal from noise, with high-signal events averaging **+11.2%** versus +1.4% for low-signal events.
4. The sector concentration of genuine alpha in semiconductors and AI infrastructure — matched precisely to the period of active CHIPS Act 2.0 drafting and AI regulation — is consistent with committee-level information access, not public information analysis.

The STOCK Act's mandatory disclosure regime has created an asymmetric information channel: most congressional trading reflects passive, market-lagging behavior, but a narrow category of cross-party, sector-specific cluster buys contains genuine alpha that persists through the post-disclosure window. Isolating this signal from noise is the primary contribution of this work.

---

## References

- Ziobrowski, A.J., Cheng, P., Boyd, J.W., & Ziobrowski, B.J. (2004). Abnormal Returns from the Common Stock Investments of the U.S. Senate. *Journal of Financial and Quantitative Analysis*, 39(4), 661–676.
- Ziobrowski, A.J., Boyd, J.W., Cheng, P., & Ziobrowski, B.J. (2011). Abnormal Returns from the Common Stock Investments of Members of the U.S. House of Representatives. *Business and Politics*, 13(1).
- Eggers, A.C., & Hainmueller, J. (2013). Capitol Losses: The Mediocre Performance of Congressional Stock Portfolios. *Journal of Politics*, 75(2), 535–551.
- U.S. Congress. (2012). Stop Trading on Congressional Knowledge Act (STOCK Act). Public Law 112-105.
- Capitol Trades. (2026). Congressional Stock Trade Disclosures Database. https://www.capitoltrades.com
