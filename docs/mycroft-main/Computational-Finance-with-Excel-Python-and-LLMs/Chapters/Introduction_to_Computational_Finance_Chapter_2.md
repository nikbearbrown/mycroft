# Chapter 2: Return Calculations and Risk Measures

## 2.1 Simple vs. Logarithmic Returns

The foundation of financial analysis lies in accurately measuring the performance of investments. Returns represent the gain or loss on an investment over a specified period and are typically expressed as a percentage of the initial investment. Two fundamental approaches to calculating returns are widely used in finance: simple returns and logarithmic returns. Each has distinct properties and applications that make them suitable for different analytical contexts.

### Simple Returns

Simple returns (also called arithmetic or discrete returns) measure the percentage change in the value of an investment over a specific period.

#### Formula

For a single period without dividends or cash flows:

$$R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1$$

Where:
- $R_t$ is the simple return for period $t$
- $P_t$ is the price at the end of period $t$
- $P_{t-1}$ is the price at the beginning of period $t$

When dividends or other cash flows are present, the formula becomes:

$$R_t = \frac{P_t + D_t - P_{t-1}}{P_{t-1}}$$

Where $D_t$ represents dividends or other cash flows received during period $t$.

#### Properties of Simple Returns

1. **Intuitive Interpretation**: Simple returns are easily understood as the percentage gain or loss on an investment.

2. **Additivity Across Assets**: Portfolio returns can be calculated as the weighted average of individual asset returns:
   
   $$R_p = \sum_{i=1}^n w_i R_i$$
   
   Where $w_i$ is the weight of asset $i$ in the portfolio and $R_i$ is the return of asset $i$.

3. **Non-Additivity Across Time**: Simple returns cannot be directly added across time periods. For multi-period returns, we must use compounding:
   
   $$1 + R_{(0,T)} = (1 + R_1) \times (1 + R_2) \times ... \times (1 + R_T)$$

4. **Asymmetry**: Simple returns are bounded below by -100% (complete loss) but have no upper bound.

### Logarithmic Returns

Logarithmic returns (also called continuously compounded returns or log returns) are calculated using the natural logarithm of the ratio of prices.

#### Formula

For a single period without dividends:

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$$

Where:
- $r_t$ is the logarithmic return for period $t$
- $\ln$ is the natural logarithm function

For investments with dividends, adjustments to the price series are typically made before calculating log returns.

#### Properties of Logarithmic Returns

1. **Additivity Across Time**: Log returns can be directly added across time periods:
   
   $$r_{(0,T)} = r_1 + r_2 + ... + r_T$$

2. **Non-Additivity Across Assets**: Unlike simple returns, portfolio log returns cannot be calculated as a weighted average of individual log returns.

3. **Symmetry**: Log returns are unbounded both above and below, providing a more symmetric distribution.

4. **Normal Distribution Approximation**: Log returns often more closely approximate a normal distribution, making them suitable for statistical analyses.

5. **Relationship to Simple Returns**: For small returns, log returns closely approximate simple returns:
   
   $$r_t \approx R_t \text{ when } R_t \text{ is small}$$

   The exact relationship is: $r_t = \ln(1 + R_t)$ and $R_t = e^{r_t} - 1$

### Comparison and Conversion

Let's illustrate the differences between simple and logarithmic returns with an example using Tesla (TSLA) stock.

#### Example: TSLA Returns Calculation

Consider the following closing prices for TSLA over a week:

| Date       | Closing Price ($) | Simple Return (%) | Log Return (%) |
|------------|-------------------|-------------------|----------------|
| 2023-01-02 | 123.18            | -                 | -              |
| 2023-01-03 | 108.10            | -12.24%           | -13.04%        |
| 2023-01-04 | 113.64            | 5.12%             | 5.00%          |
| 2023-01-05 | 110.34            | -2.90%            | -2.94%         |
| 2023-01-06 | 113.06            | 2.46%             | 2.44%          |

**Simple Return Calculation (January 3):**
```
R = (108.10 - 123.18) / 123.18 = -0.1224 = -12.24%
```

**Log Return Calculation (January 3):**
```
r = ln(108.10 / 123.18) = ln(0.8776) = -0.1304 = -13.04%
```

#### Implementation in Excel

Simple and logarithmic returns can be easily calculated in Excel:

```
# Simple Return
= (B3 - B2) / B2

# Log Return
= LN(B3 / B2)
```

#### Implementation in Python

```python
import numpy as np
import pandas as pd

# Assuming prices is a pandas Series of stock prices
# Simple returns
simple_returns = prices.pct_change()

# Log returns
log_returns = np.log(prices / prices.shift(1))

# Or directly using pandas
log_returns = np.log(prices).diff()
```

#### When to Use Each Type of Return

**Use Simple Returns When:**
- Calculating portfolio returns from individual asset returns
- Communicating performance to non-technical stakeholders
- Working with returns over a single period
- Analyzing actual realized gains and losses

