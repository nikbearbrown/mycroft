# Chapter 7: Options and Derivatives - Cheat Sheet

## 7.1 Option Contracts and Payoff Structures

### Basic Option Types

**Call Option**: Right to **buy** the underlying asset at the strike price
**Put Option**: Right to **sell** the underlying asset at the strike price

**Key Components:**
- **Underlying Asset**: Security the option is based on (stock, ETF, index)
- **Strike Price**: Price at which option can be exercised
- **Expiration Date**: Date after which option becomes void
- **Premium**: Price paid to acquire the option
- **Exercise Style**: American (any time) or European (only at expiration)

### Option Positions

| Position | Max Gain | Max Loss | Break-even |
|----------|----------|----------|------------|
| **Long Call** | Unlimited | Premium paid | Strike + Premium |
| **Long Put** | Strike - Premium | Premium paid | Strike - Premium |
| **Short Call** | Premium received | Unlimited | Strike + Premium |
| **Short Put** | Premium received | Strike - Premium | Strike - Premium |

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
    if position.lower() == "long":
        return max(spot_price - strike_price, 0) - premium
    else:  # short position
        return min(premium, premium - (spot_price - strike_price))

def put_option_payoff(spot_price, strike_price, premium, position="long"):
    if position.lower() == "long":
        return max(strike_price - spot_price, 0) - premium
    else:  # short position
        return min(premium, premium - (strike_price - spot_price))
```

### Option Strategies

| Strategy | Components | Max Gain | Max Loss |
|----------|------------|----------|----------|
| **Covered Call** | Long stock + Short call | Strike - Stock price + Premium | Stock price - Premium |
| **Protective Put** | Long stock + Long put | Unlimited | Stock price - Strike + Premium |
| **Bull Spread** | Long call (lower strike) + Short call (higher strike) | Difference in strikes - Net premium | Net premium paid |
| **Bear Spread** | Long put (higher strike) + Short put (lower strike) | Difference in strikes - Net premium | Net premium paid |
| **Straddle** | Long call + Long put (same strike) | Unlimited | Total premium paid |

## 7.2 Binomial Option Pricing Models

### Single-Period Binomial Model

**Key Parameters:**
- **S**: Current price of underlying asset
- **u**: Up-move factor (S_up = S * u)
- **d**: Down-move factor (S_down = S * d)
- **r**: Risk-free interest rate
- **p**: Risk-neutral probability
- **Δt**: Time step

**Risk-Neutral Probability:**
```
p = (e^(r*Δt) - d) / (u - d)
```

**Option Value:**
```
Option Value = (p * Option_up + (1-p) * Option_down) * e^(-r*Δt)
```

**Python Implementation:**
```python
def single_period_binomial(S, K, r, sigma, T, option_type='call'):
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
    
    # Calculate option price
    option_price = (p * option_up + (1-p) * option_down) * np.exp(-r * T)
    
    return option_price
```

### Multi-Period Binomial Model

**Implementation Steps:**
1. Construct price tree from current time to expiration
2. Calculate option payoffs at expiration nodes
3. Work backwards through the tree, calculating option values at each node

**Python Implementation:**
```python
def multi_period_binomial(S, K, r, sigma, T, n, option_type='call', american=False):
    # Calculate parameters
    dt = T/n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1/u
    p = (np.exp(r * dt) - d) / (u - d)
    
    # Initialize price and option value arrays
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
                # For American options, check early exercise
                if option_type.lower() == 'call':
                    exercise_value = max(stock_prices[j, i] - K, 0)
                else:  # put option
                    exercise_value = max(K - stock_prices[j, i], 0)
                option_values[j, i] = max(expected_value, exercise_value)
            else:
                option_values[j, i] = expected_value
    
    # Return option price at root node
    return option_values[0, 0]
```

## 7.3 Black-Scholes Formula Implementation

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

**Formula:**
```
C + K*e^(-r*T) = P + S
```

**Python Implementation:**
```python
def put_call_parity_check(call_price, put_price, S, K, r, T):
    left_side = call_price + K * np.exp(-r * T)
    right_side = put_price + S
    
    tolerance = 0.01  # 1 cent tolerance
    parity_holds = abs(left_side - right_side) < tolerance
    
    return parity_holds, (left_side, right_side)
```

### Dividend Adjustments

**For Continuous Dividend Yield:**
Replace S with S*e^(-q*T) where q is the continuous dividend yield.

**Python Implementation:**
```python
def black_scholes_with_dividends(S, K, r, sigma, T, q, option_type='call'):
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

