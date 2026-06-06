# Chapter 3: Equity Securities and Fixed Income - Practice Exercises

## Section 3.1: Common and Preferred Stock Characteristics

### Exercise 1: Common Stock Valuation Metrics
**Problem:** Calculate the following metrics for Company XYZ:
- Current stock price: $78.50
- Earnings per share (EPS): $3.92
- Annual dividend per share: $1.56
- Shares outstanding: 420 million

**Tasks:**
1. Calculate the P/E ratio
2. Calculate the dividend yield
3. Calculate the market capitalization
4. If the industry average P/E ratio is 20, is XYZ stock relatively overvalued or undervalued based solely on P/E?

**Equations:**
- P/E Ratio = Price per Share ÷ Earnings per Share
- Dividend Yield = (Annual Dividend per Share ÷ Price per Share) × 100%
- Market Capitalization = Price per Share × Shares Outstanding

**Excel Implementation:**
```excel
# P/E Ratio
=78.50/3.92  'Result: 20.03

# Dividend Yield
=1.56/78.50*100  'Result: 1.99%

# Market Capitalization (in billions)
=78.50*420000000/1000000000  'Result: 32.97
```

**Python Implementation:**
```python
# Input values
price = 78.50
eps = 3.92
annual_dividend = 1.56
shares_outstanding = 420000000

# Calculate metrics
pe_ratio = price / eps
dividend_yield = (annual_dividend / price) * 100
market_cap = price * shares_outstanding / 1000000000  # In billions

# Display results
print(f"P/E Ratio: {pe_ratio:.2f}")
print(f"Dividend Yield: {dividend_yield:.2f}%")
print(f"Market Cap: ${market_cap:.2f} billion")
print(f"Valuation status: {'Fairly valued' if 19.5 <= pe_ratio <= 20.5 else 'Overvalued' if pe_ratio > 20.5 else 'Undervalued'}")
```

### Exercise 2: Preferred Stock Analysis
**Problem:** ABC Corporation has issued preferred stock with the following characteristics:
- Par value: $100
- Annual dividend: $6.50 (6.5% of par)
- Current market price: $92.75
- Call price: $105 (callable in 3 years)
- Current market interest rate: 7.2%

**Tasks:**
1. Calculate the current yield of the preferred stock
2. Calculate the yield to call
3. Calculate the theoretical value of the preferred stock using the perpetuity model
4. Would you recommend purchasing this preferred stock? Why or why not?

**Equations:**
- Current Yield = Annual Dividend ÷ Current Market Price
- Yield to Call (approximate) = [(Call Price - Current Price) ÷ Years to Call + Annual Dividend] ÷ [(Call Price + Current Price) ÷ 2]
- Theoretical Value (Perpetuity Model) = Annual Dividend ÷ Required Return Rate

**Excel Implementation:**
```excel
# Current yield
=6.50/92.75  'Result: 0.0701 or 7.01%

# Yield to call (approximation)
=((105-92.75)/3+6.50)/((105+92.75)/2)  'Result: 0.0841 or 8.41%

# Theoretical value using perpetuity model
=6.50/0.072  'Result: 90.28
```

**Python Implementation:**
```python
def preferred_stock_value(dividend, required_return):
    """Calculate the value of a preferred stock using the perpetuity model"""
    return dividend / required_return

def yield_to_call(price, dividend, call_price, years_to_call):
    """Calculate approximate yield to call"""
    annual_gain = (call_price - price) / years_to_call
    average_investment = (call_price + price) / 2
    return (annual_gain + dividend) / average_investment

# Input values
par_value = 100
annual_dividend = 6.50
market_price = 92.75
call_price = 105
years_to_call = 3
market_rate = 0.072

# Calculate metrics
current_yield = annual_dividend / market_price
ytc = yield_to_call(market_price, annual_dividend, call_price, years_to_call)
theoretical_value = preferred_stock_value(annual_dividend, market_rate)

# Display results
print(f"Current Yield: {current_yield:.2%}")
print(f"Yield to Call: {ytc:.2%}")
print(f"Theoretical Value: ${theoretical_value:.2f}")
print(f"Recommendation: {'Consider purchase' if ytc > market_rate else 'Look elsewhere'}")
```

### Exercise 3: Common vs. Preferred Stock Comparison
**Problem:** Tech Innovations Inc. has both common and preferred stock outstanding. Compare the two securities:

**Common Stock:**
- Current price: $145.30
- EPS: $5.20
- Annual dividend: $2.25
- Beta: 1.35

**Preferred Stock:**
- Par value: $100
- Current price: $98.50
- Annual dividend: $6.25
- Callable at $102 in 2 years

**Equations:**
- Common Stock Dividend Yield = Annual Dividend ÷ Current Price
- Preferred Stock Dividend Yield = Annual Dividend ÷ Current Price
- Preferred Yield to Call = [(Call Price - Current Price) ÷ Years to Call + Annual Dividend] ÷ [(Call Price + Current Price) ÷ 2]

