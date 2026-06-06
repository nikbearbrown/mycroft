# Chapter 4 Exercises: Mutual Funds and Exchange-Traded Funds (ETFs)

## Exercise 1: Mutual Fund Share Class Analysis

**Problem:** You are a financial advisor helping a client decide between different share classes of the Oakbrook Growth Fund, which has the following structure:

- **Class A Shares**:
  - Front-end load: 5.25%
  - Annual expense ratio: 0.85%
  - Minimum investment: $2,500

- **Class B Shares**:
  - No front-end load
  - Contingent deferred sales charge (CDSC): 5% (year 1), 4% (year 2), 3% (year 3), 2% (year 4), 1% (year 5), 0% (year 6+)
  - Annual expense ratio: 1.60% (converts to Class A after 8 years)
  - Minimum investment: $2,500

- **Class C Shares**:
  - No front-end load
  - CDSC: 1% if redeemed within first year, 0% thereafter
  - Annual expense ratio: 1.60% (does not convert)
  - Minimum investment: $2,500

- **Class I Shares**:
  - No loads
  - Annual expense ratio: 0.60%
  - Minimum investment: $1,000,000

**Assumptions:**
- Investment amount: $50,000
- Expected annual return before expenses: 8%
- Investment horizon options: 3 years, 8 years, or 15 years

**Tasks:**
1. Calculate the net initial investment for each share class after accounting for front-end loads
2. Create a table showing the projected value of the investment after 3, 8, and 15 years for each share class
3. Calculate the difference in final value between the most and least expensive options at each time horizon
4. Determine the breakeven point between Class A and Class C shares
5. Provide a recommendation for which share class is most appropriate for different investment horizons

**Excel Solution:**
```excel
'Inputs
Initial_Investment = 50000
Expected_Return = 0.08

'Class A
Class_A_Front_Load = 0.0525
Class_A_Expense_Ratio = 0.0085
Class_A_Net_Investment = Initial_Investment * (1 - Class_A_Front_Load)

'Class B
Class_B_Front_Load = 0
Class_B_Expense_Ratio_Initial = 0.016
Class_B_Expense_Ratio_After_Conversion = Class_A_Expense_Ratio
Class_B_Conversion_Year = 8
Class_B_Net_Investment = Initial_Investment * (1 - Class_B_Front_Load)

'Class C
Class_C_Front_Load = 0
Class_C_Expense_Ratio = 0.016
Class_C_Net_Investment = Initial_Investment * (1 - Class_C_Front_Load)

'Class I
Class_I_Front_Load = 0
Class_I_Expense_Ratio = 0.006
Class_I_Net_Investment = Initial_Investment * (1 - Class_I_Front_Load)

'CDSC Calculation Function (helper calculation)
'This would be implemented using IF statements in Excel

'3-Year Projection
Class_A_3Year = Class_A_Net_Investment * (1 + Expected_Return - Class_A_Expense_Ratio)^3
Class_B_3Year = Class_B_Net_Investment * (1 + Expected_Return - Class_B_Expense_Ratio_Initial)^3 * (1 - 0.03) 'Including CDSC
Class_C_3Year = Class_C_Net_Investment * (1 + Expected_Return - Class_C_Expense_Ratio)^3
Class_I_3Year = Class_I_Net_Investment * (1 + Expected_Return - Class_I_Expense_Ratio)^3

'8-Year Projection
Class_A_8Year = Class_A_Net_Investment * (1 + Expected_Return - Class_A_Expense_Ratio)^8
Class_B_8Year = Class_B_Net_Investment * (1 + Expected_Return - Class_B_Expense_Ratio_Initial)^8
Class_C_8Year = Class_C_Net_Investment * (1 + Expected_Return - Class_C_Expense_Ratio)^8
Class_I_8Year = Class_I_Net_Investment * (1 + Expected_Return - Class_I_Expense_Ratio)^8

'15-Year Projection
Class_A_15Year = Class_A_Net_Investment * (1 + Expected_Return - Class_A_Expense_Ratio)^15
'For Class B, we use initial expense ratio for 8 years, then Class A expense ratio
Class_B_15Year = Class_B_Net_Investment * (1 + Expected_Return - Class_B_Expense_Ratio_Initial)^8 * (1 + Expected_Return - Class_A_Expense_Ratio)^7
Class_C_15Year = Class_C_Net_Investment * (1 + Expected_Return - Class_C_Expense_Ratio)^15
Class_I_15Year = Class_I_Net_Investment * (1 + Expected_Return - Class_I_Expense_Ratio)^15

'Difference between highest and lowest
Diff_3Year = MAX(Class_A_3Year, Class_B_3Year, Class_C_3Year, Class_I_3Year) - MIN(Class_A_3Year, Class_B_3Year, Class_C_3Year, Class_I_3Year)
Diff_8Year = MAX(Class_A_8Year, Class_B_8Year, Class_C_8Year, Class_I_8Year) - MIN(Class_A_8Year, Class_B_8Year, Class_C_8Year, Class_I_8Year)
Diff_15Year = MAX(Class_A_15Year, Class_B_15Year, Class_C_15Year, Class_I_15Year) - MIN(Class_A_15Year, Class_B_15Year, Class_C_15Year, Class_I_15Year)

'Breakeven Analysis between Class A and Class C
'This would require a Goal Seek or solver function in Excel
```

**Python Solution:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Input parameters
initial_investment = 50000
expected_return = 0.08
time_horizons = [3, 8, 15]