**Use Log Returns When:**
- Analyzing returns over multiple time periods
- Performing statistical analyses that assume normality
- Modeling continuous-time processes
- Working with time series models and volatility forecasting

### Impact of Dividends and Cash Flows

For accurate return calculations, it's essential to account for dividends and other cash flows. There are two main approaches:

1. **Total Return Calculation**: Add dividends to the price at the time they are received.

2. **Adjusted Price Series**: Adjust historical prices to reflect the reinvestment of dividends, creating a "total return index."

Most financial data providers offer adjusted price series that account for dividends, stock splits, and other corporate actions.

#### Example: NVIDIA with Dividends

Let's calculate returns for NVIDIA (NVDA) including its quarterly dividend:

| Date       | Closing Price ($) | Dividend ($) | Simple Return (%) | Log Return (%) |
|------------|-------------------|--------------|-------------------|----------------|
| 2023-03-07 | 242.28            | -            | -                 | -              |
| 2023-03-08 | 238.90            | 0.04         | -1.38%            | -1.39%         |

**Simple Return Calculation with Dividend:**
```
R = (238.90 + 0.04 - 242.28) / 242.28 = -0.0138 = -1.38%
```

**Log Return Approximation with Dividend:**
```
r = ln((238.90 + 0.04) / 242.28) = ln(0.9862) = -0.0139 = -1.39%
```

## 2.2 Arithmetic and Geometric Average Returns

When analyzing investment performance over multiple periods, we need methods to calculate average returns. The two primary approaches—arithmetic and geometric averages—serve different purposes and can lead to significantly different results, especially for volatile investments or long time horizons.

### Arithmetic Average Return

The arithmetic average return is the simple mean of a series of periodic returns.

#### Formula

$$\bar{R}_A = \frac{1}{T} \sum_{t=1}^T R_t$$

Where:
- $\bar{R}_A$ is the arithmetic average return
- $R_t$ is the simple return for period $t$
- $T$ is the total number of periods

#### Properties of Arithmetic Average Returns

1. **Interpretation**: Represents the expected return in any single period, assuming returns are independent and identically distributed.

2. **Forward-Looking**: Appropriate for forecasting single-period expected returns.

3. **Upward Bias**: Tends to overstate the long-term growth rate of an investment due to the asymmetry of percentage gains and losses.

### Geometric Average Return

The geometric average return (also called the compound annual growth rate or CAGR for annual data) measures the compound growth rate of an investment over multiple periods.

#### Formula

$$\bar{R}_G = \left[ \prod_{t=1}^T (1 + R_t) \right]^{1/T} - 1$$

Or equivalently:

$$\bar{R}_G = \left( \frac{P_T}{P_0} \right)^{1/T} - 1$$

Where:
- $\bar{R}_G$ is the geometric average return
- $R_t$ is the simple return for period $t$
- $T$ is the total number of periods
- $P_0$ is the initial price
- $P_T$ is the final price

For log returns, the geometric average is:

$$\bar{r}_G = \frac{1}{T} \sum_{t=1}^T r_t$$

Which is one of the advantages of working with log returns.

#### Properties of Geometric Average Returns

1. **Interpretation**: Represents the constant rate of return that would yield the same cumulative performance over the entire period.

2. **Backward-Looking**: Measures the actual realized compound growth rate over a multi-period investment horizon.

3. **Always Less Than or Equal to Arithmetic Average**: Due to Jensen's inequality, the geometric average is always less than or equal to the arithmetic average, with equality only when all returns are identical.

4. **Path Dependency**: Accounts for the sequence and compounding effects of returns.

### Comparison of Arithmetic and Geometric Averages

The difference between arithmetic and geometric averages increases with:
1. The volatility of returns
2. The length of the measurement period

#### Mathematical Relationship

Under certain assumptions, the relationship between arithmetic and geometric averages can be approximated as:

$$\bar{R}_G \approx \bar{R}_A - \frac{\sigma^2}{2}$$

Where $\sigma^2$ is the variance of returns.

#### Example: AMD Returns

Let's analyze five years of annual returns for Advanced Micro Devices (AMD):

| Year | Return (%) |
|------|------------|
| 2019 | 148.43     |
| 2020 | 99.98      |
| 2021 | 56.91      |
| 2022 | -55.14     |
| 2023 | 127.64     |

**Arithmetic Average Calculation:**
```
R̄_A = (148.43 + 99.98 + 56.91 + (-55.14) + 127.64) / 5 = 75.56%
```

**Geometric Average Calculation:**
```
R̄_G = [(1 + 1.4843) × (1 + 0.9998) × (1 + 0.5691) × (1 - 0.5514) × (1 + 1.2764)]^(1/5) - 1
     = [1.4843 × 1.9998 × 1.5691 × 0.4486 × 2.2764]^(1/5) - 1
     = [5.8959]^(1/5) - 1
     = 1.4263 - 1
     = 42.63%
```

