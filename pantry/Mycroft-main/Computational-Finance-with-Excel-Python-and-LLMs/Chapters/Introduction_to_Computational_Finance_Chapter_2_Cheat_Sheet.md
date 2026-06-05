# CHEAT SHEET Chapter 2: RETURN CALCULATIONS AND RISK MEASURES

## Simple vs. Logarithmic Returns

### Simple Returns
- **Formula (without dividends)**: $R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1$
- **Formula (with dividends)**: $R_t = \frac{P_t + D_t - P_{t-1}}{P_{t-1}}$
- **Excel Implementation**: `=(B3-B2)/B2` or `=(B3+D3-B2)/B2` (with dividends)
- **Python Implementation**: 
  ```python
  simple_returns = prices.pct_change()
  # With dividends
  simple_returns = (prices + dividends - prices.shift(1)) / prices.shift(1)
  ```
- **Properties**: 
  - Additive across assets (portfolio return = weighted average of individual returns)
  - Non-additive across time (must use compounding)
  - Bounded below by -100%, no upper bound

### Logarithmic Returns
- **Formula**: $r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$
- **Excel Implementation**: `=LN(B3/B2)`
- **Python Implementation**: 
  ```python
  log_returns = np.log(prices / prices.shift(1))
  # Or
  log_returns = np.log(prices).diff()
  ```
- **Properties**:
  - Additive across time (multi-period return = sum of individual period returns)
  - Non-additive across assets
  - Symmetric (unbounded)
  - Often closer to normal distribution

### Relationship Between Return Types
- $r_t = \ln(1 + R_t)$
- $R_t = e^{r_t} - 1$
- For small returns: $r_t \approx R_t$

## Arithmetic and Geometric Average Returns

### Arithmetic Average Return
- **Formula**: $\bar{R}_A = \frac{1}{T} \sum_{t=1}^T R_t$
- **Excel Implementation**: `=AVERAGE(R1:Rn)`
- **Python Implementation**: `arithmetic_avg = np.mean(returns)`
- **Use when**: Forecasting single-period returns, short horizons, low volatility

### Geometric Average Return
- **Formula**: $\bar{R}_G = \left[ \prod_{t=1}^T (1 + R_t) \right]^{1/T} - 1$ or $\bar{R}_G = \left( \frac{P_T}{P_0} \right)^{1/T} - 1$
- **Excel Implementation**: `=(PRODUCT(1+R1:Rn)^(1/COUNT(R1:Rn)))-1`
- **Python Implementation**: `geometric_avg = (np.prod(1 + returns))**(1/len(returns)) - 1`
- **For log returns**: $\bar{r}_G = \frac{1}{T} \sum_{t=1}^T r_t$
- **Use when**: Measuring actual historical performance, long horizons, high volatility

### Relationship Between Averages
- Geometric average ≤ Arithmetic average (equality only when all returns are identical)
- Approximation: $\bar{R}_G \approx \bar{R}_A - \frac{\sigma^2}{2}$ (where σ² is return variance)

## Standard Deviation and Variance

### Variance
- **Formula (sample)**: $\sigma^2 = \frac{1}{n-1} \sum_{i=1}^n (R_i - \bar{R})^2$
- **Excel Implementation**: `=VAR.S(R1:Rn)`
- **Python Implementation**: `variance = np.var(returns, ddof=1)`
- **Properties**: 
  - Expressed in squared units
  - Always ≥ 0
  - Additive for independent random variables

### Standard Deviation
- **Formula**: $\sigma = \sqrt{\sigma^2}$
- **Excel Implementation**: `=STDEV.S(R1:Rn)`
- **Python Implementation**: `std_dev = np.std(returns, ddof=1)`
- **Properties**:
  - Same units as returns
  - For normal distribution: ~68% of values within ±1σ, ~95% within ±2σ
  - Annualization: $\sigma_{\text{annual}} = \sigma_{\text{period}} \times \sqrt{k}$ where k = periods per year

### Downside Risk Measures
- **Semi-Variance**: Variance considering only negative returns
- **Value at Risk (VaR)**: Maximum loss at specific confidence level
  - Parametric VaR: $\text{VaR}_\alpha = \mu - Z_\alpha \sigma$ (where Zα is the α-quantile of standard normal)
  - Historical VaR: Specific percentile of historical returns
- **Maximum Drawdown**: Largest peak-to-trough decline

## Risk-Return Relationships

### Sharpe Ratio
- **Formula**: $\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}$
- **Excel Implementation**: `=(PortfolioReturn-RiskFreeRate)/PortfolioStdDev`
- **Python Implementation**: `sharpe_ratio = (mean_return - risk_free_rate) / std_dev`
- **Interpretation**: Higher is better; >1 good, >2 very good, >3 excellent