### Key Greeks

| Greek | Formula | Measures | Call | Put |
|-------|---------|----------|------|-----|
| **Delta (Δ)** | ∂V/∂S | Price sensitivity to underlying | N(d1) | N(d1) - 1 |
| **Gamma (Γ)** | ∂²V/∂S² | Delta sensitivity to underlying | N'(d1) / (S * σ * √T) | Same as call |
| **Theta (Θ)** | -∂V/∂T | Time decay | -(S * N'(d1) * σ) / (2 * √T) - r * K * e^(-r*T) * N(d2) | -(S * N'(d1) * σ) / (2 * √T) + r * K * e^(-r*T) * N(-d2) |
| **Vega (ν)** | ∂V/∂σ | Volatility sensitivity | S * √T * N'(d1) | Same as call |
| **Rho (ρ)** | ∂V/∂r | Interest rate sensitivity | K * T * e^(-r*T) * N(d2) | -K * T * e^(-r*T) * N(-d2) |

**Python Implementation:**
```python
def calculate_greeks(S, K, r, sigma, T, option_type='call'):
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

**Delta Hedging:**
```python
def delta_hedge_ratio(option_delta, shares_per_contract=100):
    """Calculate shares needed to delta hedge"""
    return -option_delta * shares_per_contract
```

## Common Option Strategies: Risk-Return Profiles

| Strategy | Bullish | Bearish | Market View | Max Profit | Max Loss | Time Value Impact |
|----------|---------|---------|------------|------------|----------|-------------------|
| **Long Call** | ✓ |  | Strong upside | Unlimited | Premium paid | Negative |
| **Long Put** |  | ✓ | Strong downside | Strike - Premium | Premium paid | Negative |
| **Short Call** |  | ✓ | No/slight downside | Premium received | Unlimited | Positive |
| **Short Put** | ✓ |  | No/slight upside | Premium received | Strike - Premium | Positive |
| **Bull Spread** | ✓ |  | Moderate upside | Diff in strikes - Premium | Net premium | Mixed |
| **Bear Spread** |  | ✓ | Moderate downside | Diff in strikes - Premium | Net premium | Mixed |
| **Straddle** |  |  | High volatility | Unlimited | Total premium | Negative |
| **Strangle** |  |  | High volatility | Unlimited | Total premium | Negative |
| **Iron Condor** |  |  | Low volatility | Net premium | Diff in strikes - Net premium | Positive |
| **Butterfly** |  |  | Low volatility | Diff in strikes - Net premium | Net premium | Mixed |

## Quick Reference: Option Calculations

### Moneyness

| Term | Call Option | Put Option |
|------|------------|------------|
| **In-the-Money (ITM)** | S > K | S < K |
| **At-the-Money (ATM)** | S ≈ K | S ≈ K |
| **Out-of-the-Money (OTM)** | S < K | S > K |

### Option Premium Components

**Intrinsic Value:**
- Call: max(S - K, 0)
- Put: max(K - S, 0)

**Time Value:**
- Premium - Intrinsic Value

### Implied Volatility

Solve for σ in the Black-Scholes formula using the market price:
```python
from scipy.optimize import newton

def implied_volatility(market_price, S, K, r, T, option_type='call'):
    def objective_function(sigma):
        return black_scholes(S, K, r, sigma, T, option_type) - market_price
    
    # Initial guess and bounds
    initial_guess = 0.3  # 30% volatility as starting point
    
    try:
        implied_vol = newton(objective_function, initial_guess)
        return max(0.001, implied_vol)  # Ensure positive value
    except:
        return None  # Failed to converge
```

### Early Exercise Conditions (American Options)

**Call Option:**
- Generally not optimal to exercise early (except with high dividends)

**Put Option:**
- May be optimal when deeply ITM or interest rates high
- If K > present value of expected future stock price

### Model Selection Guide

| Feature | Binomial Model | Black-Scholes |
|---------|---------------|---------------|
| **Option Type** | American/European | European |
| **Early Exercise** | Yes | No |
| **Dividends** | Discrete/Continuous | Continuous yield |
| **Implementation** | Numerical/Tree | Analytical formula |
| **Accuracy vs Steps** | Improves with more steps | N/A (exact formula) |
| **Computation Speed** | Slower | Faster |
| **Path Dependency** | Can handle | Cannot handle |

### Implied Volatility Smile/Skew

- **Volatility Smile**: Implied volatility higher for deep ITM and OTM options
- **Volatility Skew**: Implied volatility higher for OTM puts (downside protection)