The substantial difference between the arithmetic average (75.56%) and geometric average (42.63%) reflects the high volatility of AMD's returns.

#### Implementation in Excel

```
# Arithmetic Average
=AVERAGE(C2:C6)

# Geometric Average
=(PRODUCT(1+C2:C6)^(1/COUNT(C2:C6)))-1
```

#### Implementation in Python

```python
import numpy as np

# Assuming returns is a numpy array or pandas Series of simple returns
# Arithmetic average
arithmetic_avg = np.mean(returns)

# Geometric average
geometric_avg = (np.prod(1 + returns))**(1/len(returns)) - 1

# For log returns
log_returns = np.log(1 + returns)
geometric_avg_from_log = np.exp(np.mean(log_returns)) - 1
```

### When to Use Each Type of Average

**Use Arithmetic Average When:**
- Estimating expected return for a single future period
- Analyzing investment alternatives over short horizons
- Working with low-volatility assets
- Calculating inputs for portfolio optimization models

**Use Geometric Average When:**
- Measuring actual historical performance
- Comparing investments over long time horizons
- Working with compounded growth rates
- Reporting annualized returns for multi-year investments
- Analyzing high-volatility assets

### The Bliss Point: Weighted Averages for Forecasting

For forecasting future returns over multiple periods, some researchers suggest using a weighted average of arithmetic and geometric means, with the weight determined by the forecast horizon:

$$\bar{R}_w = w \times \bar{R}_A + (1 - w) \times \bar{R}_G$$

Where $w$ decreases as the forecast horizon increases.

## 2.3 Standard Deviation and Variance

Risk is an essential consideration in investment analysis. While return measures the reward, risk quantifies the uncertainty associated with that reward. The most commonly used measures of risk in finance are variance and standard deviation, which capture the dispersion of returns around their average.

### Variance

Variance measures the average squared deviation of returns from their mean.

#### Formula

For a sample of returns:

$$\sigma^2 = \frac{1}{n-1} \sum_{i=1}^n (R_i - \bar{R})^2$$

Where:
- $\sigma^2$ is the sample variance
- $R_i$ is the return for period $i$
- $\bar{R}$ is the mean return
- $n$ is the number of observations
- We use $n-1$ for the sample variance to obtain an unbiased estimator

For the population variance:

$$\sigma^2 = \frac{1}{N} \sum_{i=1}^N (R_i - \bar{R})^2$$

Where $N$ is the total population size.

#### Properties of Variance

1. **Units**: Variance is expressed in squared units of returns, making it less intuitive to interpret directly.

2. **Non-Negativity**: Variance is always greater than or equal to zero, with zero indicating no variation (constant returns).

3. **Additivity for Independent Random Variables**: The variance of a sum of independent random variables is the sum of their variances.

### Standard Deviation

Standard deviation is the square root of variance and measures the average deviation of returns from their mean.

#### Formula

$$\sigma = \sqrt{\sigma^2} = \sqrt{\frac{1}{n-1} \sum_{i=1}^n (R_i - \bar{R})^2}$$

#### Properties of Standard Deviation

1. **Units**: Standard deviation is expressed in the same units as returns (percentages), making it more intuitive than variance.

2. **Interpretation**: For normally distributed returns, approximately 68% of returns fall within one standard deviation of the mean, and approximately 95% fall within two standard deviations.

3. **Scaling with Time**: Under certain assumptions, standard deviation scales with the square root of time:
   
   $$\sigma_{\text{annual}} \approx \sigma_{\text{daily}} \times \sqrt{252}$$
   
   Where 252 is the typical number of trading days in a year.

### Calculating Risk for Different Return Types

Risk calculations can be performed using either simple or logarithmic returns, but the choice should be consistent with the return calculation method.

#### Risk for Simple Returns

Standard deviation of simple returns captures the dispersion of percentage changes in value.

#### Risk for Logarithmic Returns

Standard deviation of logarithmic returns is often preferred in statistical analyses because:
1. Log returns are more likely to be normally distributed
2. Volatility estimates based on log returns are less affected by extreme values
3. Standard deviation of log returns is directly related to the geometric average return

### Annualizing Risk Measures

To compare investments with different measurement frequencies, risk measures need to be annualized.

#### Formula for Annualization

$$\sigma_{\text{annual}} = \sigma_{\text{period}} \times \sqrt{k}$$

Where:
- $\sigma_{\text{period}}$ is the standard deviation per period
- $k$ is the number of periods per year (e.g., 252 for daily trading days, 52 for weeks, 12 for months)

This formula assumes returns are independent and identically distributed (IID), which is a simplification of reality.

### Example: Risk Measures for Meta Platforms (META)

Let's calculate risk measures for META using monthly returns over the past 24 months:

| Month     | Return (%) |
|-----------|------------|
| Jan 2023  | 23.54      |
| Feb 2023  | -0.25      |
| Mar 2023  | 8.21       |
| ...       | ...        |
| Dec 2024  | 5.43       |

