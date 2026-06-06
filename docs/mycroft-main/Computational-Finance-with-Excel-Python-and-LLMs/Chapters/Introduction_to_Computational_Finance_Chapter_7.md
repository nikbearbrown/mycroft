# Chapter 7: Options and Derivatives

## 7.1 Option Contracts and Payoff Structures

Options are financial derivatives that give buyers the right, but not the obligation, to buy or sell an underlying asset at a predetermined price (strike price) before or at expiration. These contracts provide flexibility for investors to hedge risk, generate income, or speculate on price movements.

### Basic Option Types

**Call Option**: Gives the holder the right to buy the underlying asset at the strike price.

**Put Option**: Gives the holder the right to sell the underlying asset at the strike price.

**Key Components:**
- **Underlying Asset**: The security upon which the option is based (stock, ETF, index, etc.)
- **Strike Price**: The price at which the option holder can buy/sell the underlying
- **Expiration Date**: The date after which the option becomes void
- **Premium**: The price paid to acquire the option
- **Exercise Style**: American (any time before expiration) or European (only at expiration)

### Option Positions

**Long Call**: Buying a call option
- Maximum loss: Premium paid
- Maximum gain: Unlimited as underlying price rises
- Break-even: Strike price + premium

**Long Put**: Buying a put option
- Maximum loss: Premium paid
- Maximum gain: Strike price - premium (as underlying approaches zero)
- Break-even: Strike price - premium

**Short Call**: Selling a call option
- Maximum gain: Premium received
- Maximum loss: Unlimited as underlying price rises
- Break-even: Strike price + premium

**Short Put**: Selling a put option
- Maximum gain: Premium received
- Maximum loss: Strike price - premium (as underlying approaches zero)
- Break-even: Strike price - premium

**Excel Implementation:**
```excel
'Calculate Call Option Payoff at Expiration
=MAX(UnderlyingPrice-StrikePrice,0)-Premium

'Calculate Put Option Payoff at Expiration
=MAX(StrikePrice-UnderlyingPrice,0)-Premium
```

**Python Implementation:**
```python
def call_option_payoff(spot_price, strike_price, premium, position="long"):
    """
    Calculate call option payoff at expiration
    
    Parameters:
    spot_price (float): Price of the underlying at expiration
    strike_price (float): Option strike price
    premium (float): Option premium paid/received
    position (str): "long" for buying call, "short" for selling call
    
    Returns:
    float: Payoff amount
    """
    if position.lower() == "long":
        return max(spot_price - strike_price, 0) - premium
    else:  # short position
        return min(premium, premium - (spot_price - strike_price))

def put_option_payoff(spot_price, strike_price, premium, position="long"):
    """
    Calculate put option payoff at expiration
    
    Parameters:
    spot_price (float): Price of the underlying at expiration
    strike_price (float): Option strike price
    premium (float): Option premium paid/received
    position (str): "long" for buying put, "short" for selling put
    
    Returns:
    float: Payoff amount
    """
    if position.lower() == "long":
        return max(strike_price - spot_price, 0) - premium
    else:  # short position
        return min(premium, premium - (strike_price - spot_price))
```

### Payoff Visualization

Visualizing option payoffs helps understand the risk-reward profile of different strategies.

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_option_payoffs(strike_price, premium, price_range):
    """
    Plot payoff diagrams for call and put options
    
    Parameters:
    strike_price (float): Option strike price
    premium (float): Option premium
    price_range (array): Range of underlying prices to plot
    """
    # Calculate payoffs
    long_call = [max(price - strike_price, 0) - premium for price in price_range]
    short_call = [min(premium, premium - (price - strike_price)) for price in price_range]
    long_put = [max(strike_price - price, 0) - premium for price in price_range]
    short_put = [min(premium, premium - (strike_price - price)) for price in price_range]
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Call options
    ax1.plot(price_range, long_call, 'b-', label='Long Call')
    ax1.plot(price_range, short_call, 'r-', label='Short Call')
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.axvline(x=strike_price, color='k', linestyle='--', alpha=0.3)
    ax1.set_xlabel('Underlying Price')
    ax1.set_ylabel('Profit/Loss')
    ax1.set_title('Call Option Payoffs')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Put options
    ax2.plot(price_range, long_put, 'g-', label='Long Put')
    ax2.plot(price_range, short_put, 'y-', label='Short Put')
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax2.axvline(x=strike_price, color='k', linestyle='--', alpha=0.3)
    ax2.set_xlabel('Underlying Price')
    ax2.set_ylabel('Profit/Loss')
    ax2.set_title('Put Option Payoffs')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    return fig
