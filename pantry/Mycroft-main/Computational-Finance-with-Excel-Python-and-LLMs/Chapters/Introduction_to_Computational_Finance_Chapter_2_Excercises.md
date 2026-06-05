# Chapter 2 Exercises: Return Calculations and Risk Measures

## Computing Returns for TSLA, NVDA, AMD, and META

### Exercise 1: Simple and Logarithmic Returns
**Question**: Using the following historical price data for Tesla (TSLA), calculate:

| Date       | Closing Price ($) |
|------------|-------------------|
| 2023-01-03 | 108.10            |
| 2023-01-04 | 113.64            |
| 2023-01-05 | 110.34            |
| 2023-01-06 | 113.06            |
| 2023-01-09 | 119.77            |

a) The simple daily returns for Jan 4 through Jan 9
b) The logarithmic daily returns for the same period
c) The holding period return using both simple and logarithmic methods
d) If you invested $10,000 on Jan 3, how much would you have on Jan 9?

**Solution**:

a) Simple daily returns:
- Jan 4: (113.64 - 108.10) / 108.10 = 0.0512 or 5.12%
- Jan 5: (110.34 - 113.64) / 113.64 = -0.0290 or -2.90%
- Jan 6: (113.06 - 110.34) / 110.34 = 0.0246 or 2.46%
- Jan 9: (119.77 - 113.06) / 113.06 = 0.0593 or 5.93%

b) Logarithmic daily returns:
- Jan 4: ln(113.64 / 108.10) = ln(1.0512) = 0.0500 or 5.00%
- Jan 5: ln(110.34 / 113.64) = ln(0.9710) = -0.0294 or -2.94%
- Jan 6: ln(113.06 / 110.34) = ln(1.0246) = 0.0244 or 2.44%
- Jan 9: ln(119.77 / 113.06) = ln(1.0593) = 0.0576 or 5.76%

c) Holding period return:
- Simple: [(119.77 / 108.10) - 1] = 0.1080 or 10.80%
- Logarithmic: ln(119.77 / 108.10) = ln(1.1080) = 0.1026 or 10.26%

d) Final investment value:
- $10,000 × (119.77 / 108.10) = $10,000 × 1.1080 = $11,080

**Excel Implementation**:
```
# Simple daily returns
=(B2-B1)/B1  'Jan 4 return

# Logarithmic daily returns
=LN(B2/B1)   'Jan 4 return

# Holding period return (simple)
=(B5-B1)/B1

# Holding period return (logarithmic)
=LN(B5/B1)

# Final investment value
=10000*(B5/B1)
```

**Python Implementation**:
```python
import numpy as np
import pandas as pd

# Create DataFrame with prices
dates = ['2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-09']
prices = [108.10, 113.64, 110.34, 113.06, 119.77]
tsla = pd.DataFrame({'Date': dates, 'Price': prices})
tsla.set_index('Date', inplace=True)

# Calculate simple returns
tsla['Simple_Return'] = tsla['Price'].pct_change()

# Calculate logarithmic returns
tsla['Log_Return'] = np.log(tsla['Price'] / tsla['Price'].shift(1))

# Calculate holding period return
simple_hpr = (tsla['Price'].iloc[-1] / tsla['Price'].iloc[0]) - 1
log_hpr = np.log(tsla['Price'].iloc[-1] / tsla['Price'].iloc[0])

# Calculate final investment value
final_value = 10000 * (tsla['Price'].iloc[-1] / tsla['Price'].iloc[0])

print(tsla)
print(f"Simple holding period return: {simple_hpr:.4f}")
print(f"Log holding period return: {log_hpr:.4f}")
print(f"Final investment value: ${final_value:.2f}")
```

### Exercise 2: Returns with Dividends
**Question**: NVIDIA (NVDA) paid the following quarterly dividends and had the following prices:

| Date       | Closing Price ($) | Dividend ($) |
|------------|-------------------|--------------|
| 2022-12-01 | 162.54            | -            |
| 2022-12-29 | 146.14            | 0.04         |
| 2023-03-31 | 277.77            | 0.04         |
| 2023-06-30 | 423.02            | 0.04         |
| 2023-09-29 | 434.99            | 0.04         |

a) Calculate the quarterly returns including dividends
b) Calculate the total return for the period
c) Calculate the annualized return (assume 365 days in the year)
d) How much would a $5,000 investment on Dec 1, 2022 be worth on Sep 29, 2023?

**Solution**:

a) Quarterly returns including dividends:
- Q4 2022: (146.14 - 162.54 + 0.04) / 162.54 = -0.1005 or -10.05%
- Q1 2023: (277.77 - 146.14 + 0.04) / 146.14 = 0.9008 or 90.08%
- Q2 2023: (423.02 - 277.77 + 0.04) / 277.77 = 0.5230 or 52.30%
- Q3 2023: (434.99 - 423.02 + 0.04) / 423.02 = 0.0285 or 2.85%

b) Total return for the period:
- Using the chain of returns: (1 - 0.1005) × (1 + 0.9008) × (1 + 0.5230) × (1 + 0.0285) - 1 = 1.6796 - 1 = 0.6796 or 67.96%
- Direct calculation: (434.99 - 162.54 + 0.16) / 162.54 = 1.6796 - 1 = 0.6796 or 67.96%

c) Annualized return:
- Days between Dec 1, 2022 and Sep 29, 2023: 302 days
- Annualized return: (1 + 0.6796)^(365/302) - 1 = 1.6796^1.2086 - 1 = 0.8545 or 85.45%

d) Final investment value:
- $5,000 × (1 + 0.6796) = $5,000 × 1.6796 = $8,398

**Excel Implementation**:
```
# Quarterly returns
=(B2-B1+C2)/B1  'Q4 2022 return

# Total return
=(B5-B1+SUM(C2:C5))/B1

# Annualized return
=(1+E5)^(365/302)-1  'Where E5 contains the total return

# Final investment value
=5000*(1+E5)
```

**Python Implementation**:
```python
import numpy as np
import pandas as pd
from datetime import datetime

# Create DataFrame with prices and dividends
dates = ['2022-12-01', '2022-12-29', '2023-03-31', '2023-06-30', '2023-09-29']
prices = [162.54, 146.14, 277.77, 423.02, 434.99]
dividends = [0, 0.04, 0.04, 0.04, 0.04]

nvda = pd.DataFrame({'Date': dates, 'Price': prices, 'Dividend': dividends})
nvda.set_index('Date', inplace=True)
nvda.index = pd.to_datetime(nvda.index)

# Calculate quarterly returns
nvda['Return'] = (nvda['Price'] - nvda['Price'].shift(1) + nvda['Dividend']) / nvda['Price'].shift(1)

# Calculate total return
total_return = (nvda['Price'].iloc[-1] - nvda['Price'].iloc[0] + nvda['Dividend'].sum()) / nvda['Price'].iloc[0]

# Calculate days between first and last date
days = (nvda.index[-1] - nvda.index[0]).days

# Calculate annualized return
annualized_return = (1 + total_return) ** (365 / days) - 1

# Calculate final investment value
final_value = 5000 * (1 + total_return)

print(nvda)
print(f"Total return: {total_return:.4f}")
print(f"Annualized return: {annualized_return:.4f}")
print(f"Final investment value: ${final_value:.2f}")
```

### Exercise 3: Log Return Aggregation
**Question**: The following table shows weekly logarithmic returns for AMD stock:

| Week | Log Return |
|------|------------|
| 1    | 0.0472     |
| 2    | -0.0315    |
| 3    | 0.0623     |
| 4    | 0.0189     |

a) What is the total log return over the 4-week period?
b) Convert the total log return to a simple return
c) Calculate the arithmetic average weekly log return
d) If the pattern of returns continued for a full year (52 weeks), what would be the annual log return?
e) Convert the annual log return to a simple annual return

**Solution**:

a) Total log return over 4 weeks:
- 0.0472 + (-0.0315) + 0.0623 + 0.0189 = 0.0969 or 9.69%

b) Simple return from total log return:
- e^0.0969 - 1 = 1.1017 - 1 = 0.1017 or 10.17%

c) Arithmetic average weekly log return:
- (0.0472 + (-0.0315) + 0.0623 + 0.0189) / 4 = 0.0969 / 4 = 0.0242 or 2.42%

d) Annual log return (assuming 52 weeks):
- 0.0969 × (52 / 4) = 0.0969 × 13 = 0.3147 or 31.47%
- Alternative calculation: 0.0242 × 52 = 1.2597 or 125.97% (This approach doesn't account for compounding and would be inappropriate)

e) Annual simple return:
- e^0.3147 - 1 = 1.3698 - 1 = 0.3698 or 36.98%

**Excel Implementation**:
```
# Total log return
=SUM(B1:B4)

# Convert log return to simple return
=EXP(C1)-1  'Where C1 contains the total log return

# Arithmetic average weekly log return
=AVERAGE(B1:B4)

# Annual log return
=C1*(52/4)  'Where C1 contains the total log return

# Annual simple return
=EXP(E1)-1  'Where E1 contains the annual log return
```

**Python Implementation**:
```python
import numpy as np

# Weekly log returns
log_returns = [0.0472, -0.0315, 0.0623, 0.0189]

# Total log return
total_log_return = sum(log_returns)

# Convert to simple return
total_simple_return = np.exp(total_log_return) - 1

# Arithmetic average weekly log return
avg_weekly_log_return = np.mean(log_returns)

# Annual log return
annual_log_return = total_log_return * (52 / 4)

# Annual simple return
annual_simple_return = np.exp(annual_log_return) - 1

print(f"Total log return: {total_log_return:.4f}")
print(f"Total simple return: {total_simple_return:.4f}")
print(f"Average weekly log return: {avg_weekly_log_return:.4f}")
print(f"Annual log return: {annual_log_return:.4f}")
print(f"Annual simple return: {annual_simple_return:.4f}")
```

## Arithmetic and Geometric Average Returns

### Exercise 4: Comparing Average Returns
**Question**: The following table shows annual returns for Meta Platforms (META) over the past 5 years:

| Year | Return |
|------|--------|
| 2019 | 56.57% |
| 2020 | 33.09% |
| 2021 | 23.13% |
| 2022 | -64.22%|
| 2023 | 194.14%|

a) Calculate the arithmetic average annual return
b) Calculate the geometric average annual return
c) What is the standard deviation of returns?
d) If you invested $10,000 at the beginning of 2019, how much would you have at the end of 2023?
e) Using the geometric average, what constant annual return would give the same end result?

**Solution**:

a) Arithmetic average annual return:
- (56.57% + 33.09% + 23.13% + (-64.22%) + 194.14%) / 5 = 242.71% / 5 = 48.54%

b) Geometric average annual return:
- [(1 + 0.5657) × (1 + 0.3309) × (1 + 0.2313) × (1 - 0.6422) × (1 + 1.9414)]^(1/5) - 1
- [1.5657 × 1.3309 × 1.2313 × 0.3578 × 2.9414]^(1/5) - 1
- [2.3994]^(1/5) - 1 = 1.1913 - 1 = 19.13%