**Mean Return Calculation:**
```
R̄ = (23.54 + (-0.25) + 8.21 + ... + 5.43) / 24 = 2.87%
```

**Variance Calculation:**
```
σ² = [(23.54 - 2.87)² + (-0.25 - 2.87)² + (8.21 - 2.87)² + ... + (5.43 - 2.87)²] / (24 - 1)
   = 103.92
```

**Standard Deviation Calculation:**
```
σ = √103.92 = 10.19%
```

**Annualized Standard Deviation:**
```
σ_annual = 10.19% × √12 = 35.32%
```

#### Implementation in Excel

```
# Sample Variance
=VAR.S(C2:C25)

# Sample Standard Deviation
=STDEV.S(C2:C25)

# Annualized Standard Deviation (for monthly data)
=STDEV.S(C2:C25)*SQRT(12)
```

#### Implementation in Python

```python
import numpy as np

# Assuming returns is a numpy array or pandas Series of monthly returns
# Sample variance
variance = np.var(returns, ddof=1)  # ddof=1 for sample variance

# Sample standard deviation
std_dev = np.std(returns, ddof=1)

# Annualized standard deviation (for monthly data)
annualized_std = std_dev * np.sqrt(12)
```

### Alternative Risk Measures

While standard deviation is the most common risk measure, it has limitations, especially for non-normal return distributions. Alternative risk measures include:

1. **Semi-Variance**: Measures dispersion only of returns below the mean, focusing on downside risk.

2. **Value at Risk (VaR)**: Estimates the maximum loss over a specific time horizon at a given confidence level.

3. **Conditional Value at Risk (CVaR)**: Also called Expected Shortfall, measures the average loss beyond VaR.

4. **Maximum Drawdown**: The largest percentage drop from peak to trough over a specific period.

### Risk for Multi-Asset Portfolios

For portfolios with multiple assets, risk depends not only on the individual asset risks but also on how their returns move together, captured by covariance or correlation.

#### Portfolio Variance Formula

$$\sigma_p^2 = \sum_{i=1}^n \sum_{j=1}^n w_i w_j \sigma_{ij}$$

Where:
- $\sigma_p^2$ is the portfolio variance
- $w_i$ and $w_j$ are the weights of assets $i$ and $j$
- $\sigma_{ij}$ is the covariance between assets $i$ and $j$

For a two-asset portfolio, this simplifies to:

$$\sigma_p^2 = w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2w_1 w_2 \sigma_{12}$$

We'll explore portfolio risk in more detail in Chapter 4.

## 2.4 Risk-Return Relationships and Visualization

The relationship between risk and return is fundamental to finance theory and investment decision-making. Visualizing this relationship helps investors understand the trade-offs involved and make more informed decisions.

### The Risk-Return Tradeoff

Modern portfolio theory suggests that higher expected returns are generally associated with higher levels of risk. This principle, often called the "risk-return tradeoff," implies that investors must accept more risk to pursue higher returns.

#### Historical Evidence

Historical data for major asset classes generally supports the risk-return tradeoff:

| Asset Class              | Annualized Return (%) | Annualized Std. Dev. (%) |
|--------------------------|----------------------|--------------------------|
| U.S. T-Bills (1926-2023) | 3.30                 | 3.10                     |
| U.S. Bonds (1926-2023)   | 5.10                 | 7.80                     |
| U.S. Large Stocks (1926-2023) | 10.40           | 19.80                    |
| U.S. Small Stocks (1926-2023) | 11.90           | 27.50                    |

This data demonstrates that higher-returning asset classes have historically exhibited higher volatility.

### The Sharpe Ratio

The Sharpe ratio is a widely used measure that combines risk and return into a single metric, representing the excess return per unit of risk.

#### Formula

$$\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}$$

Where:
- $R_p$ is the portfolio return
- $R_f$ is the risk-free rate
- $\sigma_p$ is the portfolio standard deviation

#### Interpretation

- A higher Sharpe ratio indicates a more favorable risk-adjusted return.
- The Sharpe ratio allows for comparison between investments with different risk levels.
- A Sharpe ratio above 1.0 is generally considered good, above 2.0 is very good, and above 3.0 is excellent.

#### Example: Sharpe Ratio for Tech Stocks

Let's calculate and compare Sharpe ratios for four tech stocks using annual data, assuming a risk-free rate of 3%:

| Stock | Annual Return (%) | Annual Std. Dev. (%) | Sharpe Ratio |
|-------|-------------------|----------------------|--------------|
| TSLA  | 37.5              | 65.2                 | 0.53         |
| NVDA  | 45.8              | 48.3                 | 0.89         |
| AMD   | 42.6              | 53.7                 | 0.74         |
| META  | 28.3              | 39.6                 | 0.64         |

Based on this analysis, NVDA offers the best risk-adjusted return among these four tech stocks.

### Visualizing the Risk-Return Relationship

Several visualization techniques help investors understand the risk-return characteristics of investments.

#### 1. Risk-Return Scatter Plot