**Excel Implementation:**
```excel
# Common stock dividend yield
=2.25/145.30  'Result: 0.0155 or 1.55%

# Preferred stock dividend yield
=6.25/98.50  'Result: 0.0635 or 6.35%

# Preferred stock yield to call
=((102-98.50)/2+6.25)/((102+98.50)/2)  'Result: 0.0686 or 6.86%
```

**Python Implementation:**
```python
# Input values
# Common stock
common_price = 145.30
common_eps = 5.20
common_dividend = 2.25
common_beta = 1.35

# Preferred stock
preferred_par = 100
preferred_price = 98.50
preferred_dividend = 6.25
preferred_call_price = 102
preferred_call_years = 2

# Calculate yields
common_dividend_yield = common_dividend / common_price
preferred_dividend_yield = preferred_dividend / preferred_price

# Calculate yield to call for preferred
preferred_ytc = ((preferred_call_price - preferred_price) / preferred_call_years + preferred_dividend) / ((preferred_call_price + preferred_price) / 2)

# Display results
print(f"Common Stock Dividend Yield: {common_dividend_yield:.2%}")
print(f"Preferred Stock Dividend Yield: {preferred_dividend_yield:.2%}")
print(f"Preferred Stock Yield to Call: {preferred_ytc:.2%}")
```

## Section 3.2: Equity Valuation Approaches

### Exercise 4: Dividend Discount Model (Gordon Growth Model)
**Problem:** You are evaluating shares of MegaCorp, which has the following characteristics:
- Current annual dividend (D₀): $3.50
- Expected dividend growth rate: 5.2% per year
- Required rate of return: 9.8%

**Tasks:**
1. Calculate the expected dividend for next year (D₁)
2. Calculate the stock's intrinsic value using the Gordon Growth Model
3. If the current market price is $84.25, is the stock undervalued or overvalued?
4. What happens to the valuation if the required rate of return increases to 11%?

**Equations:**
- Next Year's Dividend (D₁) = Current Dividend (D₀) × (1 + Growth Rate)
- Gordon Growth Model: P₀ = D₁ ÷ (r - g)
  - Where: P₀ = Current Stock Price, D₁ = Next Year's Dividend, r = Required Return Rate, g = Growth Rate

**Excel Implementation:**
```excel
# Expected dividend for next year (D₁)
=3.50*(1+0.052)  'Result: $3.682

# Intrinsic value using Gordon Growth Model
=3.682/(0.098-0.052)  'Result: $80.04

# Valuation status
="Overvalued"  'Since $84.25 > $80.04

# New valuation with 11% required return
=3.682/(0.11-0.052)  'Result: $63.48
```

**Python Implementation:**
```python
def gordon_growth_model(next_dividend, required_return, growth_rate):
    """Calculate stock price using the Gordon Growth Model"""
    if growth_rate >= required_return:
        return "Invalid: Growth rate must be less than required return"
    return next_dividend / (required_return - growth_rate)

# Input values
current_dividend = 3.50
growth_rate = 0.052
required_return = 0.098
current_price = 84.25

# Calculate expected dividend for next year
next_dividend = current_dividend * (1 + growth_rate)

# Calculate intrinsic value
intrinsic_value = gordon_growth_model(next_dividend, required_return, growth_rate)

# Calculate with higher required return
new_required_return = 0.11
new_intrinsic_value = gordon_growth_model(next_dividend, new_required_return, growth_rate)

# Display results
print(f"Expected Dividend (D₁): ${next_dividend:.2f}")
print(f"Intrinsic Value: ${intrinsic_value:.2f}")
print(f"Valuation Status: {'Undervalued' if intrinsic_value > current_price else 'Overvalued'}")
print(f"New Intrinsic Value (11% required return): ${new_intrinsic_value:.2f}")
```

### Exercise 5: Two-Stage Dividend Discount Model
**Problem:** TechGrowth Inc. is expected to experience high growth over the next 5 years before settling into a stable growth phase. You have the following information:
- Current annual dividend (D₀): $1.25
- Initial growth rate (years 1-5): 20% per year
- Long-term growth rate (after year 5): 3.5% per year
- Required rate of return: 10%

**Tasks:**
1. Calculate the dividends for years 1 through 6
2. Calculate the present value of dividends during the high-growth phase
3. Calculate the terminal value at the end of year 5
4. Calculate the stock's intrinsic value today

**Equations:**
- Dividend in Year t = Previous Year's Dividend × (1 + Growth Rate)
- Present Value of Dividend = Dividend ÷ (1 + Required Return)^Year
- Terminal Value = D₆ ÷ (r - g)
  - Where: D₆ = Year 6 Dividend, r = Required Return, g = Long-term Growth Rate
- Present Value of Terminal Value = Terminal Value ÷ (1 + Required Return)^5
- Stock's Intrinsic Value = Sum of PV of Dividends + PV of Terminal Value