# Share class parameters
share_classes = {
    'Class A': {
        'front_load': 0.0525,
        'expense_ratio': 0.0085,
        'cdsc': [0] * 15,  # No CDSC for Class A
        'conversion_year': None
    },
    'Class B': {
        'front_load': 0,
        'expense_ratio': 0.016,
        'cdsc': [0.05, 0.04, 0.03, 0.02, 0.01] + [0] * 10,  # CDSC schedule
        'conversion_year': 8  # Converts to Class A after 8 years
    },
    'Class C': {
        'front_load': 0,
        'expense_ratio': 0.016,
        'cdsc': [0.01] + [0] * 14,  # 1% CDSC in first year only
        'conversion_year': None
    },
    'Class I': {
        'front_load': 0,
        'expense_ratio': 0.006,
        'cdsc': [0] * 15,  # No CDSC
        'conversion_year': None
    }
}

# Calculate net initial investment after front-end load
net_investments = {}
for class_name, params in share_classes.items():
    net_investments[class_name] = initial_investment * (1 - params['front_load'])

# Calculate projected values at different time horizons
results = pd.DataFrame(index=share_classes.keys(), columns=[f"{year}yr" for year in time_horizons])

for class_name, params in share_classes.items():
    # Initial investment after front-end load
    current_value = net_investments[class_name]
    
    # Track value over time
    for year in range(1, max(time_horizons) + 1):
        # Determine expense ratio for this year
        if params['conversion_year'] is not None and year > params['conversion_year']:
            # After conversion, use Class A expense ratio
            expense_ratio = share_classes['Class A']['expense_ratio']
        else:
            expense_ratio = params['expense_ratio']
        
        # Calculate growth for the year
        current_value *= (1 + expected_return - expense_ratio)
        
        # Record value at specified time horizons
        if year in time_horizons:
            # Apply CDSC if redeeming at this point
            redemption_value = current_value * (1 - params['cdsc'][year-1])
            results.loc[class_name, f"{year}yr"] = redemption_value

# Calculate differences
differences = {}
for year in time_horizons:
    col = f"{year}yr"
    max_val = results[col].max()
    min_val = results[col].min()
    differences[col] = max_val - min_val

# Find breakeven point between Class A and Class C
years = range(1, 21)  # Check up to 20 years
class_a_values = []
class_c_values = []

a_value = net_investments['Class A']
c_value = net_investments['Class C']

for year in years:
    a_value *= (1 + expected_return - share_classes['Class A']['expense_ratio'])
    c_value *= (1 + expected_return - share_classes['Class C']['expense_ratio'])
    
    class_a_values.append(a_value)
    class_c_values.append(c_value)

# Find the first year where Class A value exceeds Class C
breakeven_year = next((i+1 for i, (a, c) in enumerate(zip(class_a_values, class_c_values)) if a > c), None)

# Display results
print("Net Initial Investment After Front-Load:")
for class_name, net_inv in net_investments.items():
    print(f"{class_name}: ${net_inv:.2f}")

print("\nProjected Values:")
print(results.round(2))

print("\nDifference Between Highest and Lowest Values:")
for year, diff in differences.items():
    print(f"{year}: ${diff:.2f}")

print(f"\nBreakeven Point between Class A and Class C: {breakeven_year} years")

# Create recommendation based on time horizon
print("\nRecommendations:")
print(f"For short-term horizon (≤3 years): {results['3yr'].idxmax()}")
print(f"For medium-term horizon (≤8 years): {results['8yr'].idxmax()}")
print(f"For long-term horizon (≤15 years): {results['15yr'].idxmax()}")
```

## Exercise 2: ETF vs. Mutual Fund Performance Analysis

**Problem:** You're evaluating the performance of an S&P 500 index strategy implemented through three different investment vehicles:

- **Vanguard S&P 500 ETF (VOO)**:
  - Expense ratio: 0.03%
  - Trading at $440.25 (0.05% premium to NAV)
  - Average daily volume: 5 million shares
  - Bid-ask spread: $0.01 (0.002%)

- **Vanguard 500 Index Fund Admiral Shares (VFIAX)**:
  - Expense ratio: 0.04%
  - NAV: $440.00
  - Minimum investment: $3,000
  - No transaction fees on Vanguard platform

- **Fidelity S&P 500 Index Fund (FNILX)**:
  - Expense ratio: 0.00%
  - NAV: $27.50
  - Minimum investment: $0
  - No transaction fees on Fidelity platform

**Additional Information:**
- Brokerage commission for ETF: $0
- Annual account fee: $0
- Expected annual return of S&P 500 before expenses: 9%
- Tax considerations: Assume 20% long-term capital gains tax rate and 35% for ordinary income
- Dividend yield: 1.5% annually (paid quarterly)
- Your brokerage account is with Vanguard

**Tasks:**
1. Calculate the tracking error and tracking difference for each fund compared to the S&P 500 index (before taxes)
2. Calculate the after-tax return for each investment vehicle, accounting for both dividends and capital gains
3. Analyze the impact of premium/discount on ETF returns
4. Calculate the breakeven investment amount where the expense ratio difference becomes more significant than the bid-ask spread cost
5. Determine the most cost-effective option for different investment amounts: $1,000, $10,000, and $100,000

**Excel Solution:**
```excel
'Inputs
Investment_Amount_Small = 1000
Investment_Amount_Medium = 10000
Investment_Amount_Large = 100000
Expected_Return = 0.09
Dividend_Yield = 0.015
LT_Cap_Gains_Tax = 0.2
Ordinary_Income_Tax = 0.35
Investment_Period_Years = 10

'Fund Characteristics
VOO_Expense_Ratio = 0.0003
VOO_Premium = 0.0005
VOO_Bid_Ask = 0.00002
VOO_NAV = 440.00
VOO_Price = 440.25

VFIAX_Expense_Ratio = 0.0004
VFIAX_NAV = 440.00

FNILX_Expense_Ratio = 0.0000
FNILX_NAV = 27.50