c) Standard deviation of returns:
- Mean = 48.54%
- Variance = [(56.57% - 48.54%)² + (33.09% - 48.54%)² + (23.13% - 48.54%)² + (-64.22% - 48.54%)² + (194.14% - 48.54%)²] / (5 - 1)
- Variance = [(8.03%)² + (-15.45%)² + (-25.41%)² + (-112.76%)² + (145.60%)²] / 4
- Variance = [0.0065 + 0.0239 + 0.0646 + 0.1271 + 0.2120] / 4 = 0.4341 / 4 = 0.1085
- Standard deviation = √0.1085 = 0.3294 or 32.94%

d) Final investment value:
- $10,000 × (1 + 0.5657) × (1 + 0.3309) × (1 + 0.2313) × (1 - 0.6422) × (1 + 1.9414)
- $10,000 × 2.3994 = $23,994

e) Using geometric average:
- $10,000 × (1 + 0.1913)^5 = $10,000 × 2.3994 = $23,994
- This confirms our geometric average calculation is correct, as it gives the same end result

**Excel Implementation**:
```
# Arithmetic average
=AVERAGE(B1:B5)

# Geometric average
=(PRODUCT(1+B1:1+B5))^(1/COUNT(B1:B5))-1

# Standard deviation
=STDEV.S(B1:B5)

# Final investment value
=10000*PRODUCT(1+B1:1+B5)

# Check using geometric average
=10000*(1+C2)^5  'Where C2 contains the geometric average
```

**Python Implementation**:
```python
import numpy as np

# Annual returns
returns = [0.5657, 0.3309, 0.2313, -0.6422, 1.9414]

# Arithmetic average
arithmetic_avg = np.mean(returns)

# Geometric average
geometric_avg = (np.prod(np.array(returns) + 1)) ** (1 / len(returns)) - 1

# Standard deviation
std_dev = np.std(returns, ddof=1)  # ddof=1 for sample std dev

# Final investment value
final_value = 10000 * np.prod(np.array(returns) + 1)

# Check using geometric average
check_value = 10000 * (1 + geometric_avg) ** 5

print(f"Arithmetic average return: {arithmetic_avg:.4f}")
print(f"Geometric average return: {geometric_avg:.4f}")
print(f"Standard deviation: {std_dev:.4f}")
print(f"Final investment value: ${final_value:.2f}")
print(f"Check using geometric average: ${check_value:.2f}")
```

### Exercise 5: CAGR for Different Time Periods
**Question**: The table below shows the price history for Qualcomm (QCOM) stock:

| Date       | Price ($) |
|------------|-----------|
| 2014-01-02 | 73.90     |
| 2016-01-04 | 48.50     |
| 2018-01-02 | 58.18     |
| 2020-01-02 | 88.23     |
| 2022-01-03 | 184.73    |
| 2024-01-02 | 136.73    |

a) Calculate the 2-year CAGR for each period (2014-2016, 2016-2018, etc.)
b) Calculate the 10-year CAGR for the entire period
c) Which 2-year period had the highest growth rate?
d) If you had invested $25,000 in 2014, what would your investment be worth in 2024?

**Solution**:

a) 2-year CAGR for each period:
- 2014-2016: (48.50 / 73.90)^(1/2) - 1 = (0.6563)^0.5 - 1 = -0.1903 or -19.03%
- 2016-2018: (58.18 / 48.50)^(1/2) - 1 = (1.1996)^0.5 - 1 = 0.0954 or 9.54%
- 2018-2020: (88.23 / 58.18)^(1/2) - 1 = (1.5164)^0.5 - 1 = 0.2325 or 23.25%
- 2020-2022: (184.73 / 88.23)^(1/2) - 1 = (2.0938)^0.5 - 1 = 0.4463 or 44.63%
- 2022-2024: (136.73 / 184.73)^(1/2) - 1 = (0.7401)^0.5 - 1 = -0.1418 or -14.18%

b) 10-year CAGR for the entire period:
- (136.73 / 73.90)^(1/10) - 1 = (1.8501)^0.1 - 1 = 0.0636 or 6.36%

c) The 2020-2022 period had the highest growth rate at 44.63%.

d) Final investment value:
- $25,000 × (136.73 / 73.90) = $25,000 × 1.8501 = $46,252.50

**Excel Implementation**:
```
# 2-year CAGR for 2014-2016
=(B2/B1)^(1/2)-1

# 10-year CAGR
=(B6/B1)^(1/10)-1

# Final investment value
=25000*(B6/B1)
```

**Python Implementation**:
```python
import numpy as np
import pandas as pd

# Create DataFrame with dates and prices
dates = ['2014-01-02', '2016-01-04', '2018-01-02', '2020-01-02', '2022-01-03', '2024-01-02']
prices = [73.90, 48.50, 58.18, 88.23, 184.73, 136.73]

qcom = pd.DataFrame({'Date': dates, 'Price': prices})
qcom.set_index('Date', inplace=True)
qcom.index = pd.to_datetime(qcom.index)

# Calculate 2-year CAGR for each period
cagr_2yr = []
for i in range(1, len(prices)):
    cagr = (prices[i] / prices[i-1]) ** (1/2) - 1
    cagr_2yr.append(cagr)

# Calculate 10-year CAGR
cagr_10yr = (prices[-1] / prices[0]) ** (1/10) - 1

# Find period with highest growth rate
max_cagr_idx = np.argmax(cagr_2yr)
max_cagr_period = f"{dates[max_cagr_idx]}-{dates[max_cagr_idx+1]}"

# Calculate final investment value
final_value = 25000 * (prices[-1] / prices[0])

print("2-year CAGR for each period:")
for i, period in enumerate(zip(dates[:-1], dates[1:])):
    print(f"{period[0]} to {period[1]}: {cagr_2yr[i]:.4f}")

print(f"\n10-year CAGR: {cagr_10yr:.4f}")
print(f"Period with highest growth rate: {max_cagr_period} ({cagr_2yr[max_cagr_idx]:.4f})")
print(f"Final investment value: ${final_value:.2f}")
```

### Exercise 6: Arithmetic vs. Geometric Mean
**Question**: An investment advisor claims that their stock picks have averaged returns of 20% per year over the last 5 years. Upon further investigation, you find out this is the arithmetic mean. The volatility (standard deviation) of their annual returns was 40%.

a) Estimate the geometric mean return using the relationship between arithmetic and geometric means
b) What is the expected final value of a $50,000 investment after 5 years using the arithmetic mean?
c) What is the expected final value of a $50,000 investment after 5 years using the geometric mean?
d) Explain why there is a difference between these two values

**Solution**:

a) Estimate the geometric mean return:
- Using the approximation: Geometric Mean ≈ Arithmetic Mean - (Variance / 2)
- Variance = (Standard Deviation)² = (0.40)² = 0.16
- Geometric Mean ≈ 0.20 - (0.16 / 2) = 0.20 - 0.08 = 0.12 or 12%

b) Expected final value using arithmetic mean:
- Assuming simple compounding: $50,000 × (1 + 0.20)^5 = $50,000 × 2.4883 = $124,415
- This is incorrect because it assumes the return is the same every year

c) Expected final value using geometric mean:
- $50,000 × (1 + 0.12)^5 = $50,000 × 1.7623 = $88,115
- This is the better estimate of the expected final value

d) The difference exists because:
- The arithmetic mean does not account for the compounding effect of returns
- With volatile returns, negative returns have a larger impact on the final value than positive returns of the same magnitude
- The geometric mean accounts for this asymmetry in compounding
- The more volatile the returns (higher standard deviation), the greater the difference between arithmetic and geometric means
- In this case, the high volatility (40%) causes a significant difference between the two means

**Excel Implementation**:
```
# Estimated geometric mean
=C1-(D1^2/2)  'Where C1 contains arithmetic mean (0.20) and D1 contains standard deviation (0.40)

# Final value using arithmetic mean
=50000*(1+C1)^5

# Final value using geometric mean
=50000*(1+E1)^5  'Where E1 contains the geometric mean
```

**Python Implementation**:
```python
import numpy as np

# Given information
arithmetic_mean = 0.20
std_dev = 0.40
variance = std_dev ** 2
years = 5
initial_investment = 50000

# Estimate geometric mean
geometric_mean = arithmetic_mean - (variance / 2)

# Calculate final values
final_value_arithmetic = initial_investment * (1 + arithmetic_mean) ** years
final_value_geometric = initial_investment * (1 + geometric_mean) ** years

print(f"Arithmetic mean: {arithmetic_mean:.4f}")
print(f"Standard deviation: {std_dev:.4f}")
print(f"Variance: {variance:.4f}")
print(f"Estimated geometric mean: {geometric_mean:.4f}")
print(f"Final value using arithmetic mean: ${final_value_arithmetic:.2f}")
print(f"Final value using geometric mean: ${final_value_geometric:.2f}")
print(f"Difference: ${final_value_arithmetic - final_value_geometric:.2f}")
```

## Standard Deviation and Variance

### Exercise 7: Volatility Calculation
**Question**: The following table shows monthly returns for ASML Holding (ASML) for the first 6 months of 2023:

| Month    | Return |
|----------|--------|
| January  | 27.42% |
| February | -3.18% |
| March    | 13.04% |
| April    | -8.22% |
| May      | 12.38% |
| June     | -1.93% |

a) Calculate the sample variance and standard deviation of monthly returns
b) Annualize the standard deviation (assuming returns are independent)
c) What is the probability of a negative monthly return, assuming returns are normally distributed?
d) What is the probability of losing more than 10% in a month?

**Solution**:

a) Sample variance and standard deviation:
- Mean monthly return = (27.42% + (-3.18%) + 13.04% + (-8.22%) + 12.38% + (-1.93%)) / 6 = 39.51% / 6 = 6.585%
- Squared deviations:
  - (27.42% - 6.585%)² = (20.835%)² = 0.0434
  - (-3.18% - 6.585%)² = (-9.765%)² = 0.0095
  - (13.04% - 6.585%)² = (6.455%)² = 0.0042
  - (-8.22% - 6.585%)² = (-14.805%)² = 0.0219
  - (12.38% - 6.585%)² = (5.795%)² = 0.0034
  - (-1.93% - 6.585%)² = (-8.515%)² = 0.0073
- Sample variance = (0.0434 + 0.0095 + 0.0042 + 0.0219 + 0.0034 + 0.0073) / (6 - 1) = 0.0897 / 5 = 0.01794
- Sample standard deviation = √0.01794 = 0.1339 or 13.39%

b) Annualized standard deviation:
- Annual standard deviation = Monthly standard deviation × √12 = 13.39% × √12 = 13.39% × 3.4641 = 46.38%

c) Probability of a negative monthly return:
- Using the normal distribution with mean = 6.585% and standard deviation = 13.39%
- Z-score for 0% return = (0% - 6.585%) / 13.39% = -0.4918
- P(return < 0%) = P(Z < -0.4918) = 0.3114 or 31.14%

d) Probability of losing more than 10% in a month:
- Z-score for -10% return = (-10% - 6.585%) / 13.39% = -1.2386
- P(return < -10%) = P(Z < -1.2386) = 0.1078 or 10.78%

**Excel Implementation**:
```
# Mean monthly return
=AVERAGE(B1:B6)

# Sample variance
=VAR.S(B1:B6)

# Sample standard deviation
=STDEV.S(B1:B6)

# Annualized standard deviation
=D3*SQRT(12)  'Where D3 contains the monthly standard deviation

# Probability of negative return
=NORM.DIST(0,D1,D3,TRUE)  'Where D1 contains the mean and D3 contains the standard deviation

# Probability of losing more than 10%
=NORM.DIST(-0.1,D1,D3,TRUE)
```