**Excel Implementation:**
```excel
# Dividends for years 1-6
# Year 1
=1.25*(1+0.2)  'Result: $1.50
# Year 2
=1.50*(1+0.2)  'Result: $1.80
# Year 3
=1.80*(1+0.2)  'Result: $2.16
# Year 4
=2.16*(1+0.2)  'Result: $2.59
# Year 5
=2.59*(1+0.2)  'Result: $3.11
# Year 6 (first year of stable growth)
=3.11*(1+0.035)  'Result: $3.22

# PV of dividends during high-growth phase
=1.50/(1+0.1)^1 + 1.80/(1+0.1)^2 + 2.16/(1+0.1)^3 + 2.59/(1+0.1)^4 + 3.11/(1+0.1)^5
'Result: $8.32

# Terminal value at end of year 5
=3.22/(0.1-0.035)  'Result: $49.54

# PV of terminal value
=49.54/(1+0.1)^5  'Result: $30.75

# Stock's intrinsic value
=8.32+30.75  'Result: $39.07
```

**Python Implementation:**
```python
def two_stage_ddm(current_dividend, high_growth_rate, stable_growth_rate, 
                 required_return, high_growth_years):
    """Calculate stock price using a two-stage dividend discount model"""
    # Calculate present value of dividends during high-growth phase
    pv_high_growth = 0
    dividend = current_dividend
    
    dividends = []
    
    for year in range(1, high_growth_years + 1):
        dividend *= (1 + high_growth_rate)
        dividends.append(dividend)
        pv_high_growth += dividend / (1 + required_return) ** year
    
    # Calculate terminal value at end of high growth phase
    last_dividend = dividends[-1]
    next_dividend = last_dividend * (1 + stable_growth_rate)
    terminal_value = next_dividend / (required_return - stable_growth_rate)
    
    # Calculate present value of terminal value
    pv_terminal_value = terminal_value / (1 + required_return) ** high_growth_years
    
    # Total stock value
    return dividends, pv_high_growth, terminal_value, pv_terminal_value, pv_high_growth + pv_terminal_value

# Input values
current_dividend = 1.25
high_growth_rate = 0.20
stable_growth_rate = 0.035
required_return = 0.10
high_growth_years = 5

# Calculate values
dividends, pv_high_growth, terminal_value, pv_terminal_value, intrinsic_value = two_stage_ddm(
    current_dividend, high_growth_rate, stable_growth_rate, required_return, high_growth_years)

# Display results
print("Dividends for years 1-6:")
for i, div in enumerate(dividends):
    print(f"Year {i+1}: ${div:.2f}")
print(f"Year 6: ${dividends[-1] * (1 + stable_growth_rate):.2f}")
print(f"PV of High-Growth Dividends: ${pv_high_growth:.2f}")
print(f"Terminal Value: ${terminal_value:.2f}")
print(f"PV of Terminal Value: ${pv_terminal_value:.2f}")
print(f"Stock's Intrinsic Value: ${intrinsic_value:.2f}")
```

### Exercise 6: Discounted Cash Flow (DCF) Model
**Problem:** You are evaluating Innovation Corp. using a DCF model. You have projected the following free cash flows (in millions):
- Year 1: $85
- Year 2: $92
- Year 3: $102
- Year 4: $110
- Year 5: $120

Additional information:
- Terminal growth rate: 3%
- Weighted average cost of capital (WACC): 9%
- Net debt: $350 million
- Shares outstanding: 50 million

**Tasks:**
1. Calculate the present value of explicit period cash flows
2. Calculate the terminal value using the perpetuity growth method
3. Calculate the enterprise value and equity value
4. Calculate the per share value

**Equations:**
- Present Value of FCF for year t = FCF_t ÷ (1 + WACC)^t
- Terminal Value = FCF_n × (1 + g) ÷ (WACC - g)
  - Where: FCF_n = Final Year FCF, g = Terminal Growth Rate
- Present Value of Terminal Value = Terminal Value ÷ (1 + WACC)^n
- Enterprise Value = Sum of PV of FCFs + PV of Terminal Value
- Equity Value = Enterprise Value - Net Debt
- Per Share Value = Equity Value ÷ Shares Outstanding

**Excel Implementation:**
```excel
# Present value of explicit period cash flows
=85/(1+0.09)^1 + 92/(1+0.09)^2 + 102/(1+0.09)^3 + 110/(1+0.09)^4 + 120/(1+0.09)^5
'Result: $379.45 million

# Terminal value
=120*(1+0.03)/(0.09-0.03)  'Result: $2,060 million

# Present value of terminal value
=2060/(1+0.09)^5  'Result: $1,337.94 million

# Enterprise value
=379.45+1337.94  'Result: $1,717.39 million

# Equity value
=1717.39-350  'Result: $1,367.39 million

# Per share value
=1367.39/50  'Result: $27.35
```