A scatter plot with risk (standard deviation) on the x-axis and return on the y-axis provides a simple visual representation of the risk-return profile of different investments.

#### Implementation in Excel

Create a scatter plot using standard deviation values on the x-axis and returns on the y-axis. Add a trendline to visualize the general risk-return relationship.

#### Implementation in Python

```python
import matplotlib.pyplot as plt
import numpy as np

# Assuming we have lists of returns and risks for different assets
assets = ['TSLA', 'NVDA', 'AMD', 'META', 'ASML', 'INTC', 'QCOM', 'TSM']
returns = [37.5, 45.8, 42.6, 28.3, 32.1, 15.7, 22.4, 27.9]
risks = [65.2, 48.3, 53.7, 39.6, 42.3, 31.8, 36.5, 38.2]

# Create scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(risks, returns)

# Add labels for each point
for i, asset in enumerate(assets):
    plt.annotate(asset, (risks[i], returns[i]), 
                 textcoords="offset points", 
                 xytext=(0,10), 
                 ha='center')

# Add trendline
z = np.polyfit(risks, returns, 1)
p = np.poly1d(z)
plt.plot(risks, p(risks), "r--", alpha=0.8)

# Add labels and title
plt.xlabel('Risk (Annual Standard Deviation, %)')
plt.ylabel('Return (Annual, %)')
plt.title('Risk-Return Profile of Tech Stocks')
plt.grid(True, alpha=0.3)

# Add risk-free rate
plt.axhline(y=3, color='g', linestyle='-', alpha=0.5, label='Risk-Free Rate (3%)')
plt.legend()

plt.tight_layout()
plt.show()
```

#### 2. Return Distribution Histograms

Histograms of returns provide insights into the distribution characteristics, including skewness and kurtosis.

#### Implementation in Python

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

# Download daily returns for Tesla
tsla = yf.download('TSLA', period='2y')
tsla_returns = tsla['Adj Close'].pct_change().dropna()

# Create histogram
plt.figure(figsize=(10, 6))
n, bins, patches = plt.hist(tsla_returns, bins=50, density=True, alpha=0.75)

# Add normal distribution curve for comparison
mu, sigma = tsla_returns.mean(), tsla_returns.std()
x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
plt.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2)

# Add statistics
skewness = stats.skew(tsla_returns)
kurtosis = stats.kurtosis(tsla_returns)
plt.text(0.05, 0.95, f'Mean: {mu:.4f}\nStd Dev: {sigma:.4f}\nSkewness: {skewness:.4f}\nKurtosis: {kurtosis:.4f}',
         transform=plt.gca().transAxes, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.title('Distribution of Daily Returns - Tesla (TSLA)')
plt.xlabel('Daily Return')
plt.ylabel('Frequency (Density)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

#### 3. Time Series Visualization

Time series plots of cumulative returns help visualize the path of investments over time, including periods of significant gains or losses.

#### Implementation in Python

```python
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np

# Download data for tech stocks
tickers = ['TSLA', 'NVDA', 'AMD', 'META']
start_date = '2020-01-01'
end_date = '2023-12-31'

data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

# Calculate cumulative returns
cum_returns = (1 + data.pct_change()).cumprod() - 1

# Plot cumulative returns
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(cum_returns[ticker], label=ticker)

plt.title('Cumulative Returns of Tech Stocks (2020-2023)')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

#### 4. Rolling Volatility Charts

Plotting rolling standard deviation over time shows how risk levels change, helping identify periods of market stress.

#### Implementation in Python

```python
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np

# Download data for NVIDIA
nvda = yf.download('NVDA', period='5y')
nvda_returns = nvda['Adj Close'].pct_change().dropna()

# Calculate 21-day (approximately 1 month) rolling volatility, annualized
window = 21
rolling_vol = nvda_returns.rolling(window=window).std() * np.sqrt(252)

# Plot rolling volatility
plt.figure(figsize=(12, 6))
rolling_vol.plot()

plt.title(f'NVIDIA (NVDA) - {window}-Day Rolling Volatility (Annualized)')
plt.xlabel('Date')
plt.ylabel('Annualized Volatility')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### Efficient Frontier Visualization

The efficient frontier represents the set of optimal portfolios that offer the highest expected return for a given level of risk.

#### Implementation in Python

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

# Download data for tech stocks
tickers = ['TSLA', 'NVDA', 'AMD', 'META', 'ASML', 'INTC']
start_date = '2018-01-01'
end_date = '2023-12-31'

data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
returns = data.pct_change().dropna()

# Calculate mean returns and covariance matrix
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# Function to calculate portfolio performance
def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns * weights)
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return std, returns

# Function to minimize negative Sharpe Ratio
def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate=0.03):
    p_std, p_ret = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(p_ret - risk_free_rate) / p_std