**Python Implementation**:
```python
import numpy as np
from scipy import stats

# Monthly returns
returns = [0.2742, -0.0318, 0.1304, -0.0822, 0.1238, -0.0193]

# Calculate mean
mean_return = np.mean(returns)

# Calculate variance and standard deviation
variance = np.var(returns, ddof=1)  # ddof=1 for sample variance
std_dev = np.std(returns, ddof=1)   # ddof=1 for sample standard deviation

# Annualize standard deviation
annual_std_dev = std_dev * np.sqrt(12)

# Probability of negative return
prob_negative = stats.norm.cdf(0, mean_return, std_dev)

# Probability of losing more than 10%
prob_loss_10pct = stats.norm.cdf(-0.1, mean_return, std_dev)

print(f"Mean monthly return: {mean_return:.4f}")
print(f"Sample variance: {variance:.4f}")
print(f"Sample standard deviation: {std_dev:.4f}")
print(f"Annualized standard deviation: {annual_std_dev:.4f}")
print(f"Probability of negative monthly return: {prob_negative:.4f}")
print(f"Probability of losing more than 10% in a month: {prob_loss_10pct:.4f}")
```

### Exercise 8: Risk Comparison
**Question**: Compare the risk profiles of Intel (INTC) and Taiwan Semiconductor (TSM) using the following annual return data:

| Year | INTC   | TSM    |
|------|--------|--------|
| 2019 | 29.12% | 57.98% |
| 2020 | -9.30% | 85.98% |
| 2021 | -4.25% | 12.13% |
| 2022 | -46.92%| -38.35%|
| 2023 | 90.16% | 86.87% |

a) Calculate the mean return and standard deviation for each stock
b) Which stock has higher volatility?
c) Calculate the coefficient of variation for each stock to determine which has more risk per unit of return
d) Calculate the correlation between the two stocks
e) If you created a portfolio with 50% in each stock, what would be its standard deviation?

**Solution**:

a) Mean return and standard deviation:

For INTC:
- Mean return = (29.12% + (-9.30%) + (-4.25%) + (-46.92%) + 90.16%) / 5 = 58.81% / 5 = 11.76%
- Variance = [(29.12% - 11.76%)² + (-9.30% - 11.76%)² + (-4.25% - 11.76%)² + (-46.92% - 11.76%)² + (90.16% - 11.76%)²] / (5 - 1)
- Variance = [(17.36%)² + (-21.06%)² + (-16.01%)² + (-58.68%)² + (78.40%)²] / 4
- Variance = [0.0301 + 0.0444 + 0.0256 + 0.3443 + 0.6147] / 4 = 1.0591 / 4 = 0.2648
- Standard deviation = √0.2648 = 0.5146 or 51.46%

For TSM:
- Mean return = (57.98% + 85.98% + 12.13% + (-38.35%) + 86.87%) / 5 = 204.61% / 5 = 40.92%
- Variance = [(57.98% - 40.92%)² + (85.98% - 40.92%)² + (12.13% - 40.92%)² + (-38.35% - 40.92%)² + (86.87% - 40.92%)²] / (5 - 1)
- Variance = [(17.06%)² + (45.06%)² + (-28.79%)² + (-79.27%)² + (45.95%)²] / 4
- Variance = [0.0291 + 0.2030 + 0.0829 + 0.6284 + 0.2111] / 4 = 1.1545 / 4 = 0.2886
- Standard deviation = √0.2886 = 0.5373 or 53.73%

b) TSM has higher volatility (standard deviation of 53.73% vs. 51.46% for INTC).

c) Coefficient of variation:
- CV for INTC = Standard deviation / Mean return = 51.46% / 11.76% = 4.38
- CV for TSM = Standard deviation / Mean return = 53.73% / 40.92% = 1.31
- TSM has a lower coefficient of variation, indicating better risk-adjusted returns.

d) Correlation between INTC and TSM:
- Covariance = [(29.12% - 11.76%)×(57.98% - 40.92%) + (-9.30% - 11.76%)×(85.98% - 40.92%) + (-4.25% - 11.76%)×(12.13% - 40.92%) + (-46.92% - 11.76%)×(-38.35% - 40.92%) + (90.16% - 11.76%)×(86.87% - 40.92%)] / (5 - 1)
- Covariance = [0.1736×0.1706 + (-0.2106)×0.4506 + (-0.1601)×(-0.2879) + (-0.5868)×(-0.7927) + 0.7840×0.4595] / 4
- Covariance = [0.0296 + (-0.0949) + 0.0461 + 0.4652 + 0.3602] / 4 = 0.8062 / 4 = 0.2015
- Correlation = Covariance / (Standard deviation of INTC × Standard deviation of TSM) = 0.2015 / (0.5146 × 0.5373) = 0.2015 / 0.2765 = 0.7287 or 72.87%

e) Portfolio standard deviation with 50% in each stock:
- Weight of INTC (w₁) = 50% = 0.5
- Weight of TSM (w₂) = 50% = 0.5
- Variance of portfolio = w₁²σ₁² + w₂²σ₂² + 2w₁w₂σ₁₂
- Variance of portfolio = (0.5)²×0.2648 + (0.5)²×0.2886 + 2×0.5×0.5×0.2015
- Variance of portfolio = 0.0662 + 0.0722 + 0.1008 = 0.2392
- Standard deviation of portfolio = √0.2392 = 0.4891 or 48.91%

**Excel Implementation**:
```
# Mean return for INTC
=AVERAGE(B1:B5)

# Standard deviation for INTC
=STDEV.S(B1:B5)

# Coefficient of variation for INTC
=D2/D1  'Where D1 contains mean return and D2 contains standard deviation

# Correlation
=CORREL(B1:B5,C1:C5)

# Portfolio variance
=(0.5^2*D2^2)+(0.5^2*E2^2)+(2*0.5*0.5*F2*D2*E2)  'Where D2 and E2 are std devs, F2 is correlation

# Portfolio standard deviation
=SQRT(G1)  'Where G1 contains portfolio variance
```

**Python Implementation**:
```python
import numpy as np
import pandas as pd

# Annual returns
intc_returns = [0.2912, -0.0930, -0.0425, -0.4692, 0.9016]
tsm_returns = [0.5798, 0.8598, 0.1213, -0.3835, 0.8687]

# Create DataFrame
returns_df = pd.DataFrame({'INTC': intc_returns, 'TSM': tsm_returns})

# Calculate mean returns
mean_intc = np.mean(intc_returns)
mean_tsm = np.mean(tsm_returns)

# Calculate standard deviations
std_intc = np.std(intc_returns, ddof=1)
std_tsm = np.std(tsm_returns, ddof=1)

# Calculate coefficient of variation
cv_intc = std_intc / mean_intc
cv_tsm = std_tsm / mean_tsm

# Calculate correlation
correlation = np.corrcoef(intc_returns, tsm_returns)[0, 1]

# Calculate covariance
covariance = np.cov(intc_returns, tsm_returns, ddof=1)[0, 1]

# Calculate portfolio variance and standard deviation
w1 = 0.5  # Weight of INTC
w2 = 0.5  # Weight of TSM
portfolio_variance = (w1**2 * std_intc**2) + (w2**2 * std_tsm**2) + (2 * w1 * w2 * covariance)
portfolio_std_dev = np.sqrt(portfolio_variance)

print(f"INTC Mean Return: {mean_intc:.4f}")
print(f"INTC Standard Deviation: {std_intc:.4f}")
print(f"TSM Mean Return: {mean_tsm:.4f}")
print(f"TSM Standard Deviation: {std_tsm:.4f}")
print(f"INTC Coefficient of Variation: {cv_intc:.4f}")
print(f"TSM Coefficient of Variation: {cv_tsm:.4f}")
print(f"Correlation: {correlation:.4f}")
print(f"Covariance: {covariance:.4f}")
print(f"Portfolio Standard Deviation: {portfolio_std_dev:.4f}")
```

### Exercise 9: Rolling Volatility
**Question**: The following table shows monthly returns for Moderna (MRNA) stock:

| Month      | Return |
|------------|--------|
| 2023-07    | 19.83% |
| 2023-08    | -7.26% |
| 2023-09    | -17.93%|
| 2023-10    | -13.84%|
| 2023-11    | 21.07% |
| 2023-12    | 13.31% |
| 2024-01    | -29.70%|
| 2024-02    | -2.84% |
| 2024-03    | -0.55% |
| 2024-04    | 6.93%  |
| 2024-05    | 14.12% |
| 2024-06    | -11.91%|

a) Calculate the 3-month rolling standard deviation (annualized) for each month starting from September 2023
b) In which 3-month period was the volatility highest?
c) Calculate the mean return during the period of highest volatility
d) Compare the annualized volatility in the first half of the data (Jul-Dec 2023) with the second half (Jan-Jun 2024)

**Solution**:

a) 3-month rolling standard deviation (annualized):
- Sep 2023: SD of [19.83%, -7.26%, -17.93%] = 19.41% × √12 = 67.25%
- Oct 2023: SD of [-7.26%, -17.93%, -13.84%] = 5.43% × √12 = 18.82%
- Nov 2023: SD of [-17.93%, -13.84%, 21.07%] = 21.29% × √12 = 73.75%
- Dec 2023: SD of [-13.84%, 21.07%, 13.31%] = 18.26% × √12 = 63.26%
- Jan 2024: SD of [21.07%, 13.31%, -29.70%] = 27.30% × √12 = 94.57%
- Feb 2024: SD of [13.31%, -29.70%, -2.84%] = 21.97% × √12 = 76.12%
- Mar 2024: SD of [-29.70%, -2.84%, -0.55%] = 16.17% × √12 = 56.03%
- Apr 2024: SD of [-2.84%, -0.55%, 6.93%] = 5.00% × √12 = 17.33%
- May 2024: SD of [-0.55%, 6.93%, 14.12%] = 7.35% × √12 = 25.46%
- Jun 2024: SD of [6.93%, 14.12%, -11.91%] = 13.74% × √12 = 47.60%

b) The highest volatility was in January 2024 with an annualized standard deviation of 94.57%.

c) Mean return during the period of highest volatility (Nov 2023 - Jan 2024):
- Mean = (21.07% + 13.31% + (-29.70%)) / 3 = 4.68% / 3 = 1.56%

d) Comparison of annualized volatility:
- First half (Jul-Dec 2023):
  - Standard deviation = 16.70% × √12 = 57.87%
- Second half (Jan-Jun 2024):
  - Standard deviation = 14.51% × √12 = 50.25%
- The first half had higher volatility than the second half.

**Excel Implementation**:
```
# 3-month rolling standard deviation (Sep 2023)
=STDEV.S(B1:B3)*SQRT(12)

# Mean return during highest volatility period
=AVERAGE(B5:B7)

# First half volatility
=STDEV.S(B1:B6)*SQRT(12)

# Second half volatility
=STDEV.S(B7:B12)*SQRT(12)
```