**Python Implementation:**
```python
import numpy as np

def dcf_valuation(fcf_projections, terminal_growth_rate, wacc, net_debt, shares_outstanding):
    """Perform a DCF valuation"""
    
    # Present value of explicit period cash flows
    pv_explicit = 0
    for year, fcf in enumerate(fcf_projections, 1):
        pv_explicit += fcf / (1 + wacc) ** year
    
    # Terminal value calculation
    last_fcf = fcf_projections[-1]
    terminal_fcf = last_fcf * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    
    # Present value of terminal value
    pv_terminal = terminal_value / (1 + wacc) ** len(fcf_projections)
    
    # Enterprise value
    enterprise_value = pv_explicit + pv_terminal
    
    # Equity value
    equity_value = enterprise_value - net_debt
    
    # Per share value
    share_price = equity_value / shares_outstanding
    
    return pv_explicit, terminal_value, pv_terminal, enterprise_value, equity_value, share_price

# Input values
fcf_projections = [85, 92, 102, 110, 120]  # in millions
terminal_growth_rate = 0.03
wacc = 0.09
net_debt = 350  # in millions
shares_outstanding = 50  # in millions

# Calculate DCF valuation
pv_explicit, terminal_value, pv_terminal, enterprise_value, equity_value, share_price = dcf_valuation(
    fcf_projections, terminal_growth_rate, wacc, net_debt, shares_outstanding)

# Display results
print(f"PV of Explicit Cash Flows: ${pv_explicit:.2f} million")
print(f"Terminal Value: ${terminal_value:.2f} million")
print(f"PV of Terminal Value: ${pv_terminal:.2f} million")
print(f"Enterprise Value: ${enterprise_value:.2f} million")
print(f"Equity Value: ${equity_value:.2f} million")
print(f"Per Share Value: ${share_price:.2f}")
```

### Exercise 7: Relative Valuation
**Problem:** You are analyzing Digital Solutions Inc. along with its industry peers. You have the following information:

**Digital Solutions Inc.:**
- Current price: $72.40
- EPS: $3.15
- Book value per share: $21.80
- Sales per share: $42.50
- EBITDA per share: $8.90
- Expected earnings growth: 14%

**Industry averages:**
- P/E ratio: 24.5
- P/B ratio: 3.4
- P/S ratio: 1.8
- EV/EBITDA: 12.2
- PEG ratio: 1.6

**Tasks:**
1. Calculate Digital Solutions' valuation multiples
2. Compare to industry averages and determine if the stock appears undervalued or overvalued
3. Estimate fair value using each multiple
4. Provide a final valuation range and recommendation

**Equations:**
- P/E Ratio = Price per Share ÷ Earnings per Share
- P/B Ratio = Price per Share ÷ Book Value per Share
- P/S Ratio = Price per Share ÷ Sales per Share
- PEG Ratio = P/E Ratio ÷ Expected Earnings Growth Rate
- Fair Value using P/E = EPS × Industry P/E Ratio
- Fair Value using P/B = Book Value per Share × Industry P/B Ratio
- Fair Value using P/S = Sales per Share × Industry P/S Ratio
- Fair Value using PEG = EPS × Growth Rate × Industry PEG Ratio

**Excel Implementation:**
```excel
# Calculate Digital Solutions' multiples
# P/E Ratio
=72.40/3.15  'Result: 22.98

# P/B Ratio
=72.40/21.80  'Result: 3.32

# P/S Ratio
=72.40/42.50  'Result: 1.70

# PEG Ratio
=22.98/14  'Result: 1.64

# Estimated fair values using industry multiples
# Based on P/E
=3.15*24.5  'Result: $77.18

# Based on P/B
=21.80*3.4  'Result: $74.12

# Based on P/S
=42.50*1.8  'Result: $76.50

# Based on PEG
=3.15*14*1.6  'Result: $70.56
```

**Python Implementation:**
```python
def relative_valuation(company_metrics, industry_multiples):
    """Perform relative valuation analysis"""
    
    # Calculate company multiples
    company_multiples = {
        'P/E': company_metrics['price'] / company_metrics['eps'],
        'P/B': company_metrics['price'] / company_metrics['book_value'],
        'P/S': company_metrics['price'] / company_metrics['sales'],
        'PEG': (company_metrics['price'] / company_metrics['eps']) / company_metrics['growth']
    }
    
    # Calculate estimated fair values
    fair_values = {
        'P/E based': company_metrics['eps'] * industry_multiples['P/E'],
        'P/B based': company_metrics['book_value'] * industry_multiples['P/B'],
        'P/S based': company_metrics['sales'] * industry_multiples['P/S'],
        'PEG based': company_metrics['eps'] * company_metrics['growth'] * industry_multiples['PEG']
    }
    
    # Valuation status
    valuation_status = {
        'P/E': 'Undervalued' if company_multiples['P/E'] < industry_multiples['P/E'] else 'Overvalued',
        'P/B': 'Undervalued' if company_multiples['P/B'] < industry_multiples['P/B'] else 'Overvalued',
        'P/S': 'Undervalued' if company_multiples['P/S'] < industry_multiples['P/S'] else 'Overvalued',
        'PEG': 'Undervalued' if company_multiples['PEG'] < industry_multiples['PEG'] else 'Overvalued'
    }
    
    return company_multiples, fair_values, valuation_status

# Input values
company_metrics = {
    'price': 72.40,
    'eps': 3.15,
    'book_value': 21.80,
    'sales': 42.50,
    'ebitda': 8.90,
    'growth': 14
}

industry_multiples = {
    'P/E': 24.5,
    'P/B': 3.4,
    'P/S': 1.8,
    'EV/EBITDA': 12.2,
    'PEG': 1.6
}

# Perform valuation
company_multiples, fair_values, valuation_status = relative_valuation(company_metrics, industry_multiples)

# Display results
print("Digital Solutions' Multiples:")
for key, value in company_multiples.items():
    print(f"{key}: {value:.2f} ({valuation_status[key]})")

print("\nEstimated Fair Values:")
for key, value in fair_values.items():
    print(f"{key}: ${value:.2f}")

fair_value_avg = sum(fair_values.values()) / len(fair_values)
print(f"\nAverage Fair Value: ${fair_value_avg:.2f}")
print(f"Current Price: ${company_metrics['price']:.2f}")
print(f"Valuation Status: {'Undervalued' if fair_value_avg > company_metrics['price'] else 'Overvalued'}")
```