# Function to find minimum volatility portfolio
def min_variance(mean_returns, cov_matrix, constraints):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for asset in range(num_assets))
    result = minimize(lambda weights: portfolio_performance(weights, mean_returns, cov_matrix)[0],
                      np.array(num_assets * [1. / num_assets]), bounds=bounds, constraints=constraints)
    return result

# Function to find portfolio with target return
def efficient_return(mean_returns, cov_matrix, target_return, constraints):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints.append({'type': 'eq', 'fun': lambda x: portfolio_performance(x, mean_returns, cov_matrix)[1] - target_return})
    constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for asset in range(num_assets))
    result = minimize(lambda weights: portfolio_performance(weights, mean_returns, cov_matrix)[0],
                      np.array(num_assets * [1. / num_assets]), method='SLSQP', bounds=bounds, constraints=constraints)
    return result

# Calculate efficient frontier
def efficient_frontier(mean_returns, cov_matrix, returns_range):
    constraints = []
    efficient_portfolios = []
    for ret in returns_range:
        efficient_portfolios.append(efficient_return(mean_returns, cov_matrix, ret, constraints.copy()))
    return efficient_portfolios

# Generate efficient frontier curve
target_returns = np.linspace(0.10, 0.40, 50)
efficient_portfolios = efficient_frontier(mean_returns, cov_matrix, target_returns)
risks = [p['fun'] for p in efficient_portfolios]

# Calculate optimal portfolio (maximum Sharpe ratio)
num_assets = len(tickers)
constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
bounds = tuple((0, 1) for asset in range(num_assets))
optimal_result = minimize(neg_sharpe_ratio, np.array(num_assets * [1. / num_assets]),
                          args=(mean_returns, cov_matrix), method='SLSQP',
                          bounds=bounds, constraints=constraints)
optimal_sharpe = optimal_result['x']
optimal_performance = portfolio_performance(optimal_sharpe, mean_returns, cov_matrix)

# Calculate minimum volatility portfolio
min_vol_result = min_variance(mean_returns, cov_matrix, constraints.copy())
min_vol_weights = min_vol_result['x']
min_vol_performance = portfolio_performance(min_vol_weights, mean_returns, cov_matrix)

# Calculate individual stock risks and returns
individual_risks = np.sqrt(np.diag(cov_matrix))

# Plot efficient frontier
plt.figure(figsize=(12, 8))

# Plot efficient frontier
plt.plot(risks, target_returns, 'b-', linewidth=2, label='Efficient Frontier')

# Plot individual stocks
plt.scatter(individual_risks, mean_returns, s=50, c='red', label='Individual Stocks')
for i, txt in enumerate(tickers):
    plt.annotate(txt, (individual_risks[i], mean_returns[i]), xytext=(5, 5), textcoords='offset points')

# Plot optimal portfolio
plt.scatter(optimal_performance[0], optimal_performance[1], s=100, c='green', marker='*', label='Maximum Sharpe Ratio')

# Plot minimum volatility portfolio
plt.scatter(min_vol_performance[0], min_vol_performance[1], s=100, c='orange', marker='o', label='Minimum Volatility')

# Add capital market line
risk_free_rate = 0.03
max_sharpe = (optimal_performance[1] - risk_free_rate) / optimal_performance[0]
cml_x = np.linspace(0, max(individual_risks) * 1.2, 100)
cml_y = risk_free_rate + max_sharpe * cml_x
plt.plot(cml_x, cml_y, 'g--', label='Capital Market Line')

plt.xlabel('Risk (Annual Standard Deviation)')
plt.ylabel('Expected Annual Return')
plt.title('Efficient Frontier of Tech Stock Portfolios')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print optimal portfolio weights
print("Optimal Portfolio Weights (Maximum Sharpe Ratio):")
for i, ticker in enumerate(tickers):
    print(f"{ticker}: {optimal_sharpe[i]:.4f}")
print(f"Expected Annual Return: {optimal_performance[1]:.4f}")
print(f"Expected Annual Volatility: {optimal_performance[0]:.4f}")
print(f"Sharpe Ratio: {(optimal_performance[1] - risk_free_rate) / optimal_performance[0]:.4f}")
```

### LLM Implementation

LLMs can be particularly useful for generating explanations of risk-return visualizations and providing context for investment decisions. Here's an example of using an LLM to interpret risk-return data:

**Prompt to LLM:**

```
I've calculated the following risk-return metrics for four tech stocks:

| Stock | Annual Return (%) | Annual Std. Dev. (%) | Sharpe Ratio |
|-------|-------------------|----------------------|--------------|
| TSLA  | 37.5              | 65.2                 | 0.53         |
| NVDA  | 45.8              | 48.3                 | 0.89         |
| AMD   | 42.6              | 53.7                 | 0.74         |
| META  | 28.3              | 39.6                 | 0.64         |

Please interpret these results, explaining the risk-return relationship and which stock offers the best risk-adjusted return. Also, suggest how I might visualize this data effectively.
```

**Expected LLM Response:**

```
Based on the risk-return metrics you've provided for these four tech stocks, I can offer the following interpretation:

Risk-Return Analysis:
1. TSLA (Tesla) shows the highest volatility (65.2% annual standard deviation) with a moderate return (37.5%). This reflects Tesla's position as a disruptive but volatile player in the automotive and energy sectors.

2. NVDA (NVIDIA) demonstrates an impressive return (45.8%) with moderate risk (48.3% standard deviation), resulting in the highest Sharpe ratio (0.89). This suggests NVIDIA is delivering strong performance relative to the risk taken.

3. AMD shows high returns (42.6%) but also high volatility (53.7%), placing it second in terms of risk-adjusted returns with a Sharpe ratio of 0.74.

4. META has the lowest return (28.3%) but also the lowest risk (39.6%), resulting in a moderate Sharpe ratio (0.64).

Best Risk-Adjusted Return:
NVIDIA (NVDA) offers the best risk-adjusted return with the highest Sharpe ratio of 0.89. This means investors are being better compensated for each unit of risk they take compared to the other stocks.

Visualization Suggestions:
1. Risk-Return Scatter Plot: Plot standard deviation on the x-axis and returns on the y-axis. This would create a visual representation of the risk-return trade-off, where NVIDIA would appear in the most favorable position (upper-left relative to the other stocks).

2. Sharpe Ratio Bar Chart: Create a bar chart of Sharpe ratios to clearly show which stock offers the best risk-adjusted return.

3. Efficient Frontier: If you're considering portfolios of these stocks, plot an efficient frontier to show optimal combinations.

4. Risk Contribution Chart: Show how much each stock contributes to the overall risk of a portfolio containing all four stocks.

For your investment decision-making, these visualizations would help demonstrate that while TSLA might appeal to investors with higher risk tolerance seeking growth, NVDA currently offers a more balanced profile with strong returns for the risk taken.
```

This approach combines quantitative analysis with qualitative interpretation, helping investors understand the implications of the risk-return metrics.

### Incorporating Machine Learning for Risk-Return Analysis

Advanced techniques from machine learning can enhance risk-return analysis. Here's a brief example using clustering to identify stocks with similar risk-return profiles:

```python
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

# Download data for tech stocks
tickers = ['TSLA', 'NVDA', 'AMD', 'META', 'ASML', 'INTC', 'QCOM', 'TSM', 
           'ORCL', 'CSCO', 'NOW', 'V', 'MRNA', 'TLRY']
start_date = '2020-01-01'
end_date = '2023-12-31'

data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
returns = data.pct_change().dropna()

# Calculate mean returns and standard deviations
mean_returns = returns.mean() * 252
std_returns = returns.std() * np.sqrt(252)

# Combine into DataFrame for clustering
risk_return_df = pd.DataFrame({
    'Return': mean_returns,
    'Risk': std_returns
})

# Apply K-means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
risk_return_df['Cluster'] = kmeans.fit_predict(risk_return_df)

# Create scatter plot with clusters
plt.figure(figsize=(12, 8))
colors = ['blue', 'green', 'red']
for cluster in range(3):
    cluster_data = risk_return_df[risk_return_df['Cluster'] == cluster]
    plt.scatter(cluster_data['Risk'], cluster_data['Return'], 
                s=50, c=colors[cluster], label=f'Cluster {cluster+1}')
    for idx in cluster_data.index:
        plt.annotate(idx, (cluster_data.loc[idx, 'Risk'], cluster_data.loc[idx, 'Return']),
                     xytext=(5, 5), textcoords='offset points')

plt.title('Clustering of Tech Stocks Based on Risk-Return Profile')
plt.xlabel('Risk (Annual Standard Deviation)')
plt.ylabel('Expected Annual Return')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print cluster information
for cluster in range(3):
    print(f"Cluster {cluster+1} stocks:")
    print(risk_return_df[risk_return_df['Cluster'] == cluster].index.tolist())
    print(f"Average Return: {risk_return_df[risk_return_df['Cluster'] == cluster]['Return'].mean():.4f}")
    print(f"Average Risk: {risk_return_df[risk_return_df['Cluster'] == cluster]['Risk'].mean():.4f}")
    print()