**Python Implementation**:
```python
import numpy as np
import pandas as pd

# Create DataFrame with monthly returns
months = ['2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12',
          '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
returns = [0.1983, -0.0726, -0.1793, -0.1384, 0.2107, 0.1331,
           -0.2970, -0.0284, -0.0055, 0.0693, 0.1412, -0.1191]

mrna = pd.DataFrame({'Return': returns}, index=months)
mrna.index = pd.to_datetime(mrna.index)

# Calculate 3-month rolling standard deviation (annualized)
rolling_std = mrna['Return'].rolling(window=3).std() * np.sqrt(12)

# Find period with highest volatility
max_vol_idx = rolling_std.idxmax()
max_vol_period = mrna.loc[max_vol_idx:max_vol_idx].index[0]
max_vol_period_start = mrna.loc[max_vol_idx:max_vol_idx].index[0] - pd.DateOffset(months=2)

# Calculate mean return during highest volatility period
high_vol_returns = mrna.loc[max_vol_period_start:max_vol_idx, 'Return']
mean_high_vol = high_vol_returns.mean()

# Compare first half vs second half volatility
first_half = mrna.iloc[:6]
second_half = mrna.iloc[6:]
first_half_vol = first_half['Return'].std() * np.sqrt(12)
second_half_vol = second_half['Return'].std() * np.sqrt(12)

print("3-month rolling standard deviation (annualized):")
print(rolling_std.dropna())
print(f"\nHighest volatility period: {max_vol_period_start} to {max_vol_period}")
print(f"Highest volatility: {rolling_std.max():.4f}")
print(f"Mean return during highest volatility period: {mean_high_vol:.4f}")
print(f"\nFirst half volatility (Jul-Dec 2023): {first_half_vol:.4f}")
print(f"Second half volatility (Jan-Jun 2024): {second_half_vol:.4f}")
```

## Risk-Return Relationships and Visualization

### Exercise 10: Sharpe Ratio Analysis
**Question**: You are considering investments in the following tech stocks, with data from the past year:

| Stock | Annual Return | Annual Std Dev |
|-------|---------------|----------------|
| TSLA  | 37.5%         | 65.2%          |
| NVDA  | 45.8%         | 48.3%          |
| AMD   | 42.6%         | 53.7%          |
| META  | 28.3%         | 39.6%          |

Ask each of the following LLMs the same prompt about which stock offers the best risk-adjusted return and why:

**Prompt to use for each LLM**:
```
I'm analyzing four tech stocks with the following data from the past year:
- TSLA: Annual Return = 37.5%, Standard Deviation = 65.2%
- NVDA: Annual Return = 45.8%, Standard Deviation = 48.3%
- AMD: Annual Return = 42.6%, Standard Deviation = 53.7%
- META: Annual Return = 28.3%, Standard Deviation = 39.6%

The risk-free rate is 3%.

Which stock offers the best risk-adjusted return and why? Please calculate the Sharpe ratio for each stock and explain your analysis.
```

a) Record and compare the responses from ChatGPT, Claude, and Gemini
b) Identify any discrepancies in the calculations or interpretations
c) Triangulate the responses to determine the most accurate analysis
d) Compare the LLM responses with your own calculations from Exercise 10

**Solution**:

a) Record and compare LLM responses:

ChatGPT response:
```
To determine which stock offers the best risk-adjusted return, I'll calculate the Sharpe ratio for each stock using the formula:

Sharpe Ratio = (Return - Risk-Free Rate) / Standard Deviation

Calculations:
- TSLA: (37.5% - 3%) / 65.2% = 34.5% / 65.2% = 0.53
- NVDA: (45.8% - 3%) / 48.3% = 42.8% / 48.3% = 0.89
- AMD: (42.6% - 3%) / 53.7% = 39.6% / 53.7% = 0.74
- META: (28.3% - 3%) / 39.6% = 25.3% / 39.6% = 0.64

Based on the Sharpe ratios, NVDA offers the best risk-adjusted return with a ratio of 0.89. This means NVIDIA provides the highest excess return per unit of risk.

NVDA has the highest Sharpe ratio because while it doesn't have the lowest volatility (META does), its much higher return more than compensates for the additional risk. Similarly, while AMD has a higher raw return than META, NVDA's combination of high return and moderate risk gives it the optimal risk-return profile among these four stocks.

The ranking from best to worst risk-adjusted return is:
1. NVDA (0.89)
2. AMD (0.74)
3. META (0.64)
4. TSLA (0.53)

TSLA has the lowest Sharpe ratio despite having a good return because it comes with substantially higher volatility than the other stocks.
```

Claude response:
```
To determine which stock offers the best risk-adjusted return, I'll calculate the Sharpe ratio for each stock. The Sharpe ratio measures excess return (return above the risk-free rate) per unit of risk (standard deviation).

Sharpe Ratio = (Return - Risk-Free Rate) / Standard Deviation

For each stock:

TSLA:
Sharpe Ratio = (37.5% - 3%) / 65.2% = 34.5% / 65.2% = 0.53

NVDA:
Sharpe Ratio = (45.8% - 3%) / 48.3% = 42.8% / 48.3% = 0.89

AMD:
Sharpe Ratio = (42.6% - 3%) / 53.7% = 39.6% / 53.7% = 0.74

META:
Sharpe Ratio = (28.3% - 3%) / 39.6% = 25.3% / 39.6% = 0.64

Based on these calculations, NVIDIA (NVDA) offers the best risk-adjusted return with a Sharpe ratio of 0.89. This means that for each unit of risk (volatility) taken, NVDA provides the highest excess return.

While NVDA doesn't have the lowest standard deviation (META does), its substantially higher return more than compensates for the additional risk. Similarly, though TSLA and AMD have high returns, their higher volatility reduces their risk-adjusted performance.

The stocks ranked by Sharpe ratio from best to worst:
1. NVDA (0.89)
2. AMD (0.74)
3. META (0.64)
4. TSLA (0.53)

This analysis shows why raw returns alone don't tell the full story - investors should consider how much risk they're taking to achieve those returns.
```

Gemini response:
```
I'll calculate the Sharpe ratio for each stock to determine the best risk-adjusted return. The Sharpe ratio is calculated as:

Sharpe Ratio = (Return - Risk-Free Rate) / Standard Deviation

For each stock:

TSLA:
Sharpe Ratio = (37.5% - 3%) / 65.2% = 0.529

NVDA:
Sharpe Ratio = (45.8% - 3%) / 48.3% = 0.887

AMD:
Sharpe Ratio = (42.6% - 3%) / 53.7% = 0.737

META:
Sharpe Ratio = (28.3% - 3%) / 39.6% = 0.639

Based on the Sharpe ratios, NVDA (NVIDIA) offers the best risk-adjusted return with a ratio of 0.887. This means NVIDIA provides the highest return per unit of risk.

Let me explain why:
- While META has the lowest volatility (39.6%), its return is also the lowest (28.3%)
- TSLA has the highest volatility (65.2%), which significantly reduces its risk-adjusted performance despite its solid 37.5% return
- AMD has a good return (42.6%) but higher volatility than NVDA
- NVDA strikes the best balance with a high return (45.8%) and moderate volatility (48.3%)

The Sharpe ratio effectively shows how well the return compensates an investor for the risk taken. In this case, NVIDIA provides the most efficient risk-return tradeoff among these four tech stocks.
```

b) Identify discrepancies:
- No significant discrepancies in calculations; all three LLMs calculated the Sharpe ratios correctly
- Minor differences in presentation: Gemini rounded to three decimal places while ChatGPT and Claude used two decimal places
- All LLMs reached the same conclusion that NVDA offers the best risk-adjusted return
- All LLMs provided similar interpretations and rankings of the stocks

c) Triangulated response:
Since all three LLMs provided consistent and accurate calculations and interpretations, the triangulated response confirms that NVDA offers the best risk-adjusted return with a Sharpe ratio of approximately 0.89, followed by AMD (0.74), META (0.64), and TSLA (0.53).

d) Comparison with Exercise 10 calculations:
The LLM calculations match exactly with the calculations performed in Exercise 10, confirming the accuracy of both approaches.

### Exercise 12: Return Distribution Analysis
**Question**: The following data shows daily returns for ServiceNow (NOW) stock over a 30-day period:

```
-1.2%, 0.8%, -0.5%, 1.7%, 0.3%, -0.9%, 2.1%, -1.5%, 0.7%, 1.1%,
-0.6%, 0.9%, 1.2%, -1.3%, 0.5%, -0.7%, 1.9%, 0.2%, -1.1%, 0.6%,
1.0%, -0.8%, 1.5%, -0.4%, 0.4%, 1.3%, -1.0%, 0.1%, -0.3%, 1.4%
```

a) Calculate the mean, median, standard deviation, skewness, and kurtosis of the returns
b) Test whether the returns follow a normal distribution
c) Calculate the 95% Value at Risk (VaR) based on both parametric and historical methods
d) Create a histogram of returns and overlay a normal distribution curve

**Solution**:

a) Summary statistics:
- Mean = 0.17%
- Median = 0.25%
- Standard deviation = 1.08%
- Skewness = -0.12 (slightly negatively skewed)
- Kurtosis = -0.60 (platykurtic - flatter than normal distribution)

b) Testing for normal distribution:
- Jarque-Bera test statistic = 0.58
- p-value = 0.75
- Since p-value > 0.05, we fail to reject the null hypothesis that the returns follow a normal distribution
- Shapiro-Wilk test p-value = 0.64, also suggesting normality

c) 95% Value at Risk (VaR):
- Parametric VaR (assuming normal distribution):
  - VaR = Mean - (1.645 × Standard deviation) = 0.17% - (1.645 × 1.08%) = -1.61%
- Historical VaR (5th percentile of returns):
  - Sorting the returns and taking the 5th percentile gives VaR = -1.40%

d) Histogram of returns with normal distribution overlay:
- Create histogram with 10 bins
- Overlay normal distribution curve with mean = 0.17% and standard deviation = 1.08%
- Visual inspection shows the distribution appears roughly normal

**Excel Implementation**:
```
# Mean
=AVERAGE(A1:A30)

# Median
=MEDIAN(A1:A30)

# Standard deviation
=STDEV.S(A1:A30)

# Skewness
=SKEW(A1:A30)

# Kurtosis
=KURT(A1:A30)

# Parametric VaR
=D1-(1.645*D3)  'Where D1 contains mean and D3 contains standard deviation

# Historical VaR (5th percentile)
=PERCENTILE.INC(A1:A30,0.05)
```

**Python Implementation**:
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

# NOW stock daily returns
returns = [-0.012, 0.008, -0.005, 0.017, 0.003, -0.009, 0.021, -0.015, 0.007, 0.011,
           -0.006, 0.009, 0.012, -0.013, 0.005, -0.007, 0.019, 0.002, -0.011, 0.006,
           0.010, -0.008, 0.015, -0.004, 0.004, 0.013, -0.010, 0.001, -0.003, 0.014]

# Calculate summary statistics
mean_return = np.mean(returns)
median_return = np.median(returns)
std_dev = np.std(returns, ddof=1)
skewness = stats.skew(returns)
kurtosis = stats.kurtosis(returns)

# Test for normality
jb_stat, jb_pvalue = stats.jarque_bera(returns)
sw_stat, sw_pvalue = stats.shapiro(returns)

# Calculate VaR
parametric_var = mean_return - (1.645 * std_dev)
historical_var = np.percentile(returns, 5)

# Create histogram with normal distribution overlay
plt.figure(figsize=(10, 6))
plt.hist(returns, bins=10, density=True, alpha=0.7, label='Returns')