```

### Option Strategies

Combining multiple options creates strategies with unique risk-reward profiles.

**Covered Call**: Long stock + Short call
- Maximum gain: Strike price - stock purchase price + premium
- Maximum loss: Stock purchase price - premium (if stock price falls to zero)

**Protective Put**: Long stock + Long put
- Maximum gain: Unlimited (stock price increase - put premium)
- Maximum loss: Stock purchase price - strike price + put premium

**Bull Spread**: Long call at lower strike + Short call at higher strike
- Maximum gain: Difference in strikes - net premium paid
- Maximum loss: Net premium paid

**Bear Spread**: Long put at higher strike + Short put at lower strike
- Maximum gain: Difference in strikes - net premium paid
- Maximum loss: Net premium paid

**Straddle**: Long call + Long put (same strike and expiration)
- Maximum gain: Unlimited (stock moves significantly in either direction)
- Maximum loss: Total premium paid (if stock price equals strike at expiration)

**Python Implementation:**
```python
def calculate_strategy_payoff(spot_prices, strategy_components):
    """
    Calculate payoff for a multi-leg option strategy
    
    Parameters:
    spot_prices (array): Array of potential underlying prices
    strategy_components (list): List of dictionaries with option parameters
        Each dict should have keys: type, strike, premium, position
    
    Returns:
    array: Payoff at each spot price
    """
    payoffs = np.zeros_like(spot_prices, dtype=float)
    
    for component in strategy_components:
        option_type = component['type']
        strike = component['strike']
        premium = component['premium']
        position = component['position']
        
        # Calculate component payoff
        if option_type == 'call':
            for i, price in enumerate(spot_prices):
                payoffs[i] += call_option_payoff(price, strike, premium, position)
        elif option_type == 'put':
            for i, price in enumerate(spot_prices):
                payoffs[i] += put_option_payoff(price, strike, premium, position)
        elif option_type == 'stock':
            # For long stock: payoff = current price - purchase price
            # For short stock: payoff = purchase price - current price
            purchase_price = strike  # Using strike as purchase price
            for i, price in enumerate(spot_prices):
                if position == 'long':
                    payoffs[i] += price - purchase_price
                else:
                    payoffs[i] += purchase_price - price
    
    return payoffs
```

## 7.2 Binomial Option Pricing Models

The binomial option pricing model uses a discrete-time framework to value options by constructing a binomial tree representing the possible paths of the underlying asset price.

### Single-Period Binomial Model

In a single-period model, the underlying asset price can move up or down with specified probabilities.

**Key Parameters:**
- **S**: Current price of the underlying asset
- **u**: Up-move factor (S_up = S * u)
- **d**: Down-move factor (S_down = S * d)
- **r**: Risk-free interest rate
- **p**: Risk-neutral probability of an up-move
- **Δt**: Time step

**Risk-Neutral Probability:**
```
p = (e^(r*Δt) - d) / (u - d)
```

**Option Value:**
```
Option Value = (p * Option_up + (1-p) * Option_down) * e^(-r*Δt)
```

**Excel Implementation:**
```excel
'Calculate risk-neutral probability
=IF((UpFactor-DownFactor)=0, 0, (EXP(RiskFreeRate*TimeStep)-DownFactor)/(UpFactor-DownFactor))

