# Chapter 7 Exercises: Options and Derivatives

## Exercise 1: Option Pricing and Model Comparison

**Problem:** You are a quantitative analyst at a trading firm tasked with validating option pricing models for three popular tech stocks: Apple (AAPL), Microsoft (MSFT), and Amazon (AMZN). You need to compare the Black-Scholes model against the binomial tree model for various option scenarios.

**Current Market Data:**
- **AAPL**: Current price $205.00, Volatility 25%, Dividend yield 0.50%
- **MSFT**: Current price $425.00, Volatility 22%, Dividend yield 0.70%
- **AMZN**: Current price $185.00, Volatility 30%, Dividend yield 0.00%
- **Risk-free rate**: 3.50%

**Tasks:**
1. Calculate the prices of 3-month ATM (at-the-money) call and put options for each stock using both the Black-Scholes model and a 50-step binomial tree model
2. Calculate the prices of 6-month options with strikes at 90%, 100%, and 110% of the current price for each stock
3. Compare the pricing differences between models and explain the reasons for any discrepancies
4. Determine how the pricing differences change as time to expiration increases (analyze 1-month, 3-month, 6-month, and 12-month expirations)
5. Analyze how dividend yields affect the option pricing and the difference between models
6. For the AMZN 6-month ATM call option, show how the binomial price converges to the Black-Scholes price as the number of steps increases