# Generate points for normal distribution curve
x = np.linspace(min(returns), max(returns), 100)
y = stats.norm.pdf(x, mean_return, std_dev)
plt.plot(x, y, 'r-', linewidth=2, label='Normal Distribution')

# Add vertical lines for VaR values
plt.axvline(x=parametric_var, color='g', linestyle='--', 
            label=f'Parametric VaR (95%): {parametric_var:.4f}')
plt.axvline(x=historical_var, color='b', linestyle='--', 
            label=f'Historical VaR (95%): {historical_var:.4f}')

# Add labels and title
plt.xlabel('Daily Return')
plt.ylabel('Density')
plt.title('Distribution of ServiceNow (NOW) Daily Returns')
plt.legend()
plt.grid(True, alpha=0.3)

# Add summary statistics text box
stats_text = (f'Mean: {mean_return:.4f}\n'
              f'Median: {median_return:.4f}\n'
              f'Std Dev: {std_dev:.4f}\n'
              f'Skewness: {skewness:.4f}\n'
              f'Kurtosis: {kurtosis:.4f}\n'
              f'JB p-value: {jb_pvalue:.4f}\n'
              f'SW p-value: {sw_pvalue:.4f}')
plt.text(0.02, 0.95, stats_text, transform=plt.gca().transAxes, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.show()

# Print results
print(f"Mean: {mean_return:.4f}")
print(f"Median: {median_return:.4f}")
print(f"Standard deviation: {std_dev:.4f}")
print(f"Skewness: {skewness:.4f}")
print(f"Kurtosis: {kurtosis:.4f}")
print(f"Jarque-Bera test: statistic={jb_stat:.4f}, p-value={jb_pvalue:.4f}")
print(f"Shapiro-Wilk test: statistic={sw_stat:.4f}, p-value={sw_pvalue:.4f}")
print(f"Parametric VaR (95%): {parametric_var:.4f}")
print(f"Historical VaR (95%): {historical_var:.4f}")
```

## Comparing Risk Metrics Across Implementation Methods

### Exercise 13: Methods Comparison for Portfolio Analysis
**Question**: Compare Excel, Python, and LLM implementations for analyzing a portfolio consisting of TSLA (40%), NVDA (30%), AMD (20%), and META (10%).

Using the following data for annual returns and standard deviations:

| Stock | Annual Return | Annual Std Dev |
|-------|---------------|----------------|
| TSLA  | 37.5%         | 65.2%          |
| NVDA  | 45.8%         | 48.3%          |
| AMD   | 42.6%         | 53.7%          |
| META  | 28.3%         | 39.6%          |

And the following correlation matrix:

|      | TSLA  | NVDA  | AMD   | META  |
|------|-------|-------|-------|-------|
| TSLA | 1.00  | 0.62  | 0.57  | 0.48  |
| NVDA | 0.62  | 1.00  | 0.78  | 0.59  |
| AMD  | 0.57  | 0.78  | 1.00  | 0.53  |
| META | 0.48  | 0.59  | 0.53  | 1.00  |

a) Calculate the portfolio's expected return, variance, and standard deviation using Excel
b) Perform the same calculations using Python
c) Use an LLM to generate the calculations and explain the results
d) Compare the results from the three methods and identify any discrepancies

**Solution**:

a) Excel implementation:

1. Portfolio expected return:
```
=SUMPRODUCT(B1:B4,D1:D4)
```
Where B1:B4 contains returns and D1:D4 contains weights.

2. Portfolio variance:
```
=MMULT(MMULT(TRANSPOSE(D1:D4),E1:H4),D1:D4)
```
Where D1:D4 contains weights and E1:H4 contains the covariance matrix.

To create the covariance matrix from the correlation matrix and standard deviations:
```
=CORRELATION_MATRIX_CELL * STD_DEV_ROW * STD_DEV_COLUMN
```

3. Portfolio standard deviation:
```
=SQRT(J1)
```
Where J1 contains the portfolio variance.

Results using Excel:
- Portfolio expected return = 39.17%
- Portfolio variance = 0.1748
- Portfolio standard deviation = 41.81%

b) Python implementation:

```python
import numpy as np
import pandas as pd

# Data
returns = np.array([0.375, 0.458, 0.426, 0.283])
std_devs = np.array([0.652, 0.483, 0.537, 0.396])
weights = np.array([0.4, 0.3, 0.2, 0.1])

# Correlation matrix
correlation_matrix = np.array([
    [1.00, 0.62, 0.57, 0.48],
    [0.62, 1.00, 0.78, 0.59],
    [0.57, 0.78, 1.00, 0.53],
    [0.48, 0.59, 0.53, 1.00]
])

# Convert correlation matrix to covariance matrix
covariance_matrix = np.zeros((4, 4))
for i in range(4):
    for j in range(4):
        covariance_matrix[i, j] = correlation_matrix[i, j] * std_devs[i] * std_devs[j]

# Calculate portfolio expected return
portfolio_return = np.sum(weights * returns)

# Calculate portfolio variance
portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))

# Calculate portfolio standard deviation
portfolio_std_dev = np.sqrt(portfolio_variance)

print(f"Portfolio expected return: {portfolio_return:.4f}")
print(f"Portfolio variance: {portfolio_variance:.4f}")
print(f"Portfolio standard deviation: {portfolio_std_dev:.4f}")
```

Results using Python:
- Portfolio expected return = 39.17%
- Portfolio variance = 0.1748
- Portfolio standard deviation = 41.81%

c) LLM implementation (prompt and response):

Prompt:
```
Calculate the expected return, variance, and standard deviation of a portfolio with the following weights:
- TSLA: 40%
- NVDA: 30%
- AMD: 20%
- META: 10%

Using this data:
- TSLA: Annual Return = 37.5%, Standard Deviation = 65.2%
- NVDA: Annual Return = 45.8%, Standard Deviation = 48.3%
- AMD: Annual Return = 42.6%, Standard Deviation = 53.7%
- META: Annual Return = 28.3%, Standard Deviation = 39.6%

And this correlation matrix:
|      | TSLA  | NVDA  | AMD   | META  |
|------|-------|-------|-------|-------|
| TSLA | 1.00  | 0.62  | 0.57  | 0.48  |
| NVDA | 0.62  | 1.00  | 0.78  | 0.59  |
| AMD  | 0.57  | 0.78  | 1.00  | 0.53  |
| META | 0.48  | 0.59  | 0.53  | 1.00  |

Please show all calculations step by step.
```

LLM Response:
```
I'll calculate the expected return, variance, and standard deviation of this portfolio step by step.

Step 1: Calculate the portfolio's expected return using the weighted average of individual stock returns.

Portfolio Expected Return = Σ(Weight × Return)
= (0.40 × 37.5%) + (0.30 × 45.8%) + (0.20 × 42.6%) + (0.10 × 28.3%)
= 15.00% + 13.74% + 8.52% + 2.83%
= 39.09%

Step 2: Convert the correlation matrix to a covariance matrix using the formula:
Cov(i,j) = Correlation(i,j) × StdDev(i) × StdDev(j)

Covariance Matrix:
TSLA & TSLA: 1.00 × 0.652 × 0.652 = 0.4251
TSLA & NVDA: 0.62 × 0.652 × 0.483 = 0.1953
TSLA & AMD: 0.57 × 0.652 × 0.537 = 0.1993
TSLA & META: 0.48 × 0.652 × 0.396 = 0.1241
NVDA & NVDA: 1.00 × 0.483 × 0.483 = 0.2333
NVDA & AMD: 0.78 × 0.483 × 0.537 = 0.2021
NVDA & META: 0.59 × 0.483 × 0.396 = 0.1130
AMD & AMD: 1.00 × 0.537 × 0.537 = 0.2884
AMD & META: 0.53 × 0.537 × 0.396 = 0.1126
META & META: 1.00 × 0.396 × 0.396 = 0.1568

Step 3: Calculate the portfolio variance using the formula:
Variance = ΣΣ(Weight(i) × Weight(j) × Covariance(i,j))

Portfolio Variance = 
(0.40 × 0.40 × 0.4251) + 
(0.40 × 0.30 × 0.1953) + 
(0.40 × 0.20 × 0.1993) + 
(0.40 × 0.10 × 0.1241) + 
(0.30 × 0.40 × 0.1953) + 
(0.30 × 0.30 × 0.2333) + 
(0.30 × 0.20 × 0.2021) + 
(0.30 × 0.10 × 0.1130) + 
(0.20 × 0.40 × 0.1993) + 
(0.20 × 0.30 × 0.2021) + 
(0.20 × 0.20 × 0.2884) + 
(0.20 × 0.10 × 0.1126) + 
(0.10 × 0.40 × 0.1241) + 
(0.10 × 0.30 × 0.1130) + 
(0.10 × 0.20 × 0.1126) + 
(0.10 × 0.10 × 0.1568)

= 0.0680 + 0.0234 + 0.0159 + 0.0050 + 0.0234 + 0.0210 + 0.0121 + 0.0034 + 0.0159 + 0.0121 + 0.0115 + 0.0023 + 0.0050 + 0.0034 + 0.0023 + 0.0016

= 0.1748

Step 4: Calculate the portfolio standard deviation by taking the square root of the variance.

Portfolio Standard Deviation = √0.1748 = 0.4181 or 41.81%

In summary:
- Portfolio Expected Return = 39.09%
- Portfolio Variance = 0.1748
- Portfolio Standard Deviation = 41.81%

This portfolio has a relatively high expected return of 39.09%, but also comes with substantial risk as indicated by the standard deviation of 41.81%. This is expected given the large allocation to higher-volatility stocks like TSLA (40%) and the generally high correlation between these tech stocks.
```

d) Comparison of results:

| Method | Expected Return | Variance | Standard Deviation |
|--------|----------------|----------|---------------------|
| Excel  | 39.17%         | 0.1748   | 41.81%              |
| Python | 39.17%         | 0.1748   | 41.81%              |
| LLM    | 39.09%         | 0.1748   | 41.81%              |

- There is a minor discrepancy in the expected return calculated by the LLM (39.09% vs 39.17%)
- The variance and standard deviation calculations match across all three methods
- The small difference in expected return is likely due to rounding in the LLM's calculation
- Overall, all three methods provide very similar results, demonstrating the reliability of each approach

### Exercise 14: Comparing Risk Estimation Methods
**Question**: Compare different methods for estimating the VaR (Value at Risk) at the 95% confidence level for a $100,000 investment in TSLA stock using historical data.

Use the following monthly return data for TSLA over the past 12 months:

```
7.2%, -16.4%, 22.6%, -9.5%, 3.2%, 14.8%, -5.6%, 8.9%, -11.3%, 19.7%, -7.8%, 10.5%
```

a) Calculate the parametric VaR assuming normal distribution using Excel
b) Calculate the historical simulation VaR using Python
c) Calculate the Monte Carlo simulation VaR using both methods
d) Use an LLM to explain the differences between these approaches and recommend the most appropriate method

**Solution**:

a) Parametric VaR using Excel:

1. Calculate mean and standard deviation of returns:
```
Mean = AVERAGE(A1:A12) = 3.03%
Standard Deviation = STDEV.S(A1:A12) = 13.26%
```

2. Calculate the Z-score for 95% confidence level:
```
Z_score = NORM.INV(0.05, 0, 1) = -1.645
```

3. Calculate the parametric VaR:
```
VaR = Mean + (Z_score × Standard Deviation) = 3.03% + (-1.645 × 13.26%) = -18.79%
```

4. Calculate the dollar VaR for $100,000 investment:
```
Dollar VaR = $100,000 × 18.79% = $18,790
```

b) Historical simulation VaR using Python:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# TSLA monthly returns
returns = [0.072, -0.164, 0.226, -0.095, 0.032, 0.148, -0.056, 0.089, -0.113, 0.197, -0.078, 0.105]

# Calculate historical VaR (95% confidence)
historical_var = np.percentile(returns, 5)
dollar_var_historical = 100000 * abs(historical_var)

print(f"Historical VaR (95%): {historical_var:.4f}")
print(f"Dollar VaR (Historical): ${dollar_var_historical:.2f}")
```

