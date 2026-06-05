# Chapter 4: Mutual Funds and Exchange-Traded Funds (ETFs) - Cheat Sheet

## 4.1 Fund Structures and Share Classes

### Open-End Mutual Funds
**Definition**: Investment vehicles that continuously issue and redeem shares at NAV

**Key Characteristics**:
- No limit on shares issued
- Trade directly with fund company
- Priced once daily at NAV
- AUM fluctuates with flows

**Fund Types**:
- **Standalone Funds**: Independent investment vehicles
- **Fund of Funds (FoF)**: Invest in other mutual funds
- **Target-Date Funds**: Auto-adjust allocation based on time horizon
- **Lifestyle Funds**: Maintain specific risk profiles

### Closed-End Funds (CEFs)
**Definition**: Investment companies that issue fixed number of shares through IPO, then trade on exchanges

**Key Characteristics**:
- Fixed share count
- Trade on exchanges at market prices
- Often trade at premium/discount to NAV
- Can use more leverage

**Premium/Discount Formula**:
```
Premium/Discount = (Market Price - NAV) / NAV
```

**Excel Implementation**:
```excel
=(MarketPrice-NAV)/NAV
```

**Python Implementation**:
```python
def premium_discount(market_price, nav):
    return (market_price - nav) / nav
```

### Share Classes

| Class | Load Structure | Expense Ratio | Key Features |
|-------|---------------|--------------|-------------|
| **A** | Front-end (3-5.75%) | Lower | Breakpoints for larger investments |
| **B** | Back-end (CDSC) | Higher | CDSC declines over time; converts to Class A |
| **C** | Level-load | Highest | Small back-end load if redeemed in first year |
| **I** | No load | Lowest | High minimum investment; institutional |
| **R** | No load | Medium | Designed for retirement plans |

**Fee Calculations**:
```
Front-End Load Impact = Investment × (1 - Front-End Load Rate)
Back-End Load Impact = Redemption Value × (1 - Back-End Load Rate)
Annual Expense Cost = Average Investment Value × Expense Ratio
```

### Exchange-Traded Funds (ETFs)
**Definition**: Pooled investments that trade on exchanges throughout the day

**Key Characteristics**:
- Trade on exchanges like stocks
- Intraday trading and pricing
- More tax-efficient than mutual funds
- Lower expense ratios
- Primarily passive, some active

**Comparison to Mutual Funds**:

| Feature | Open-End Mutual Funds | ETFs |
|---------|------------------------|------|
| Trading | Once daily at NAV | Throughout day at market price |
| Minimum Investment | Often $1,000+ | Price of one share |
| Fees | Higher expense ratios, possible loads | Lower expense ratios, brokerage commissions |
| Tax Efficiency | Less tax-efficient | More tax-efficient |
| Transparency | Holdings disclosed quarterly | Holdings typically disclosed daily |

## 4.2 Active vs. Passive Management

### Active Management
**Definition**: Portfolio managers make specific investment decisions aiming to outperform a benchmark

**Characteristics**:
- Aims to beat benchmark
- Higher expenses (0.5-1.5%)
- Higher turnover (50-100%)
- Potential outperformance/underperformance
- Relies on manager skill

**Performance Metrics**:

1. **Alpha (α)**:
```
Alpha = Fund Return - [Risk-Free Rate + Beta × (Benchmark Return - Risk-Free Rate)]
```

2. **Active Share**:
```
Active Share = (1/2) × Σ|Fund Weight_i - Benchmark Weight_i|
```

3. **Information Ratio**:
```
Information Ratio = (Fund Return - Benchmark Return) / Tracking Error
```

**Python Implementation**:
```python
def calculate_alpha(fund_returns, benchmark_returns, risk_free_rate, beta):
    expected_return = risk_free_rate + beta * (benchmark_returns - risk_free_rate)
    return fund_returns - expected_return

def calculate_information_ratio(fund_returns, benchmark_returns):
    excess_returns = fund_returns - benchmark_returns
    tracking_error = np.std(excess_returns, ddof=1)
    return np.mean(excess_returns) / tracking_error
```

### Passive Management
**Definition**: Aims to replicate the performance of a specific index rather than beat it

**Characteristics**:
- Aims to match benchmark
- Lower expenses (0.03-0.25%)
- Lower turnover (3-20%)
- Predictable relative performance
- Rules-based approach

**Performance Metrics**:

1. **Tracking Error**:
```
Tracking Error = Standard Deviation of (Fund Return - Benchmark Return)
```

2. **Tracking Difference**:
```
Tracking Difference = Fund Return - Benchmark Return
```

**Python Implementation**:
```python
def calculate_tracking_error(fund_returns, benchmark_returns):
    return np.std(fund_returns - benchmark_returns, ddof=1)

def calculate_tracking_difference(fund_returns, benchmark_returns):
    return np.mean(fund_returns - benchmark_returns)
```