'Tracking Error Calculation (annualized standard deviation of return differences)
'Assuming historical tracking error data is available:
VOO_Tracking_Error = 0.0002  'Illustrative value
VFIAX_Tracking_Error = 0.0003  'Illustrative value
FNILX_Tracking_Error = 0.0005  'Illustrative value

'Tracking Difference Calculation (return difference)
VOO_Tracking_Diff = -VOO_Expense_Ratio
VFIAX_Tracking_Diff = -VFIAX_Expense_Ratio
FNILX_Tracking_Diff = -FNILX_Expense_Ratio

'After-Tax Return Calculation (simplified approach)
'For ETF (assuming more tax-efficient)
VOO_Pre_Tax_Return = Expected_Return - VOO_Expense_Ratio
VOO_Dividend_Tax = Dividend_Yield * Ordinary_Income_Tax
VOO_Cap_Gains_Tax = (VOO_Pre_Tax_Return - Dividend_Yield) * LT_Cap_Gains_Tax * 0.8  'Assuming 20% lower turnover
VOO_After_Tax_Return = VOO_Pre_Tax_Return - VOO_Dividend_Tax - VOO_Cap_Gains_Tax

'For Mutual Funds
VFIAX_Pre_Tax_Return = Expected_Return - VFIAX_Expense_Ratio
VFIAX_Dividend_Tax = Dividend_Yield * Ordinary_Income_Tax
VFIAX_Cap_Gains_Tax = (VFIAX_Pre_Tax_Return - Dividend_Yield) * LT_Cap_Gains_Tax
VFIAX_After_Tax_Return = VFIAX_Pre_Tax_Return - VFIAX_Dividend_Tax - VFIAX_Cap_Gains_Tax

FNILX_Pre_Tax_Return = Expected_Return - FNILX_Expense_Ratio
FNILX_Dividend_Tax = Dividend_Yield * Ordinary_Income_Tax
FNILX_Cap_Gains_Tax = (FNILX_Pre_Tax_Return - Dividend_Yield) * LT_Cap_Gains_Tax
FNILX_After_Tax_Return = FNILX_Pre_Tax_Return - FNILX_Dividend_Tax - FNILX_Cap_Gains_Tax

'Impact of Premium/Discount on ETF
VOO_Premium_Impact = -VOO_Premium  'Negative impact on return

'Breakeven Calculation between VOO and VFIAX
'Where: Investment * (VFIAX_Expense_Ratio - VOO_Expense_Ratio) = VOO_Bid_Ask * Investment
Breakeven_Amount = VOO_Bid_Ask / (VFIAX_Expense_Ratio - VOO_Expense_Ratio)

'Total Cost Analysis for Different Investment Amounts
'For $1,000
VOO_Cost_Small = Investment_Amount_Small * VOO_Expense_Ratio + Investment_Amount_Small * VOO_Bid_Ask
VFIAX_Cost_Small = Investment_Amount_Small * VFIAX_Expense_Ratio
FNILX_Cost_Small = Investment_Amount_Small * FNILX_Expense_Ratio

'For $10,000
VOO_Cost_Medium = Investment_Amount_Medium * VOO_Expense_Ratio + Investment_Amount_Medium * VOO_Bid_Ask
VFIAX_Cost_Medium = Investment_Amount_Medium * VFIAX_Expense_Ratio
FNILX_Cost_Medium = Investment_Amount_Medium * FNILX_Expense_Ratio

'For $100,000
VOO_Cost_Large = Investment_Amount_Large * VOO_Expense_Ratio + Investment_Amount_Large * VOO_Bid_Ask
VFIAX_Cost_Large = Investment_Amount_Large * VFIAX_Expense_Ratio
FNILX_Cost_Large = Investment_Amount_Large * FNILX_Expense_Ratio

'10-Year Projected Value After All Costs and Taxes
VOO_Final_Small = Investment_Amount_Small * (1 + VOO_After_Tax_Return - VOO_Premium_Impact)^Investment_Period_Years
VFIAX_Final_Small = Investment_Amount_Small * (1 + VFIAX_After_Tax_Return)^Investment_Period_Years
FNILX_Final_Small = Investment_Amount_Small * (1 + FNILX_After_Tax_Return)^Investment_Period_Years

VOO_Final_Medium = Investment_Amount_Medium * (1 + VOO_After_Tax_Return - VOO_Premium_Impact)^Investment_Period_Years
VFIAX_Final_Medium = Investment_Amount_Medium * (1 + VFIAX_After_Tax_Return)^Investment_Period_Years
FNILX_Final_Medium = Investment_Amount_Medium * (1 + FNILX_After_Tax_Return)^Investment_Period_Years