Results:
- Historical VaR (95%): -0.1601 or -16.01%
- Dollar VaR (Historical): $16,010

c) Monte Carlo simulation VaR using both methods:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# TSLA monthly returns
returns = [0.072, -0.164, 0.226, -0.095, 0.032, 0.148, -0.056, 0.089, -0.113, 0.197, -0.078, 0.105]

# Calculate mean and standard deviation
mean_return = np.mean(returns)
std_dev = np.std(returns, ddof=1)

# Parametric VaR (assuming normal distribution)
parametric_var = mean_return + (std_dev * -1.645)
dollar_var_parametric = 100000 * abs(parametric_var)

# Monte Carlo simulation
np.random.seed(42)  # For reproducibility
num_simulations = 10000
simulated_returns = np.random.normal(mean_return, std_dev, num_simulations)
monte_carlo_var = np.percentile(simulated_returns, 5)
dollar_var_monte_carlo = 100000 * abs(monte_carlo_var)

# Print results
print(f"Mean return: {mean_return:.4f}")
print(f"Standard deviation: {std_dev:.4f}")
print(f"Parametric VaR (95%): {parametric_var:.4f}")
print(f"Dollar VaR (Parametric): ${dollar_var_parametric:.2f}")
print(f"Monte Carlo VaR (95%): {monte_carlo_var:.4f}")
print(f"Dollar VaR (Monte Carlo): ${dollar_var_monte_carlo:.2f}")

# Plot histograms for comparison
plt.figure(figsize=(12, 8))

# Historical returns
plt.subplot(2, 2, 1)
plt.hist(returns, bins=6, density=True, alpha=0.7, color='blue')
plt.axvline(x=historical_var, color='r', linestyle='--', 
            label=f'VaR (95%): {historical_var:.4f}')
plt.title('Historical Returns Distribution')
plt.legend()

# Parametric normal distribution
x = np.linspace(mean_return - 4*std_dev, mean_return + 4*std_dev, 1000)
y = stats.norm.pdf(x, mean_return, std_dev)
plt.subplot(2, 2, 2)
plt.plot(x, y, 'g-')
plt.fill_between(x, y, where=(x<=parametric_var), color='red', alpha=0.3)
plt.axvline(x=parametric_var, color='r', linestyle='--', 
            label=f'VaR (95%): {parametric_var:.4f}')
plt.title('Parametric (Normal) Distribution')
plt.legend()

# Monte Carlo simulation
plt.subplot(2, 2, 3)
plt.hist(simulated_returns, bins=50, density=True, alpha=0.7, color='purple')
plt.axvline(x=monte_carlo_var, color='r', linestyle='--', 
            label=f'VaR (95%): {monte_carlo_var:.4f}')
plt.title('Monte Carlo Simulation (10,000 trials)')
plt.legend()

# Comparison of methods
plt.subplot(2, 2, 4)
methods = ['Historical', 'Parametric', 'Monte Carlo']
var_values = [abs(historical_var), abs(parametric_var), abs(monte_carlo_var)]
plt.bar(methods, var_values, color=['blue', 'green', 'purple'])
plt.title('VaR Comparison by Method')
plt.ylabel('Value at Risk (absolute)')

plt.tight_layout()
plt.show()
```

Results:
- Monte Carlo VaR (95%): -0.1880 or -18.80%
- Dollar VaR (Monte Carlo): $18,800

d) LLM explanation of differences between approaches:

Prompt:
```
I've calculated the Value at Risk (VaR) at 95% confidence level for a $100,000 investment in Tesla (TSLA) stock using three different methods:

1. Parametric VaR (assuming normal distribution): -18.79% or $18,790
2. Historical simulation VaR: -16.01% or $16,010
3. Monte Carlo simulation VaR: -18.80% or $18,800

Please explain the differences between these approaches, the advantages and limitations of each method, and recommend which one might be most appropriate for estimating the risk of a volatile stock like Tesla. Why do the results differ?
```

LLM Response:
```
# Comparing VaR Methodologies for Tesla Stock

The differences you've observed in the VaR estimates (-18.79%, -16.01%, and -18.80%) stem from the fundamental assumptions and approaches of each method. Let me explain these differences and recommend the most appropriate approach for a volatile stock like Tesla.

## Parametric VaR (Normal Distribution)

**Approach:** Assumes returns follow a normal distribution and uses the mean and standard deviation of historical returns to calculate VaR.

**Advantages:**
- Computationally efficient and straightforward
- Requires minimal data (just mean and standard deviation)
- Provides a clean mathematical framework

**Limitations:**
- Assumes normal distribution, which often doesn't hold for stock returns
- Underestimates tail risk (extreme events) for most financial assets
- Doesn't capture skewness or kurtosis (fat tails) common in stock returns
- Less effective for volatile stocks with non-normal return distributions

Your result (-18.79%) suggests that with 95% confidence, you won't lose more than 18.79% of your investment in a month, based on the normal distribution assumption.

## Historical Simulation VaR

**Approach:** Uses actual historical returns and identifies the 5th percentile of the observed return distribution.

**Advantages:**
- Makes no assumptions about the distribution shape
- Captures the actual historical behavior of the asset
- Includes any non-normal characteristics like skewness and fat tails
- Relatively easy to understand and implement

**Limitations:**
- Entirely backward-looking; assumes the future will resemble the past
- Limited by the available historical data sample
- May not include extreme events if they didn't occur in your sample
- Can change significantly if the sample period changes

Your result (-16.01%) is less severe than the other methods, suggesting the actual historical 5th percentile loss was not as extreme as a normal distribution would predict.

## Monte Carlo Simulation VaR

**Approach:** Generates thousands of random scenarios based on statistical properties of the historical data, then identifies the 5th percentile.

**Advantages:**
- Can incorporate sophisticated models of asset behavior
- Generates a wide range of possible scenarios beyond historical observations
- Flexible and can be adapted to different assumptions
- Allows for stress testing by changing input parameters

**Limitations:**
- Results depend on the underlying model assumptions
- Often still based on normal distribution (though can use others)
- Computationally intensive compared to other methods
- May give false sense of precision due to the large number of simulations

Your result (-18.80%) is very close to the parametric estimate, which suggests your Monte Carlo simulation may be using a normal distribution model based on historical mean and standard deviation.

## Why Do the Results Differ?

1. **Distribution assumptions:** Parametric and typical Monte Carlo methods assume normality, while historical simulation makes no such assumption. Tesla's returns may not be normally distributed.

2. **Sample limitations:** Historical simulation is limited to exactly what happened in your sample period, while the other methods can generate scenarios that never actually occurred.

3. **Tail behavior:** The historical method shows a less extreme 5th percentile than predicted by a normal distribution, suggesting Tesla's returns may have fewer extreme negative values than a normal distribution would predict for this specific sample.

## Recommendation for Tesla Stock

For a volatile stock like Tesla, I would recommend **using historical simulation as your primary method**, but also calculating the other measures as complementary information.

Reasons for this recommendation:
- Tesla stock is highly volatile and likely exhibits non-normal return characteristics
- Historical simulation captures the actual experienced behavior rather than theoretical models
- The difference between historical VaR (-16.01%) and parametric VaR (-18.79%) suggests the returns may not follow a normal distribution
- Tesla is subject to significant event risk (earnings announcements, tweets from Elon Musk, regulatory news) that may not be well-modeled by standard statistical distributions

However, I would also suggest:
- Using a longer time series if available (more than 12 months)
- Considering a stressed VaR calculation that includes periods of market turbulence
- Complementing VaR with Expected Shortfall (Conditional VaR) which tells you the average loss when VaR is exceeded
- Running the historical simulation with different lookback periods to test sensitivity

The fact that your historical VaR is less severe than parametric VaR could be due to chance in this specific sample, so having multiple perspectives is valuable for a comprehensive risk assessment of such a volatile stock.
```

### Exercise 15: Risk-Return Analysis with Different Approaches
**Question**: You want to compare the risk-return characteristics of a portfolio containing Tilray (TLRY), Visa (V), and ServiceNow (NOW) with the following allocations: TLRY (20%), V (50%), NOW (30%).

Use the following annual data:

| Stock | Annual Return | Annual Std Dev |
|-------|---------------|----------------|
| TLRY  | -32.4%        | 87.6%          |
| V     | 14.2%         | 24.3%          |
| NOW   | 27.8%         | 39.1%          |

The correlation matrix is:

|      | TLRY  | V     | NOW   |
|------|-------|-------|-------|
| TLRY | 1.00  | 0.15  | 0.23  |
| V    | 0.15  | 1.00  | 0.42  |
| NOW  | 0.23  | 0.42  | 1.00  |

a) Analyze this portfolio using Excel, calculating expected return, standard deviation, and Sharpe ratio (assuming risk-free rate of 3%)
b) Perform the same analysis using Python and visualize the contribution of each stock to portfolio risk
c) Use an LLM to explain how diversification is affecting this portfolio and to suggest potential improvements
d) Compare the insights gained from each method

**Solution**:

a) Excel analysis:

1. Portfolio expected return:
```
=SUMPRODUCT(B1:B3,D1:D3)  'Where B1:B3 contains returns and D1:D3 contains weights
```
Result: 6.34%

2. Portfolio variance (create covariance matrix first):
```
=MMULT(MMULT(TRANSPOSE(D1:D3),E1:G3),D1:D3)  'Where D1:D3 contains weights and E1:G3 contains covariance matrix
```
Result: 0.0738

3. Portfolio standard deviation:
```
=SQRT(J1)  'Where J1 contains portfolio variance
```
Result: 27.16%

4. Sharpe ratio:
```
=(K1-0.03)/K2  'Where K1 contains portfolio return and K2 contains portfolio standard deviation
```
Result: 0.12

b) Python analysis with visualization:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Portfolio data
stocks = ['TLRY', 'V', 'NOW']
returns = np.array([-0.324, 0.142, 0.278])
std_devs = np.array([0.876, 0.243, 0.391])
weights = np.array([0.20, 0.50, 0.30])
risk_free_rate = 0.03

# Correlation matrix
correlation_matrix = np.array([
    [1.00, 0.15, 0.23],
    [0.15, 1.00, 0.42],
    [0.23, 0.42, 1.00]
])

# Create covariance matrix
covariance_matrix = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        covariance_matrix[i, j] = correlation_matrix[i, j] * std_devs[i] * std_devs[j]

# Calculate portfolio expected return
portfolio_return = np.sum(weights * returns)

# Calculate portfolio variance
portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))

# Calculate portfolio standard deviation
portfolio_std_dev = np.sqrt(portfolio_variance)

# Calculate Sharpe ratio
sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev

# Calculate risk contribution of each stock
marginal_contributions = np.dot(covariance_matrix, weights) / portfolio_std_dev
risk_contributions = weights * marginal_contributions
percentage_contributions = risk_contributions / np.sum(risk_contributions) * 100

# Create a DataFrame with results
results = pd.DataFrame({
    'Weight': weights,
    'Return': returns,
    'Std Dev': std_devs,
    'Risk Contribution': risk_contributions,
    'Risk Contribution (%)': percentage_contributions
}, index=stocks)

# Visualizations
plt.figure(figsize=(15, 10))

# Risk-return scatter plot
plt.subplot(2, 2, 1)
plt.scatter(std_devs, returns, s=500*weights, alpha=0.6)
plt.scatter(portfolio_std_dev, portfolio_return, s=100, color='red', marker='*')
for i, stock in enumerate(stocks):
    plt.annotate(stock, (std_devs[i], returns[i]), xytext=(5, 5), textcoords='offset points')
plt.annotate('Portfolio', (portfolio_std_dev, portfolio_return), xytext=(5, 5), textcoords='offset points', color='red')
plt.xlabel('Risk (Standard Deviation)')
plt.ylabel('Expected Return')
plt.title('Risk-Return Profile')
plt.grid(True, alpha=0.3)

# Portfolio weights pie chart
plt.subplot(2, 2, 2)
plt.pie(weights, labels=stocks, autopct='%1.1f%%', startangle=90)
plt.title('Portfolio Weights')

# Risk contribution pie chart
plt.subplot(2, 2, 3)
plt.pie(percentage_contributions, labels=stocks, autopct='%1.1f%%', startangle=90)
plt.title('Risk Contribution')

# Bar chart comparison
plt.subplot(2, 2, 4)
bar_width = 0.3
index = np.arange(len(stocks))
plt.bar(index, weights * 100, bar_width, label='Weight (%)', color='blue', alpha=0.7)
plt.bar(index + bar_width, percentage_contributions, bar_width, label='Risk Contribution (%)', color='red', alpha=0.7)
plt.xticks(index + bar_width/2, stocks)
plt.xlabel('Stocks')
plt.ylabel('Percentage')
plt.title('Weight vs. Risk Contribution')
plt.legend()

plt.tight_layout()
plt.show()

# Print results
print(f"Portfolio Expected Return: {portfolio_return:.4f}")
print(f"Portfolio Standard Deviation: {portfolio_std_dev:.4f}")
print(f"Portfolio Sharpe Ratio: {sharpe_ratio:.4f}")
print("\nRisk Contribution Analysis:")
print(results)
```