**Excel Solution:**
```excel
'Inputs
AAPL_Price = 205
AAPL_Volatility = 0.25
AAPL_Dividend = 0.005

MSFT_Price = 425
MSFT_Volatility = 0.22
MSFT_Dividend = 0.007

AMZN_Price = 185
AMZN_Volatility = 0.3
AMZN_Dividend = 0

Risk_Free_Rate = 0.035

'Time periods
T_1M = 1/12
T_3M = 3/12
T_6M = 6/12
T_12M = 12/12

'Number of steps for binomial model
Steps = 50

'Black-Scholes Formula
'Calculate d1 for Black-Scholes
'=LN(S/K)+(r-q+σ^2/2)*T)/(σ*SQRT(T))

'Calculate d2 for Black-Scholes
'd1-σ*SQRT(T)

'Calculate call price
'=S*EXP(-q*T)*NORM.DIST(d1,0,1,TRUE)-K*EXP(-r*T)*NORM.DIST(d2,0,1,TRUE)

'Calculate put price
'=K*EXP(-r*T)*NORM.DIST(-d2,0,1,TRUE)-S*EXP(-q*T)*NORM.DIST(-d1,0,1,TRUE)

'Binomial Model Implementation
'u = EXP(σ*SQRT(T/n))
'd = 1/u
'p = (EXP((r-q)*T/n)-d)/(u-d)

'1. ATM options (3-month)
'AAPL
AAPL_ATM_Strike = AAPL_Price
AAPL_Call_BS_3M = [Black-Scholes calculation]
AAPL_Put_BS_3M = [Black-Scholes calculation]
AAPL_Call_Binomial_3M = [Binomial calculation]
AAPL_Put_Binomial_3M = [Binomial calculation]
AAPL_Call_Diff_3M = AAPL_Call_BS_3M - AAPL_Call_Binomial_3M
AAPL_Put_Diff_3M = AAPL_Put_BS_3M - AAPL_Put_Binomial_3M

'MSFT and AMZN calculations follow the same pattern

'2. 6-month options with different strikes
'AAPL 90%
AAPL_90_Strike = AAPL_Price * 0.9
AAPL_Call_BS_90 = [Black-Scholes calculation]
AAPL_Put_BS_90 = [Black-Scholes calculation]
AAPL_Call_Binomial_90 = [Binomial calculation]
AAPL_Put_Binomial_90 = [Binomial calculation]

'Continue for other strikes and stocks

'6. Convergence Analysis for AMZN
'Create a table with different numbers of steps: 5, 10, 20, 50, 100, 200
Steps_Array = {5, 10, 20, 50, 100, 200}
AMZN_ATM_Strike = AMZN_Price

'For each number of steps, calculate the binomial price and the difference from BS
'First row example (5 steps):
AMZN_Call_Binomial_5 = [Binomial calculation with 5 steps]
AMZN_Call_Diff_5 = AMZN_Call_BS_6M - AMZN_Call_Binomial_5
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Define the option pricing functions
def black_scholes(S, K, r, sigma, T, option_type='call', q=0):
    """
    Calculate option price using Black-Scholes formula
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    option_type (str): 'call' or 'put'
    q (float): Dividend yield (annualized)
    
    Returns:
    float: Option price
    """
    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r - q + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate option price
    if option_type.lower() == 'call':
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    
    return price

def binomial_tree(S, K, r, sigma, T, n, option_type='call', american=False, q=0):
    """
    Calculate option price using binomial tree model
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    n (int): Number of time steps
    option_type (str): 'call' or 'put'
    american (bool): True for American option, False for European
    q (float): Dividend yield (annualized)
    
    Returns:
    float: Option price
    """
    # Calculate parameters
    dt = T/n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1/u
    p = (np.exp((r-q) * dt) - d) / (u - d)
    
    # Initialize stock price and option value arrays
    stock_prices = np.zeros((n+1, n+1))
    option_values = np.zeros((n+1, n+1))
    
    # Build stock price tree
    for i in range(n+1):
        for j in range(i+1):
            stock_prices[j, i] = S * (u ** (i-j)) * (d ** j)
    
    # Calculate option values at expiration
    for j in range(n+1):
        if option_type.lower() == 'call':
            option_values[j, n] = max(stock_prices[j, n] - K, 0)
        else:  # put option
            option_values[j, n] = max(K - stock_prices[j, n], 0)
    
    # Work backwards through the tree
    for i in range(n-1, -1, -1):
        for j in range(i+1):
            # Expected option value (discounted)
            expected_value = (p * option_values[j, i+1] + 
                             (1-p) * option_values[j+1, i+1]) * np.exp(-r * dt)
            
            if american:
                # For American options, check if early exercise is optimal
                if option_type.lower() == 'call':
                    exercise_value = max(stock_prices[j, i] - K, 0)
                else:  # put option
                    exercise_value = max(K - stock_prices[j, i], 0)
                # Option value is the maximum of exercise now or hold
                option_values[j, i] = max(expected_value, exercise_value)
            else:
                # For European options, only use the expected value
                option_values[j, i] = expected_value
    
    # Return the option price at the root node
    return option_values[0, 0]

# Define market data
stocks = {
    'AAPL': {'price': 205.00, 'volatility': 0.25, 'dividend': 0.005},
    'MSFT': {'price': 425.00, 'volatility': 0.22, 'dividend': 0.007},
    'AMZN': {'price': 185.00, 'volatility': 0.30, 'dividend': 0.000}
}

risk_free_rate = 0.035
time_periods = {
    '1M': 1/12,
    '3M': 3/12,
    '6M': 6/12,
    '12M': 12/12
}
binomial_steps = 50

# Task 1: Calculate 3-month ATM option prices
results_task1 = []

for ticker, data in stocks.items():
    S = data['price']
    K = S  # ATM
    sigma = data['volatility']
    q = data['dividend']
    T = time_periods['3M']
    
    # Calculate prices using Black-Scholes
    call_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'call', q)
    put_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'put', q)
    
    # Calculate prices using Binomial Tree
    call_bin = binomial_tree(S, K, risk_free_rate, sigma, T, binomial_steps, 'call', False, q)
    put_bin = binomial_tree(S, K, risk_free_rate, sigma, T, binomial_steps, 'put', False, q)
    
    # Calculate differences
    call_diff = call_bs - call_bin
    put_diff = put_bs - put_bin
    
    results_task1.append({
        'Stock': ticker,
        'Stock Price': S,
        'Strike': K,
        'Call (BS)': call_bs,
        'Call (Binomial)': call_bin,
        'Call Difference': call_diff,
        'Put (BS)': put_bs,
        'Put (Binomial)': put_bin,
        'Put Difference': put_diff
    })

df_task1 = pd.DataFrame(results_task1)

# Task 2: Calculate 6-month options with different strikes
results_task2 = []

for ticker, data in stocks.items():
    S = data['price']
    sigma = data['volatility']
    q = data['dividend']
    T = time_periods['6M']
    
    for strike_pct in [0.9, 1.0, 1.1]:
        K = S * strike_pct
        
        # Calculate prices using Black-Scholes
        call_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'call', q)
        put_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'put', q)
        
        # Calculate prices using Binomial Tree
        call_bin = binomial_tree(S, K, risk_free_rate, sigma, T, binomial_steps, 'call', False, q)
        put_bin = binomial_tree(S, K, risk_free_rate, sigma, T, binomial_steps, 'put', False, q)
        
        # Calculate differences
        call_diff = call_bs - call_bin
        put_diff = put_bs - put_bin
        
        results_task2.append({
            'Stock': ticker,
            'Stock Price': S,
            'Strike': K,
            'Strike %': f"{strike_pct*100:.0f}%",
            'Call (BS)': call_bs,
            'Call (Binomial)': call_bin,
            'Call Difference': call_diff,
            'Put (BS)': put_bs,
            'Put (Binomial)': put_bin,
            'Put Difference': put_diff
        })

df_task2 = pd.DataFrame(results_task2)

# Task 4: Analyze how differences change with time to expiration
results_task4 = []

for ticker, data in stocks.items():
    S = data['price']
    K = S  # ATM
    sigma = data['volatility']
    q = data['dividend']
    
    for period_name, T in time_periods.items():
        # Calculate prices using Black-Scholes
        call_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'call', q)
        put_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'put', q)
        
        # Calculate prices using Binomial Tree
        call_bin = binomial_tree(S, K, risk_free_rate, sigma, T, binomial_steps, 'call', False, q)
        put_bin = binomial_tree(S, K, risk_free_rate, sigma, T, binomial_steps, 'put', False, q)
        
        # Calculate differences
        call_diff = call_bs - call_bin
        put_diff = put_bs - put_bin
        call_diff_pct = call_diff / call_bs * 100 if call_bs != 0 else 0
        put_diff_pct = put_diff / put_bs * 100 if put_bs != 0 else 0
        
        results_task4.append({
            'Stock': ticker,
            'Period': period_name,
            'Time (Years)': T,
            'Call (BS)': call_bs,
            'Call (Binomial)': call_bin,
            'Call Difference': call_diff,
            'Call Diff %': call_diff_pct,
            'Put (BS)': put_bs,
            'Put (Binomial)': put_bin,
            'Put Difference': put_diff,
            'Put Diff %': put_diff_pct
        })

df_task4 = pd.DataFrame(results_task4)

# Task 6: Convergence analysis for AMZN 6-month ATM call
results_task6 = []

S = stocks['AMZN']['price']
K = S  # ATM
sigma = stocks['AMZN']['volatility']
q = stocks['AMZN']['dividend']
T = time_periods['6M']

# Calculate Black-Scholes price
call_bs = black_scholes(S, K, risk_free_rate, sigma, T, 'call', q)

# Calculate Binomial prices with different step sizes
step_sizes = [5, 10, 20, 50, 100, 200, 500, 1000]
for n in step_sizes:
    call_bin = binomial_tree(S, K, risk_free_rate, sigma, T, n, 'call', False, q)
    diff = call_bs - call_bin
    diff_pct = diff / call_bs * 100
    
    results_task6.append({
        'Steps': n,
        'Call (BS)': call_bs,
        'Call (Binomial)': call_bin,
        'Difference': diff,
        'Difference %': diff_pct
    })

df_task6 = pd.DataFrame(results_task6)

# Create visualizations
plt.figure(figsize=(15, 10))

# Plot 1: Model differences by stock
plt.subplot(2, 2, 1)
for ticker in stocks.keys():
    data = df_task4[df_task4['Stock'] == ticker]
    plt.plot(data['Time (Years)'], data['Call Diff %'], marker='o', label=f"{ticker} Call")
    plt.plot(data['Time (Years)'], data['Put Diff %'], marker='x', linestyle='--', label=f"{ticker} Put")

plt.xlabel('Time to Expiration (Years)')
plt.ylabel('Price Difference (%)')
plt.title('Model Price Differences by Stock and Time')
plt.grid(alpha=0.3)
plt.legend()

# Plot 2: Strike price impact
plt.subplot(2, 2, 2)
for ticker in stocks.keys():
    data = df_task2[df_task2['Stock'] == ticker]
    strikes = [0.9, 1.0, 1.1]  # 90%, 100%, 110%
    call_diffs = data[data['Strike %'].isin(['90%', '100%', '110%'])]['Call Difference'].values
    put_diffs = data[data['Strike %'].isin(['90%', '100%', '110%'])]['Put Difference'].values
    
    plt.plot(strikes, call_diffs, marker='o', label=f"{ticker} Call")
    plt.plot(strikes, put_diffs, marker='x', linestyle='--', label=f"{ticker} Put")

plt.xlabel('Strike Price (% of Stock Price)')
plt.ylabel('Price Difference (BS - Binomial)')
plt.title('Impact of Strike Price on Model Differences')
plt.grid(alpha=0.3)
plt.legend()

# Plot 3: Convergence analysis
plt.subplot(2, 2, 3)
plt.plot(df_task6['Steps'], df_task6['Difference'], marker='o')
plt.axhline(y=0, color='r', linestyle='--')
plt.xscale('log')
plt.xlabel('Number of Steps (log scale)')
plt.ylabel('Price Difference (BS - Binomial)')
plt.title('Binomial Model Convergence (AMZN 6M ATM Call)')
plt.grid(alpha=0.3)

# Plot 4: Call and Put prices by time to expiration
plt.subplot(2, 2, 4)
for ticker in stocks.keys():
    data = df_task4[df_task4['Stock'] == ticker]
    plt.plot(data['Time (Years)'], data['Call (BS)'], marker='o', label=f"{ticker} Call")
    plt.plot(data['Time (Years)'], data['Put (BS)'], marker='x', linestyle='--', label=f"{ticker} Put")

plt.xlabel('Time to Expiration (Years)')
plt.ylabel('Option Price')
plt.title('Option Prices by Time to Expiration')
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('option_pricing_analysis.png')

# Print results
print("Task 1: 3-Month ATM Option Prices")
print(df_task1.to_string(index=False))

print("\nTask 2: 6-Month Options with Different Strikes")
print(df_task2.to_string(index=False))

print("\nTask 4: Impact of Time to Expiration")
print(df_task4.to_string(index=False))

print("\nTask 6: Binomial Model Convergence")
print(df_task6.to_string(index=False))
```

