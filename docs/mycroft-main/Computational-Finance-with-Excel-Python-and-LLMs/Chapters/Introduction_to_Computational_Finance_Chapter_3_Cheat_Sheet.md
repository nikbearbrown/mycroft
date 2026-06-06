# Chapter 3: Equity Securities and Fixed Income - Cheat Sheet

## 3.1 Common and Preferred Stock Characteristics

### Common Stock
**Definition**: Represents residual ownership interest in a corporation

**Key Characteristics**:
- **Residual Claim**: Last in line for assets and income after other obligations
- **Voting Rights**: Typically one vote per share to elect directors and approve major decisions
- **Limited Liability**: Financial responsibility limited to investment amount
- **Capital Appreciation**: Unlimited upside potential
- **Dividend Flexibility**: Not mandatory; discretionary payments

**Valuation Metrics**:
| Metric | Formula | Excel | Description |
|--------|---------|-------|-------------|
| P/E Ratio | Price ÷ EPS | `=Price/EPS` | How much investors pay for each dollar of earnings |
| Dividend Yield | Annual Dividends ÷ Price | `=AnnualDividend/Price*100` | Cash return relative to investment |
| Market Cap | Price × Shares Outstanding | `=Price*SharesOutstanding` | Total market value of company's equity |

### Preferred Stock
**Definition**: Hybrid security combining features of both stocks and bonds

**Key Characteristics**:
- **Dividend Preference**: Receive dividends before common stockholders
- **Claim Priority**: Stand ahead of common equity but behind bondholders
- **Limited/No Voting Rights**: Typically have restricted voting privileges
- **Convertibility**: Some issues can be converted to common shares
- **Callability**: Many can be redeemed by issuer at specified price

**Types of Preferred Stock**:
- **Cumulative**: Missed dividends accumulate and must be paid later
- **Non-Cumulative**: Missed dividends are lost forever
- **Participating**: May receive additional dividends if company performs well
- **Convertible**: Can be exchanged for common shares
- **Adjustable-Rate**: Dividend rate adjusts with market interest rates

**Preferred Stock Valuation**:
- Basic model (perpetuity): Value = Dividend ÷ Required Return
- `=AnnualDividend/RequiredReturn`

## 3.2 Equity Valuation Approaches

### Dividend Discount Model (DDM)
**Basic Formula**: 
```
P₀ = Σ[D_t/(1+r)^t]
```

**Gordon Growth Model** (constant growth):
```
P₀ = D₁/(r-g)
```
Where:
- D₁ = Next year's dividend
- r = Required return
- g = Constant growth rate (must be < r)

**Excel Implementation**:
```
=NextYearDividend/(RequiredReturn-GrowthRate)
```

**Two-Stage DDM Python Implementation**:
```python
def two_stage_ddm(current_dividend, high_growth_rate, stable_growth_rate, 
                 required_return, high_growth_years):
    # PV of dividends during high-growth phase
    pv_high_growth = 0
    dividend = current_dividend
    
    for year in range(1, high_growth_years + 1):
        dividend *= (1 + high_growth_rate)
        pv_high_growth += dividend / (1 + required_return) ** year
    
    # Terminal value using Gordon Growth Model
    last_dividend = current_dividend * (1 + high_growth_rate) ** high_growth_years
    next_dividend = last_dividend * (1 + stable_growth_rate)
    terminal_value = next_dividend / (required_return - stable_growth_rate)
    
    # PV of terminal value
    pv_terminal_value = terminal_value / (1 + required_return) ** high_growth_years
    
    # Total stock value
    return pv_high_growth + pv_terminal_value
```

### Discounted Cash Flow (DCF) Model
**Formula**:
```
P₀ = Σ[FCF_t/(1+WACC)^t] + TV_n/(1+WACC)^n
```

**Terminal Value Methods**:
1. **Perpetuity Growth**: TV_n = FCF_(n+1)/(WACC-g)
2. **Exit Multiple**: TV_n = FCF_n × Multiple

**Key DCF Components**:
- Free Cash Flow (FCF)
- Weighted Average Cost of Capital (WACC)
- Terminal Value (TV)

### Relative Valuation (Multiples)
**Common Multiples**:

| Multiple | Formula | Usage |
|----------|---------|-------|
| P/E | Price ÷ EPS | Most widely used; affected by accounting policies |
| P/B | Price ÷ Book Value per Share | Good for financial firms; ignores intangibles |
| P/S | Price ÷ Sales per Share | Useful for unprofitable companies |
| EV/EBITDA | Enterprise Value ÷ EBITDA | Accounts for capital structure differences |
| PEG | P/E ÷ Growth Rate | Incorporates expected growth |

**Implementation**:
```
# Value using industry average P/E
=IndustryAverageP/E * CompanyEPS
```

## 3.3 Fixed Income Fundamentals

### Bond Characteristics
- **Par/Face Value**: Amount repaid at maturity (typically $1,000)
- **Coupon Rate**: Annual interest as percentage of face value
- **Coupon Frequency**: How often interest is paid (typically semi-annually in US)
- **Maturity Date**: When principal is repaid
- **Yield to Maturity (YTM)**: Total return if held to maturity
- **Credit Rating**: Assessment of default risk (AAA to D)

### Types of Fixed Income Securities
1. **Government Bonds**: Treasuries, TIPS
2. **Municipal Bonds**: GO bonds, revenue bonds
3. **Corporate Bonds**: Investment-grade, high-yield (junk)
4. **Agency Bonds**: Fannie Mae, Freddie Mac
5. **Asset-Backed Securities**: MBS, CDOs
6. **Money Market Instruments**: T-bills, commercial paper, CDs