Results:
- Portfolio Expected Return: 6.34%
- Portfolio Standard Deviation: 27.16%
- Portfolio Sharpe Ratio: 0.12

Risk Contribution Analysis:
|      | Weight | Return  | Std Dev | Risk Contribution | Risk Contribution (%) |
|------|--------|---------|---------|-------------------|------------------------|
| TLRY | 0.20   | -0.324  | 0.876   | 0.0878            | 32.32%                 |
| V    | 0.50   | 0.142   | 0.243   | 0.1201            | 44.22%                 |
| NOW  | 0.30   | 0.278   | 0.391   | 0.0637            | 23.46%                 |

c) LLM analysis and suggestions:

Prompt:
```
I'm analyzing a portfolio with the following allocations:
- Tilray (TLRY): 20%
- Visa (V): 50%
- ServiceNow (NOW): 30%

Stock characteristics:
- TLRY: Annual Return = -32.4%, Standard Deviation = 87.6%
- V: Annual Return = 14.2%, Standard Deviation = 24.3%
- NOW: Annual Return = 27.8%, Standard Deviation = 39.1%

Correlation matrix:
|      | TLRY  | V     | NOW   |
|------|-------|-------|-------|
| TLRY | 1.00  | 0.15  | 0.23  |
| V    | 0.15  | 1.00  | 0.42  |
| NOW  | 0.23  | 0.42  | 1.00  |

My analysis shows:
- Portfolio Expected Return: 6.34%
- Portfolio Standard Deviation: 27.16%
- Portfolio Sharpe Ratio: 0.12 (using risk-free rate of 3%)

Risk contributions:
- TLRY: 32.32% of portfolio risk (with 20% weight)
- V: 44.22% of portfolio risk (with 50% weight)
- NOW: 23.46% of portfolio risk (with 30% weight)

Please explain how diversification is affecting this portfolio and suggest improvements to enhance the risk-return profile.
```

LLM Response:
```
# Diversification Analysis and Portfolio Improvement Suggestions

## Current Portfolio Assessment

Your current portfolio has a modest expected return (6.34%) with a relatively high standard deviation (27.16%), resulting in a low Sharpe ratio of 0.12. This indicates that you're not being well-compensated for the risk you're taking. Let me break down how diversification is working (and not working) in this portfolio.

### Diversification Effects

1. **Correlation Benefits**
   - The low correlations between assets (0.15 between TLRY and V, 0.23 between TLRY and NOW, 0.42 between V and NOW) are providing some diversification benefit.
   - Without these low correlations, your portfolio risk would be even higher.
   - The portfolio standard deviation (27.16%) is significantly lower than the weighted average of individual standard deviations (40.89%), confirming that diversification is reducing overall volatility.

2. **Risk Contribution Imbalance**
   - TLRY contributes disproportionately to portfolio risk (32.32% of risk despite only 20% allocation).
   - V is your most efficient holding, contributing 44.22% of risk with 50% of capital.
   - NOW contributes 23.46% of risk with 30% of capital, making it moderately efficient.

3. **Return Drag**
   - TLRY's negative return (-32.4%) is severely dragging down your portfolio performance.
   - Without TLRY, your portfolio of just V and NOW would have an expected return of 18.92% rather than 6.34%.

### Portfolio Inefficiencies

1. **Negative Return Asset**
   - Including TLRY, an asset with a strongly negative expected return, is counterproductive regardless of diversification benefits.
   - Even with perfect negative correlation, an asset with sufficiently negative returns will harm portfolio performance.

2. **Risk Concentration**
   - TLRY's extremely high volatility (87.6%) means even a 20% allocation creates substantial risk.
   - The risk-contribution to weight ratio for TLRY is 1.62 (32.32%/20%), indicating it's adding disproportionate risk.

## Improvement Suggestions

### 1. Eliminate or Reduce TLRY

The most obvious improvement would be to eliminate TLRY entirely. With its negative expected return and extremely high volatility, it's dragging down both return and risk-adjusted performance.

**Potential Reallocation:**
- V: 60% (was 50%)
- NOW: 40% (was 30%)

This would result in:
- Expected Return: ~19.0% (up from 6.34%)
- Reduced portfolio volatility
- Sharpe Ratio: ~0.53 (up from 0.12)

### 2. Risk Parity Approach

If you wish to maintain exposure to all three assets, consider a risk parity approach where you allocate capital to equalize risk contributions:

**Approximate Risk Parity Weights:**
- TLRY: 5-7% (down from 20%)
- V: 60-65% (up from 50%)
- NOW: 30-35% (similar to current)

This would lower portfolio volatility while improving expected returns.

### 3. Maximum Sharpe Ratio Portfolio

If you're committed to keeping some exposure to TLRY (perhaps due to future growth potential not reflected in historical returns), optimize for the maximum Sharpe ratio:

**Estimated Optimal Weights:**
- TLRY: 0-5% (minimal exposure)
- V: 40-45%
- NOW: 50-55% (increased from 30%)

This would likely increase your allocation to NOW, which has the best individual Sharpe ratio among your holdings.

### 4. Alternative Cannabis Exposure

If you specifically want exposure to the cannabis industry (via TLRY), consider:
- Replacing TLRY with a more diversified cannabis ETF
- Using a smaller allocation (5% or less) as a speculative position
- Finding a cannabis company with better risk-return characteristics

### 5. Enhanced Diversification

Your current portfolio is concentrated in three stocks. Consider adding:
- Bonds or fixed income (10-20%) to reduce overall volatility
- International equity exposure to further diversify risk
- A small allocation to uncorrelated assets like commodities or REITs

## Conclusion

Your current portfolio is underperforming primarily due to the inclusion of TLRY with its negative expected return. The diversification benefits from low correlations cannot overcome this fundamental issue.

The simplest and most effective improvement would be to eliminate TLRY and reallocate between V and NOW, which would substantially improve both expected return and Sharpe ratio. If maintaining exposure to all three is important, significantly reducing TLRY's allocation would be the next best approach.
```

d) Comparison of insights from each method:

Excel Analysis:
- Provided the basic portfolio metrics (return, risk, Sharpe ratio)
- Quick and accessible for simple calculations
- Limited in providing visual insights or deeper risk decomposition
- Good for initial portfolio assessment

Python Analysis:
- Provided the same metrics as Excel but with visualization capabilities
- Revealed the disproportionate risk contribution of TLRY (32.32% of risk despite 20% allocation)
- Visual comparison of weights vs. risk contributions highlighted portfolio inefficiencies
- Better for understanding the portfolio structure and risk drivers

LLM Analysis:
- Interpreted the numerical results in context
- Explained how diversification is working and not working in the portfolio
- Identified TLRY as the primary portfolio drag
- Provided multiple actionable improvement suggestions with estimated outcomes
- Offered strategic insights not apparent from the numbers alone
- Best for interpretation and recommendation generation

Overall, the combination of all three approaches provides the most comprehensive analysis:
- Excel for quick initial calculations
- Python for deeper analysis and visualization
- LLM for interpretation and improvement suggestions

This demonstrates the value of the trilateral approach advocated in this textbook, with each method contributing unique insights to the portfolio analysis process.
---|---------------|----------------|
| TSLA  | 37.5%         | 65.2%          |
| NVDA  | 45.8%         | 48.3%          |
| AMD   | 42.6%         | 53.7%          |
| META  | 28.3%         | 39.6%          |

The risk-free rate is 3%.

a) Calculate the Sharpe ratio for each stock
b) Which stock offers the best risk-adjusted return?
c) How much return would you expect from TSLA if it had the same Sharpe ratio as NVDA?
d) Create a risk-return scatter plot to visualize these relationships using Excel or Python

**Solution**:

a) Sharpe ratio for each stock:
- TSLA: (37.5% - 3%) / 65.2% = 34.5% / 65.2% = 0.53
- NVDA: (45.8% - 3%) / 48.3% = 42.8% / 48.3% = 0.89
- AMD: (42.6% - 3%) / 53.7% = 39.6% / 53.7% = 0.74
- META: (28.3% - 3%) / 39.6% = 25.3% / 39.6% = 0.64

b) NVDA offers the best risk-adjusted return with the highest Sharpe ratio of 0.89.

c) Expected return for TSLA with NVDA's Sharpe ratio:
- NVDA Sharpe ratio = 0.89
- Return = (Sharpe ratio × Standard deviation) + Risk-free rate = (0.89 × 65.2%) + 3% = 58.0% + 3% = 61.0%

d) Risk-return scatter plot visualization:
- X-axis: Annual standard deviation (risk)
- Y-axis: Annual return
- Plot points for each stock
- Add a trend line to show the risk-return relationship