VOO_Final_Large = Investment_Amount_Large * (1 + VOO_After_Tax_Return - VOO_Premium_Impact)^Investment_Period_Years
VFIAX_Final_Large = Investment_Amount_Large * (1 + VFIAX_After_Tax_Return)^Investment_Period_Years
FNILX_Final_Large = Investment_Amount_Large * (1 + FNILX_After_Tax_Return)^Investment_Period_Years
```

**Python Solution:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Input parameters
investment_amounts = {
    'Small': 1000,
    'Medium': 10000,
    'Large': 100000
}

expected_return = 0.09
dividend_yield = 0.015
lt_cap_gains_tax = 0.20
ordinary_income_tax = 0.35
investment_period = 10  # years

# Fund characteristics
funds = {
    'VOO (ETF)': {
        'expense_ratio': 0.0003,
        'premium': 0.0005,
        'bid_ask': 0.00002,
        'nav': 440.00,
        'price': 440.25,
        'tax_efficiency': 0.8  # Relative capital gains distribution (lower is better)
    },
    'VFIAX (Mutual Fund)': {
        'expense_ratio': 0.0004,
        'premium': 0,
        'bid_ask': 0,
        'nav': 440.00,
        'price': 440.00,
        'tax_efficiency': 1.0
    },
    'FNILX (Mutual Fund)': {
        'expense_ratio': 0.0000,
        'premium': 0,
        'bid_ask': 0,
        'nav': 27.50,
        'price': 27.50,
        'tax_efficiency': 1.0
    }
}

# Tracking error (illustrative values)
tracking_errors = {
    'VOO (ETF)': 0.0002,
    'VFIAX (Mutual Fund)': 0.0003,
    'FNILX (Mutual Fund)': 0.0005
}

# Calculate tracking difference
tracking_diffs = {fund: -params['expense_ratio'] for fund, params in funds.items()}

# Calculate after-tax returns
after_tax_returns = {}
for fund_name, params in funds.items():
    pre_tax_return = expected_return - params['expense_ratio']
    dividend_tax = dividend_yield * ordinary_income_tax
    cap_gains_tax = (pre_tax_return - dividend_yield) * lt_cap_gains_tax * params['tax_efficiency']
    after_tax_return = pre_tax_return - dividend_tax - cap_gains_tax
    
    # Account for premium/discount for ETFs
    premium_impact = -params['premium'] if 'ETF' in fund_name else 0
    
    after_tax_returns[fund_name] = after_tax_return - premium_impact

# Calculate breakeven amount between VOO and VFIAX
voo_expense = funds['VOO (ETF)']['expense_ratio']
vfiax_expense = funds['VFIAX (Mutual Fund)']['expense_ratio']
voo_bid_ask = funds['VOO (ETF)']['bid_ask']

breakeven_amount = voo_bid_ask / (vfiax_expense - voo_expense) if vfiax_expense > voo_expense else float('inf')

# Calculate total costs for different investment amounts
results = pd.DataFrame(index=funds.keys(), columns=investment_amounts.keys())

for amount_name, amount in investment_amounts.items():
    for fund_name, params in funds.items():
        # One-time costs
        transaction_cost = amount * params['bid_ask']
        
        # Annual costs over 10 years (simplified)
        annual_expense = amount * params['expense_ratio'] * investment_period
        
        # Total cost
        total_cost = transaction_cost + annual_expense
        
        # Project final value after costs and taxes
        final_value = amount * (1 + after_tax_returns[fund_name]) ** investment_period
        
        results.loc[fund_name, amount_name] = final_value

# Determine most cost-effective option for each investment amount
best_options = {amount: results[amount].idxmax() for amount in investment_amounts.keys()}

# Display results
print("Tracking Error and Tracking Difference:")
for fund in funds:
    print(f"{fund}: TE = {tracking_errors[fund]:.6f}, TD = {tracking_diffs[fund]:.6f}")

print("\nAfter-Tax Annual Returns:")
for fund, ret in after_tax_returns.items():
    print(f"{fund}: {ret:.4%}")

print(f"\nBreakeven Amount between VOO and VFIAX: ${breakeven_amount:.2f}")

print("\nProjected Values After 10 Years:")
print(results.round(2))

print("\nMost Cost-Effective Option:")
for amount, fund in best_options.items():
    print(f"For ${investment_amounts[amount]:,}: {fund}")
```

## Exercise 3: Fund Flow Analysis and Impact on Performance

**Problem:** You are analyzing the relationship between fund flows and performance for the Summit Global Equity Fund, a large actively managed global equity fund. You have the following quarterly data for the past 5 years:

| Quarter | AUM (millions) | Return (%) | Fund Flow (millions) | Benchmark Return (%) |
|---------|----------------|------------|----------------------|----------------------|
| Q1 2020 | $1,200 | -12.5% | -$150 | -11.2% |
| Q2 2020 | $1,150 | 18.2% | $75 | 17.5% |
| Q3 2020 | $1,450 | 6.8% | $125 | 7.2% |
| Q4 2020 | $1,650 | 9.5% | $150 | 8.8% |
| Q1 2021 | $1,950 | 5.2% | $180 | 4.9% |
| Q2 2021 | $2,250 | 4.8% | $120 | 5.3% |
| Q3 2021 | $2,450 | -2.1% | -$80 | -1.8% |
| Q4 2021 | $2,300 | 7.5% | $90 | 7.2% |
| Q1 2022 | $2,550 | -5.8% | -$200 | -4.9% |
| Q2 2022 | $2,200 | -15.2% | -$300 | -14.5% |
| Q3 2022 | $1,600 | 3.8% | -$75 | 4.2% |
| Q4 2022 | $1,550 | 8.2% | $50 | 7.8% |
| Q1 2023 | $1,720 | 6.5% | $85 | 6.2% |
| Q2 2023 | $1,900 | 4.2% | $100 | 4.5% |
| Q3 2023 | $2,070 | -3.5% | -$90 | -3.1% |
| Q4 2023 | $1,910 | 9.2% | $120 | 8.8% |
| Q1 2024 | $2,200 | 2.8% | $150 | 3.2% |
| Q2 2024 | $2,400 | 5.5% | $180 | 5.1% |
| Q3 2024 | $2,700 | -1.2% | -$50 | -0.9% |
| Q4 2024 | $2,620 | 6.8% | $90 | 6.5% |

**Tasks:**
1. Calculate quarterly flow rate as a percentage of beginning AUM
2. Calculate the fund's alpha (excess return over benchmark) for each quarter
3. Analyze the correlation between fund flows and subsequent performance
4. Calculate the impact of fund size (AUM) on alpha generation
5. Determine if there is evidence of performance chasing by investors (correlation between past returns and subsequent flows)
6. Estimate the transaction costs associated with fund flows and their impact on returns