### Market Efficiency Spectrum

| Market Segment | Efficiency Level | Active Opportunity |
|----------------|------------------|-------------------|
| Large-cap U.S. equities | High | Lower |
| Small-cap equities | Moderate | Moderate |
| Emerging markets | Lower | Higher |
| Fixed income | Varies | Varies |
| Alternative assets | Low | Higher |

## 4.3 NAV Calculation and Fund Flows

### NAV Calculation
**Formula**:
```
NAV = (Total Assets - Total Liabilities) / Shares Outstanding
```

**Excel Implementation**:
```excel
=((TotalAssets+Cash+Receivables)-(Expenses+Payables+OtherLiabilities))/SharesOutstanding
```

**Python Implementation**:
```python
def calculate_nav(total_assets, total_liabilities, shares_outstanding):
    net_assets = total_assets - total_liabilities
    return net_assets / shares_outstanding
```

### Fair Valuation Methods
1. **Comparable Security**: Pricing based on similar securities
2. **Matrix Pricing**: Using metrics like credit quality and duration
3. **DCF**: Present value of expected cash flows
4. **Third-Party Services**: Independent valuations

### Fund Flows
**Definitions**:
- **Inflows**: New investments into fund
- **Outflows**: Redemptions/withdrawals
- **Net Flows**: Inflows - Outflows

**Formulas**:
```
Net Fund Flow = Inflows - Outflows
Flow Rate = Net Fund Flow / Beginning AUM
```

**Python Implementation**:
```python
def calculate_fund_flows(beginning_aum, ending_aum, performance_return):
    performance_impact = beginning_aum * performance_return
    net_flows = ending_aum - beginning_aum - performance_impact
    return net_flows

def calculate_flow_rate(net_flows, beginning_aum):
    return net_flows / beginning_aum
```

### Flow Impact on Performance
1. **Cash Drag**: Uninvested cash during inflows
2. **Forced Selling**: Selling at inopportune times during outflows
3. **Transaction Costs**: Both flows create trading costs
4. **Strategy Capacity**: Some strategies work better at smaller sizes

## 4.4 ETF Creation/Redemption Mechanism

### Authorized Participants (APs)
**Definition**: Large financial institutions with agreements to create/redeem ETF shares

**Key Roles**:
1. Create/redeem ETF shares in large blocks
2. Facilitate primary market transactions
3. Provide secondary market liquidity
4. Enable price discovery and arbitrage

### Creation Process
**Steps**:
1. AP assembles securities basket matching index
2. AP delivers basket to ETF sponsor
3. ETF sponsor provides creation units to AP
4. AP sells ETF shares in market

### Redemption Process
**Steps**:
1. AP acquires creation unit of ETF shares
2. AP delivers ETF shares to sponsor
3. ETF sponsor provides securities basket
4. AP sells or holds securities

### Arbitrage Mechanism
**ETF Premium Scenario**:
1. AP buys underlying securities
2. Exchanges for ETF shares
3. Sells ETF shares at premium
4. Premium disappears through arbitrage

**ETF Discount Scenario**:
1. AP buys ETF shares at discount
2. Exchanges for underlying securities
3. Sells securities at higher value
4. Discount disappears through arbitrage

**Python Implementation**:
```python
def etf_arbitrage_opportunity(etf_price, nav, transaction_costs):
    premium = (etf_price - nav) / nav
    
    if premium > transaction_costs:
        return (True, "Creation", premium - transaction_costs)
    
    if -premium > transaction_costs:
        return (True, "Redemption", -premium - transaction_costs)
    
    return (False, None, 0)
```

### Transaction Types

| Feature | In-Kind Transactions | Cash Transactions |
|---------|----------------------|-------------------|
| **Process** | Exchange securities for ETF shares | AP provides/receives cash |
| **Tax Efficiency** | More tax-efficient | Less tax-efficient |
| **Common For** | Equity ETFs, many fixed-income ETFs | Commodity ETFs, some international ETFs |

### ETF Tax Advantages
1. **In-Kind Redemptions**: Purge low-cost-basis securities without realizing gains
2. **Lower Turnover**: Less portfolio turnover than active mutual funds
3. **No Forced Sales**: Don't need to sell securities to meet redemptions

**Python Implementation**:
```python
def compare_tax_efficiency(etf_turnover, etf_capital_gain_distribution,
                          mutual_fund_turnover, mutual_fund_capital_gain_distribution,
                          tax_rate, investment_amount):
    etf_tax_impact = investment_amount * etf_capital_gain_distribution * tax_rate
    mutual_fund_tax_impact = investment_amount * mutual_fund_capital_gain_distribution * tax_rate
    
    tax_savings = mutual_fund_tax_impact - etf_tax_impact
    return tax_savings
```