## Exercise 2: Option Greeks Analysis and Hedging Strategy

**Problem:** You are managing a portfolio of NVIDIA (NVDA) options and need to develop hedging strategies based on option Greeks. The current NVDA stock price is $480, and you have the following option positions:

- Long 10 NVDA 3-month call options with strike $500
- Short 5 NVDA 3-month put options with strike $450
- Long 15 NVDA 6-month call options with strike $480

Additional information:
- NVDA volatility: 40%
- Risk-free rate: 3.5%
- Dividend yield: 0.1%

**Tasks:**
1. Calculate all Greeks (Delta, Gamma, Vega, Theta, Rho) for each option position
2. Determine the overall portfolio Greeks by aggregating the individual positions
3. Design a delta-neutral hedging strategy using the underlying stock
4. Design a delta-gamma neutral hedging strategy using additional options
5. Calculate how the portfolio value would change under the following scenarios:
   - NVDA rises by 5%
   - NVDA falls by 5%
   - Volatility increases by 5 percentage points
   - Volatility decreases by 5 percentage points
   - One month passes with no change in price or volatility
6. Create a visualization showing how portfolio value changes across a range of stock prices

**Excel Solution:**
```excel
'Inputs
NVDA_Price = 480
NVDA_Volatility = 0.4
NVDA_Dividend = 0.001
Risk_Free_Rate = 0.035

'Option Positions
Call_1_Strike = 500
Call_1_Expiry = 3/12
Call_1_Quantity = 10

Put_1_Strike = 450
Put_1_Expiry = 3/12
Put_1_Quantity = -5  'Short position

Call_2_Strike = 480
Call_2_Expiry = 6/12
Call_2_Quantity = 15

'Greeks Calculation
'Call Option 1 Greeks
Call_1_Price = [Black-Scholes calculation]
Call_1_Delta = [Delta calculation]
Call_1_Gamma = [Gamma calculation]
Call_1_Vega = [Vega calculation]
Call_1_Theta = [Theta calculation]
Call_1_Rho = [Rho calculation]

'Put Option 1 Greeks
Put_1_Price = [Black-Scholes calculation]
Put_1_Delta = [Delta calculation]
Put_1_Gamma = [Gamma calculation]
Put_1_Vega = [Vega calculation]
Put_1_Theta = [Theta calculation]
Put_1_Rho = [Rho calculation]

'Call Option 2 Greeks
Call_2_Price = [Black-Scholes calculation]
Call_2_Delta = [Delta calculation]
Call_2_Gamma = [Gamma calculation]
Call_2_Vega = [Vega calculation]
Call_2_Theta = [Theta calculation]
Call_2_Rho = [Rho calculation]

'Portfolio Greeks
Portfolio_Delta = Call_1_Quantity * Call_1_Delta + Put_1_Quantity * Put_1_Delta + Call_2_Quantity * Call_2_Delta
Portfolio_Gamma = Call_1_Quantity * Call_1_Gamma + Put_1_Quantity * Put_1_Gamma + Call_2_Quantity * Call_2_Gamma
Portfolio_Vega = Call_1_Quantity * Call_1_Vega + Put_1_Quantity * Put_1_Vega + Call_2_Quantity * Call_2_Vega
Portfolio_Theta = Call_1_Quantity * Call_1_Theta + Put_1_Quantity * Put_1_Theta + Call_2_Quantity * Call_2_Theta
Portfolio_Rho = Call_1_Quantity * Call_1_Rho + Put_1_Quantity * Put_1_Rho + Call_2_Quantity * Call_2_Rho

'Delta Hedging Strategy
Shares_Needed_For_Delta_Neutral = -Portfolio_Delta
Shares_Cost = Shares_Needed_For_Delta_Neutral * NVDA_Price

'Scenario Analysis
'Scenario 1: NVDA +5%
New_Price_Up = NVDA_Price * 1.05
Call_1_Price_Up = [Black-Scholes with New_Price_Up]
Put_1_Price_Up = [Black-Scholes with New_Price_Up]
Call_2_Price_Up = [Black-Scholes with New_Price_Up]
Portfolio_Value_Up = Call_1_Quantity * Call_1_Price_Up + Put_1_Quantity * Put_1_Price_Up + Call_2_Quantity * Call_2_Price_Up
Portfolio_Change_Up = Portfolio_Value_Up - (Call_1_Quantity * Call_1_Price + Put_1_Quantity * Put_1_Price + Call_2_Quantity * Call_2_Price)

'Similar calculations for other scenarios

'Scenario 5: One month passes
'Adjust time to expiration and recalculate prices
Call_1_Expiry_Reduced = Call_1_Expiry - 1/12
Put_1_Expiry_Reduced = Put_1_Expiry - 1/12
Call_2_Expiry_Reduced = Call_2_Expiry - 1/12

Call_1_Price_Time = [Black-Scholes with reduced expiry]
Put_1_Price_Time = [Black-Scholes with reduced expiry]
Call_2_Price_Time = [Black-Scholes with reduced expiry]
Portfolio_Value_Time = Call_1_Quantity * Call_1_Price_Time + Put_1_Quantity * Put_1_Price_Time + Call_2_Quantity * Call_2_Price_Time
Portfolio_Change_Time = Portfolio_Value_Time - (Call_1_Quantity * Call_1_Price + Put_1_Quantity * Put_1_Price + Call_2_Quantity * Call_2_Price)
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Define the Greeks calculation function
def calculate_option_greeks(S, K, r, sigma, T, option_type='call', q=0):
    """
    Calculate option price and Greeks using Black-Scholes model
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    option_type (str): 'call' or 'put'
    q (float): Dividend yield (annualized)
    
    Returns:
    dict: Dictionary containing price and all Greeks
    """
    # Check for extreme values
    if T <= 0:
        if option_type.lower() == 'call':
            return {'price': max(0, S - K), 'delta': 1 if S > K else 0, 'gamma': 0, 
                    'theta': 0, 'vega': 0, 'rho': 0}
        else:
            return {'price': max(0, K - S), 'delta': -1 if S < K else 0, 'gamma': 0, 
                    'theta': 0, 'vega': 0, 'rho': 0}
    
    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r - q + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Standard normal PDF and CDF
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    N_prime_d1 = norm.pdf(d1)
    
    # Calculate option price and Greeks for call option
    if option_type.lower() == 'call':
        price = S * np.exp(-q * T) * N_d1 - K * np.exp(-r * T) * N_d2
        delta = np.exp(-q * T) * N_d1
        theta = (-np.exp(-q * T) * S * N_prime_d1 * sigma) / (2 * np.sqrt(T)) - \
                r * K * np.exp(-r * T) * N_d2 + q * S * np.exp(-q * T) * N_d1
        rho = K * T * np.exp(-r * T) * N_d2
    # Calculate option price and Greeks for put option
    else:  # put option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        delta = np.exp(-q * T) * (N_d1 - 1)
        theta = (-np.exp(-q * T) * S * N_prime_d1 * sigma) / (2 * np.sqrt(T)) + \
                r * K * np.exp(-r * T) * norm.cdf(-d2) - q * S * np.exp(-q * T) * norm.cdf(-d1)
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    
    # Greeks that are the same for calls and puts
    gamma = np.exp(-q * T) * N_prime_d1 / (S * sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * np.sqrt(T) * N_prime_d1
    
    # Convert to more standard units
    theta = theta / 365.0  # Daily theta
    vega = vega / 100.0    # Vega per 1% change in volatility
    rho = rho / 100.0      # Rho per 1% change in interest rate
    
    return {
        'price': price,
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho
    }

# Input parameters
nvda_price = 480
nvda_volatility = 0.4
nvda_dividend = 0.001
risk_free_rate = 0.035

# Option positions
option_positions = [
    {'type': 'call', 'strike': 500, 'expiry': 3/12, 'quantity': 10},
    {'type': 'put', 'strike': 450, 'expiry': 3/12, 'quantity': -5},  # Short position
    {'type': 'call', 'strike': 480, 'expiry': 6/12, 'quantity': 15}
]

# Task 1: Calculate Greeks for each position
for i, position in enumerate(option_positions):
    greeks = calculate_option_greeks(
        nvda_price, position['strike'], risk_free_rate, 
        nvda_volatility, position['expiry'], position['type'], nvda_dividend
    )
    
    # Store Greeks in the position dictionary
    for greek_name, greek_value in greeks.items():
        position[greek_name] = greek_value
    
    print(f"Position {i+1}: {position['quantity']} {position['type']} options, K=${position['strike']}, T={position['expiry']:.2f} years")
    print(f"  Price: ${position['price']:.2f}")
    print(f"  Delta: {position['delta']:.4f}")
    print(f"  Gamma: {position['gamma']:.6f}")
    print(f"  Vega: {position['vega']:.4f}")
    print(f"  Theta: ${position['theta']:.4f}/day")
    print(f"  Rho: {position['rho']:.4f}")
    print()

# Task 2: Calculate portfolio Greeks
portfolio_greeks = {greek: 0 for greek in ['price', 'delta', 'gamma', 'theta', 'vega', 'rho']}
portfolio_value = 0

for position in option_positions:
    for greek in portfolio_greeks:
        portfolio_greeks[greek] += position[greek] * position['quantity']
    portfolio_value += position['price'] * position['quantity']

print("Portfolio Greeks:")
print(f"  Total Value: ${portfolio_value:.2f}")
print(f"  Delta: {portfolio_greeks['delta']:.4f}")
print(f"  Gamma: {portfolio_greeks['gamma']:.6f}")
print(f"  Vega: {portfolio_greeks['vega']:.4f}")
print(f"  Theta: ${portfolio_greeks['theta']:.4f}/day")
print(f"  Rho: {portfolio_greeks['rho']:.4f}")
print()

# Task 3: Delta-neutral hedging strategy
shares_needed = -portfolio_greeks['delta']
shares_cost = shares_needed * nvda_price

print("Delta-Neutral Hedging Strategy:")
print(f"  Shares needed: {shares_needed:.2f} shares of NVDA")
print(f"  Cost: ${shares_cost:.2f}")
print()

# Task 4: Delta-gamma neutral hedging strategy
# We'll use an additional option to neutralize both delta and gamma
# For simplicity, we'll use a 3-month ATM put option
hedge_option_type = 'put'
hedge_option_strike = nvda_price
hedge_option_expiry = 3/12

hedge_option_greeks = calculate_option_greeks(
    nvda_price, hedge_option_strike, risk_free_rate,
    nvda_volatility, hedge_option_expiry, hedge_option_type, nvda_dividend
)

# Solve for the number of hedge options and shares to achieve delta-gamma neutrality
# We need to solve the system:
# delta_hedge * hedge_options + shares = -portfolio_delta
# gamma_hedge * hedge_options = -portfolio_gamma

hedge_options_needed = -portfolio_greeks['gamma'] / hedge_option_greeks['gamma']
hedge_shares_needed = -portfolio_greeks['delta'] - hedge_options_needed * hedge_option_greeks['delta']

print("Delta-Gamma Neutral Hedging Strategy:")
print(f"  Hedge with {hedge_options_needed:.2f} {hedge_option_type} options, K=${hedge_option_strike}, T={hedge_option_expiry:.2f} years")
print(f"  Option cost: ${hedge_options_needed * hedge_option_greeks['price']:.2f}")
print(f"  Also need {hedge_shares_needed:.2f} shares of NVDA")
print(f"  Share cost: ${hedge_shares_needed * nvda_price:.2f}")
print(f"  Total hedge cost: ${hedge_options_needed * hedge_option_greeks['price'] + hedge_shares_needed * nvda_price:.2f}")
print()

# Task 5: Scenario analysis
scenarios = [
    {'name': 'NVDA +5%', 'price_change': 0.05, 'vol_change': 0, 'time_change': 0},
    {'name': 'NVDA -5%', 'price_change': -0.05, 'vol_change': 0, 'time_change': 0},
    {'name': 'Vol +5%', 'price_change': 0, 'vol_change': 0.05, 'time_change': 0},
    {'name': 'Vol -5%', 'price_change': 0, 'vol_change': -0.05, 'time_change': 0},
    {'name': '1 Month Later', 'price_change': 0, 'vol_change': 0, 'time_change': 1/12}
]

scenario_results = []

for scenario in scenarios:
    new_price = nvda_price * (1 + scenario['price_change'])
    new_vol = nvda_volatility + scenario['vol_change']
    
    new_portfolio_value = 0
    
    for position in option_positions:
        new_expiry = position['expiry'] - scenario['time_change']
        
        # Skip expired options
        if new_expiry <= 0:
            continue
            
        new_greeks = calculate_option_greeks(
            new_price, position['strike'], risk_free_rate,
            new_vol, new_expiry, position['type'], nvda_dividend
        )
        
        new_portfolio_value += new_greeks['price'] * position['quantity']
    
    value_change = new_portfolio_value - portfolio_value
    value_change_pct = value_change / portfolio_value * 100
    
    scenario_results.append({
        'Scenario': scenario['name'],
        'New Value': new_portfolio_value,
        'Change': value_change,
        'Change %': value_change_pct
    })

scenario_df = pd.DataFrame(scenario_results)
print("Scenario Analysis:")
print(scenario_df.to_string(index=False))
print()

# Task 6: Portfolio value across stock price range
price_range = np.linspace(nvda_price * 0.8, nvda_price * 1.2, 41)  # +/- 20% in 1% increments
values = []

for price in price_range:
    portfolio_value_at_price = 0
    
    for position in option_positions:
        greeks = calculate_option_greeks(
            price, position['strike'], risk_free_rate,
            nvda_volatility, position['expiry'], position['type'], nvda_dividend
        )
        
        portfolio_value_at_price += greeks['price'] * position['quantity']
    
    values.append(portfolio_value_at_price)

# Create visualization
plt.figure(figsize=(12, 8))

# Plot portfolio value vs. stock price
plt.subplot(2, 2, 1)
plt.plot(price_range, values)
plt.axvline(x=nvda_price, color='r', linestyle='--', label='Current Price')
plt.xlabel('NVDA Stock Price ($)')
plt.ylabel('Portfolio Value ($)')
plt.title('Portfolio Value vs. Stock Price')
plt.grid(alpha=0.3)
plt.legend()

# Plot scenario analysis
plt.subplot(2, 2, 2)
plt.bar(scenario_df['Scenario'], scenario_df['Change %'])
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.ylabel('Portfolio Value Change (%)')
plt.title('Impact of Different Scenarios')
plt.xticks(rotation=45)
plt.grid(alpha=0.3)

# Plot option position values
plt.subplot(2, 2, 3)
for i, position in enumerate(option_positions):
    position_values = []
    
    for price in price_range:
        greeks = calculate_option_greeks(
            price, position['strike'], risk_free_rate,
            nvda_volatility, position['expiry'], position['type'], nvda_dividend
        )
        
        position_values.append(greeks['price'] * position['quantity'])
    
    plt.plot(price_range, position_values, label=f"Position {i+1}")

plt.axvline(x=nvda_price, color='r', linestyle='--', label='Current Price')
plt.xlabel('NVDA Stock Price ($)')
plt.ylabel('Position Value ($)')
plt.title('Individual Position Values')
plt.grid(alpha=0.3)
plt.legend()

# Plot delta and gamma profiles
plt.subplot(2, 2, 4)
deltas = []
gammas = []

for price in price_range:
    portfolio_delta = 0
    portfolio_gamma = 0
    
    for position in option_positions:
        greeks = calculate_option_greeks(
            price, position['strike'], risk_free_rate,
            nvda_volatility, position['expiry'], position['type'], nvda_dividend
        )
        
        portfolio_delta += greeks['delta'] * position['quantity']
        portfolio_gamma += greeks['gamma'] * position['quantity']
    
    deltas.append(portfolio_delta)
    gammas.append(portfolio_gamma * 100)  # Scale gamma for visualization

plt.plot(price_range, deltas, label='Delta')
plt.plot(price_range, gammas, label='Gamma (×100)')
plt.axvline(x=nvda_price, color='r', linestyle='--', label='Current Price')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.xlabel('NVDA Stock Price ($)')
plt.ylabel('Greek Value')
plt.title('Portfolio Delta and Gamma Profiles')
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('option_greeks_analysis.png')
plt.show()
```