**Excel Solution:**
```excel
'Set up data table with provided information
'Columns: Quarter, AUM, Return, Fund Flow, Benchmark Return

'Calculate Flow Rate
Flow_Rate = Fund_Flow / AUM_Beginning

'Calculate Alpha
Alpha = Return - Benchmark_Return

'Calculate Subsequent Quarter Return
'Use LEAD function in newer Excel versions or offset references

'Calculate Correlation between Flow Rate and Subsequent Return
Correlation_Flow_Subsequent_Return = CORREL(Flow_Rate_Range, Subsequent_Return_Range)

'Calculate Correlation between AUM and Alpha
Correlation_AUM_Alpha = CORREL(AUM_Range, Alpha_Range)

'Calculate Correlation between Past Return and Subsequent Flow Rate
'For performance chasing analysis
Correlation_Return_Subsequent_Flow = CORREL(Return_Range, Subsequent_Flow_Rate_Range)

'Estimate Transaction Costs
'Assuming 0.2% average cost for transactions
Transaction_Cost_Rate = 0.002
Transaction_Costs = ABS(Fund_Flow) * Transaction_Cost_Rate

'Calculate Impact on Returns
Transaction_Cost_Impact = Transaction_Costs / AUM

'Adjusted Return
Adjusted_Return = Return - Transaction_Cost_Impact

'Regression Analysis
'Use Data Analysis ToolPak or LINEST function to analyze:
'1. Alpha = β₀ + β₁ × AUM + ε
'2. Flow_Rate = β₀ + β₁ × Previous_Return + ε
```

**Python Solution:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm

# Create DataFrame from the provided data
data = {
    'Quarter': [
        'Q1 2020', 'Q2 2020', 'Q3 2020', 'Q4 2020',
        'Q1 2021', 'Q2 2021', 'Q3 2021', 'Q4 2021',
        'Q1 2022', 'Q2 2022', 'Q3 2022', 'Q4 2022',
        'Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023',
        'Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'
    ],
    'AUM': [1200, 1150, 1450, 1650, 1950, 2250, 2450, 2300, 2550, 2200, 
            1600, 1550, 1720, 1900, 2070, 1910, 2200, 2400, 2700, 2620],
    'Return': [-0.125, 0.182, 0.068, 0.095, 0.052, 0.048, -0.021, 0.075, 
               -0.058, -0.152, 0.038, 0.082, 0.065, 0.042, -0.035, 0.092, 
               0.028, 0.055, -0.012, 0.068],
    'Fund_Flow': [-150, 75, 125, 150, 180, 120, -80, 90, -200, -300, 
                 -75, 50, 85, 100, -90, 120, 150, 180, -50, 90],
    'Benchmark_Return': [-0.112, 0.175, 0.072, 0.088, 0.049, 0.053, -0.018, 0.072, 
                        -0.049, -0.145, 0.042, 0.078, 0.062, 0.045, -0.031, 0.088, 
                         0.032, 0.051, -0.009, 0.065]
}

df = pd.DataFrame(data)

# Calculate Beginning AUM (AUM before returns and flows)
df['Beginning_AUM'] = df['AUM'].shift(1)
df.loc[0, 'Beginning_AUM'] = df.loc[0, 'AUM'] / (1 + df.loc[0, 'Return']) - df.loc[0, 'Fund_Flow']

# Calculate Flow Rate
df['Flow_Rate'] = df['Fund_Flow'] / df['Beginning_AUM']

# Calculate Alpha
df['Alpha'] = df['Return'] - df['Benchmark_Return']

# Add subsequent quarter return and flow rate
df['Subsequent_Return'] = df['Return'].shift(-1)
df['Subsequent_Flow_Rate'] = df['Flow_Rate'].shift(-1)

# Estimate transaction costs (assuming 0.2% cost for transactions)
transaction_cost_rate = 0.002
df['Transaction_Costs'] = np.abs(df['Fund_Flow']) * transaction_cost_rate
df['Transaction_Cost_Impact'] = df['Transaction_Costs'] / df['Beginning_AUM']
df['Adjusted_Return'] = df['Return'] - df['Transaction_Cost_Impact']
df['Adjusted_Alpha'] = df['Adjusted_Return'] - df['Benchmark_Return']

# Analysis 1: Correlation between flow rate and subsequent performance
flow_perf_corr = df['Flow_Rate'].corr(df['Subsequent_Return'])

# Analysis 2: Correlation between AUM and alpha generation
aum_alpha_corr = df['AUM'].corr(df['Alpha'])
aum_adj_alpha_corr = df['AUM'].corr(df['Adjusted_Alpha'])

# Analysis 3: Performance chasing (correlation between past returns and subsequent flows)
perf_chase_corr = df['Return'].corr(df['Subsequent_Flow_Rate'])

# Regression Analysis 1: Impact of AUM on Alpha
X = sm.add_constant(df['AUM'])
y = df['Alpha']
model1 = sm.OLS(y, X).fit()

# Regression Analysis 2: Performance chasing
X = sm.add_constant(df['Return'])
y = df['Subsequent_Flow_Rate'].iloc[:-1]  # Remove last row which has NaN
X = X.iloc[:-1]  # Remove last row to match y
model2 = sm.OLS(y, X).fit()

# Calculate average impact of transaction costs
avg_transaction_impact = df['Transaction_Cost_Impact'].mean()
avg_alpha_reduction = df['Alpha'].mean() - df['Adjusted_Alpha'].mean()

# Display results
print("Fund Flow Analysis Results:")
print(f"1. Average Flow Rate: {df['Flow_Rate'].mean():.2%}")
print(f"2. Average Alpha: {df['Alpha'].mean():.2%}")
print(f"3. Average Adjusted Alpha (after transaction costs): {df['Adjusted_Alpha'].mean():.2%}")
print(f"4. Correlation between Flow Rate and Subsequent Return: {flow_perf_corr:.4f}")
print(f"5. Correlation between AUM and Alpha: {aum_alpha_corr:.4f}")
print(f"6. Correlation between Return and Subsequent Flow Rate: {perf_chase_corr:.4f}")
print(f"7. Average Transaction Cost Impact: {avg_transaction_impact:.2%}")
print(f"8. Average Alpha Reduction due to Transaction Costs: {avg_alpha_reduction:.2%}")