## Section 3.3: Fixed Income Fundamentals

### Exercise 8: Bond Pricing Basics
**Problem:** You are analyzing a corporate bond with the following characteristics:
- Face value: $1,000
- Coupon rate: 4.5% (semiannual payments)
- Maturity: 10 years
- Yield to maturity: 5.2%

**Tasks:**
1. Calculate the semiannual coupon payment
2. Calculate the bond price
3. Determine if the bond is trading at a premium, discount, or par
4. Calculate the current yield

**Equations:**
- Semiannual Coupon Payment = (Face Value × Coupon Rate) ÷ 2
- Bond Price = ∑[Coupon Payment ÷ (1 + YTM/2)^t] + [Face Value ÷ (1 + YTM/2)^n]
  - Where: t = payment period, n = total number of periods
- Bond Price Status:
  - Premium: Price > Face Value
  - Discount: Price < Face Value
  - Par: Price = Face Value
- Current Yield = (Annual Coupon Payment ÷ Bond Price) × 100%

**Excel Implementation:**
```excel
# Semiannual coupon payment
=1000*0.045/2  'Result: $22.50

# Semiannual yield
=0.052/2  'Result: 0.026

# Number of periods
=10*2  'Result: 20

# Bond price using PV function
=PV(0.026,20,22.5,1000)  'Result: -$947.17 (negative because it's an outflow)
'Or simplified version:
=22.5*(1-(1+0.026)^(-20))/0.026+1000/(1+0.026)^20  'Result: $947.17

# Trading status
="Discount"  'Since price < face value

# Current yield
=45/947.17  'Result: 0.0475 or 4.75%
```

**Python Implementation:**
```python
def bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """Calculate the price of a bond"""
    # Periodic interest rate
    rate_per_period = ytm / periods_per_year
    
    # Number of periods
    n_periods = years_to_maturity * periods_per_year
    
    # Coupon payment per period
    coupon_per_period = (coupon_rate * par) / periods_per_year
    
    # Calculate present value of coupon payments
    pv_coupons = coupon_per_period * ((1 - (1 + rate_per_period) ** -n_periods) / rate_per_period)
    
    # Calculate present value of par value
    pv_par = par / ((1 + rate_per_period) ** n_periods)
    
    # Bond price is sum of present values
    return pv_coupons + pv_par

# Input values
par = 1000
coupon_rate = 0.045
ytm = 0.052
years_to_maturity = 10
periods_per_year = 2

# Calculate bond price
price = bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year)

# Calculate semiannual coupon payment
semiannual_coupon = (par * coupon_rate) / periods_per_year

# Determine trading status
if price > par:
    status = "Premium"
elif price < par:
    status = "Discount"
else:
    status = "Par"

# Calculate current yield
current_yield = (coupon_rate * par) / price

# Display results
print(f"Semiannual Coupon Payment: ${semiannual_coupon:.2f}")
print(f"Bond Price: ${price:.2f}")
print(f"Trading Status: {status}")
print(f"Current Yield: {current_yield*100:.2f}%")
```

### Exercise 9: Bond Duration and Convexity
**Problem:** Calculate the duration and convexity for a bond with the following characteristics:
- Face value: $1,000
- Coupon rate: 6% (annual payments)
- Maturity: 15 years
- Yield to maturity: 7%

**Tasks:**
1. Calculate the Macaulay duration
2. Calculate the modified duration
3. Calculate the convexity
4. Estimate the price change if yields increase by 50 basis points (0.5%)

**Equations:**
- Macaulay Duration = ∑[t × CF_t ÷ (1 + YTM)^t] ÷ Bond Price
  - Where: t = time period, CF_t = Cash flow at time t
- Modified Duration = Macaulay Duration ÷ (1 + YTM)
- Convexity = ∑[t × (t + 1) × CF_t ÷ (1 + YTM)^(t+2)] ÷ [Bond Price × (1 + YTM)^2]
- Price Change Estimate:
  - First-order (Duration): ΔP/P ≈ -Modified Duration × Δy
  - Second-order (Duration + Convexity): ΔP/P ≈ -Modified Duration × Δy + (1/2) × Convexity × (Δy)^2