## Exercise 3: Option Strategy Construction and Analysis

**Problem:** You are a portfolio manager who believes that Microsoft (MSFT) stock, currently trading at $410, will remain relatively stable over the next three months but might experience some increased volatility. You want to design and analyze option strategies that could profit from this market view.

**Market Data:**
- Current MSFT price: $410
- Implied volatility: 25%
- Risk-free rate: 3.5%
- Dividend yield: 0.8%
- Time frame: 3 months

**Option pricing data for 3-month options:**

| Strike | Call Price | Put Price |
|--------|------------|-----------|
| $370   | $45.78     | $4.12     |
| $380   | $37.92     | $6.14     |
| $390   | $30.64     | $8.75     |
| $400   | $23.95     | $11.94    |
| $410   | $18.03     | $15.91    |
| $420   | $13.03     | $20.79    |
| $430   | $9.07      | $26.71    |
| $440   | $6.10      | $33.63    |
| $450   | $3.99      | $41.41    |

**Tasks:**
1. Construct and analyze the following option strategies:
   a. Iron Condor (Sell $380 call, buy $370 call, sell $440 put, buy $450 put)
   b. Short Strangle (Sell $380 call, sell $440 put)
   c. Butterfly Spread (Buy $390 call, sell 2 $410 calls, buy $430 call)
   d. Calendar Spread (Sell 1-month $410 call, buy 3-month $410 call)