### Portfolio Risk and Return
- **Portfolio Return**: $R_p = \sum_{i=1}^n w_i R_i$
- **Portfolio Variance**: $\sigma_p^2 = \sum_{i=1}^n \sum_{j=1}^n w_i w_j \sigma_{ij}$
- **Two-Asset Portfolio Variance**: $\sigma_p^2 = w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2w_1 w_2 \sigma_{12}$
- **Portfolio Standard Deviation**: $\sigma_p = \sqrt{\sigma_p^2}$

## Key Excel Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| AVERAGE | `=AVERAGE(range)` | Arithmetic mean of values |
| STDEV.S | `=STDEV.S(range)` | Sample standard deviation |
| VAR.S | `=VAR.S(range)` | Sample variance |
| PRODUCT | `=PRODUCT(range)` | Multiplies all numbers in range |
| SUMPRODUCT | `=SUMPRODUCT(array1,array2)` | Sum of products of corresponding values |
| LN | `=LN(number)` | Natural logarithm |
| EXP | `=EXP(number)` | Exponential function (e^x) |
| NORM.DIST | `=NORM.DIST(x,mean,std_dev,TRUE)` | Normal cumulative distribution function |
| NORM.INV | `=NORM.INV(probability,mean,std_dev)` | Normal inverse distribution function |

## Key Python Functions

```python
# Import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Download data
data = yf.download(['TSLA', 'NVDA', 'AMD', 'META'], start='2020-01-01')['Adj Close']

# Calculate returns
simple_returns = data.pct_change()
log_returns = np.log(data / data.shift(1))

# Calculate average returns
arithmetic_avg = simple_returns.mean()
geometric_avg = (np.prod(1 + simple_returns))**(1/len(simple_returns)) - 1

# Calculate risk measures
std_dev = simple_returns.std()
annual_std = std_dev * np.sqrt(252)  # Annualize daily std dev (252 trading days)

# Calculate Sharpe ratio
risk_free_rate = 0.03  # 3%
sharpe_ratio = (arithmetic_avg * 252 - risk_free_rate) / annual_std

# Calculate rolling volatility (30-day window)
rolling_vol = simple_returns.rolling(window=30).std() * np.sqrt(252)

# Calculate correlation matrix
correlation = simple_returns.corr()

# Calculate VaR (95% confidence)
var_95 = simple_returns.quantile(0.05)  # Historical VaR
```

## LLM Prompts for Return and Risk Analysis

### Simple/Log Returns Explanation
```
Explain the difference between simple returns and logarithmic returns in finance. 
When should each be used? What are their mathematical properties?
Compare their calculations for a stock that goes from $100 to $110, then to $99.
```

### Arithmetic vs. Geometric Returns
```
Compare arithmetic and geometric average returns for [STOCK] over the past 5 years.
Why do they differ? Which should be used for reporting historical performance?
Which should be used for forecasting future returns?
```

### Risk Measurement
```
Analyze the standard deviation of returns for [STOCK]. 
How does its volatility compare to the market average?
What does this tell us about the stock's risk profile?
What other risk measures might provide additional insight?
```

### Risk-Return Tradeoff
```
I've calculated the following metrics for tech stocks:
[Insert return and risk data]

Which stock offers the best risk-adjusted return?
How would you visualize this data to highlight the risk-return tradeoff?
What portfolio allocation would you recommend based on this data?
```

## Common Pitfalls and Mistakes

1. **Forgetting to adjust for dividends** when calculating total returns
2. **Using arithmetic average for multi-period compounding** instead of geometric average
3. **Improper annualization** of returns or standard deviation
4. **Not accounting for time period differences** when comparing investments
5. **Using wrong formula for portfolio risk** (forgetting correlations)
6. **Assuming normal distribution** for returns without testing
7. **Interpreting variance directly** rather than standard deviation
8. **Incorrect handling of outliers** in return series

## Quick Conversion Factors

- **Daily to Annual Returns**: Multiply by 252 (trading days)
- **Daily to Annual Std Dev**: Multiply by √252 ≈ 15.87
- **Weekly to Annual Returns**: Multiply by 52
- **Weekly to Annual Std Dev**: Multiply by √52 ≈ 7.21
- **Monthly to Annual Returns**: Multiply by 12
- **Monthly to Annual Std Dev**: Multiply by √12 ≈ 3.46
- **Quarterly to Annual Returns**: Multiply by 4
- **Quarterly to Annual Std Dev**: Multiply by √4 = 2