print("\nRegression Analysis: Impact of AUM on Alpha")
print(model1.summary().tables[1])

print("\nRegression Analysis: Performance Chasing")
print(model2.summary().tables[1])

# Visualizations
plt.figure(figsize=(15, 10))

# Plot 1: AUM vs Alpha
plt.subplot(2, 2, 1)
plt.scatter(df['AUM'], df['Alpha'], alpha=0.7)
plt.plot(df['AUM'], model1.predict(X), 'r--')
plt.xlabel('AUM (millions $)')
plt.ylabel('Alpha')
plt.title('Fund Size vs. Alpha Generation')
plt.grid(True, alpha=0.3)

# Plot 2: Flow Rate vs Subsequent Return
plt.subplot(2, 2, 2)
plt.scatter(df['Flow_Rate'], df['Subsequent_Return'], alpha=0.7)
plt.xlabel('Flow Rate')
plt.ylabel('Subsequent Quarter Return')
plt.title('Fund Flows vs. Subsequent Performance')
plt.grid(True, alpha=0.3)

# Plot 3: Return vs Subsequent Flow Rate
plt.subplot(2, 2, 3)
plt.scatter(df['Return'], df['Subsequent_Flow_Rate'], alpha=0.7)
plt.xlabel('Return')
plt.ylabel('Subsequent Quarter Flow Rate')
plt.title('Performance Chasing Behavior')
plt.grid(True, alpha=0.3)

# Plot 4: Transaction Cost Impact over time
plt.subplot(2, 2, 4)
plt.bar(df['Quarter'], df['Transaction_Cost_Impact'])
plt.xlabel('Quarter')
plt.ylabel('Transaction Cost Impact on Return')
plt.title('Impact of Transaction Costs')
plt.xticks(rotation=90)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('fund_flow_analysis.png')
plt.show()
```

## Exercise 4: ETF Creation/Redemption Arbitrage Analysis

**Problem:** You are a trader at an authorized participant (AP) firm responsible for maintaining efficient markets in ETFs. You're currently monitoring the iShares S&P 500 ETF (IVV) and identifying arbitrage opportunities. You have the following information:

- **Current ETF market price**: $459.75
- **Current NAV**: $458.90
- **Creation unit size**: 50,000 shares
- **Creation/redemption fee**: $3,000 per creation unit
- **Average bid-ask spread for underlying securities**: 0.03%
- **Your firm's trading costs for basket securities**: 0.02% of trade value
- **Securities lending revenue potential**: 0.05% annually for borrowed securities
- **Daily volume of IVV**: 5 million shares
- **Your firm's capital available for arbitrage**: $100 million

**Tasks:**
1. Calculate the current premium/discount of the ETF to its NAV
2. Determine if there is a profitable arbitrage opportunity through creation or redemption
3. Calculate the profit potential and break-even point for an arbitrage trade
4. Analyze how many creation/redemption units you should execute given your capital constraints
5. Calculate the impact on the ETF's premium/discount if you execute the arbitrage
6. Determine how market volatility would affect the arbitrage opportunity (scenario analysis)

**Excel Solution:**
```excel
'Inputs
ETF_Market_Price = 459.75
ETF_NAV = 458.90
Creation_Unit_Size = 50000
Creation_Fee = 3000
Bid_Ask_Spread = 0.0003
Trading_Costs = 0.0002
Securities_Lending_Revenue = 0.0005
Daily_Volume = 5000000
Available_Capital = 100000000

'Premium/Discount Calculation
Premium_Discount = (ETF_Market_Price - ETF_NAV) / ETF_NAV
Premium_Discount_Percentage = Premium_Discount * 100

'Arbitrage Analysis
Creation_Unit_NAV_Value = ETF_NAV * Creation_Unit_Size
Creation_Unit_Market_Value = ETF_Market_Price * Creation_Unit_Size

'Profit Calculation for Creation Arbitrage (buy basket, create ETF, sell ETF)
Creation_Basket_Cost = Creation_Unit_NAV_Value * (1 + Trading_Costs + Bid_Ask_Spread/2)
Creation_Fee_Cost = Creation_Fee
ETF_Sale_Proceeds = Creation_Unit_Market_Value * (1 - Trading_Costs)
Creation_Profit = ETF_Sale_Proceeds - Creation_Basket_Cost - Creation_Fee_Cost
Creation_Profit_Percentage = Creation_Profit / Creation_Basket_Cost * 100

'Profit Calculation for Redemption Arbitrage (buy ETF, redeem ETF, sell basket)
Redemption_ETF_Cost = Creation_Unit_Market_Value * (1 + Trading_Costs)
Redemption_Fee_Cost = Creation_Fee
Basket_Sale_Proceeds = Creation_Unit_NAV_Value * (1 - Trading_Costs - Bid_Ask_Spread/2)
Redemption_Profit = Basket_Sale_Proceeds - Redemption_ETF_Cost - Redemption_Fee_Cost
Redemption_Profit_Percentage = Redemption_Profit / Redemption_ETF_Cost * 100

'Determine Arbitrage Direction
Arbitrage_Direction = IF(Creation_Profit > 0, "Creation", IF(Redemption_Profit > 0, "Redemption", "No Arbitrage"))

'Maximum Units Given Capital Constraints
Max_Creation_Units = FLOOR(Available_Capital / (Creation_Unit_NAV_Value * (1 + Trading_Costs + Bid_Ask_Spread/2) + Creation_Fee), 1)
Max_Redemption_Units = FLOOR(Available_Capital / (Creation_Unit_Market_Value * (1 + Trading_Costs) + Creation_Fee), 1)

