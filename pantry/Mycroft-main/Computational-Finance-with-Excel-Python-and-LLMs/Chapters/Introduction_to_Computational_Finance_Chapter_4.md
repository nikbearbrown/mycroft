# Chapter 4: Mutual Funds and Exchange-Traded Funds (ETFs)

Mutual funds and ETFs are investment vehicles that pool money from multiple investors to purchase a diversified portfolio of securities. This chapter explores their structures, management approaches, valuation methods, and unique characteristics.

## 4.1 Fund Structures and Share Classes

Investment funds exist in various structures designed to meet different investor needs, from traditional mutual funds to innovative exchange-traded products.

### Open-End Mutual Funds

Open-end funds continuously issue and redeem shares at the net asset value (NAV) calculated at the end of each trading day.

**Key Characteristics:**
- No limit on shares that can be issued
- Shares traded directly with the fund company
- Priced once daily at NAV
- Assets expand or contract based on investor flows

**Fund Structures:**
- **Standalone Funds**: Independent investment vehicles with specific objectives
- **Fund of Funds (FoF)**: Invest in other mutual funds for added diversification
- **Target-Date Funds**: Automatically adjust asset allocation as target date approaches
- **Lifestyle/Risk-Based Funds**: Maintain specific risk profiles (conservative to aggressive)

### Closed-End Funds (CEFs)

Closed-end funds issue a fixed number of shares through an IPO and then trade on exchanges like stocks, often at prices different from their NAV.

**Key Characteristics:**
- Fixed number of shares outstanding
- Trade on exchanges at market-determined prices
- Often trade at premiums or discounts to NAV
- Can use more leverage than open-end funds

**Premium/Discount Calculation:**
```
Premium/Discount = (Market Price - NAV) / NAV
```

### Share Classes

Many mutual funds offer multiple share classes with different fee structures tailored to various investor types and distribution channels.

**Common Share Classes:**
1. **Class A Shares**:
   - Front-end load (typically 3-5.75%)
   - Lower ongoing expenses
   - Breakpoints for larger investments

2. **Class B Shares**:
   - Back-end load (contingent deferred sales charge)
   - Higher expense ratios
   - CDSC typically declines over time
   - Often convert to Class A after CDSC period

3. **Class C Shares**:
   - Level-load structure
   - Small back-end load if redeemed within first year
   - Higher ongoing expense ratios

4. **Institutional/Class I Shares**:
   - No loads
   - Lowest expense ratios
   - High minimum investments

5. **Retirement/Class R Shares**:
   - Designed for retirement plans
   - No loads but may have revenue sharing fees

### Exchange-Traded Funds (ETFs)

ETFs combine features of both open-end and closed-end funds, trading on exchanges throughout the day while maintaining a structure that helps keep prices aligned with NAV.

**Key Characteristics:**
- Trade on exchanges at market prices
- Can be bought/sold throughout trading day
- Generally more tax-efficient than mutual funds
- Typically have lower expense ratios
- Most follow passive strategies, though active ETFs exist

## 4.2 Active vs. Passive Management

The debate between active and passive investment approaches represents one of the fundamental choices in fund selection.

### Active Management

Active management involves portfolio managers making specific investment decisions with the goal of outperforming a benchmark index.

**Characteristics:**
- Aims to outperform a benchmark
- Higher expense ratios (typically 0.5-1.5% for equity funds)
- Potential for outperformance and underperformance
- Higher portfolio turnover (typically 50-100% annually)
- Relies on manager skill and research

**Performance Metrics:**
1. **Alpha (α)**: Measures excess return relative to benchmark adjusted for risk
   ```
   Alpha = Fund Return - [Risk-Free Rate + Beta × (Benchmark Return - Risk-Free Rate)]
   ```

2. **Active Share**: Percentage of holdings that differ from benchmark
   ```
   Active Share = (1/2) × Σ|Fund Weight_i - Benchmark Weight_i|
   ```

3. **Information Ratio**: Excess return per unit of active risk
   ```
   Information Ratio = (Fund Return - Benchmark Return) / Tracking Error
   ```

### Passive Management

Passive management aims to replicate the performance of a specific index rather than trying to outperform it.

**Characteristics:**
- Aims to match benchmark performance
- Lower expense ratios (typically 0.03-0.25%)
- Predictable relative performance
- Rules-based approach with minimal discretion
- Lower portfolio turnover (typically 3-20% annually)

**Performance Metrics:**
1. **Tracking Error**: Standard deviation of fund return minus benchmark return
   ```
   Tracking Error = Standard Deviation of (Fund Return - Benchmark Return)
   ```

2. **Tracking Difference**: Actual difference in returns over a period
   ```
   Tracking Difference = Fund Return - Benchmark Return
   ```

### Factors Influencing Active vs. Passive Decision