**Excel Implementation:**
```excel
# Calculate bond price
=PV(0.07,15,-60,1000)  'Result: $913.52 (negative to represent outflow)

# Macaulay Duration calculation
=(1*60/(1+0.07)^1 + 2*60/(1+0.07)^2 + ... + 15*1060/(1+0.07)^15)/913.52  'Result: 8.78

# Modified Duration
=8.78/(1+0.07)  'Result: 8.21

# Convexity calculation
=(1*(1+1)*60/(1+0.07)^3 + 2*(2+1)*60/(1+0.07)^4 + ... + 15*(15+1)*1060/(1+0.07)^17)/(913.52*(1+0.07)^2)  'Result: 98.65

# Price change estimate (duration only)
=-8.21*0.005*913.52  'Result: -$37.50

# Price change estimate (duration + convexity)
=(-8.21*0.005+0.5*98.65*0.005^2)*913.52  'Result: -$36.04
```

**Python Implementation:**
```python
import numpy as np

def bond_duration_convexity(par, coupon_rate, ytm, years_to_maturity):
    """Calculate the duration and convexity of a bond"""
    # Calculate bond price
    cash_flows = np.zeros(years_to_maturity + 1)
    cash_flows[1:] = coupon_rate * par
    cash_flows[-1] += par
    
    # Discount factors
    discount_factors = 1 / (1 + ytm) ** np.arange(1, years_to_maturity + 1)
    
    # Bond price
    price = np.sum(cash_flows[1:] * discount_factors)
    
    # Macaulay Duration
    weighted_times = np.arange(1, years_to_maturity + 1) * cash_flows[1:] * discount_factors
    macaulay_duration = np.sum(weighted_times) / price
    
    # Modified Duration
    modified_duration = macaulay_duration / (1 + ytm)
    
    # Convexity
    weighted_times_squared = np.arange(1, years_to_maturity + 1) * (np.arange(1, years_to_maturity + 1) + 1) * cash_flows[1:] * discount_factors / (1 + ytm) ** 2
    convexity = np.sum(weighted_times_squared) / price
    
    return price, macaulay_duration, modified_duration, convexity

def price_change_estimate(price, modified_duration, convexity, yield_change):
    """Estimate price change using duration and convexity"""
    # First-order approximation (duration effect)
    duration_effect = -modified_duration * yield_change
    
    # Second-order approximation (convexity effect)
    convexity_effect = 0.5 * convexity * (yield_change ** 2)
    
    # Total estimated price change
    percentage_change = duration_effect + convexity_effect
    dollar_change = percentage_change * price
    
    return percentage_change, dollar_change

# Input values
par = 1000
coupon_rate = 0.06
ytm = 0.07
years_to_maturity = 15
yield_change = 0.005  # 50 basis points

# Calculate duration and convexity
price, macaulay_duration, modified_duration, convexity = bond_duration_convexity(par, coupon_rate, ytm, years_to_maturity)

# Estimate price change
percentage_change, dollar_change = price_change_estimate(price, modified_duration, convexity, yield_change)

# Display results
print(f"Bond Price: ${price:.2f}")
print(f"Macaulay Duration: {macaulay_duration:.2f} years")
print(f"Modified Duration: {modified_duration:.2f}")
print(f"Convexity: {convexity:.2f}")
print(f"Estimated Price Change (Duration Only): ${-modified_duration * yield_change * price:.2f}")
print(f"Estimated Price Change (Duration + Convexity): ${dollar_change:.2f}")
print(f"Percentage Change: {percentage_change*100:.2f}%")
```

### Exercise 10: Yield Curve Analysis
**Problem:** You have the following yield curve data for U.S. Treasury securities:

| Maturity | Yield (%) |
|----------|-----------|
| 3-month  | 5.10      |
| 6-month  | 5.25      |
| 1-year   | 5.40      |
| 2-year   | 5.30      |
| 3-year   | 5.20      |
| 5-year   | 5.15      |
| 7-year   | 5.25      |
| 10-year  | 5.35      |
| 20-year  | 5.55      |
| 30-year  | 5.60      |

**Tasks:**
1. Identify the shape of the yield curve
2. Calculate the 1-year forward rate, 1 year from now
3. Calculate the 2-year forward rate, 3 years from now
4. Explain what the yield curve suggests about market expectations

**Equations:**
- Forward Rate: (1 + r_T)^T = (1 + r_t)^t × (1 + f_{t,T})^(T-t)
- Solving for f_{t,T}: f_{t,T} = [(1 + r_T)^T ÷ (1 + r_t)^t]^(1/(T-t)) - 1
  - Where: r_T = spot rate for maturity T, r_t = spot rate for maturity t, f_{t,T} = forward rate from t to T

**Excel Implementation:**
```excel
# 1-year forward rate, 1 year from now
=((1+0.0530)^2/(1+0.0540)^1)^(1/1)-1  'Result: 0.0520 or 5.20%

# 2-year forward rate, 3 years from now
=((1+0.0515)^5/(1+0.0520)^3)^(1/2)-1  'Result: 0.0508 or 5.08%
```