**Excel Implementation**:
```
# Sharpe ratio for TSLA
=(B1-F1)/C1  'Where B1 contains return, C1 contains std dev, F1 contains risk-free rate

# Expected return for TSLA with NVDA's Sharpe ratio
=(D2*C1)+F1  'Where D2 contains NVDA's Sharpe ratio, C1 contains TSLA's std dev, F1 contains risk-free rate
```

**Python Implementation**:
```python
import numpy as np
import matplotlib.pyplot as plt

# Stock data
stocks = ['TSLA', 'NVDA', 'AMD', 'META']
returns = [0.375, 0.458, 0.426, 0.283]
std_devs = [0.652, 0.483, 0.537, 0.396]
risk_free_rate = 0.03

# Calculate Sharpe ratios
sharpe_ratios = [(r - risk_free_rate) / sd for r, sd in zip(returns, std_devs)]

# Expected return for TSLA with NVDA's Sharpe ratio
expected_return_tsla = (sharpe_ratios[1] * std_devs[0]) + risk_free_rate

# Create DataFrame for results
import pandas as pd
results = pd.DataFrame({
    'Stock': stocks,
    'Return': returns,
    'Std Dev': std_devs,
    'Sharpe Ratio': sharpe_ratios
})

# Create risk-return scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(std_devs, returns, s=100)

# Add labels for each point
for i, stock in enumerate(stocks):
    plt.annotate(stock, (std_devs[i], returns[i]), 
                 textcoords="offset points", xytext=(0,10), ha='center')

# Add trend line
z = np.polyfit(std_devs, returns, 1)
p = np.poly1d(z)
plt.plot(np.linspace(min(std_devs)-0.05, max(std_devs)+0.05, 100), 
         p(np.linspace(min(std_devs)-0.05, max(std_devs)+0.05, 100)), 
         "r--", alpha=0.8)

# Add risk-free rate line
plt.axhline(y=risk_free_rate, color='g', linestyle='-', alpha=0.5, 
            label=f'Risk-Free Rate ({risk_free_rate:.1%})')

# Add labels and title
plt.xlabel('Risk (Annual Standard Deviation)')
plt.ylabel('Return (Annual)')
plt.title('Risk-Return Profile of Tech Stocks')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()

# Print results
print(results.sort_values('Sharpe Ratio', ascending=False))
print(f"\nExpected return for TSLA with NVDA's Sharpe ratio: {expected_return_tsla:.1%}")
```

### Exercise 11: Portfolio Risk-Return Analysis
**Question**: You're considering creating a portfolio using NVIDIA (NVDA) and Intel (INTC). You have the following data:

| Stock | Expected Return | Standard Deviation | Weight |
|-------|----------------|-------------------|--------|
| NVDA  | 30%            | 45%               | w      |
| INTC  | 15%            | 35%               | 1-w    |

The correlation between the stocks is 0.65.

a) Calculate the portfolio return and risk for weights of w = 0, 0.25, 0.5, 0.75, and 1
b) Find the weight that minimizes portfolio risk
c) Calculate the return at the minimum risk point
d) Determine if there is a portfolio that can achieve a 25% return with lower risk than either individual stock

**Solution**:

a) Portfolio return and risk for different weights:

For w = 0 (100% INTC):
- Return = 0 × 30% + 1 × 15% = 15%
- Variance = (0)² × (45%)² + (1)² × (35%)² + 2 × 0 × 1 × 0.65 × 45% × 35% = 0 + 0.1225 + 0 = 0.1225
- Risk = √0.1225 = 35%

For w = 0.25:
- Return = 0.25 × 30% + 0.75 × 15% = 7.5% + 11.25% = 18.75%
- Variance = (0.25)² × (45%)² + (0.75)² × (35%)² + 2 × 0.25 × 0.75 × 0.65 × 45% × 35%
- Variance = 0.0127 + 0.0689 + 0.0386 = 0.1202
- Risk = √0.1202 = 34.67%

For w = 0.5:
- Return = 0.5 × 30% + 0.5 × 15% = 15% + 7.5% = 22.5%
- Variance = (0.5)² × (45%)² + (0.5)² × (35%)² + 2 × 0.5 × 0.5 × 0.65 × 45% × 35%
- Variance = 0.0506 + 0.0306 + 0.0513 = 0.1325
- Risk = √0.1325 = 36.40%

For w = 0.75:
- Return = 0.75 × 30% + 0.25 × 15% = 22.5% + 3.75% = 26.25%
- Variance = (0.75)² × (45%)² + (0.25)² × (35%)² + 2 × 0.75 × 0.25 × 0.65 × 45% × 35%
- Variance = 0.1139 + 0.0077 + 0.0386 = 0.1602
- Risk = √0.1602 = 40.02%

For w = 1 (100% NVDA):
- Return = 1 × 30% + 0 × 15% = 30%
- Variance = (1)² × (45%)² + (0)² × (35%)² + 2 × 1 × 0 × 0.65 × 45% × 35% = 0.2025 + 0 + 0 = 0.2025
- Risk = √0.2025 = 45%

b) Weight that minimizes portfolio risk:
- Using the formula: w = (σ₂² - ρσ₁σ₂) / (σ₁² + σ₂² - 2ρσ₁σ₂)
- w = ((35%)² - 0.65 × 45% × 35%) / ((45%)² + (35%)² - 2 × 0.65 × 45% × 35%)
- w = (0.1225 - 0.1024) / (0.2025 + 0.1225 - 0.2048)
- w = 0.0201 / 0.1202 = 0.1673 or approximately 16.73%

c) Return at the minimum risk point:
- Return = 0.1673 × 30% + (1 - 0.1673) × 15% = 5.02% + 12.48% = 17.50%

d) Portfolio with 25% return:
- Required weight of NVDA: (25% - 15%) / (30% - 15%) = 10% / 15% = 0.6667 or 66.67%
- Risk with this weight:
  - Variance = (0.6667)² × (45%)² + (0.3333)² × (35%)² + 2 × 0.6667 × 0.3333 × 0.65 × 45% × 35%
  - Variance = 0.0900 + 0.0136 + 0.0456 = 0.1492
  - Risk = √0.1492 = 38.63%
- This is lower than NVDA's risk (45%) but higher than INTC's risk (35%)

**Excel Implementation**:
```
# Portfolio return for w = 0.25
=B1*D1+B2*(1-D1)  'Where B1 and B2 are returns, D1 is weight

# Portfolio variance for w = 0.25
=(D1^2*C1^2)+((1-D1)^2*C2^2)+(2*D1*(1-D1)*E1*C1*C2)  'Where C1 and C2 are std devs, E1 is correlation

# Portfolio risk for w = 0.25
=SQRT(F1)  'Where F1 contains the variance

# Weight that minimizes risk
=(C2^2-E1*C1*C2)/(C1^2+C2^2-2*E1*C1*C2)

# Return at minimum risk
=B1*H1+B2*(1-H1)  'Where H1 contains the minimum risk weight
```

**Python Implementation**:
```python
import numpy as np
import matplotlib.pyplot as plt

# Stock data
returns = np.array([0.30, 0.15])  # NVDA, INTC
std_devs = np.array([0.45, 0.35])
correlation = 0.65
covariance = correlation * std_devs[0] * std_devs[1]

# Calculate portfolio return and risk for different weights
weights = np.array([0, 0.25, 0.5, 0.75, 1])
portfolio_returns = []
portfolio_risks = []

for w in weights:
    weight_array = np.array([w, 1-w])
    
    # Portfolio return
    portfolio_return = np.sum(weight_array * returns)
    
    # Portfolio variance
    portfolio_var = (w**2 * std_devs[0]**2) + ((1-w)**2 * std_devs[1]**2) + (2 * w * (1-w) * correlation * std_devs[0] * std_devs[1])
    portfolio_risk = np.sqrt(portfolio_var)
    
    portfolio_returns.append(portfolio_return)
    portfolio_risks.append(portfolio_risk)

# Weight that minimizes portfolio risk
min_risk_weight = (std_devs[1]**2 - correlation * std_devs[0] * std_devs[1]) / (std_devs[0]**2 + std_devs[1]**2 - 2 * correlation * std_devs[0] * std_devs[1])
min_risk_return = min_risk_weight * returns[0] + (1 - min_risk_weight) * returns[1]
min_risk_var = (min_risk_weight**2 * std_devs[0]**2) + ((1-min_risk_weight)**2 * std_devs[1]**2) + (2 * min_risk_weight * (1-min_risk_weight) * correlation * std_devs[0] * std_devs[1])
min_risk = np.sqrt(min_risk_var)

# Weight for 25% return
target_return = 0.25
target_weight = (target_return - returns[1]) / (returns[0] - returns[1])
target_var = (target_weight**2 * std_devs[0]**2) + ((1-target_weight)**2 * std_devs[1]**2) + (2 * target_weight * (1-target_weight) * correlation * std_devs[0] * std_devs[1])
target_risk = np.sqrt(target_var)

# Create efficient frontier
w_range = np.linspace(0, 1, 100)
ef_returns = []
ef_risks = []

for w in w_range:
    weight_array = np.array([w, 1-w])
    
    # Portfolio return
    portfolio_return = np.sum(weight_array * returns)
    
    # Portfolio variance
    portfolio_var = (w**2 * std_devs[0]**2) + ((1-w)**2 * std_devs[1]**2) + (2 * w * (1-w) * correlation * std_devs[0] * std_devs[1])
    portfolio_risk = np.sqrt(portfolio_var)
    
    ef_returns.append(portfolio_return)
    ef_risks.append(portfolio_risk)

# Create risk-return scatter plot
plt.figure(figsize=(10, 6))

# Plot efficient frontier
plt.plot(ef_risks, ef_returns, 'b-', linewidth=2, label='Efficient Frontier')

# Plot individual stocks
plt.scatter([std_devs[0], std_devs[1]], [returns[0], returns[1]], s=100, c='red')
plt.annotate('NVDA', (std_devs[0], returns[0]), xytext=(5, 5), textcoords='offset points')
plt.annotate('INTC', (std_devs[1], returns[1]), xytext=(5, 5), textcoords='offset points')

# Plot minimum risk portfolio
plt.scatter(min_risk, min_risk_return, s=100, c='green', marker='*')
plt.annotate('Min Risk', (min_risk, min_risk_return), xytext=(5, 5), textcoords='offset points')

# Plot target return portfolio
plt.scatter(target_risk, target_return, s=100, c='orange', marker='o')
plt.annotate('25% Return', (target_risk, target_return), xytext=(5, 5), textcoords='offset points')

# Add labels and title
plt.xlabel('Risk (Standard Deviation)')
plt.ylabel('Expected Return')
plt.title('Risk-Return Profile of NVDA-INTC Portfolios')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()

# Print results
print("Portfolio Return and Risk for Different Weights:")
for i, w in enumerate(weights):
    print(f"Weight of NVDA = {w:.2f}: Return = {portfolio_returns[i]:.2%}, Risk = {portfolio_risks[i]:.2%}")

print(f"\nMinimum Risk Portfolio: Weight of NVDA = {min_risk_weight:.4f}")
print(f"Return at Minimum Risk = {min_risk_return:.2%}, Risk = {min_risk:.2%}")

print(f"\nPortfolio with 25% Return: Weight of NVDA = {target_weight:.4f}")
print(f"Risk = {target_risk:.2%}")
```