```

This clustering approach helps identify groups of stocks with similar risk-return characteristics, which can be useful for portfolio diversification and investment strategy development.

---

## Exercises

### Computing Returns for TSLA, NVDA, AMD, and META

1. **Simple and Logarithmic Returns Calculation**
   
   Obtain daily price data for Tesla (TSLA), NVIDIA (NVDA), AMD, and Meta Platforms (META) for the past two years.
   
   a) Calculate daily simple returns and logarithmic returns for each stock using Excel.
   b) Implement the same calculations using Python.
   c) Generate a prompt for an LLM to explain the differences between simple and logarithmic returns, and evaluate its response.
   d) Compare the return series and identify any significant differences between the simple and logarithmic return calculations.

2. **Total Return Analysis with Dividends**
   
   For each of the four tech stocks (TSLA, NVDA, AMD, META):
   
   a) Calculate the total return (including dividends) for the past year using Excel.
   b) Implement the same calculation in Python, accounting for dividend reinvestment.
   c) Ask an LLM to explain how dividends impact total return calculations and verify its explanation.
   d) Compare the total returns with and without dividends for each stock.

3. **Return Aggregation Across Time Periods**
   
   Using monthly data for the past five years:
   
   a) Calculate monthly returns for each stock in Excel.
   b) Aggregate the monthly returns to quarterly and annual returns using both simple and logarithmic approaches.
   c) Implement the same aggregation in Python.
   d) Ask an LLM to explain the appropriate method for aggregating returns across time periods.
   e) Compare the results of different aggregation methods and discuss the implications.

### Calculating Risk Measures for Tech Stocks

1. **Volatility Calculation and Comparison**
   
   Using daily return data for the past three years:
   
   a) Calculate the annual volatility (standard deviation) for each stock using Excel.
   b) Implement the same calculation in Python.
   c) Use an LLM to explain what the volatility values indicate about each stock's risk profile.
   d) Compare the volatility of these tech stocks with the S&P 500 index.

2. **Downside Risk Measures**
   
   For each of the four tech stocks:
   
   a) Calculate the downside deviation (considering only negative returns) using Excel.
   b) Calculate the Value at Risk (VaR) at 95% and 99% confidence levels in Python.
   c) Use an LLM to explain the concept of downside risk and how it differs from standard deviation.
   d) Compare the rankings of stocks based on standard deviation versus downside risk measures.

3. **Rolling Volatility Analysis**
   
   For each stock:
   
   a) Calculate 30-day rolling volatility (annualized) for the past two years in Excel.
   b) Implement the same calculation in Python and create visualizations of the rolling volatility.
   c) Use an LLM to identify periods of high volatility and potential market events that might have caused them.
   d) Compare volatility clustering patterns across the four stocks.

### Visualizing Risk-Return Tradeoffs

1. **Risk-Return Scatter Plot**
   
   Using annual data for the past five years for all stocks in our focus list (TSLA, NVDA, AMD, META, INTC, QCOM, ASML, TSM, TLRY, MRNA, ORCL, CSCO, NOW, V):
   
   a) Create a risk-return scatter plot in Excel with risk on the x-axis and return on the y-axis.
   b) Implement the same visualization in Python, adding labels for each stock.
   c) Ask an LLM to interpret the visualization and identify which stocks offer the best risk-return tradeoff.
   d) Add a trend line to visualize the general risk-return relationship across these stocks.

2. **Efficient Frontier Construction**
   
   Using the same set of stocks:
   
   a) Calculate the correlation matrix of returns in Excel.
   b) Implement a Python solution to generate the efficient frontier for portfolios of these stocks.
   c) Identify the minimum variance portfolio and the optimal portfolio based on the Sharpe ratio.
   d) Use an LLM to explain the concept of the efficient frontier and interpret the results.

3. **Return Distribution Visualization**
   
   For each of the four focus stocks:
   
   a) Create histograms of daily returns in Excel.
   b) Implement more sophisticated distribution plots in Python, including normal probability plots.
   c) Calculate skewness and kurtosis for each return series.
   d) Ask an LLM to interpret the distribution characteristics and explain their implications for risk assessment.

### Comparing Risk Metrics Across Implementation Methods

1. **Arithmetic vs. Geometric Average Returns**
   
   For each of the four focus stocks:
   
   a) Calculate both arithmetic and geometric average annual returns over 1-year, 3-year, and 5-year periods using Excel.
   b) Implement the same calculations in Python.
   c) Use an LLM to explain when each average is more appropriate and why they differ.
   d) Compare the differences between arithmetic and geometric averages for high-volatility stocks (e.g., TSLA) versus lower-volatility stocks (e.g., META).

2. **Sharpe Ratio and Risk-Adjusted Return Metrics**
   
   For each stock and a portfolio of all four stocks with equal weights:
   
   a) Calculate the Sharpe ratio, Treynor ratio, and information ratio in Excel.
   b) Implement the same calculations in Python.
   c) Use an LLM to compare these risk-adjusted return metrics and explain their interpretations.
   d) Rank the stocks based on different risk-adjusted performance metrics and analyze the consistency of rankings.

3. **Implementation Comparison and Triangulation**
   
   For all metrics calculated in the previous exercises:
   
   a) Compare the results obtained from Excel, Python, and LLM explanations.
   b) Identify any discrepancies and investigate their sources.
   c) Use the triangulation methodology to determine the most accurate values and interpretations.
   d) Create a summary table or dashboard that presents the key risk-return metrics for each stock, highlighting the best-performing stock according to different criteria.

By completing these exercises, you will gain practical experience in calculating, visualizing, and interpreting risk and return measures using all three computational approaches: Excel, Python, and LLMs. The exercises progress from basic calculations to more sophisticated analyses, providing a comprehensive understanding of risk-return relationships in the context of tech stocks.