**Python Implementation:**
```python
import numpy as np
import matplotlib.pyplot as plt

def forward_rate(spot_rate_long, maturity_long, spot_rate_short, maturity_short):
    """Calculate forward rate"""
    return ((1 + spot_rate_long) ** maturity_long / 
            (1 + spot_rate_short) ** maturity_short) ** (1 / (maturity_long - maturity_short)) - 1

# Input yield curve data
maturities = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
yields = [0.0510, 0.0525, 0.0540, 0.0530, 0.0520, 0.0515, 0.0525, 0.0535, 0.0555, 0.0560]

# Calculate forward rates
forward_1y_1y = forward_rate(yields[3], maturities[3], yields[2], maturities[2])
forward_3y_2y = forward_rate(yields[5], maturities[5], yields[4], maturities[4])

# Plot yield curve
plt.figure(figsize=(10, 6))
plt.plot(maturities, [y*100 for y in yields], 'b-o', linewidth=2)
plt.xlabel('Maturity (Years)')
plt.ylabel('Yield (%)')
plt.title('U.S. Treasury Yield Curve')
plt.grid(True, alpha=0.3)
plt.show()

# Display results
print(f"1-year forward rate, 1 year from now: {forward_1y_1y*100:.2f}%")
print(f"2-year forward rate, 3 years from now: {forward_3y_2y*100:.2f}%")
print("\nYield Curve Shape: Humped with inversion at short end")
print("\nMarket Expectations:")
print("- Near-term interest rate increases expected (rising from 3-month to 1-year)")
print("- Economic slowdown anticipated in medium term (falling from 1-year to 5-year)")
print("- Longer-term inflation expectations remain anchored but elevated")
print("- Potential monetary policy easing expected in 2-3 years")
```

## Section 3.4: Bond Pricing and Yield Calculations

### Exercise 11: Calculating Yield to Maturity
**Problem:** You are evaluating a corporate bond with the following characteristics:
- Face value: $1,000
- Coupon rate: 3.75% (semiannual payments)
- Current price: $928.45
- Maturity: 12 years

**Tasks:**
1. Calculate the yield to maturity (YTM)
2. If interest rates increase by 100 basis points (1%), what will be the new bond price?
3. Calculate the current yield
4. Compare the coupon rate, current yield, and YTM

**Equations:**
- Bond Price Equation: P = ∑[C/(1+r)^t] + F/(1+r)^n
- Current Yield = Annual Coupon Payment ÷ Current Price

**Excel Implementation:**
```excel
# Calculate yield to maturity
=RATE(12*2,1000*0.0375/2,928.45,-1000)*2  'Result: 0.0432 or 4.32%

# New bond price if rates increase by 1%
=PV(0.0432/2+0.01/2,12*2,1000*0.0375/2,1000)  'Result: $810.73

# Current yield
=1000*0.0375/928.45  'Result: 0.0404 or 4.04%
```

**Python Implementation:**
```python
import numpy as np
from scipy.optimize import newton

def bond_price(ytm, par, coupon_rate, years_to_maturity, periods_per_year=2):
    """Calculate bond price given yield to maturity"""
    periods = years_to_maturity * periods_per_year
    periodic_rate = ytm / periods_per_year
    periodic_coupon = (coupon_rate * par) / periods_per_year
    
    # Present value of coupon payments
    pv_coupons = periodic_coupon * (1 - (1 + periodic_rate) ** -periods) / periodic_rate
    
    # Present value of par value
    pv_par = par / (1 + periodic_rate) ** periods
    
    return pv_coupons + pv_par

def yield_to_maturity(price, par, coupon_rate, years_to_maturity, periods_per_year=2):
    """Calculate yield to maturity using Newton's method"""
    
    def objective_function(ytm):
        return bond_price(ytm, par, coupon_rate, years_to_maturity, periods_per_year) - price
    
    # Initial guess: try coupon rate
    initial_guess = coupon_rate
    
    return newton(objective_function, initial_guess)

# Input values
par = 1000
coupon_rate = 0.0375
price = 928.45
years_to_maturity = 12
periods_per_year = 2

# Calculate YTM
ytm = yield_to_maturity(price, par, coupon_rate, years_to_maturity, periods_per_year)

# Calculate new price if rates increase by 1%
new_ytm = ytm + 0.01
new_price = bond_price(new_ytm, par, coupon_rate, years_to_maturity, periods_per_year)

# Calculate current yield
current_yield = (coupon_rate * par) / price

# Display results
print(f"Yield to Maturity: {ytm*100:.2f}%")
print(f"New Bond Price: ${new_price:.2f}")
print(f"Current Yield: {current_yield*100:.2f}%")
print(f"Coupon Rate: {coupon_rate*100:.2f}%")
print("\nComparison:")
print(f"YTM ({ytm*100:.2f}%) > Current Yield ({current_yield*100:.2f}%) > Coupon Rate ({coupon_rate*100:.2f}%)")
print("This relationship indicates the bond is trading at a discount to par value.")
```

### Exercise 12: Bond Portfolio Management
**Problem:** You manage a fixed income portfolio with the following bonds:

| Bond | Face Value | Coupon Rate | Maturity (years) | YTM | Price | Weight |
|------|------------|-------------|------------------|-----|-------|--------|
| A    | $1,000     | 4.5%        | 5                | 5.2%| $965.03 | 30%   |
| B    | $1,000     | 3.2%        | 3                | 4.1%| $973.58 | 25%   |
| C    | $1,000     | 6.0%        | 10               | 5.8%| $1,015.40| 45%   |