'Calculate call option value in single-period model
=(RiskNeutralProb*MAX(CurrentPrice*UpFactor-StrikePrice,0) + (1-RiskNeutralProb)*MAX(CurrentPrice*DownFactor-StrikePrice,0))*EXP(-RiskFreeRate*TimeStep)
```

**Python Implementation:**
```python
def single_period_binomial(S, K, r, sigma, T, option_type='call'):
    """
    Single-period binomial option pricing model
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    option_type (str): 'call' or 'put'
    
    Returns:
    float: Option price
    """
    # Calculate up and down factors
    u = np.exp(sigma * np.sqrt(T))
    d = 1/u
    
    # Calculate risk-neutral probability
    p = (np.exp(r * T) - d) / (u - d)
    
    # Calculate stock prices at expiration
    S_up = S * u
    S_down = S * d
    
    # Calculate option payoffs at expiration
    if option_type.lower() == 'call':
        option_up = max(S_up - K, 0)
        option_down = max(S_down - K, 0)
    else:  # put option
        option_up = max(K - S_up, 0)
        option_down = max(K - S_down, 0)
    
    # Calculate option price using risk-neutral valuation
    option_price = (p * option_up + (1-p) * option_down) * np.exp(-r * T)
    
    return option_price
```

### Multi-Period Binomial Model

The multi-period model extends the single-period approach by dividing the time to expiration into multiple steps, creating a more accurate representation of price evolution.

**Implementation Steps:**
1. Construct price tree from current time to expiration
2. Calculate option payoffs at expiration nodes
3. Work backwards through the tree, calculating option values at each node

**Excel Implementation:**
(Using formulas in a structured grid representing the binomial tree)

**Python Implementation:**
```python
def multi_period_binomial(S, K, r, sigma, T, n, option_type='call', american=False):
    """
    Multi-period binomial option pricing model
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    n (int): Number of time steps
    option_type (str): 'call' or 'put'
    american (bool): True for American option, False for European
    
    Returns:
    float: Option price
    """
    # Calculate parameters
    dt = T/n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1/u
    p = (np.exp(r * dt) - d) / (u - d)
    
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
```

### Valuation Examples

**Example 1: European Call Option**
```python
# Input parameters
S = 100    # Current stock price
K = 100    # Strike price
r = 0.05   # Risk-free rate (5%)
sigma = 0.2  # Volatility (20%)
T = 1      # Time to expiration (1 year)
n = 50     # Number of time steps

# Calculate option price
call_price = multi_period_binomial(S, K, r, sigma, T, n, option_type='call', american=False)
print(f"European Call Option Price: ${call_price:.2f}")
```

**Example 2: American Put Option**
```python
# Calculate American put option price
put_price = multi_period_binomial(S, K, r, sigma, T, n, option_type='put', american=True)
print(f"American Put Option Price: ${put_price:.2f}")
```

## 7.3 Black-Scholes Formula Implementation

The Black-Scholes model provides a closed-form solution for pricing European options and serves as a foundation for modern option pricing theory.

### The Black-Scholes Formula

**Call Option Price:**
```
C = S * N(d1) - K * e^(-r*T) * N(d2)
```

**Put Option Price:**
```
P = K * e^(-r*T) * N(-d2) - S * N(-d1)
```

Where:
```
d1 = (ln(S/K) + (r + σ^2/2)*T) / (σ*√T)
d2 = d1 - σ*√T
```

And N(x) is the cumulative distribution function of the standard normal distribution.

**Excel Implementation:**
```excel
'Calculate d1
=(LN(StockPrice/StrikePrice)+(RiskFreeRate+Volatility^2/2)*TimeToExpiration)/(Volatility*SQRT(TimeToExpiration))

'Calculate d2
=d1-Volatility*SQRT(TimeToExpiration)

'Calculate call option price
=StockPrice*NORM.DIST(d1,0,1,TRUE)-StrikePrice*EXP(-RiskFreeRate*TimeToExpiration)*NORM.DIST(d2,0,1,TRUE)

'Calculate put option price
=StrikePrice*EXP(-RiskFreeRate*TimeToExpiration)*NORM.DIST(-d2,0,1,TRUE)-StockPrice*NORM.DIST(-d1,0,1,TRUE)
```

**Python Implementation:**
```python
from scipy.stats import norm