2. For each strategy, calculate:
   a. Maximum profit
   b. Maximum loss
   c. Break-even points
   d. Initial cost/credit
3. Create payoff diagrams for each strategy at expiration
4. Calculate the position Greeks (Delta, Gamma, Vega, Theta) for each strategy
5. Analyze how each strategy would perform under different scenarios:
   a. MSFT stays at $410
   b. MSFT rises to $430
   c. MSFT falls to $390
   d. Volatility increases by 5 percentage points
   e. Volatility decreases by 5 percentage points
6. Recommend the most appropriate strategy based on your market view

**Excel Solution:**
```excel
'Inputs
MSFT_Price = 410
MSFT_Volatility = 0.25
MSFT_Dividend = 0.008
Risk_Free_Rate = 0.035
Time_To_Expiration = 3/12

'Option Prices from the given data
Call_370 = 45.78
Call_380 = 37.92
Call_390 = 30.64
Call_400 = 23.95
Call_410 = 18.03
Call_420 = 13.03
Call_430 = 9.07
Call_440 = 6.1
Call_450 = 3.99

Put_370 = 4.12
Put_380 = 6.14
Put_390 = 8.75
Put_400 = 11.94
Put_410 = 15.91
Put_420 = 20.79
Put_430 = 26.71
Put_440 = 33.63
Put_450 = 41.41

'1-month option prices (calculated using Black-Scholes)
Call_410_1M = [Calculate using Black-Scholes]

'Strategy 1: Iron Condor
IC_Net_Credit = Call_380 - Call_370 + Put_440 - Put_450
IC_Max_Profit = IC_Net_Credit
IC_Max_Loss = 10 - IC_Net_Credit  'Width of spreads (10) minus net credit
IC_BE_Lower = 380 - IC_Net_Credit
IC_BE_Upper = 440 + IC_Net_Credit

'Strategy 2: Short Strangle
SS_Net_Credit = Call_380 + Put_440
SS_Max_Profit = SS_Net_Credit
SS_Max_Loss = "Unlimited"  'Theoretically unlimited, but can calculate for specific price move
SS_BE_Lower = 380 - SS_Net_Credit
SS_BE_Upper = 440 + SS_Net_Credit

'Strategy 3: Butterfly Spread
BF_Net_Debit = Call_390 - 2*Call_410 + Call_430
BF_Max_Profit = 20 - BF_Net_Debit  'Width between strikes (20) minus net debit
BF_Max_Loss = BF_Net_Debit
BF_BE_Lower = 390 + BF_Net_Debit
BF_BE_Upper = 430 - BF_Net_Debit

'Strategy 4: Calendar Spread
CS_Net_Debit = Call_410 - Call_410_1M
CS_Max_Profit = "Limited but variable"  'Depends on volatility and price movement
CS_Max_Loss = CS_Net_Debit
CS_BE = "Variable"  'Depends on 1-month option decay

'Create payoff tables for each strategy at different prices
'For each strategy, calculate payoff at price points from $370 to $450 in $5 increments

'Calculate Greeks for each strategy using the Black-Scholes formulas
'For example, for Iron Condor:
IC_Delta = -Delta_Call_380 + Delta_Call_370 - Delta_Put_440 + Delta_Put_450
IC_Gamma = -Gamma_Call_380 + Gamma_Call_370 - Gamma_Put_440 + Gamma_Put_450
IC_Vega = -Vega_Call_380 + Vega_Call_370 - Vega_Put_440 + Vega_Put_450
IC_Theta = -Theta_Call_380 + Theta_Call_370 - Theta_Put_440 + Theta_Put_450

'Scenario analysis for each strategy
'For each scenario, recalculate option prices and strategy values
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Define Black-Scholes function for option pricing and Greeks
def black_scholes(S, K, r, sigma, T, option_type='call', q=0):
    """
    Calculate option price using Black-Scholes formula
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    option_type (str): 'call' or 'put'
    q (float): Dividend yield (annualized)
    
    Returns:
    float: Option price
    """
    if T <= 0:
        if option_type.lower() == 'call':
            return max(0, S - K)
        else:
            return max(0, K - S)
            
    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r - q + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate option price
    if option_type.lower() == 'call':
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    
    return price

def calculate_greeks(S, K, r, sigma, T, option_type='call', q=0):
    """Calculate option Greeks using Black-Scholes model"""
    if T <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
        
    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r - q + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate PDF and CDF of standard normal distribution
    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)
    
    # Calculate Greeks
    if option_type.lower() == 'call':
        delta = np.exp(-q * T) * cdf_d1
        theta = (-np.exp(-q * T) * S * pdf_d1 * sigma) / (2 * np.sqrt(T)) - \
                r * K * np.exp(-r * T) * cdf_d2 + q * S * np.exp(-q * T) * cdf_d1
        rho = K * T * np.exp(-r * T) * cdf_d2
    else:  # put option
        delta = np.exp(-q * T) * (cdf_d1 - 1)
        theta = (-np.exp(-q * T) * S * pdf_d1 * sigma) / (2 * np.sqrt(T)) + \
                r * K * np.exp(-r * T) * norm.cdf(-d2) - q * S * np.exp(-q * T) * norm.cdf(-d1)
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    
    # Common Greeks
    gamma = np.exp(-q * T) * pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * np.sqrt(T) * pdf_d1
    
    # Convert to more standard units
    theta = theta / 365.0  # Daily theta
    vega = vega / 100.0    # Vega per 1% change in volatility
    rho = rho / 100.0      # Rho per 1% change in interest rate
    
    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho
    }

# Input parameters
msft_price = 410
msft_volatility = 0.25
msft_dividend = 0.008
risk_free_rate = 0.035
time_to_expiration_3m = 3/12
time_to_expiration_1m = 1/12

# Given option prices for 3-month options
option_prices = {
    370: {'call': 45.78, 'put': 4.12},
    380: {'call': 37.92, 'put': 6.14},
    390: {'call': 30.64, 'put': 8.75},
    400: {'call': 23.95, 'put': 11.94},
    410: {'call': 18.03, 'put': 15.91},
    420: {'call': 13.03, 'put': 20.79},
    430: {'call': 9.07, 'put': 26.71},
    440: {'call': 6.10, 'put': 33.63},
    450: {'call': 3.99, 'put': 41.41}
}

# Calculate 1-month option price for the calendar spread
call_410_1m = black_scholes(msft_price, 410, risk_free_rate, msft_volatility, time_to_expiration_1m, 'call', msft_dividend)

# Calculate Greeks for each option
option_greeks = {}

for strike in option_prices.keys():
    option_greeks[strike] = {
        'call': calculate_greeks(msft_price, strike, risk_free_rate, msft_volatility, time_to_expiration_3m, 'call', msft_dividend),
        'put': calculate_greeks(msft_price, strike, risk_free_rate, msft_volatility, time_to_expiration_3m, 'put', msft_dividend)
    }

# 1. Define the option strategies
strategies = {
    'Iron Condor': {
        'components': [
            {'type': 'call', 'strike': 380, 'position': -1},  # Sell $380 call
            {'type': 'call', 'strike': 370, 'position': 1},   # Buy $370 call
            {'type': 'put', 'strike': 440, 'position': -1},   # Sell $440 put
            {'type': 'put', 'strike': 450, 'position': 1}     # Buy $450 put
        ]
    },
    'Short Strangle': {
        'components': [
            {'type': 'call', 'strike': 380, 'position': -1},  # Sell $380 call
            {'type': 'put', 'strike': 440, 'position': -1}    # Sell $440 put
        ]
    },
    'Butterfly Spread': {
        'components': [
            {'type': 'call', 'strike': 390, 'position': 1},   # Buy $390 call
            {'type': 'call', 'strike': 410, 'position': -2},  # Sell 2 $410 calls
            {'type': 'call', 'strike': 430, 'position': 1}    # Buy $430 call
        ]
    },
    'Calendar Spread': {
        'components': [
            {'type': 'call', 'strike': 410, 'position': -1, 'expiry': time_to_expiration_1m},  # Sell 1-month $410 call
            {'type': 'call', 'strike': 410, 'position': 1, 'expiry': time_to_expiration_3m}    # Buy 3-month $410 call
        ]
    }
}

# 2. Calculate strategy metrics
for strategy_name, strategy in strategies.items():
    # Calculate initial cost/credit
    initial_value = 0
    
    for component in strategy['components']:
        strike = component['strike']
        option_type = component['type']
        position = component['position']
        
        if 'expiry' in component and component['expiry'] == time_to_expiration_1m:
            # 1-month option for calendar spread
            price = call_410_1m
        else:
            # 3-month options
            price = option_prices[strike][option_type]
        
        initial_value += position * price
    
    strategy['initial_value'] = initial_value
    
    # For display: negative value means credit (received), positive means debit (paid)
    if initial_value < 0:
        print(f"{strategy_name}: Net Credit = ${-initial_value:.2f}")
    else:
        print(f"{strategy_name}: Net Debit = ${initial_value:.2f}")
    
    # Calculate Greeks
    strategy_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
    
    for component in strategy['components']:
        strike = component['strike']
        option_type = component['type']
        position = component['position']
        
        if 'expiry' in component and component['expiry'] == time_to_expiration_1m:
            # 1-month option Greeks
            greeks = calculate_greeks(msft_price, strike, risk_free_rate, msft_volatility, time_to_expiration_1m, option_type, msft_dividend)
        else:
            # 3-month option Greeks
            greeks = option_greeks[strike][option_type]
        
        for greek in strategy_greeks:
            strategy_greeks[greek] += position * greeks[greek]
    
    strategy['greeks'] = strategy_greeks
    print(f"  Greeks: Delta={strategy_greeks['delta']:.4f}, Gamma={strategy_greeks['gamma']:.6f}, Vega={strategy_greeks['vega']:.4f}, Theta=${strategy_greeks['theta']:.4f}/day")
    
    # Calculate specific strategy metrics
    if strategy_name == 'Iron Condor':
        max_profit = -initial_value
        max_loss = 10 + initial_value  # Width of spreads (10) minus net credit
        be_lower = 380 + initial_value
        be_upper = 440 + initial_value
        
        print(f"  Max Profit: ${max_profit:.2f}")
        print(f"  Max Loss: ${max_loss:.2f}")
        print(f"  Break-even points: ${be_lower:.2f} and ${be_upper:.2f}")
        
    elif strategy_name == 'Short Strangle':
        max_profit = -initial_value
        max_loss = "Unlimited"  # Theoretically unlimited
        be_lower = 380 + initial_value
        be_upper = 440 + initial_value
        
        print(f"  Max Profit: ${max_profit:.2f}")
        print(f"  Max Loss: {max_loss}")
        print(f"  Break-even points: ${be_lower:.2f} and ${be_upper:.2f}")
        
    elif strategy_name == 'Butterfly Spread':
        max_profit = 20 - initial_value  # Width between strikes (20) minus net debit
        max_loss = initial_value
        be_lower = 390 + initial_value
        be_upper = 430 - initial_value
        
        print(f"  Max Profit: ${max_profit:.2f}")
        print(f"  Max Loss: ${max_loss:.2f}")
        print(f"  Break-even points: ${be_lower:.2f} and ${be_upper:.2f}")
        
    elif strategy_name == 'Calendar Spread':
        max_profit = "Limited but variable"  # Depends on volatility and price movement
        max_loss = initial_value
        be_point = "Variable"  # Depends on 1-month option decay
        
        print(f"  Max Profit: {max_profit}")
        print(f"  Max Loss: ${max_loss:.2f}")
        print(f"  Break-even: {be_point}")
    
    print()

# 3. Create payoff diagrams
price_range = np.arange(350, 471, 1)  # From $350 to $470 in $1 increments

# Function to calculate option payoff at expiration
def option_payoff(S, K, option_type, position):
    if option_type == 'call':
        return position * max(0, S - K)
    else:  # put
        return position * max(0, K - S)

# Calculate payoffs for each strategy
strategy_payoffs = {}

for strategy_name, strategy in strategies.items():
    payoffs = np.zeros_like(price_range, dtype=float)
    
    for component in strategy['components']:
        strike = component['strike']
        option_type = component['type']
        position = component['position']
        
        # For calendar spread, only consider the long option at 3 months
        # (short option is already expired)
        if 'expiry' in component and component['expiry'] == time_to_expiration_1m:
            continue
            
        # Calculate component payoff at each price point
        for i, price in enumerate(price_range):
            payoffs[i] += option_payoff(price, strike, option_type, position)
    
    # Adjust for initial cost/credit
    payoffs += strategy['initial_value']
    strategy_payoffs[strategy_name] = payoffs

# 5. Scenario analysis
scenarios = [
    {'name': 'Current', 'price': 410, 'vol_change': 0},
    {'name': 'MSFT +$20', 'price': 430, 'vol_change': 0},
    {'name': 'MSFT -$20', 'price': 390, 'vol_change': 0},
    {'name': 'Vol +5%', 'price': 410, 'vol_change': 0.05},
    {'name': 'Vol -5%', 'price': 410, 'vol_change': -0.05}
]

scenario_results = []

for scenario in scenarios:
    new_price = scenario['price']
    new_vol = msft_volatility + scenario['vol_change']
    
    # Calculate new option prices
    new_option_prices = {}
    for strike in option_prices.keys():
        new_option_prices[strike] = {
            'call': black_scholes(new_price, strike, risk_free_rate, new_vol, time_to_expiration_3m, 'call', msft_dividend),
            'put': black_scholes(new_price, strike, risk_free_rate, new_vol, time_to_expiration_3m, 'put', msft_dividend)
        }
    
    # Calculate new 1-month option price
    new_call_410_1m = black_scholes(new_price, 410, risk_free_rate, new_vol, time_to_expiration_1m, 'call', msft_dividend)
    
    # Calculate new strategy values
    strategy_values = {}
    
    for strategy_name, strategy in strategies.items():
        new_value = 0
        
        for component in strategy['components']:
            strike = component['strike']
            option_type = component['type']
            position = component['position']
            
            if 'expiry' in component and component['expiry'] == time_to_expiration_1m:
                # 1-month option
                new_value += position * new_call_410_1m
            else:
                # 3-month options
                new_value += position * new_option_prices[strike][option_type]
        
        # Calculate P&L
        pnl = new_value - strategy['initial_value']
        pnl_pct = pnl / -strategy['initial_value'] * 100 if strategy['initial_value'] != 0 else 0
        
        strategy_values[strategy_name] = {
            'value': new_value,