'Optimal Units Based on Profit
Optimal_Creation_Units = IF(Creation_Profit > 0, MIN(Max_Creation_Units, FLOOR(Daily_Volume/Creation_Unit_Size/2, 1)), 0)
Optimal_Redemption_Units = IF(Redemption_Profit > 0, MIN(Max_Redemption_Units, FLOOR(Daily_Volume/Creation_Unit_Size/2, 1)), 0)

'Total Profit
Total_Creation_Profit = Optimal_Creation_Units * Creation_Profit
Total_Redemption_Profit = Optimal_Redemption_Units * Redemption_Profit

'Break-Even Premium/Discount
Creation_Break_Even = (Creation_Fee / Creation_Unit_NAV_Value + Trading_Costs + Bid_Ask_Spread/2) * 100
Redemption_Break_Even = (Creation_Fee / Creation_Unit_NAV_Value + Trading_Costs + Bid_Ask_Spread/2) * 100

'Impact on Premium/Discount
Market_Value_Before = ETF_Market_Price * Daily_Volume
NAV_Value = ETF_NAV * Daily_Volume
Creation_Impact = IF(Optimal_Creation_Units > 0, Optimal_Creation_Units * Creation_Unit_Size / Daily_Volume * Premium_Discount, 0)
Redemption_Impact = IF(Optimal_Redemption_Units > 0, Optimal_Redemption_Units * Creation_Unit_Size / Daily_Volume * Premium_Discount, 0)
Expected_New_Premium_Discount = Premium_Discount - Creation_Impact - Redemption_Impact

'Scenario Analysis for Market Volatility
'Low Volatility (tighter spreads)
Low_Vol_Bid_Ask = 0.0002
Low_Vol_Creation_Profit = ETF_Market_Price * Creation_Unit_Size * (1 - Trading_Costs) - ETF_NAV * Creation_Unit_Size * (1 + Trading_Costs + Low_Vol_Bid_Ask/2) - Creation_Fee
Low_Vol_Redemption_Profit = ETF_NAV * Creation_Unit_Size * (1 - Trading_Costs - Low_Vol_Bid_Ask/2) - ETF_Market_Price * Creation_Unit_Size * (1 + Trading_Costs) - Creation_Fee