### Bond Market Terminology
- **Current Yield**: Annual coupon payment ÷ Current price
- **Price Quotation**: Percentage of par (>100: premium, <100: discount)
- **Accrued Interest**: Interest earned but not yet paid
- **Duration**: Measure of price sensitivity to interest rate changes
- **Convexity**: Measure of how duration changes as yields change

### Risk Factors
1. **Interest Rate Risk**: Bond prices move inversely to interest rates
2. **Credit/Default Risk**: Issuer fails to make payments
3. **Liquidity Risk**: Cannot sell quickly at fair value
4. **Inflation Risk**: Erodes purchasing power of fixed payments
5. **Reinvestment Risk**: Future coupons reinvested at lower rates
6. **Call Risk**: Issuer redeems bond before maturity
7. **Extension Risk**: Expected prepayments slow down

## 3.4 Bond Pricing and Yield Calculations

### Basic Bond Pricing Formula
```
P = Σ[C/(1+r)^t] + F/(1+r)^n
```
Where:
- P = Bond price
- C = Periodic coupon payment
- F = Face value
- r = Yield per period
- n = Number of periods

**Excel Implementation**:
```
=PV(YieldPerPeriod, NumberOfPeriods, CouponPaymentPerPeriod, FaceValue)
```

### Key Bond Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Yield to Maturity (YTM) | Solved iteratively | Return if held to maturity |
| Current Yield | Annual Coupon ÷ Price | Simple income measure |
| Yield to Call (YTC) | Yield if called at earliest date | Used for callable bonds |
| Macaulay Duration | Weighted average time to receive cash flows | Measured in years |
| Modified Duration | Macaulay Duration ÷ (1 + YTM/n) | % price change per 1% yield change |
| Convexity | Second derivative of price-yield function | Curvature of price-yield relationship |

### Python Implementation for Bond Metrics
```python
def bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    rate_per_period = ytm / periods_per_year
    n_periods = years_to_maturity * periods_per_year
    coupon_per_period = coupon_rate * par / periods_per_year
    
    # PV of coupon payments
    pv_coupons = coupon_per_period * (1 - (1 + rate_per_period) ** -n_periods) / rate_per_period
    
    # PV of par value
    pv_par = par / (1 + rate_per_period) ** n_periods
    
    return pv_coupons + pv_par

def yield_to_maturity(price, par, coupon_rate, years_to_maturity, 
                     periods_per_year=2, precision=0.0001):
    # Initial guesses
    ytm_low = 0.0
    ytm_high = 1.0
    
    # Bisection method
    for _ in range(100):
        ytm_mid = (ytm_low + ytm_high) / 2
        price_mid = bond_price(par, coupon_rate, ytm_mid, years_to_maturity, periods_per_year)
        
        if abs(price_mid - price) < precision:
            return ytm_mid
        
        if price_mid > price:
            ytm_low = ytm_mid
        else:
            ytm_high = ytm_mid
    
    return (ytm_low + ytm_high) / 2
```

### Yield Curve and Term Structure
**Types of Yield Curves**:
1. **Normal (Upward Sloping)**: Long-term yields > short-term yields
2. **Inverted (Downward Sloping)**: Short-term yields > long-term yields
3. **Flat**: Similar yields across maturities
4. **Humped**: Yields rise then fall for longer maturities

**Theories Explaining Yield Curve**:
1. **Expectations Theory**: Reflects market expectations of future rates
2. **Liquidity Preference Theory**: Investors demand premium for longer-term bonds
3. **Market Segmentation Theory**: Different investors prefer different maturity segments
4. **Preferred Habitat Theory**: Investors will shift if yield premiums are sufficient

### Interest Rate Risk Management
1. **Duration Management**: Adjust portfolio duration based on rate outlook
2. **Laddering**: Create staggered maturities for regular reinvestment
3. **Barbell Strategy**: Invest in short-term and long-term bonds, avoid intermediates
4. **Immunization**: Match duration of assets with liabilities

### Credit Risk and Bond Ratings
**Rating Scales**:

| S&P/Fitch | Moody's | Category | Risk Level |
|-----------|---------|----------|------------|
| AAA | Aaa | Investment Grade | Minimal |
| AA | Aa | Investment Grade | Very low |
| A | A | Investment Grade | Low |
| BBB | Baa | Investment Grade | Moderate |
| BB | Ba | High Yield/Junk | Substantial |
| B | B | High Yield/Junk | High |
| CCC | Caa | High Yield/Junk | Very high |
| D | D | Default | In default |

**Credit Spread**:
```
Credit Spread = Corporate Bond Yield - Treasury Yield
```

## Fixed Income Portfolio Strategies
1. **Credit Selection**: Identify undervalued bonds with improving credit profiles
2. **Sector Rotation**: Shift allocations based on relative value
3. **Yield Curve Positioning**: Focus on segments expected to outperform
4. **Duration Management**: Adjust based on interest rate forecasts
5. **Security Selection**: Identify bonds with attractive structures
</artifact>

Here's a comprehensive cheat sheet for Chapter 3: Equity Securities and Fixed Income. I've organized it to cover all the key concepts including common and preferred stock characteristics, equity valuation approaches, fixed income fundamentals, and bond pricing calculations.

The cheat sheet includes:
- Clear definitions of key terms
- Essential formulas with Excel implementations
- Python code snippets for complex calculations
- Comparison tables for different security types
- Risk factors and management strategies
- Bond metrics and yield curve analysis

This reference should be helpful for quick review before exams or when working on finance problems. Let me know if you'd like me to expand any particular section or add more examples!