1. **Market Efficiency**: Active management may have more opportunities in less efficient markets
2. **Costs**: Passive strategies typically have lower costs, which compound over time
3. **Tax Considerations**: Passive strategies generally create fewer taxable events
4. **Risk Tolerance**: Active strategies may deviate significantly from benchmarks
5. **Market Segments**: Some markets are more conducive to active management than others

## 4.3 NAV Calculation and Fund Flows

The net asset value (NAV) represents the per-share value of a fund and serves as the basis for transactions in mutual funds.

### NAV Calculation

**Formula:**
```
NAV = (Total Assets - Total Liabilities) / Shares Outstanding
```

**Components:**
1. **Total Assets**: Market value of all securities plus cash and receivables
2. **Total Liabilities**: All expenses, payables, and other obligations
3. **Shares Outstanding**: Total fund shares owned by investors

### NAV Timing and Fair Valuation

Most U.S. mutual funds calculate NAV once per day after market close using closing prices.

**Special Considerations:**
1. **International Securities**: May require fair value adjustments
2. **Illiquid Securities**: Require pricing committees to determine fair value
3. **Forward Pricing**: Orders before cut-off time receive next calculated NAV

**Fair Valuation Methods:**
1. **Comparable Security Approach**: Pricing based on similar securities
2. **Matrix Pricing**: Using metrics like credit quality and duration
3. **Discounted Cash Flow (DCF)**: Based on present value of expected cash flows
4. **Third-Party Pricing Services**: Independent valuations

### Fund Flows and Impact

Fund flows represent the net movement of investor money into or out of a fund.

**Types of Fund Flows:**
1. **Inflows**: New investments into the fund
2. **Outflows**: Redemptions or withdrawals from the fund
3. **Net Flows**: Difference between inflows and outflows

**Calculation:**
```
Net Fund Flow = Inflows - Outflows
Flow Rate = Net Fund Flow / Beginning AUM
```

### Impact of Flows on Performance

Fund flows can significantly impact performance, especially for less liquid strategies.

**Flow-Performance Relationship:**
1. **Cash Drag**: High inflows may lead to uninvested cash
2. **Forced Selling**: Heavy outflows may force selling at inopportune times
3. **Transaction Costs**: Both inflows and outflows generate trading costs
4. **Strategy Capacity**: Some strategies perform better at smaller asset levels

## 4.4 ETF Creation/Redemption Mechanism

The creation and redemption mechanism distinguishes ETFs from mutual funds and helps keep ETF market prices aligned with their underlying NAVs.

### Authorized Participants (APs)

Authorized Participants are large financial institutions that have agreements with ETF sponsors to create and redeem ETF shares in large blocks.

**Key Roles:**
1. Create and redeem ETF shares in large blocks (creation units)
2. Facilitate primary market transactions with ETF sponsor
3. Provide liquidity in secondary market
4. Facilitate price discovery and arbitrage

### Creation Process

**Steps:**
1. AP assembles a portfolio matching the ETF's underlying index
2. AP delivers this basket to ETF sponsor
3. ETF sponsor provides AP with creation units (blocks of ETF shares)
4. AP can sell ETF shares in the secondary market

### Redemption Process

**Steps:**
1. AP acquires a creation unit worth of ETF shares
2. AP delivers these ETF shares to the ETF sponsor
3. ETF sponsor provides AP with the corresponding basket of securities
4. AP can sell these securities or hold them

### Arbitrage Mechanism

The creation/redemption process enables arbitrage that keeps ETF market prices aligned with NAVs.

**Scenarios:**
1. **ETF Trading at Premium to NAV:**
   - AP buys underlying basket of securities
   - AP exchanges securities for ETF shares
   - AP sells ETF shares at premium
   - Process continues until premium is eliminated

2. **ETF Trading at Discount to NAV:**
   - AP buys ETF shares at discount
   - AP exchanges ETF shares for underlying securities
   - AP sells underlying securities at higher value
   - Process continues until discount is eliminated

### Cash vs. In-Kind Transactions

**In-Kind Transactions:**
- AP exchanges securities for ETF shares (creation) or vice versa (redemption)
- More tax-efficient as ETF doesn't realize capital gains
- Common for equity ETFs and many fixed-income ETFs

**Cash Transactions:**
- AP provides cash instead of securities
- Less tax-efficient but sometimes necessary
- Common for commodity ETFs, international ETFs, and some fixed-income ETFs

### Tax Efficiency of ETFs

ETFs are generally more tax-efficient than mutual funds primarily due to the in-kind creation/redemption mechanism.

**Key Tax Advantages:**
1. **In-Kind Redemptions**: Allow ETFs to purge low-cost-basis securities
2. **Lower Turnover**: Index-tracking ETFs typically have less portfolio turnover
3. **No Forced Sales**: ETFs don't need to sell securities to meet redemptions