'High Volatility (wider spreads)
High_Vol_Bid_Ask = 0.0006
High_Vol_Creation_Profit = ETF_Market_Price * Creation_Unit_Size * (1 - Trading_Costs) - ETF_NAV * Creation_Unit_Size * (1 + Trading_Costs + High_Vol_Bid_Ask/2) - Creation_Fee
High_Vol_Redemption_Profit = ETF_NAV * Creation_Unit_Size * (1 - Trading_Costs - High_Vol_Bid_Ask/2) - ETF_Market_Price * Creation_Unit_Size * (1 + Trading_Costs) - Creation_Fee
```

**Python Solution:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Input parameters
etf_market_price = 459.75
etf_nav = 458.90
creation_unit_size = 50000
creation_fee = 3000
bid_ask_spread = 0.0003
trading_costs = 0.0002
securities_lending_revenue = 0.0005
daily_volume = 5000000
available_capital = 100000000

# Premium/Discount Calculation
premium_discount = (etf_market_price - etf_nav) / etf_nav
premium_discount_percentage = premium_discount * 100

# Creation Unit Values
creation_unit_nav_value = etf_nav * creation_unit_size
creation_unit_market_value = etf_market_price * creation_unit_size

# Profit Calculation for Creation Arbitrage (buy basket, create ETF, sell ETF)
creation_basket_cost = creation_unit_nav_value * (1 + trading_costs + bid_ask_spread/2)
creation_fee_cost = creation_fee
etf_sale_proceeds = creation_unit_market_value * (1 - trading_costs)
creation_profit = etf_sale_proceeds - creation_basket_cost - creation_fee_cost
creation_profit_percentage = creation_profit / creation_basket_cost * 100

# Profit Calculation for Redemption Arbitrage (buy ETF, redeem ETF, sell basket)
redemption_etf_cost = creation_unit_market_value * (1 + trading_costs)
redemption_fee_cost = creation_fee
basket_sale_proceeds = creation_unit_nav_value * (1 - trading_costs - bid_ask_spread/2)
redemption_profit = basket_sale_proceeds - redemption_etf_cost - redemption_fee_cost
redemption_profit_percentage = redemption_profit / redemption_etf_cost * 100

# Determine Arbitrage Direction
if creation_profit > 0:
    arbitrage_direction = "Creation"
elif redemption_profit > 0:
    arbitrage_direction = "Redemption"
else:
    arbitrage_direction = "No Arbitrage"

# Maximum Units Given Capital Constraints
max_creation_units = int(available_capital / (creation_unit_nav_value * (1 + trading_costs + bid_ask_spread/2) + creation_fee))
max_redemption_units = int(available_capital / (creation_unit_market_value * (1 + trading_costs) + creation_fee))

# Optimal Units Based on Profit and Market Impact
max_market_impact_units = int(daily_volume / creation_unit_size / 2)  # Limit to 50% of daily volume
optimal_creation_units = min(max_creation_units, max_market_impact_units) if creation_profit > 0 else 0
optimal_redemption_units = min(max_redemption_units, max_market_impact_units) if redemption_profit > 0 else 0

# Total Profit
total_creation_profit = optimal_creation_units * creation_profit
total_redemption_profit = optimal_redemption_units * redemption_profit

# Break-Even Premium/Discount
creation_break_even = (creation_fee / creation_unit_nav_value + trading_costs + bid_ask_spread/2) * 100
redemption_break_even = (creation_fee / creation_unit_nav_value + trading_costs + bid_ask_spread/2) * 100

# Impact on Premium/Discount
creation_impact = optimal_creation_units * creation_unit_size / daily_volume * premium_discount if optimal_creation_units > 0 else 0
redemption_impact = optimal_redemption_units * creation_unit_size / daily_volume * premium_discount if optimal_redemption_units > 0 else 0
expected_new_premium_discount = premium_discount - creation_impact - redemption_impact

# Scenario Analysis for Market Volatility
volatility_scenarios = {
    'Very Low': {'bid_ask': 0.0001, 'trading_costs': 0.0001},
    'Low': {'bid_ask': 0.0002, 'trading_costs': 0.00015},
    'Current': {'bid_ask': bid_ask_spread, 'trading_costs': trading_costs},
    'High': {'bid_ask': 0.0006, 'trading_costs': 0.0003},
    'Very High': {'bid_ask': 0.0010, 'trading_costs': 0.0004}
}

scenario_results = []

for scenario, params in volatility_scenarios.items():
    # Recalculate profits with new parameters
    scenario_bid_ask = params['bid_ask']
    scenario_trading_costs = params['trading_costs']
    
    # Creation arbitrage
    scenario_creation_basket_cost = creation_unit_nav_value * (1 + scenario_trading_costs + scenario_bid_ask/2)
    scenario_etf_sale_proceeds = creation_unit_market_value * (1 - scenario_trading_costs)
    scenario_creation_profit = scenario_etf_sale_proceeds - scenario_creation_basket_cost - creation_fee
    
    # Redemption arbitrage
    scenario_redemption_etf_cost = creation_unit_market_value * (1 + scenario_trading_costs)
    scenario_basket_sale_proceeds = creation_unit_nav_value * (1 - scenario_trading_costs - scenario_bid_ask/2)
    scenario_redemption_profit = scenario_basket_sale_proceeds - scenario_redemption_etf_cost - creation_fee
    
    # Break-even premiums
    scenario_creation_break_even = (creation_fee / creation_unit_nav_value + scenario_trading_costs + scenario_bid_ask/2) * 100
    scenario_redemption_break_even = (creation_fee / creation_unit_nav_value + scenario_trading_costs + scenario_bid_ask/2) * 100
    
    scenario_results.append({
        'Scenario': scenario,
        'Bid-Ask Spread': scenario_bid_ask * 100,
        'Trading Costs': scenario_trading_costs * 100,
        'Creation Profit': scenario_creation_profit,
        'Redemption Profit': scenario_redemption_profit,
        'Creation Break-Even (%)': scenario_creation_break_even,
        'Redemption Break-Even (%)': scenario_redemption_break_even
    })

scenario_df = pd.DataFrame(scenario_results)

# Display results
print("ETF Arbitrage Analysis")
print(f"Current Premium/Discount: {premium_discount_percentage:.4f}%")
print(f"Arbitrage Direction: {arbitrage_direction}")

print("\nCreation Arbitrage:")
print(f"Profit per Creation Unit: ${creation_profit:.2f} ({creation_profit_percentage:.4f}%)")
print(f"Break-Even Premium: {creation_break_even:.4f}%")
print(f"Maximum Creation Units (Capital Constraint): {max_creation_units}")
print(f"Optimal Creation Units: {optimal_creation_units}")
print(f"Total Creation Profit: ${total_creation_profit:.2f}")

print("\nRedemption Arbitrage:")
print(f"Profit per Redemption Unit: ${redemption_profit:.2f} ({redemption_profit_percentage:.4f}%)")
print(f"Break-Even Discount: {redemption_break_even:.4f}%")
print(f"Maximum Redemption Units (Capital Constraint): {max_redemption_units}")
print(f"Optimal Redemption Units: {optimal_redemption_units}")
print(f"Total Redemption Profit: ${total_redemption_profit:.2f}")

print(f"\nExpected New Premium/Discount after Arbitrage: {expected_new_premium_discount*100:.4f}%")

print("\nMarket Volatility Scenario Analysis:")
print(scenario_df.to_string(index=False))

# Visualization
plt.figure(figsize=(12, 8))

# Plot 1: Premium/Discount vs. Break-Even Points
plt.subplot(2, 1, 1)
plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
plt.axhline(y=premium_discount_percentage, color='blue', linestyle='-', label=f'Current Premium ({premium_discount_percentage:.4f}%)')
plt.axhline(y=creation_break_even, color='green', linestyle='--', label=f'Creation Break-Even ({creation_break_even:.4f}%)')
plt.axhline(y=-redemption_break_even, color='red', linestyle='--', label=f'Redemption Break-Even ({-redemption_break_even:.4f}%)')
plt.axhline(y=expected_new_premium_discount*100, color='purple', linestyle='-.', label=f'Expected New Premium ({expected_new_premium_discount*100:.4f}%)')
plt.ylabel('Premium/Discount (%)')
plt.title('ETF Premium/Discount and Arbitrage Break-Even Points')
plt.legend()
plt.grid(True, alpha=0.3)

# Plot 2: Volatility Impact on Arbitrage Profits
plt.subplot(2, 1, 2)
plt.plot(scenario_df['Scenario'], scenario_df['Creation Profit']/1000, marker='o', label='Creation Profit ($K)')
plt.plot(scenario_df['Scenario'], scenario_df['Redemption Profit']/1000, marker='s', label='Redemption Profit ($K)')
plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
plt.ylabel('Profit per Creation Unit ($K)')
plt.title('Impact of Market Volatility on Arbitrage Profits')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('etf_arbitrage_analysis.png')
plt.show()
```

These exercises provide a comprehensive review of the key concepts covered in Chapter 4 on Mutual Funds and ETFs. They progress from basic calculations to more complex analyses that incorporate multiple factors and real-world considerations. The exercises follow the template from the previous chapter's examples, providing both Excel and Python solutions for each problem.