def black_scholes(S, K, r, sigma, T, option_type='call'):
    """
    Black-Scholes option pricing formula
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    option_type (str): 'call' or 'put'
    
    Returns:
    float: Option price
    """
    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate option price
    if option_type.lower() == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return price
```

### Put-Call Parity

Put-call parity is a fundamental relationship between the prices of European put and call options with the same strike and expiration.

**Formula:**
```
C + K*e^(-r*T) = P + S
```

**Python Implementation:**
```python
def put_call_parity_check(call_price, put_price, S, K, r, T):
    """
    Check if put-call parity holds
    
    Parameters:
    call_price (float): Call option price
    put_price (float): Put option price
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate
    T (float): Time to expiration (in years)
    
    Returns:
    bool: True if parity holds (within a small tolerance), False otherwise
    tuple: (left side, right side) of the parity equation
    """
    left_side = call_price + K * np.exp(-r * T)
    right_side = put_price + S
    
    # Check if parity holds within a small tolerance
    tolerance = 0.01  # 1 cent tolerance
    parity_holds = abs(left_side - right_side) < tolerance
    
    return parity_holds, (left_side, right_side)
```

### Dividend Adjustments

For stocks paying dividends, the Black-Scholes formula needs to be adjusted.

**Adjustment for Known Discrete Dividends:**
Reduce the stock price by the present value of all dividends expected before expiration.

**Adjustment for Continuous Dividend Yield:**
Replace S with S*e^(-q*T) where q is the continuous dividend yield.

**Python Implementation:**
```python
def black_scholes_with_dividends(S, K, r, sigma, T, q, option_type='call'):
    """
    Black-Scholes formula with continuous dividend yield
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    q (float): Continuous dividend yield (annualized)
    option_type (str): 'call' or 'put'
    
    Returns:
    float: Option price
    """
    # Adjust stock price for dividends
    S_adj = S * np.exp(-q * T)
    
    # Calculate d1 and d2 using adjusted stock price
    d1 = (np.log(S_adj/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate option price
    if option_type.lower() == 'call':
        price = S_adj * np.exp(q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S_adj * np.exp(q * T) * norm.cdf(-d1)
    
    return price
```

## 7.4 Option Greeks and Hedging Strategies

Option Greeks measure the sensitivity of option prices to various factors and are essential for risk management and hedging strategies.

### Key Greeks

**Delta (Δ)**: Measures the rate of change of option price with respect to the underlying asset price.
```
Δ_call = N(d1)
Δ_put = N(d1) - 1
```

**Gamma (Γ)**: Measures the rate of change of delta with respect to the underlying price.
```
Γ = N'(d1) / (S * σ * √T)
```

**Theta (Θ)**: Measures the rate of change of option price with respect to time (time decay).
```
Θ_call = -(S * N'(d1) * σ) / (2 * √T) - r * K * e^(-r*T) * N(d2)
Θ_put = -(S * N'(d1) * σ) / (2 * √T) + r * K * e^(-r*T) * N(-d2)
```

**Vega (ν)**: Measures the rate of change of option price with respect to volatility.
```
ν = S * √T * N'(d1)
```

**Rho (ρ)**: Measures the rate of change of option price with respect to the risk-free interest rate.
```
ρ_call = K * T * e^(-r*T) * N(d2)
ρ_put = -K * T * e^(-r*T) * N(-d2)
```

**Python Implementation:**
```python
def calculate_greeks(S, K, r, sigma, T, option_type='call'):
    """
    Calculate option Greeks using Black-Scholes model
    
    Parameters:
    S (float): Current stock price
    K (float): Strike price
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility (annualized)
    T (float): Time to expiration (in years)
    option_type (str): 'call' or 'put'
    
    Returns:
    dict: Dictionary containing all Greeks
    """
    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Standard normal PDF and CDF
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    N_prime_d1 = norm.pdf(d1)
    
    # Calculate Greeks
    if option_type.lower() == 'call':
        delta = N_d1
        rho = K * T * np.exp(-r * T) * N_d2
        theta = -(S * N_prime_d1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * N_d2
    else:  # put option
        delta = N_d1 - 1
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        theta = -(S * N_prime_d1 * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
    
    # Greeks that are the same for calls and puts
    gamma = N_prime_d1 / (S * sigma * np.sqrt(T))
    vega = S * np.sqrt(T) * N_prime_d1
    
    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta / 365,  # Daily theta
        'vega': vega / 100,    # Vega per 1% change in volatility
        'rho': rho / 100       # Rho per 1% change in interest rate
    }
```

### Hedging Strategies

Hedging uses options and other derivatives to reduce risk exposure in a portfolio.

**Delta Hedging**: Creating a delta-neutral position to protect against small price movements.

**Delta-Gamma Hedging**: Protecting against both small and somewhat larger price movements.

**Vega Hedging**: Reducing exposure to volatility changes.

**Python Implementation:**
```python
def delta_hedge_ratio(option_delta, shares_per_contract=100):
    """
    Calculate the number of shares needed to delta hedge an option position
    
    Parameters:
    option_delta (float): Option's delta
    shares_per_contract (int): Number of shares per option contract
    
    Returns:
    float: Number of shares to buy/sell to hedge
    """
    return -option_delta * shares_per_contract

def delta_gamma_hedge(portfolio, available_options, S):
    """
    Calculate hedge positions to neutralize both delta and gamma
    
    Parameters:
    portfolio (dict): Current positions with their deltas and gammas
    available_options (list): List of options with their deltas and gammas
    S (float): Current stock price
    
    Returns:
    dict: Hedge positions
    """
    # Calculate portfolio delta and gamma
    portfolio_delta = sum(pos['delta'] * pos['quantity'] for pos in portfolio.values())
    portfolio_gamma = sum(pos['gamma'] * pos['quantity'] for pos in portfolio.values())
    
    # Find best combination of options to neutralize delta and gamma
    # This is a simplified approach; a real implementation would use 
    # optimization techniques
    
    # For illustration, let's assume we use two options from available_options
    option1 = available_options[0]
    option2 = available_options[1]
    
    # Solve the system of equations:
    # option1['delta'] * q1 + option2['delta'] * q2 = -portfolio_delta
    # option1['gamma'] * q1 + option2['gamma'] * q2 = -portfolio_gamma
    
    determinant = option1['delta'] * option2['gamma'] - option2['delta'] * option1['gamma']
    
    if abs(determinant) < 1e-10:
        return "Cannot hedge with these options - determinant too close to zero"
    
    q1 = (-portfolio_delta * option2['gamma'] + portfolio_gamma * option2['delta']) / determinant
    q2 = (portfolio_delta * option1['gamma'] - portfolio_gamma * option1['delta']) / determinant
    
    return {
        option1['name']: q1,
        option2['name']: q2
    }
```

## Exercises

### Pricing Options on TSLA and NVDA

**Problem:** Use both the binomial tree model and Black-Scholes formula to price call and put options on TSLA and NVDA with the following parameters:
- TSLA current price: $700
- NVDA current price: $450
- Strike prices: ATM, +10%, -10%
- Time to expiration: 1 month, 3 months, 6 months
- Volatility: TSLA 45%, NVDA 35%
- Risk-free rate: 2.5%
- Dividend yield: TSLA 0%, NVDA 0.1%

**Solution:**

```python
import pandas as pd
import numpy as np
from scipy.stats import norm

# Input parameters
tickers = ['TSLA', 'NVDA']
prices = {'TSLA': 700, 'NVDA': 450}
volatilities = {'TSLA': 0.45, 'NVDA': 0.35}
dividend_yields = {'TSLA': 0.0, 'NVDA': 0.001}
r = 0.025  # Risk-free rate
strike_factors = [0.9, 1.0, 1.1]  # -10%, ATM, +10%
expirations = [1/12, 3/12, 6/12]  # 1 month, 3 months, 6 months
n_steps = 50  # Number of steps for binomial tree

# Create empty results dataframe
columns = ['Ticker', 'S', 'K', 'T', 'Sigma', 'r', 'q', 'Option Type', 
           'BS Price', 'Binomial Price', 'Difference']
results = []

# Function to calculate option prices for each parameter combination
def price_options_for_params(ticker, S, K, T, sigma, r, q):
    # Price call options
    bs_call = black_scholes_with_dividends(S, K, r, sigma, T, q, 'call')
    binomial_call = multi_period_binomial(S, K, r - q, sigma, T, n_steps, 'call', False)
    
    # Price put options
    bs_put = black_scholes_with_dividends(S, K, r, sigma, T, q, 'put')
    binomial_put = multi_period_binomial(S, K, r - q, sigma, T, n_steps, 'put', False)
    
    # Add results to the list
    results.append([ticker, S, K, T, sigma, r, q, 'Call', bs_call, binomial_call, 
                   bs_call - binomial_call])
    results.append([ticker, S, K, T, sigma, r, q, 'Put', bs_put, binomial_put, 
                   bs_put - binomial_put])
```

### Calculating and Interpreting Greeks

**Problem:** Calculate and interpret the Greeks for the following options:
1. TSLA call option, strike $700, 3 months to expiration
2. NVDA put option, strike $450, 6 months to expiration
3. How do these Greeks change as the options move from out-of-the-money to in-the-money?

**Solution:**

```python
# Function to calculate Greeks for a range of stock prices
def calculate_greeks_range(S_range, K, r, sigma, T, option_type, q=0):
    results = []
    for S in S_range:
        # Calculate d1 and d2
        d1 = (np.log(S/K) + (r - q + sigma**2/2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Standard normal PDF and CDF
        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        N_prime_d1 = norm.pdf(d1)
        
        # Calculate Greeks
        if option_type.lower() == 'call':
            delta = np.exp(-q * T) * N_d1
            theta = (-np.exp(-q * T) * S * N_prime_d1 * sigma) / (2 * np.sqrt(T)) - \
                    r * K * np.exp(-r * T) * N_d2 + q * S * np.exp(-q * T) * N_d1
            rho = K * T * np.exp(-r * T) * N_d2
        else:  # put option
            delta = np.exp(-q * T) * (N_d1 - 1)
            theta = (-np.exp(-q * T) * S * N_prime_d1 * sigma) / (2 * np.sqrt(T)) + \
                    r * K * np.exp(-r * T) * norm.cdf(-d2) - q * S * np.exp(-q * T) * norm.cdf(-d1)
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        # Greeks that are the same for calls and puts
        gamma = np.exp(-q * T) * N_prime_d1 / (S * sigma * np.sqrt(T))
        vega = S * np.exp(-q * T) * np.sqrt(T) * N_prime_d1
        
        results.append({
            'S': S,
            'price': black_scholes_with_dividends(S, K, r, sigma, T, q, option_type),
            'delta': delta,
            'gamma': gamma,
            'theta': theta / 365,  # Daily theta
            'vega': vega / 100,    # Vega per 1% change in volatility
            'rho': rho / 100       # Rho per 1% change in interest rate
        })
    
    return pd.DataFrame(results)
```

### Implementing Option Strategies

**Problem:** Implement and analyze the following option strategies for TSLA, assuming a current price of $700:
1. Bull Call Spread: Buy $700 call, sell $750 call, 3 months to expiration
2. Protective Put: Buy TSLA stock, buy $650 put, 6 months to expiration
3. Straddle: Buy $700 call and $700 put, 3 months to expiration
4. Iron Condor: Sell $680 call, buy $700 call, sell $720 put, buy $700 put, 3 months to expiration

**Solution:**

```python
# Define function to calculate strategy payoffs at expiration
def calculate_strategy_payoff(strategy_name, strategy_components, price_range):
    """
    Calculate payoff for an option strategy at expiration
    
    Parameters:
    strategy_name (str): Name of the strategy
    strategy_components (list): List of dictionaries with option parameters
    price_range (array): Range of potential stock prices at expiration
    
    Returns:
    DataFrame: Payoff at each stock price
    """
    payoffs = np.zeros_like(price_range, dtype=float)
    
    for component in strategy_components:
        option_type = component.get('type')
        strike = component.get('strike', 0)
        premium = component.get('premium', 0)
        position = component.get('position', 'long')
        
        # Calculate component payoff
        if option_type == 'call':
            for i, price in enumerate(price_range):
                if position == 'long':
                    payoffs[i] += max(price - strike, 0) - premium
                else:  # short position
                    payoffs[i] += min(premium, premium - (price - strike))
        elif option_type == 'put':
            for i, price in enumerate(price_range):
                if position == 'long':
                    payoffs[i] += max(strike - price, 0) - premium
                else:  # short position
                    payoffs[i] += min(premium, premium - (strike - price))
        elif option_type == 'stock':
            purchase_price = strike  # Using strike as purchase price
            for i, price in enumerate(price_range):
                if position == 'long':
                    payoffs[i] += price - purchase_price
                else:  # short position
                    payoffs[i] += purchase_price - price
    
    return pd.DataFrame({
        'Stock Price': price_range,
        'Payoff': payoffs,
        'Strategy': [strategy_name] * len(price_range)
    })
```

### Sensitivity Analysis with Different Methods

**Problem:** Conduct a sensitivity analysis of option prices using different methods and parameters:
1. Compare binomial tree results with different numbers of steps (10, 50, 100, 200)
2. Analyze how volatility impacts option prices and Greeks
3. Compare American vs. European put options with the binomial model
4. Explore the impact of interest rate changes on option prices

**Solution:**

```python
# 1. Compare binomial tree results with different numbers of steps
def binomial_convergence_analysis(S, K, r, sigma, T, option_type='call', american=False):
    """Analyze convergence of binomial model with increasing steps"""
    steps_list = [5, 10, 20, 50, 100, 200, 500]
    results = []
    
    # Calculate Black-Scholes price for comparison (only valid for European options)
    bs_price = black_scholes(S, K, r, sigma, T, option_type)
    
    for n in steps_list:
        binomial_price = multi_period_binomial(S, K, r, sigma, T, n, option_type, american)
        results.append({
            'Steps': n,
            'Binomial Price': binomial_price,
            'BS Price': bs_price,
            'Difference': binomial_price - bs_price
        })
    
    return pd.DataFrame(results)

# 3. Compare American vs. European put options
def american_european_comparison(S, K, r, sigma, T_range, n=100):
    """Compare American and European put option prices across expirations"""
    results = []
    
    for T in T_range:
        euro_price = multi_period_binomial(S, K, r, sigma, T, n, 'put', False)
        amer_price = multi_period_binomial(S, K, r, sigma, T, n, 'put', True)
        bs_price = black_scholes(S, K, r, sigma, T, 'put')
        
        results.append({
            'Time to Expiration': T,
            'European Put (Binomial)': euro_price,
            'American Put (Binomial)': amer_price,
            'European Put (BS)': bs_price,
            'Early Exercise Premium': amer_price - euro_price
        })
    
    return pd.DataFrame(results)

# 4. Interest rate sensitivity
def interest_rate_sensitivity(S, K, r_range, sigma, T, option_type='call'):
    """Analyze sensitivity to interest rate changes"""
    results = []
    
    for r in r_range:
        price = black_scholes(S, K, r, sigma, T, option_type)
        greeks = calculate_greeks(S, K, r, sigma, T, option_type)
        
        results.append({
            'Interest Rate': r,
            'Option Price': price,
            'Delta': greeks['delta'],
            'Gamma': greeks['gamma'],
            'Theta': greeks['theta'],
            'Vega': greeks['vega'],
            'Rho': greeks['rho']
        })
    
    return pd.DataFrame(results)
```

This chapter has covered the fundamental concepts of options and derivatives, including contract specifications, pricing models (binomial and Black-Scholes), Greeks, and hedging strategies. The implementations in Excel and Python, along with the exercises, provide practical tools for option valuation and risk management in real-world scenarios.