**Tasks:**
1. Calculate the weighted average YTM of the portfolio
2. Calculate the weighted average duration of the portfolio
3. If interest rates increase by 75 basis points (0.75%), estimate the new portfolio value
4. Recommend a strategy to reduce interest rate risk

**Equations:**
- Weighted Average YTM = ∑(YTM_i × Weight_i)
- Weighted Average Duration = ∑(Duration_i × Weight_i)
- Portfolio Value Change = -Weighted Average Duration × Yield Change

**Excel Implementation:**
```excel
# Calculate Modified Duration for each bond
# Bond A
=DURATION("1/1/2023","1/1/2028",0.045,0.052,2)*100/(1+0.052/2)  'Result: 4.28

# Bond B
=DURATION("1/1/2023","1/1/2026",0.032,0.041,2)*100/(1+0.041/2)  'Result: 2.83

# Bond C
=DURATION("1/1/2023","1/1/2033",0.06,0.058,2)*100/(1+0.058/2)  'Result: 7.42

# Weighted Average YTM
=0.052*0.3+0.041*0.25+0.058*0.45  'Result: 0.0520 or 5.20%

# Weighted Average Duration
=4.28*0.3+2.83*0.25+7.42*0.45  'Result: 5.32

# Portfolio Value (assuming $100,000 investment)
=100000  'Result: $100,000

# Estimated Portfolio Value Change
=-5.32*0.0075*100000  'Result: -$3,990

# New Portfolio Value
=100000-3990  'Result: $96,010
```

**Python Implementation:**
```python
import numpy as np
import pandas as pd

def bond_duration(coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """Calculate Macaulay duration of a bond"""
    periods = years_to_maturity * periods_per_year
    periodic_rate = ytm / periods_per_year
    periodic_coupon = (coupon_rate) / periods_per_year
    
    # Calculate bond price
    bond_price = 0
    for t in range(1, int(periods) + 1):
        bond_price += periodic_coupon / (1 + periodic_rate) ** t
    bond_price += 1 / (1 + periodic_rate) ** periods
    
    # Calculate duration
    duration = 0
    for t in range(1, int(periods) + 1):
        duration += t * periodic_coupon / (1 + periodic_rate) ** t
    duration += periods * 1 / (1 + periodic_rate) ** periods
    
    duration /= bond_price
    
    # Convert to years
    return duration / periods_per_year

def modified_duration(macaulay_duration, ytm, periods_per_year=2):
    """Calculate modified duration"""
    return macaulay_duration / (1 + ytm / periods_per_year)

# Portfolio data
bonds = {
    'A': {'face_value': 1000, 'coupon_rate': 0.045, 'maturity': 5, 'ytm': 0.052, 'price': 965.03, 'weight': 0.30},
    'B': {'face_value': 1000, 'coupon_rate': 0.032, 'maturity': 3, 'ytm': 0.041, 'price': 973.58, 'weight': 0.25},
    'C': {'face_value': 1000, 'coupon_rate': 0.060, 'maturity': 10, 'ytm': 0.058, 'price': 1015.40, 'weight': 0.45}
}

# Calculate duration for each bond
for bond_id, bond in bonds.items():
    mac_duration = bond_duration(bond['coupon_rate'], bond['ytm'], bond['maturity'])
    mod_duration = modified_duration(mac_duration, bond['ytm'])
    bond['macaulay_duration'] = mac_duration
    bond['modified_duration'] = mod_duration

# Calculate portfolio metrics
weighted_ytm = sum(bond['ytm'] * bond['weight'] for bond in bonds.values())
weighted_duration = sum(bond['modified_duration'] * bond['weight'] for bond in bonds.values())

# Estimate portfolio value change
portfolio_value = 100000  # Assuming $100,000 investment
yield_change = 0.0075  # 75 basis points
value_change = -weighted_duration * yield_change * portfolio_value
new_portfolio_value = portfolio_value + value_change

# Display results
print("Bond Portfolio Analysis:")
print("\nIndividual Bond Metrics:")
for bond_id, bond in bonds.items():
    print(f"Bond {bond_id}: YTM: {bond['ytm']*100:.2f}%, Modified Duration: {bond['modified_duration']:.2f}")

print(f"\nWeighted Average YTM: {weighted_ytm*100:.2f}%")
print(f"Weighted Average Modified Duration: {weighted_duration:.2f}")
print(f"Estimated Portfolio Value Change: ${value_change:.2f}")
print(f"New Portfolio Value: ${new_portfolio_value:.2f}")

print("\nRecommendations to Reduce Interest Rate Risk:")
print("1. Decrease duration by shifting allocation to shorter-term bonds")
print("2. Implement a barbell strategy (increase weights of short and long bonds, reduce intermediate)")
print("3. Consider floating-rate securities or inflation-protected bonds")
print("4. Use interest rate derivatives to hedge (e.g., interest rate swaps or futures)")
```
