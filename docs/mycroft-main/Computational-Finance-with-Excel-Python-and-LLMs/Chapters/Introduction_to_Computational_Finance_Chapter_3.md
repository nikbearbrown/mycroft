# Chapter 3: Equity Securities and Fixed Income

## 3.1 Common and Preferred Stock Characteristics

Financial markets provide mechanisms for capital to flow from savers to businesses that need funding for growth and operations. In this section, we'll explore equity securities—specifically common and preferred stocks—which represent ownership stakes in corporations and form a fundamental building block of investment portfolios.

### Common Stock

Common stock represents a residual ownership interest in a corporation, making stockholders the ultimate owners of the business. As residual claimants, common stockholders have a claim on what remains after all other obligations have been met.

#### Key Characteristics of Common Stock

1. **Residual Claim on Assets and Income**
   - Common stockholders are entitled to what remains after creditors, bondholders, and preferred stockholders have been paid
   - This residual claim applies to both ongoing income (dividends) and liquidation proceeds
   - The claim is typically proportional to the number of shares owned

2. **Voting Rights**
   - Common stockholders generally have the right to vote on important corporate matters
   - These include electing the board of directors, approving major corporate changes (mergers, acquisitions), and authorizing new share issuances
   - Most companies follow a "one share, one vote" rule, though dual-class structures exist

3. **Limited Liability**
   - Stockholders' financial responsibility is limited to their investment
   - Personal assets are protected from the corporation's creditors
   - This limited liability encourages investment and risk-taking

4. **Potential for Capital Appreciation**
   - Common stock prices can increase, providing capital gains
   - The potential for appreciation is theoretically unlimited
   - This appreciation potential compensates for the higher risk compared to other securities

5. **Dividend Flexibility**
   - Dividends are discretionary, not mandatory
   - The board of directors decides whether to pay dividends and in what amount
   - Dividends may be increased, decreased, or eliminated based on business conditions

#### Common Stock Valuation Metrics

1. **Price-to-Earnings (P/E) Ratio**
   - Calculated as: Market Price per Share ÷ Earnings per Share
   - Indicates how much investors are willing to pay for each dollar of earnings
   - Higher ratios suggest expectations of higher growth or lower risk

2. **Dividend Yield**
   - Calculated as: Annual Dividends per Share ÷ Market Price per Share
   - Represents the cash return from dividends relative to the investment
   - Important for income-focused investors

3. **Market Capitalization**
   - Calculated as: Market Price per Share × Total Shares Outstanding
   - Represents the total market value of a company's equity
   - Used to classify companies as large-cap, mid-cap, or small-cap

Let's implement these calculations using NVIDIA (NVDA) as an example:

#### Excel Implementation for Common Stock Metrics

```
# P/E Ratio
=B1/B2  'Where B1 contains stock price and B2 contains EPS

# Dividend Yield
=B3/B1*100  'Where B3 contains annual dividend per share

# Market Capitalization (in billions)
=B1*B4/1000000000  'Where B4 contains shares outstanding
```

#### Python Implementation for Common Stock Metrics

```python
import yfinance as yf
import pandas as pd

# Get NVIDIA data
nvda = yf.Ticker("NVDA")

# Get current price
current_price = nvda.info['currentPrice']

# Get trailing EPS
trailing_eps = nvda.info['trailingEPS']

# Calculate P/E ratio
pe_ratio = current_price / trailing_eps

# Get annual dividend
annual_dividend = nvda.info['dividendRate']

# Calculate dividend yield
dividend_yield = (annual_dividend / current_price) * 100

# Get shares outstanding
shares_outstanding = nvda.info['sharesOutstanding']

# Calculate market cap
market_cap = current_price * shares_outstanding / 1_000_000_000  # In billions

# Display results
metrics = {
    'Current Price': f"${current_price:.2f}",
    'Trailing EPS': f"${trailing_eps:.2f}",
    'P/E Ratio': f"{pe_ratio:.2f}",
    'Annual Dividend': f"${annual_dividend:.2f}",
    'Dividend Yield': f"{dividend_yield:.2f}%",
    'Shares Outstanding': f"{shares_outstanding/1_000_000_000:.2f} billion",
    'Market Cap': f"${market_cap:.2f} billion"
}

for key, value in metrics.items():
    print(f"{key}: {value}")
```

### Preferred Stock

Preferred stock is a hybrid security that combines features of both common stock and bonds. It represents ownership in a company but typically comes with preferences over common stock with respect to dividends and asset claims.

#### Key Characteristics of Preferred Stock

1. **Dividend Preference**
   - Preferred stockholders receive dividends before common stockholders
   - Dividends are usually fixed, similar to bond interest payments
   - Dividends are often cumulative, meaning if missed, they accumulate and must be paid before any common dividends

2. **Claim Priority**
   - In liquidation, preferred stockholders have priority over common stockholders
   - They stand behind bondholders but ahead of common equity in the claim hierarchy
   - This provides a measure of safety compared to common stock

3. **Limited or No Voting Rights**
   - Preferred stockholders typically have limited or no voting rights
   - Voting rights may be granted in special circumstances, such as when dividend payments are in arrears

4. **Convertibility (for some issues)**
   - Some preferred stocks are convertible into a specified number of common shares
   - This feature provides potential upside participation if the common stock performs well
   - Conversion is typically at the stockholder's option

5. **Callability (for some issues)**
   - Many preferred stocks are callable, meaning the issuer can redeem them
   - Call provisions typically include a call premium over par value
   - This limits the potential price appreciation of the preferred stock

#### Types of Preferred Stock

1. **Cumulative Preferred**
   - Missed dividends accumulate as arrearage
   - All accumulated dividends must be paid before any common dividends

2. **Non-Cumulative Preferred**
   - Missed dividends do not accumulate
   - Once missed, these dividend payments are lost

3. **Participating Preferred**
   - Receives regular preferred dividend plus potential additional dividends
   - Additional payments depend on the performance of the company

4. **Convertible Preferred**
   - Can be converted into a specified number of common shares
   - Conversion ratio determines how many common shares are received

5. **Adjustable-Rate Preferred**
   - Dividend rate adjusts periodically based on market interest rates
   - Reduces interest rate risk compared to fixed-rate preferred

Let's look at an example of calculating the value of a preferred stock:

#### Excel Implementation for Preferred Stock Valuation

```
# Value of Preferred Stock (Perpetuity Model)
=B1/B2  'Where B1 contains annual dividend and B2 contains required return

# Yield to Call
=IRR(range)  'Where range contains cash flows including call price
```

#### Python Implementation for Preferred Stock Analysis

```python
def preferred_stock_value(dividend, required_return):
    """
    Calculate the value of a non-callable preferred stock using the perpetuity model.
    
    Parameters:
    dividend (float): Annual dividend amount per share
    required_return (float): Required rate of return as a decimal
    
    Returns:
    float: Theoretical value of the preferred stock
    """
    return dividend / required_return

def preferred_yield_to_call(price, dividend, call_price, years_to_call, frequency=1):
    """
    Calculate the yield to call for a callable preferred stock.
    
    Parameters:
    price (float): Current market price
    dividend (float): Annual dividend amount per share
    call_price (float): Call price
    years_to_call (int): Years until callable
    frequency (int): Dividend payment frequency per year
    
    Returns:
    float: Yield to call as a decimal
    """
    import numpy as np
    
    periods = years_to_call * frequency
    period_dividend = dividend / frequency
    
    # Create cash flow array
    cash_flows = [-price]  # Initial investment (negative)
    cash_flows.extend([period_dividend] * (periods - 1))  # Periodic dividends
    cash_flows.append(period_dividend + call_price)  # Final dividend plus call price
    
    # Calculate IRR
    irr = np.irr(cash_flows)
    
    # Convert to annual rate if necessary
    if frequency > 1:
        ytc = (1 + irr) ** frequency - 1
    else:
        ytc = irr
        
    return ytc

# Example: Bank of America Series L Preferred Stock
dividend = 7.25  # $7.25 annual dividend
required_return = 0.06  # 6% required return
price = 118.50  # Current market price
call_price = 100.00  # Call price (typically par value)
years_to_call = 2  # Assuming callable in 2 years

# Calculate value
value = preferred_stock_value(dividend, required_return)
print(f"Theoretical value: ${value:.2f}")

# Calculate yield to call
ytc = preferred_yield_to_call(price, dividend, call_price, years_to_call)
print(f"Yield to call: {ytc*100:.2f}%")
```

### Common vs. Preferred Stock: A Comparison

| Feature | Common Stock | Preferred Stock |
|---------|--------------|-----------------|
| Claim Priority | Last (residual) | Intermediate (after debt, before common) |
| Dividends | Variable, discretionary | Fixed, often cumulative |
| Voting Rights | Yes | Limited or none |
| Price Appreciation | Unlimited potential | Limited (often trades like a bond) |
| Risk Level | Higher | Intermediate |
| Typical Investors | Growth-oriented | Income-oriented, institutional |

### LLM Implementation for Stock Analysis

Large Language Models can be particularly useful for interpreting stock metrics and understanding company characteristics. Here's an example of using an LLM to analyze the differences between common and preferred stock for a specific company:

**Prompt to LLM:**

```
Analyze Bank of America's common stock (BAC) and preferred stock (BAC.PR.L) based on the following information:

Common Stock (BAC):
- Current Price: $38.75
- EPS: $3.45
- Annual Dividend: $0.96
- Market Cap: $305 billion
- Beta: 1.35

Preferred Stock (BAC.PR.L):
- Current Price: $118.50
- Par Value: $100
- Annual Dividend: $7.25 (7.25% of par)
- Callable in 2025
- No maturity date

Compare these securities in terms of:
1. Risk and return characteristics
2. Suitable investor profiles
3. How each might respond to rising interest rates
4. The impact of Bank of America's financial performance on each security
```

**Expected LLM Response:**

```
# Analysis of Bank of America Common vs. Preferred Stock

## Risk and Return Characteristics

### BAC Common Stock
- **P/E Ratio**: 11.23 (38.75/3.45), suggesting a relatively moderate valuation compared to the broader market
- **Dividend Yield**: 2.48% ($0.96/$38.75), providing moderate income
- **Beta of 1.35**: Indicates 35% more volatility than the overall market
- **Return Profile**: Combination of dividend income and potential for capital appreciation
- **Risk Level**: Higher risk with full exposure to company performance and market fluctuations

### BAC.PR.L Preferred Stock
- **Dividend Yield**: 6.12% ($7.25/$118.50), significantly higher than common stock
- **Current Price Premium**: Trading at 18.5% premium to par value ($118.50 vs $100)
- **Fixed Income Characteristics**: More stable price with focus on income
- **Call Risk**: Potential for forced redemption at $100 in 2025, creating price ceiling
- **Risk Level**: Lower than common stock but higher than bonds; vulnerable to interest rate and credit risks

## Suitable Investor Profiles

### BAC Common Stock
- **Growth-Oriented Investors**: Those seeking capital appreciation with some income
- **Risk-Tolerant Investors**: Comfortable with higher volatility for higher potential returns
- **Long-Term Investors**: Those with time horizon to ride out market fluctuations
- **Investors Wanting Economic Exposure**: Those bullish on banking sector and economic growth

### BAC.PR.L Preferred Stock
- **Income-Focused Investors**: Retirees and others prioritizing steady, higher income
- **Conservative Equity Investors**: Those seeking equity exposure with reduced volatility
- **Institutional Investors**: Insurance companies, pension funds seeking predictable income
- **Fixed-Income Investors**: Looking for higher yields than bonds with acceptable risk increase

## Response to Rising Interest Rates

### BAC Common Stock
- **Mixed Impact**: Banking profits may benefit from wider net interest margins
- **Potential Growth**: Could see earnings growth as lending becomes more profitable
- **Offsetting Factors**: Higher rates may slow economic activity and loan demand
- **Market Sentiment**: Likely to follow broader market reaction to rate increases

### BAC.PR.L Preferred Stock
- **Negative Price Pressure**: Fixed dividend becomes less attractive as rates rise
- **Increased Call Risk**: Higher rates increase likelihood of call when eligible in 2025
- **Price Ceiling**: Trading above par value increases vulnerability to price decline
- **Yield Competition**: Will face competition from newly issued higher-yield securities

## Impact of Bank of America's Financial Performance

### BAC Common Stock
- **Direct Relationship**: Price directly tied to earnings, growth prospects, and profitability
- **Dividend Growth Potential**: Strong performance could lead to dividend increases
- **Full Participation**: Shareholders fully participate in improved profitability
- **Downside Exposure**: Similarly exposed to full impact of any deterioration

### BAC.PR.L Preferred Stock
- **Limited Upside**: Strong performance provides security for dividend but limited price appreciation
- **Downside Protection**: Protected from moderate earnings declines
- **Credit Quality Focus**: Performance matters primarily as it affects ability to pay fixed dividends
- **Dividend Consistency**: Dividend remains fixed regardless of how profitable the bank becomes

## Summary
The common stock (BAC) offers higher potential returns with higher risk and volatility, making it suitable for growth-oriented investors with longer time horizons. The preferred stock (BAC.PR.L) provides higher current income with less volatility, making it appropriate for income-focused, more conservative investors. However, the preferred stock's premium to par value and callable feature in 2025 creates a meaningful risk of capital loss if interest rates rise significantly.
```

This LLM analysis complements the quantitative approaches in Excel and Python by providing context and interpretation of the metrics, helping investors understand the implications of the numbers.

## 3.2 Equity Valuation Approaches

Valuing equity securities is both an art and a science. Several methodologies have been developed to estimate the intrinsic value of stocks, each with its own strengths and limitations. In this section, we'll explore the major equity valuation approaches and implement them using Excel, Python, and LLMs.

### Dividend Discount Model (DDM)

The Dividend Discount Model is based on the premise that a stock's value equals the present value of all expected future dividends. The basic formula is:

$$P_0 = \sum_{t=1}^{\infty} \frac{D_t}{(1+r)^t}$$

Where:
- $P_0$ is the current stock price
- $D_t$ is the dividend at time t
- $r$ is the required rate of return (discount rate)

#### Gordon Growth Model

The Gordon Growth Model simplifies the DDM by assuming dividends grow at a constant rate forever:

$$P_0 = \frac{D_1}{r-g}$$

Where:
- $D_1$ is the dividend expected next year
- $r$ is the required rate of return
- $g$ is the constant growth rate of dividends

The model has several important constraints:
- Only applicable when $g < r$
- Most suitable for mature companies with stable dividend policies
- Highly sensitive to inputs, especially when $r$ and $g$ are close

#### Excel Implementation of Gordon Growth Model

```
# Gordon Growth Model
=B1/(B2-B3)  'Where B1 is next year's dividend, B2 is required return, B3 is growth rate

# Required Return (using CAPM)
=B4+B5*B6  'Where B4 is risk-free rate, B5 is beta, B6 is market risk premium
```

#### Python Implementation of Gordon Growth Model

```python
def gordon_growth_model(next_dividend, required_return, growth_rate):
    """
    Calculate stock price using the Gordon Growth Model.
    
    Parameters:
    next_dividend (float): Expected dividend next year
    required_return (float): Required rate of return as a decimal
    growth_rate (float): Expected constant growth rate as a decimal
    
    Returns:
    float: Estimated stock price
    """
    if growth_rate >= required_return:
        raise ValueError("Growth rate must be less than required return")
    
    return next_dividend / (required_return - growth_rate)

# Example for Visa (V)
current_dividend = 2.08  # Current annual dividend
growth_rate = 0.15  # Expected growth rate 15%
required_return = 0.10  # Required return 10%

# Calculate next year's dividend
next_dividend = current_dividend * (1 + growth_rate)

# Apply Gordon Growth Model
try:
    stock_price = gordon_growth_model(next_dividend, required_return, growth_rate)
    print(f"Estimated stock price for Visa: ${stock_price:.2f}")
except ValueError as e:
    print(f"Error: {e}")
    print("Using two-stage growth model instead...")
    # Implement two-stage growth model here
```

#### Multi-Stage Dividend Discount Model

For companies with changing growth rates, a multi-stage model is more appropriate:

$$P_0 = \sum_{t=1}^{n} \frac{D_t}{(1+r)^t} + \frac{P_n}{(1+r)^n}$$

Where $P_n$ is the terminal value, often calculated using the Gordon Growth Model with a sustainable long-term growth rate.

#### Python Implementation of Two-Stage Dividend Discount Model

```python
def two_stage_ddm(current_dividend, high_growth_rate, stable_growth_rate, 
                 required_return, high_growth_years):
    """
    Calculate stock price using a two-stage dividend discount model.
    
    Parameters:
    current_dividend (float): Current annual dividend
    high_growth_rate (float): Growth rate during high-growth phase
    stable_growth_rate (float): Long-term sustainable growth rate
    required_return (float): Required rate of return
    high_growth_years (int): Number of years in high-growth phase
    
    Returns:
    float: Estimated stock price
    """
    if stable_growth_rate >= required_return:
        raise ValueError("Stable growth rate must be less than required return")
    
    # Present value of dividends during high-growth phase
    pv_high_growth = 0
    dividend = current_dividend
    
    for year in range(1, high_growth_years + 1):
        dividend *= (1 + high_growth_rate)
        pv_high_growth += dividend / (1 + required_return) ** year
    
    # Terminal value using Gordon Growth Model
    last_dividend = current_dividend * (1 + high_growth_rate) ** high_growth_years
    next_dividend = last_dividend * (1 + stable_growth_rate)
    terminal_value = next_dividend / (required_return - stable_growth_rate)
    
    # Present value of terminal value
    pv_terminal_value = terminal_value / (1 + required_return) ** high_growth_years
    
    # Total stock value
    return pv_high_growth + pv_terminal_value

# Example for NVIDIA (NVDA)
current_dividend = 0.16  # Current annual dividend
high_growth_rate = 0.25  # 25% growth for initial period
stable_growth_rate = 0.04  # 4% long-term growth
required_return = 0.09  # 9% required return
high_growth_years = 5  # 5 years of high growth

stock_price = two_stage_ddm(current_dividend, high_growth_rate, stable_growth_rate,
                           required_return, high_growth_years)
print(f"Estimated stock price for NVIDIA: ${stock_price:.2f}")
```

### Discounted Cash Flow (DCF) Model

The DCF model values a company based on its expected future free cash flows (FCF), not just dividends. This is particularly useful for companies that don't pay dividends or reinvest significantly in growth.

$$P_0 = \sum_{t=1}^{n} \frac{FCF_t}{(1+WACC)^t} + \frac{TV_n}{(1+WACC)^n}$$

Where:
- $FCF_t$ is the free cash flow in year t
- $WACC$ is the weighted average cost of capital
- $TV_n$ is the terminal value at year n

#### Terminal Value Calculation

Terminal value is typically calculated using either:

1. **Perpetuity Growth Method**:
   $$TV_n = \frac{FCF_{n+1}}{WACC-g}$$

2. **Exit Multiple Method**:
   $$TV_n = FCF_n \times \text{Multiple}$$
   
   Where Multiple is often an industry-specific EV/EBITDA or P/E ratio.

#### Python Implementation of DCF Model

```python
import pandas as pd
import numpy as np

def dcf_valuation(fcf_projections, terminal_growth_rate, wacc, shares_outstanding,
                 terminal_method='perpetuity', terminal_multiple=None):
    """
    Perform a DCF valuation of a company.
    
    Parameters:
    fcf_projections (list): Projected free cash flows for explicit forecast period
    terminal_growth_rate (float): Long-term growth rate for terminal value
    wacc (float): Weighted average cost of capital
    shares_outstanding (float): Number of outstanding shares
    terminal_method (str): 'perpetuity' or 'multiple'
    terminal_multiple (float): Exit multiple if using multiple method
    
    Returns:
    tuple: (enterprise_value, equity_value, share_price)
    """
    # Present value of explicit period cash flows
    pv_explicit = 0
    for year, fcf in enumerate(fcf_projections, 1):
        pv_explicit += fcf / (1 + wacc) ** year
    
    # Terminal value calculation
    last_fcf = fcf_projections[-1]
    if terminal_method == 'perpetuity':
        # Terminal value using perpetuity growth method
        terminal_fcf = last_fcf * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    else:
        # Terminal value using exit multiple method
        terminal_value = last_fcf * terminal_multiple
    
    # Present value of terminal value
    pv_terminal = terminal_value / (1 + wacc) ** len(fcf_projections)
    
    # Enterprise value
    enterprise_value = pv_explicit + pv_terminal
    
    # Adjust for net debt to get equity value
    net_debt = 0  # This would come from balance sheet analysis
    equity_value = enterprise_value - net_debt
    
    # Per share value
    share_price = equity_value / shares_outstanding
    
    return enterprise_value, equity_value, share_price

# Example for AMD
fcf_projections = [3.2, 4.1, 5.3, 6.5, 7.8]  # Billions of dollars
terminal_growth_rate = 0.03  # 3% long-term growth
wacc = 0.09  # 9% WACC
shares_outstanding = 1.62  # Billion shares

# Perpetuity growth method
ev_perp, equity_perp, price_perp = dcf_valuation(
    fcf_projections, terminal_growth_rate, wacc, shares_outstanding)

# Exit multiple method
terminal_multiple = 18  # Industry average EV/FCF multiple
ev_mult, equity_mult, price_mult = dcf_valuation(
    fcf_projections, terminal_growth_rate, wacc, shares_outstanding,
    terminal_method='multiple', terminal_multiple=terminal_multiple)

print(f"DCF Valuation using Perpetuity Growth Method:")
print(f"Enterprise Value: ${ev_perp:.2f} billion")
print(f"Equity Value: ${equity_perp:.2f} billion")
print(f"Share Price: ${price_perp:.2f}")
print()
print(f"DCF Valuation using Exit Multiple Method:")
print(f"Enterprise Value: ${ev_mult:.2f} billion")
print(f"Equity Value: ${equity_mult:.2f} billion")
print(f"Share Price: ${price_mult:.2f}")
```

### Relative Valuation (Multiples)

Relative valuation compares a company's valuation metrics to similar companies or the broader market. This approach is simpler and more widely used than intrinsic valuation methods.

#### Common Valuation Multiples

1. **Price-to-Earnings (P/E) Ratio**:
   $$P/E = \frac{\text{Price per Share}}{\text{Earnings per Share}}$$

2. **Price-to-Book (P/B) Ratio**:
   $$P/B = \frac{\text{Price per Share}}{\text{Book Value per Share}}$$

3. **Price-to-Sales (P/S) Ratio**:
   $$P/S = \frac{\text{Price per Share}}{\text{Sales per Share}}$$

4. **Enterprise Value-to-EBITDA (EV/EBITDA)**:
   $$EV/EBITDA = \frac{\text{Enterprise Value}}{\text{EBITDA}}$$

5. **PEG Ratio (P/E to Growth)**:
   $$PEG = \frac{P/E}{\text{Expected Earnings Growth Rate}}$$

#### Excel Implementation of Relative Valuation

```
# Calculate P/E Ratio
=B1/B2  'Where B1 is Price per Share and B2 is EPS

# Calculate P/B Ratio
=B1/B3  'Where B3 is Book Value per Share

# Calculate P/S Ratio
=B1/B4  'Where B4 is Sales per Share

# Calculate PEG Ratio
=B5/B6  'Where B5 is P/E Ratio and B6 is Growth Rate

# Estimated Value using Industry Average P/E
=B7*B2  'Where B7 is Industry Average P/E and B2 is EPS
```

#### Python Implementation of Relative Valuation

```python
import pandas as pd
import yfinance as yf

def get_valuation_multiples(tickers):
    """
    Retrieve and calculate valuation multiples for a list of companies.
    
    Parameters:
    tickers (list): List of stock tickers
    
    Returns:
    DataFrame: Valuation multiples for each company
    """
    multiples = {}
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract relevant metrics
        try:
            price = info.get('currentPrice', info.get('regularMarketPrice', None))
            eps = info.get('trailingEPS', None)
            book_value = info.get('bookValue', None)
            revenue_per_share = info.get('revenuePerShare', None)
            growth_rate = info.get('earningsGrowth', None)
            ebitda = info.get('ebitda', None)
            market_cap = info.get('marketCap', None)
            total_debt = info.get('totalDebt', 0)
            cash = info.get('totalCash', 0)
            
            # Calculate multiples
            pe_ratio = price / eps if eps and eps != 0 else None
            pb_ratio = price / book_value if book_value and book_value != 0 else None
            ps_ratio = price / revenue_per_share if revenue_per_share and revenue_per_share != 0 else None
            peg_ratio = pe_ratio / growth_rate if pe_ratio and growth_rate and growth_rate != 0 else None
            
            # Calculate EV and EV/EBITDA
            enterprise_value = market_cap + total_debt - cash if market_cap else None
            ev_ebitda = enterprise_value / ebitda if enterprise_value and ebitda and ebitda != 0 else None
            
            multiples[ticker] = {
                'Price': price,
                'EPS': eps,
                'P/E': pe_ratio,
                'P/B': pb_ratio,
                'P/S': ps_ratio,
                'PEG': peg_ratio,
                'EV/EBITDA': ev_ebitda
            }
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            multiples[ticker] = {'Error': str(e)}
    
    return pd.DataFrame(multiples).T

def value_using_peer_multiples(ticker, peer_tickers):
    """
    Value a company using peer average multiples.
    
    Parameters:
    ticker (str): Ticker of the company to value
    peer_tickers (list): List of peer company tickers
    
    Returns:
    DataFrame: Estimated values using different multiples
    """
    # Get multiples for the company and peers
    all_tickers = [ticker] + peer_tickers
    multiples_df = get_valuation_multiples(all_tickers)
    
    # Extract company data
    company_data = multiples_df.loc[ticker]
    
    # Calculate peer averages (excluding the company itself)
    peer_data = multiples_df.loc[peer_tickers]
    peer_averages = peer_data.mean()
    
    # Calculate estimated values using different multiples
    estimates = {}
    
    # P/E based valuation
    if not pd.isna(company_data['EPS']) and not pd.isna(peer_averages['P/E']):
        estimates['P/E Based'] = company_data['EPS'] * peer_averages['P/E']
    
    # Add other multiple-based valuations as needed
    
    return pd.Series(estimates, name='Estimated Value')

# Example: Value AMD using peer multiples
ticker = 'AMD'
peer_tickers = ['NVDA', 'INTC', 'TSM']

# Get valuation multiples
multiples = get_valuation_multiples([ticker] + peer_tickers)
print("Valuation Multiples:")
print(multiples)

# Value using peer multiples
estimated_values = value_using_peer_multiples(ticker, peer_tickers)
print("\nEstimated Values for AMD:")
print(estimated_values)
```

### LLM Implementation for Equity Valuation

LLMs can help with interpreting valuation results and providing context for the numbers. Here's an example of using an LLM for valuation analysis:

**Prompt to LLM:**

```
I've calculated the following valuation estimates for NVIDIA (NVDA):

1. Gordon Growth Model: $450 per share
   - Assumptions: Current dividend $0.16, 25% dividend growth for 5 years, then 4% perpetual growth, 9% required return

2. DCF Model: $720 per share
   - Assumptions: 35% FCF growth for 3 years, 20% for years 4-5, then 3% perpetual growth, 9% WACC

3. Relative Valuation:
   - Industry average P/E: 25x
   - NVDA's current EPS: $12.50
   - P/E-based value: $312.50
   
   - Industry average EV/EBITDA: 18x
   - NVDA's EBITDA per share: $15.80
   - EV/EBITDA-based value: $635.20 (adjusted for debt/cash)

Current market price: $480

Analyze these valuation results, explain the wide range of estimates, and discuss which method might be most appropriate for NVIDIA given its position in the semiconductor industry and growth prospects.
```

**Expected LLM Response:**

```
# NVIDIA Valuation Analysis

## Summary of Valuation Methods

Your valuation of NVIDIA using multiple methodologies has produced a wide range of estimates from $312.50 to $720 per share, compared to the current market price of $480. This dispersion is normal when valuing high-growth technology companies and highlights the importance of understanding the assumptions and limitations of each method.

## Analysis of Different Valuation Approaches

### Gordon Growth Model ($450)

The Gordon Growth Model estimate of $450 appears optimistic given NVIDIA's current dividend policy.

**Limitations for NVIDIA:**
- NVIDIA pays a minimal dividend ($0.16 annual) with a yield of less than 0.1%, making dividend-based valuation less relevant
- The assumed 25% dividend growth rate is aggressive, even for 5 years
- NVIDIA prioritizes reinvestment and share repurchases over dividends
- The model is highly sensitive to growth assumptions

This approach assumes NVIDIA will dramatically increase its dividend payout, which contradicts its historical capital allocation strategy. The proximity to the current market price appears coincidental rather than validating.

### DCF Model ($720)

The DCF model produces the highest valuation at $720, reflecting NVIDIA's substantial growth prospects.

**Key considerations:**
- The 35% initial FCF growth assumption aligns with NVIDIA's recent performance in AI and data center segments
- DCF appropriately captures NVIDIA's reinvestment of profits rather than dividend payments
- The terminal growth rate of 3% appears reasonable for long-term sustainability
- The 9% WACC might be too low given the volatility and rapid technological change in the semiconductor industry

This method is theoretically sound for NVIDIA but highly sensitive to growth projections. A slight adjustment to growth rates or WACC could significantly impact the valuation.

### Relative Valuation (P/E: $312.50, EV/EBITDA: $635.20)

The relative valuation methods produce widely different results:

**P/E-based valuation ($312.50):**
- Uses the industry average P/E of 25x, which may undervalue NVIDIA's premium position
- NVIDIA historically trades at a premium to the semiconductor industry
- Current P/E of ~38x reflects market expectations of continued outperformance

**EV/EBITDA-based valuation ($635.20):**
- Much higher than the P/E-based value, suggesting NVIDIA has stronger cash flow generation than peers
- Better accounts for NVIDIA's capital structure and significant cash position
- EV/EBITDA is generally considered more reliable than P/E for cross-company comparisons

The large gap between these two relative valuations highlights the challenge of selecting appropriate comparables and multiples.

## Appropriate Valuation Method for NVIDIA

For a company like NVIDIA with its specific characteristics, I would recommend:

### Primary Method: DCF with Scenario Analysis
The DCF approach is most appropriate because:
- It captures NVIDIA's substantial growth potential in AI, data centers, and gaming
- It accounts for the company's reinvestment strategy rather than dividend payments
- It can incorporate changing growth rates across different time horizons

However, given uncertainty in growth projections, I recommend:
- Creating multiple DCF scenarios (bear, base, bull)
- Conducting sensitivity analysis on key variables (growth rates, WACC)
- Assigning probability weights to different scenarios

### Supporting Method: EV/EBITDA Multiple
The EV/EBITDA approach provides a useful cross-check because:
- It accounts for NVIDIA's capital structure
- It's less affected by accounting differences than P/E
- It better reflects NVIDIA's cash generation capabilities

I would suggest using a premium multiple to the industry average (perhaps 1.2-1.5x) to reflect NVIDIA's market leadership and growth potential.

## Explaining the Valuation Range

The wide range in valuation estimates ($312.50 to $720) is primarily due to:

1. **Growth uncertainty**: NVIDIA operates in rapidly evolving markets (AI, data centers) where long-term growth is difficult to predict
2. **Method limitations**: Each valuation approach has inherent biases and limitations
3. **Assumption sensitivity**: Small changes in inputs (growth rates, discount rates) cause large valuation differences
4. **Industry transformation**: NVIDIA is benefiting from and driving a technological shift, making historical comparisons less relevant

## Conclusion

The current market price of $480 falls within your valuation range, suggesting the market is pricing in significant growth but not the most optimistic scenario. Given NVIDIA's position at the forefront of AI and high-performance computing, a premium valuation is justified, but investors should be aware of the sensitivity to growth assumptions.

For most accurate results, I recommend:
1. Using DCF as the primary method with multiple scenarios
2. Supporting with EV/EBITDA using premium multiples
3. Regularly updating projections as new information becomes available about AI adoption and data center growth
4. Considering competitive dynamics, particularly from AMD, Intel, and custom AI chip developments

This balanced approach acknowledges both NVIDIA's strong growth prospects and the inherent uncertainty in valuing high-growth technology companies.
```

### Equity Valuation: Key Takeaways

1. **Multiple Methods**: No single valuation approach is perfect. Using multiple methods provides a more robust estimate.

2. **Sensitivity Analysis**: Test how changes in key assumptions affect valuation to understand the range of possible values.

3. **Qualitative Factors**: Consider factors beyond the numbers, such as management quality, competitive positioning, and industry trends.

4. **Growth vs. Value**: Different methods are appropriate for different types of companies (growth vs. value).

5. **Margin of Safety**: Due to the uncertainty in valuation, always incorporate a margin of safety in investment decisions.

## 3.3 Fixed Income Fundamentals

Fixed income securities are debt instruments that provide investors with regular income payments and the return of principal at maturity. These securities play a crucial role in investment portfolios, offering income generation, capital preservation, and diversification benefits.

### Key Characteristics of Fixed Income Securities

1. **Par Value (Face Value)**: The amount the issuer agrees to repay at maturity, typically $1,000 for corporate bonds.

2. **Coupon Rate**: The annual interest rate paid on the bond's face value.

3. **Coupon Frequency**: How often interest payments are made, typically semi-annually in the U.S.

4. **Maturity Date**: When the principal amount is repaid and the bond expires.

5. **Yield to Maturity (YTM)**: The total return anticipated if the bond is held until maturity.

6. **Credit Rating**: Assessment of the issuer's creditworthiness, indicating default risk.

### Types of Fixed Income Securities

1. **Government Bonds**: Issued by national governments.
   - U.S. Treasury securities (bills, notes, bonds)
   - Treasury Inflation-Protected Securities (TIPS)
   - Foreign government bonds

2. **Municipal Bonds**: Issued by state and local governments.
   - General Obligation (GO) bonds
   - Revenue bonds

3. **Corporate Bonds**: Issued by corporations.
   - Investment-grade bonds (rated BBB- or higher)
   - High-yield (junk) bonds (rated below BBB-)
   - Convertible bonds

4. **Agency Bonds**: Issued by government-sponsored enterprises.
   - Fannie Mae, Freddie Mac, Federal Home Loan Banks

5. **Asset-Backed Securities (ABS)**: Backed by a pool of assets.
   - Mortgage-backed securities (MBS)
   - Collateralized debt obligations (CDOs)
   - Auto loan and credit card receivables

6. **Money Market Instruments**: Short-term debt with maturities less than one year.
   - Treasury bills
   - Commercial paper
   - Certificates of deposit (CDs)

### Bond Market Terminology

1. **Yield**: Various measures of return.
   - **Current Yield**: Annual interest payment divided by current price
   - **Yield to Maturity (YTM)**: Total return if held to maturity
   - **Yield to Call (YTC)**: Total return if called at the earliest call date

2. **Price Quotation**: Bonds are typically quoted as a percentage of par value.
   - Premium bond: Price > 100
   - Discount bond: Price < 100
   - Par bond: Price = 100

3. **Accrued Interest**: Interest earned but not yet paid to the bondholder.

4. **Duration**: Measure of price sensitivity to interest rate changes.

5. **Convexity**: Measure of how duration changes as yields change.

### Risk Factors in Fixed Income Investing

1. **Interest Rate Risk**: Bond prices move inversely to interest rates.

2. **Credit Risk (Default Risk)**: Risk that the issuer fails to make payments.

3. **Liquidity Risk**: Risk of not being able to sell a bond quickly at fair value.

4. **Inflation Risk**: Risk that inflation erodes the purchasing power of fixed payments.

5. **Reinvestment Risk**: Risk that future coupon payments must be reinvested at lower rates.

6. **Call Risk**: Risk that the issuer will redeem the bond before maturity.

7. **Extension Risk**: Risk that expected prepayments will slow, extending bond's duration.

Let's implement some basic fixed income concepts using Excel, Python, and LLMs:

#### Excel Implementation for Fixed Income Analysis

```
# Current Yield
=B1/B2*100  'Where B1 is annual coupon payment and B2 is current price

# Accrued Interest
=B1/B3*B4  'Where B1 is coupon payment, B3 is days in coupon period, B4 is days since last payment

# Clean Price
=B5-B6  'Where B5 is dirty price (quoted price) and B6 is accrued interest

# Bond Price Calculation (Present Value of Cash Flows)
=PV(B7/B8,B9*B8,B10/B8*B11,B11)  'Where B7 is YTM, B8 is periods per year, B9 is years to maturity, 
                                 'B10 is coupon rate, B11 is par value
```

#### Python Implementation for Fixed Income Analysis

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def bond_price(par, coupon_rate, years_to_maturity, yield_to_maturity, 
               periods_per_year=2):
    """
    Calculate the price of a bond.
    
    Parameters:
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    years_to_maturity (float): Years until maturity
    yield_to_maturity (float): Annual yield to maturity as decimal
    periods_per_year (int): Coupon payments per year
    
    Returns:
    float: Bond price
    """
    # Coupon payment per period
    period_coupon = (coupon_rate * par) / periods_per_year
    
    # Total number of periods
    periods = years_to_maturity * periods_per_year
    
    # Yield per period
    period_yield = yield_to_maturity / periods_per_year
    
    # Calculate present value of all coupon payments
    pv_coupons = period_coupon * (1 - (1 + period_yield) ** -periods) / period_yield
    
    # Calculate present value of par value repayment
    pv_par = par / (1 + period_yield) ** periods
    
    # Bond price is sum of present values
    return pv_coupons + pv_par

def accrued_interest(par, coupon_rate, last_payment_date, settlement_date,
                    next_payment_date, day_count='30/360'):
    """
    Calculate accrued interest for a bond.
    
    Parameters:
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    last_payment_date (datetime): Date of last coupon payment
    settlement_date (datetime): Settlement date
    next_payment_date (datetime): Date of next coupon payment
    day_count (str): Day count convention ('30/360', 'actual/actual', etc.)
    
    Returns:
    float: Accrued interest
    """
    # Annual coupon payment
    annual_coupon = coupon_rate * par
    
    # Days in the coupon period
    if day_count == '30/360':
        days_in_period = 180  # Assuming semi-annual coupons
    else:  # actual/actual
        days_in_period = (next_payment_date - last_payment_date).days
    
    # Days since last payment
    days_since_payment = (settlement_date - last_payment_date).days
    
    # Calculate accrued interest
    accrued = (annual_coupon / 2) * (days_since_payment / days_in_period)
    
    return accrued

def yield_to_maturity(price, par, coupon_rate, years_to_maturity, 
                      periods_per_year=2, precision=0.0001):
    """
    Calculate yield to maturity using numerical methods.
    
    Parameters:
    price (float): Bond price
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    years_to_maturity (float): Years until maturity
    periods_per_year (int): Coupon payments per year
    precision (float): Desired precision of YTM calculation
    
    Returns:
    float: Yield to maturity as decimal
    """
    # Initial guesses for YTM
    ytm_low = 0.0
    ytm_high = 1.0
    
    # Coupon payment per period
    period_coupon = (coupon_rate * par) / periods_per_year
    
    # Total number of periods
    periods = years_to_maturity * periods_per_year
    
    while (ytm_high - ytm_low) > precision:
        ytm_mid = (ytm_low + ytm_high) / 2
        period_yield = ytm_mid / periods_per_year
        
        # Calculate price using mid YTM
        pv_coupons = period_coupon * (1 - (1 + period_yield) ** -periods) / period_yield
        pv_par = par / (1 + period_yield) ** periods
        calculated_price = pv_coupons + pv_par
        
        # Adjust bounds based on calculated price
        if calculated_price > price:
            ytm_low = ytm_mid
        else:
            ytm_high = ytm_mid
    
    return (ytm_low + ytm_high) / 2

# Example: 10-year Treasury note
par = 1000
coupon_rate = 0.025  # 2.5%
years_to_maturity = 10
ytm = 0.028  # 2.8%

# Calculate bond price
price = bond_price(par, coupon_rate, years_to_maturity, ytm)
print(f"Bond price: ${price:.2f}")

# Calculate accrued interest
last_payment_date = datetime(2023, 5, 15)
settlement_date = datetime(2023, 7, 1)
next_payment_date = datetime(2023, 11, 15)
accrued = accrued_interest(par, coupon_rate, last_payment_date, settlement_date, next_payment_date)
print(f"Accrued interest: ${accrued:.2f}")

# Calculate clean price
clean_price = price - accrued
print(f"Clean price: ${clean_price:.2f}")

# Calculate YTM from price
calculated_ytm = yield_to_maturity(price, par, coupon_rate, years_to_maturity)
print(f"Calculated YTM: {calculated_ytm:.4f} or {calculated_ytm*100:.2f}%")
```

### Yield Curve and Term Structure of Interest Rates

The yield curve represents the relationship between yields and maturities of bonds with similar credit quality. It provides valuable information about market expectations for future interest rates and economic conditions.

#### Types of Yield Curves

1. **Normal (Upward Sloping)**: Long-term yields higher than short-term yields.
   - Typical in expanding economies
   - Reflects expectations of future interest rate increases or inflation

2. **Inverted (Downward Sloping)**: Short-term yields higher than long-term yields.
   - Often precedes economic recessions
   - Reflects expectations of future interest rate decreases

3. **Flat**: Similar yields across all maturities.
   - Often occurs during transition periods
   - Reflects uncertainty about future economic conditions

4. **Humped**: Yields rise initially then fall for longer maturities.
   - Less common shape
   - May indicate mixed economic signals

#### Theories Explaining the Yield Curve

1. **Expectations Theory**: The yield curve reflects market expectations of future short-term interest rates.

2. **Liquidity Preference Theory**: Investors demand a premium for holding longer-term bonds due to increased uncertainty.

3. **Market Segmentation Theory**: Different investors prefer different maturity segments, creating distinct supply and demand dynamics.

4. **Preferred Habitat Theory**: Investors prefer certain maturities but will shift if yield premiums are sufficient.

#### Python Implementation for Yield Curve Construction

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

def construct_yield_curve(maturities, yields):
    """
    Construct and visualize a yield curve.
    
    Parameters:
    maturities (list): Bond maturities in years
    yields (list): Corresponding yields as decimals
    
    Returns:
    tuple: (interpolated_curve_function, yield_curve_dataframe)
    """
    # Create cubic spline interpolation
    cs = CubicSpline(maturities, yields)
    
    # Create a smooth curve with more points
    x_smooth = np.linspace(min(maturities), max(maturities), 100)
    y_smooth = cs(x_smooth)
    
    # Create DataFrame for the yield curve
    yield_curve_df = pd.DataFrame({
        'Maturity': x_smooth,
        'Yield': y_smooth
    })
    
    # Visualize the yield curve
    plt.figure(figsize=(10, 6))
    plt.plot(x_smooth, y_smooth * 100, 'b-', label='Interpolated Yield Curve')
    plt.scatter(maturities, np.array(yields) * 100, c='red', label='Observed Yields')
    
    plt.title('U.S. Treasury Yield Curve')
    plt.xlabel('Maturity (Years)')
    plt.ylabel('Yield (%)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    return cs, yield_curve_df

def forward_rates(yield_curve_function, start_year, end_year):
    """
    Calculate implied forward rates from the yield curve.
    
    Parameters:
    yield_curve_function: Interpolated yield curve function
    start_year (float): Start of forward period in years
    end_year (float): End of forward period in years
    
    Returns:
    float: Implied forward rate for the period
    """
    r1 = yield_curve_function(start_year)
    r2 = yield_curve_function(end_year)
    
    # Calculate forward rate using the formula:
    # (1 + r2)^end_year = (1 + r1)^start_year * (1 + f)^(end_year - start_year)
    f = ((1 + r2) ** end_year / (1 + r1) ** start_year) ** (1 / (end_year - start_year)) - 1
    
    return f

# Example: U.S. Treasury yields (as of a specific date)
maturities = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]  # Years
yields = [0.0525, 0.0545, 0.0560, 0.0520, 0.0510, 0.0515, 0.0520, 0.0525, 0.0545, 0.0550]  # Decimal yields

# Construct the yield curve
curve_function, yield_curve_data = construct_yield_curve(maturities, yields)

# Calculate some forward rates
forward_1y_2y = forward_rates(curve_function, 1, 2)
forward_2y_5y = forward_rates(curve_function, 2, 5)
forward_5y_10y = forward_rates(curve_function, 5, 10)

print(f"1Y-2Y Forward Rate: {forward_1y_2y*100:.2f}%")
print(f"2Y-5Y Forward Rate: {forward_2y_5y*100:.2f}%")
print(f"5Y-10Y Forward Rate: {forward_5y_10y*100:.2f}%")

# Generate visualization
plt.show()
```

### LLM Implementation for Fixed Income Analysis

LLMs can provide valuable context and interpretation for fixed income markets and securities:

**Prompt to LLM:**

```
Analyze the current U.S. Treasury yield curve based on the following data (as of July 2025):

Maturity | Yield (%)
---------|----------
3-month  | 5.25
6-month  | 5.45
1-year   | 5.60
2-year   | 5.20
3-year   | 5.10
5-year   | 5.15
7-year   | 5.20
10-year  | 5.25
20-year  | 5.45
30-year  | 5.50

Please interpret this yield curve shape, discuss what it suggests about market expectations, and explain the implications for different types of investors and the broader economy. Also, comment on how this curve compares to historical patterns.
```

**Expected LLM Response:**

```
# Analysis of the July 2025 U.S. Treasury Yield Curve

## Yield Curve Shape and Classification

The yield curve you've provided exhibits a **humped with inversion** shape, which is rather unusual and complex:

1. **Short-end inversion (3M to 1Y)**: Yields rise from 5.25% at 3-months to 5.60% at 1-year
2. **Medium-term inversion (1Y to 3Y)**: Yields decline from 5.60% at 1-year to 5.10% at 3-years
3. **Long-end normalization (3Y to 30Y)**: Yields gradually rise from 5.10% at 3-years to 5.50% at 30-years

This complex structure suggests the market is pricing in several different economic scenarios and timeframes.

## Market Expectations Implied by the Curve

### Near-Term (0-1 Year)
The rising yields from 3-month to 1-year (5.25% to 5.60%) suggest:
- Expectations of one or more interest rate hikes by the Federal Reserve in the coming year
- Continued inflation concerns in the immediate future
- Relatively strong economic activity in the very near term

### Medium-Term (1-3 Years)
The sharp inversion from 1-year to 3-year (5.60% to 5.10%) indicates:
- Markets expect the Fed to begin cutting rates within 1-3 years
- Anticipation of economic slowdown or possible recession in this timeframe
- Resolution of current inflationary pressures

### Long-Term (3-30 Years)
The gradual rise from 3-year to 30-year (5.10% to 5.50%) suggests:
- Long-term inflation expectations remain anchored but elevated
- Eventual return to economic growth after the potential slowdown
- Term premium returning to more normal levels for longer maturities

## Implications for Different Investors

### Bond Investors
- **Short-term investors**: The elevated short-term yields offer attractive returns with minimal duration risk
- **Intermediate investors**: The 3-year point at 5.10% represents a potential sweet spot, offering relatively high yield with limited duration risk
- **Long-term investors**: The relatively flat structure from 5-30 years suggests limited additional compensation for extending maturity beyond 5 years

### Equity Investors
- The curve's inversion between 1-3 years signals caution, as yield curve inversions have historically preceded economic recessions
- Defensive sectors may outperform in the anticipated slowdown period
- Growth stocks could face pressure if interest rates remain elevated as projected in the near term

### Corporate Borrowers
- Corporations might benefit from issuing longer-term debt rather than short-term, given the inversion
- The 3-year point represents an optimal funding opportunity given the trough in the curve
- Companies should prepare for potential economic challenges in the 1-3 year timeframe

## Broader Economic Implications

1. **Monetary Policy Trajectory**: The curve suggests markets expect the Fed to maintain tight monetary policy in the near term, followed by easing in the 1-3 year timeframe

2. **Recession Probability**: The inversion between 1-year and 3-year yields is a significant warning sign for economic slowdown, though not as severe as a full 2-10 year inversion

3. **Inflation Expectations**: The elevated level of rates across all maturities (all above 5%) indicates persistent inflation concerns, though the market expects these to moderate

4. **Long-term Growth Outlook**: The modest upward slope from 3-30 years suggests reasonable long-term growth expectations after working through near-term challenges

## Historical Context

This yield curve structure is unusual compared to historical patterns:

1. **Overall Level**: The entire curve being above 5% reflects a higher interest rate environment than the post-2008 era but more aligned with pre-2008 norms

2. **Complex Shape**: The humped with partial inversion pattern is less common than classic normal, flat, or inverted curves

3. **Historical Comparison**: Similar complex structures appeared briefly during the dot-com bubble unwinding (2000-2001) and during the late 1970s high inflation era

4. **Predictive Power**: While traditional 2-10 year inversions have predicted recessions with high accuracy, this complex curve structure has fewer historical precedents to gauge predictive reliability

## Strategic Recommendations

Based on this yield curve:

1. **Fixed Income Strategy**: Consider a "barbell" approach with allocations to both short-term (under 1 year) and intermediate (3-5 year) securities, while underweighting the 1-2 year segment

2. **Duration Management**: The 3-year point offers the best value, suggesting a portfolio duration target around 3 years

3. **Economic Positioning**: Prepare for a potential economic slowdown in the 1-3 year timeframe, but not necessarily a severe recession

4. **Inflation Protection**: The elevated rates across the curve suggest continued inflation concerns, warranting some allocation to inflation-protected securities

5. **Monitoring Triggers**: Watch for changes in the 1-year to 3-year segment, as flattening would signal reduced recession concerns while deeper inversion would heighten them

In conclusion, this complex yield curve structure tells a nuanced story of near-term monetary tightening, medium-term economic challenges, and a subsequent return to more normal conditions. Investors should position defensively for the medium term while maintaining exposure to long-term growth opportunities.
```

## 3.4 Bond Pricing and Yield Calculations

Bond pricing and yield calculations form the foundation of fixed income analysis. In this section, we'll explore the mathematical relationships between bond prices, yields, and other key metrics, and implement these calculations using Excel, Python, and LLMs.

### Basic Bond Pricing Formula

The price of a bond is the present value of all its future cash flows:

$$P = \sum_{t=1}^{n} \frac{C}{(1+r)^t} + \frac{F}{(1+r)^n}$$

Where:
- $P$ is the bond price
- $C$ is the periodic coupon payment
- $F$ is the face value (par value)
- $r$ is the yield per period
- $n$ is the number of periods until maturity

For bonds with semi-annual coupons (common in the U.S.):

$$P = \sum_{t=1}^{2n} \frac{C/2}{(1+r/2)^t} + \frac{F}{(1+r/2)^{2n}}$$

Where:
- $r$ is the annual yield to maturity
- $n$ is the number of years until maturity

### Excel Implementation of Bond Pricing

Excel provides built-in functions for bond pricing:

```
# Price of a bond using PRICE function
=PRICE(settlement_date, maturity_date, coupon_rate, yield_to_maturity, redemption_value, frequency, basis)

# Example
=PRICE("2023-07-15", "2033-07-15", 0.035, 0.04, 100, 2, 0)  'Price of a 10-year bond with 3.5% coupon and 4% YTM

# Alternative using PV function
=PV(yield_per_period, number_of_periods, coupon_payment_per_period, face_value)

# Example
=PV(0.04/2, 10*2, 0.035*1000/2, 1000)  'Same 10-year bond with 3.5% coupon and 4% YTM
```

### Python Implementation of Bond Pricing and Analysis

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """
    Calculate the price of a bond.
    
    Parameters:
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    ytm (float): Annual yield to maturity as decimal
    years_to_maturity (float): Years until maturity
    periods_per_year (int): Coupon payments per year
    
    Returns:
    float: Bond price
    """
    # Periodic interest rate
    rate_per_period = ytm / periods_per_year
    
    # Number of periods
    n_periods = years_to_maturity * periods_per_year
    
    # Coupon payment per period
    coupon_per_period = coupon_rate * par / periods_per_year
    
    # Price calculation
    price = 0
    for t in range(1, int(n_periods) + 1):
        price += coupon_per_period / (1 + rate_per_period) ** t
    
    # Add present value of par
    price += par / (1 + rate_per_period) ** n_periods
    
    return price

def bond_duration_macaulay(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """
    Calculate the Macaulay duration of a bond.
    
    Parameters:
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    ytm (float): Annual yield to maturity as decimal
    years_to_maturity (float): Years until maturity
    periods_per_year (int): Coupon payments per year
    
    Returns:
    float: Macaulay duration in years
    """
    # Periodic interest rate
    rate_per_period = ytm / periods_per_year
    
    # Number of periods
    n_periods = years_to_maturity * periods_per_year
    
    # Coupon payment per period
    coupon_per_period = coupon_rate * par / periods_per_year
    
    # Current bond price
    price = bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year)
    
    # Calculate weighted present values
    weighted_pvs = 0
    for t in range(1, int(n_periods) + 1):
        # Present value of each cash flow
        pv = coupon_per_period / (1 + rate_per_period) ** t
        # For the final period, add the present value of par
        if t == n_periods:
            pv += par / (1 + rate_per_period) ** t
        # Weight by time period
        weighted_pvs += t * pv
    
    # Macaulay duration formula
    macaulay_duration = weighted_pvs / price
    
    # Convert to years
    return macaulay_duration / periods_per_year

def bond_duration_modified(macaulay_duration, ytm, periods_per_year=2):
    """
    Calculate the modified duration of a bond.
    
    Parameters:
    macaulay_duration (float): Macaulay duration in years
    ytm (float): Annual yield to maturity as decimal
    periods_per_year (int): Coupon payments per year
    
    Returns:
    float: Modified duration
    """
    return macaulay_duration / (1 + ytm / periods_per_year)

def bond_convexity(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """
    Calculate the convexity of a bond.
    
    Parameters:
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    ytm (float): Annual yield to maturity as decimal
    years_to_maturity (float): Years until maturity
    periods_per_year (int): Coupon payments per year
    
    Returns:
    float: Bond convexity
    """
    # Periodic interest rate
    rate_per_period = ytm / periods_per_year
    
    # Number of periods
    n_periods = years_to_maturity * periods_per_year
    
    # Coupon payment per period
    coupon_per_period = coupon_rate * par / periods_per_year
    
    # Current bond price
    price = bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year)
    
    # Calculate weighted present values for convexity
    convexity_sum = 0
    for t in range(1, int(n_periods) + 1):
        # Present value of each cash flow
        pv = coupon_per_period / (1 + rate_per_period) ** t
        # For the final period, add the present value of par
        if t == n_periods:
            pv += par / (1 + rate_per_period) ** t
        # Weight by time period squared + time period
        convexity_sum += (t * (t + 1) * pv) / (1 + rate_per_period) ** 2
    
    # Convexity formula
    convexity = convexity_sum / (price * (1 + rate_per_period) ** 2)
    
    # Convert to years and adjust for periodicity
    return convexity / (periods_per_year ** 2)

def bond_price_change_estimate(price, modified_duration, convexity, yield_change):
    """
    Estimate price change using duration and convexity.
    
    Parameters:
    price (float): Current bond price
    modified_duration (float): Modified duration
    convexity (float): Bond convexity
    yield_change (float): Change in yield in decimal form
    
    Returns:
    float: Estimated price change
    """
    # First-order approximation (duration effect)
    duration_effect = -modified_duration * yield_change
    
    # Second-order approximation (convexity effect)
    convexity_effect = 0.5 * convexity * (yield_change ** 2)
    
    # Total estimated price change percentage
    percentage_change = duration_effect + convexity_effect
    
    # Convert to dollar amount
    return price * percentage_change

def yield_to_maturity(price, par, coupon_rate, years_to_maturity, 
                     periods_per_year=2, precision=0.0001, max_iterations=100):
    """
    Calculate yield to maturity using numerical methods.
    
    Parameters:
    price (float): Bond price
    par (float): Par value
    coupon_rate (float): Annual coupon rate as decimal
    years_to_maturity (float): Years until maturity
    periods_per_year (int): Coupon payments per year
    precision (float): Desired precision of YTM calculation
    max_iterations (int): Maximum number of iterations for numerical method
    
    Returns:
    float: Yield to maturity as decimal
    """
    # Initial guesses
    if price < par:
        # Bond is trading at discount, ytm > coupon rate
        ytm_low = coupon_rate
        ytm_high = coupon_rate * 2
    elif price > par:
        # Bond is trading at premium, ytm < coupon rate
        ytm_low = 0
        ytm_high = coupon_rate
    else:
        # Bond is trading at par, ytm = coupon rate
        return coupon_rate
    
    # Bisection method
    for _ in range(max_iterations):
        ytm_mid = (ytm_low + ytm_high) / 2
        price_mid = bond_price(par, coupon_rate, ytm_mid, years_to_maturity, periods_per_year)
        
        if abs(price_mid - price) < precision:
            return ytm_mid
        
        if price_mid > price:
            ytm_low = ytm_mid
        else:
            ytm_high = ytm_mid
    
    # Return best estimate if max iterations reached
    return (ytm_low + ytm_high) / 2

# Example bond analysis
par = 1000
coupon_rate = 0.04  # 4%
ytm = 0.05  # 5%
years_to_maturity = 10
periods_per_year = 2

# Calculate bond metrics
price = bond_price(par, coupon_rate, ytm, years_to_maturity)
macaulay_duration = bond_duration_macaulay(par, coupon_rate, ytm, years_to_maturity)
modified_duration = bond_duration_modified(macaulay_duration, ytm)
convexity = bond_convexity(par, coupon_rate, ytm, years_to_maturity)

# Price change estimate for 1% increase in yield
yield_change = 0.01  # 100 basis points
price_change = bond_price_change_estimate(price, modified_duration, convexity, yield_change)

# Display results
print(f"Bond Price: ${price:.2f}")
print(f"Macaulay Duration: {macaulay_duration:.2f} years")
print(f"Modified Duration: {modified_duration:.2f}")
print(f"Convexity: {convexity:.4f}")
print(f"Estimated Price Change for 1% Yield Increase: ${price_change:.2f} ({price_change/price*100:.2f}%)")

# Calculate YTM for a given price
test_price = 950
calculated_ytm = yield_to_maturity(test_price, par, coupon_rate, years_to_maturity)
print(f"Yield to Maturity for a Bond Price of ${test_price:.2f}: {calculated_ytm*100:.2f}%")
```

### Key Bond Metrics and Their Interpretation

#### 1. Yield to Maturity (YTM)

Yield to Maturity is the total return anticipated on a bond if held until maturity. It considers:
- Coupon payments
- Capital gain or loss (difference between purchase price and par value)
- Time value of money

YTM assumes:
- All coupon payments are reinvested at the YTM rate
- The bond is held until maturity
- All payments are made as scheduled

#### 2. Current Yield

Current Yield represents the annual coupon payment relative to the current bond price:

$\text{Current Yield} = \frac{\text{Annual Coupon Payment}}{\text{Current Bond Price}}$

Current yield is simpler than YTM but ignores capital gains/losses and the time value of money.

#### 3. Yield to Call (YTC)

For callable bonds, Yield to Call calculates the yield if the bond is called at the earliest call date:

$\text{YTC} = \text{Yield if bond is called at the earliest call date}$

Investors should consider the lower of YTM and YTC as the "yield to worst" when evaluating callable bonds.

#### 4. Duration

Duration measures a bond's price sensitivity to interest rate changes:

1. **Macaulay Duration**: Weighted average time until cash flows are received, measured in years.

2. **Modified Duration**: Approximates the percentage price change for a 1% change in yield.
   $\text{Modified Duration} = \frac{\text{Macaulay Duration}}{1 + \frac{\text{YTM}}{\text{Frequency}}}$

3. **Effective Duration**: Used for bonds with embedded options, calculated using price changes for small yield shifts.

#### 5. Convexity

Convexity measures how duration changes as yields change, capturing the curvature of the price-yield relationship:

- Positive convexity is beneficial, as it means price increases more when yields fall than it decreases when yields rise
- Higher convexity provides better protection against large yield movements

The relationship between price changes, duration, and convexity can be approximated:

$\frac{\Delta P}{P} \approx -\text{Duration} \times \Delta y + \frac{1}{2} \times \text{Convexity} \times (\Delta y)^2$

Where:
- $\Delta P/P$ is the percentage price change
- $\Delta y$ is the yield change in decimal form

### LLM Implementation for Bond Analysis

LLMs can help interpret bond metrics and explain investment implications:

**Prompt to LLM:**

```
I'm analyzing a corporate bond with the following characteristics:

- Issuer: Tech Corporation (A+ rated)
- Par Value: $1,000
- Coupon Rate: 4.0% (semi-annual payments)
- Maturity: 10 years
- Current Price: $920.76
- Yield to Maturity: 5.25%
- Modified Duration: 7.86
- Convexity: 76.42

Interest rates are currently at 5%, and market analysts are divided on whether the Fed will raise or lower rates in the coming year.

Please interpret these bond metrics, explain what they tell me about this bond's risk and return characteristics, and provide investment advice based on different interest rate scenarios. Also, calculate how much this bond's price might change if interest rates increase or decrease by 1%.
```

**Expected LLM Response:**

```
# Tech Corporation Bond Analysis

## Bond Metrics Interpretation

### Core Characteristics
- **Price at Discount**: The bond is trading at $920.76, which is a 7.92% discount to its par value of $1,000. This discount immediately tells us that the market yield (5.25%) exceeds the coupon rate (4.0%).

- **Yield to Maturity (5.25%)**: This represents the total annualized return you would receive if you purchased the bond at $920.76 and held it until maturity, assuming all coupon payments are reinvested at this same rate. The YTM is higher than the coupon rate because of the price discount - you'll receive capital appreciation as the bond approaches par value at maturity.

- **Coupon vs. Market Rates**: The 4.0% coupon is below current market interest rates of 5%, which explains why the bond trades at a discount. Investors demand higher yields from new and existing bonds in a higher rate environment.

### Risk Metrics

- **Modified Duration (7.86)**: This key risk metric indicates that for every 1% change in interest rates, the bond's price will change by approximately 7.86% in the opposite direction. This is relatively high duration, reflecting the bond's longer maturity and relatively low coupon rate.

- **Convexity (76.42)**: This positive, high convexity value measures the curvature in the price-yield relationship. High convexity is generally favorable for bondholders as it means the bond's price will increase more when yields fall than it will decrease when yields rise by the same amount.

- **Credit Quality (A+)**: This investment-grade rating suggests relatively low default risk, though not the highest quality. The credit spread (portion of yield compensating for default risk) is likely around 0.25-0.50% above Treasuries of similar maturity.

## Price Change Scenarios

Let's calculate potential price changes using both duration-only and duration-plus-convexity approximations:

### Interest Rates Increase by 1% (to 6.25% YTM)

**Duration-only approximation**:
- Price change = -Modified Duration × Yield change
- Price change = -7.86 × 1% = -7.86%
- New price = $920.76 × (1 - 0.0786) = $848.40

**Duration + Convexity approximation**:
- Price change = -Duration × Yield change + ½ × Convexity × (Yield change)²
- Price change = -7.86 × 1% + 0.5 × 76.42 × (0.01)² = -7.86% + 0.38% = -7.48%
- New price = $920.76 × (1 - 0.0748) = $851.89

The convexity adjustment provides a slightly more optimistic price estimate, showing how the bond's high convexity helps mitigate some of the negative impact of rising rates.

### Interest Rates Decrease by 1% (to 4.25% YTM)

**Duration-only approximation**:
- Price change = -Modified Duration × Yield change
- Price change = -7.86 × (-1%) = +7.86%
- New price = $920.76 × (1 + 0.0786) = $993.16

**Duration + Convexity approximation**:
- Price change = -7.86 × (-1%) + 0.5 × 76.42 × (0.01)² = +7.86% + 0.38% = +8.24%
- New price = $920.76 × (1 + 0.0824) = $996.63

The convexity adjustment enhances the positive impact of falling interest rates, demonstrating the asymmetrical benefit of high convexity.

## Investment Advice for Different Scenarios

### Scenario 1: Interest Rates Rise Further

If you believe rates will continue to rise:
- **Cautious Approach**: This bond's high duration (7.86) makes it particularly vulnerable to rising rates. A 1% rate increase could result in a ~7.5% price decline.
- **Alternative Strategy**: Consider shorter-duration bonds (3-5 years) to reduce interest rate risk while still capturing yields above the 4% coupon rate.
- **Hold Decision**: If you plan to hold until maturity, price fluctuations matter less, and you'll still receive the 5.25% YTM, which is attractive for an A+ rated bond.

### Scenario 2: Interest Rates Decrease

If you believe rates will decline:
- **Aggressive Approach**: This bond becomes very attractive, as its high duration and convexity would amplify price gains. A 1% rate decrease could result in an ~8.2% price appreciation, plus you continue earning the 5.25% yield.
- **Opportunity**: The high convexity (76.42) means this bond would outperform others with similar duration but lower convexity in a falling rate environment.
- **Enhancement Strategy**: Consider purchasing additional bonds or similar long-duration instruments to maximize returns in a falling rate environment.

### Scenario 3: Interest Rates Remain Stable

If you believe rates will hold steady:
- **Income Focus**: The 5.25% YTM is attractive in a stable rate environment, especially for an A+ rated bond.
- **Gradual Appreciation**: The bond will naturally appreciate from its current price ($920.76) toward par ($1,000) over time, providing capital gains in addition to coupon income.
- **Reinvestment Consideration**: Stable rates mean coupon payments can be reinvested at similar yields, supporting the YTM assumption.

## Strategic Recommendations

1. **Time Horizon Alignment**:
   - If your investment horizon matches the 10-year maturity, consider holding regardless of short-term rate movements, as you'll receive the 5.25% YTM.
   - If your horizon is shorter, be more cautious about duration risk, especially in a rising rate environment.

2. **Portfolio Context**:
   - This bond could serve as a high-quality, relatively high-yield component of a diversified fixed income portfolio.
   - Its high duration makes it an effective counterbalance to shorter-term bonds or floating-rate instruments.

3. **Tactical Positioning**:
   - If you have strong conviction about future rate movements, this high-duration, high-convexity bond offers significant potential for expressing that view.
   - For a neutral position, consider pairing this with shorter-duration instruments to moderate overall portfolio duration.

4. **Value Assessment**:
   - At current yields, this A+ rated corporate bond likely offers a reasonable spread over Treasuries, providing compensation for credit risk.
   - The high convexity is a valuable feature that is not always explicitly priced by the market.

This bond offers an attractive yield with moderate credit risk, but comes with significant interest rate sensitivity. Your investment decision should align with both your interest rate outlook and your overall portfolio strategy.
```

### Yield Curve Analysis and Interest Rate Risk

The relationship between bond prices and interest rates is fundamental to fixed income investing. As interest rates rise, bond prices fall, and vice versa. This inverse relationship is quantified through duration and convexity.

#### Interest Rate Risk Components

1. **Price Risk**: Risk that rising interest rates will decrease bond prices.

2. **Reinvestment Risk**: Risk that falling interest rates will force reinvestment of coupon payments at lower rates.

3. **Income Risk**: Risk that income from the bond portfolio will decline due to changing interest rates.

#### Managing Interest Rate Risk

1. **Duration Management**: Adjust portfolio duration based on interest rate outlook.
   - Shorten duration when rates are expected to rise
   - Lengthen duration when rates are expected to fall

2. **Laddering**: Create a bond ladder with staggered maturities.
   - Provides regular reinvestment opportunities
   - Reduces the impact of interest rate changes

3. **Barbell Strategy**: Invest in short-term and long-term bonds, avoiding intermediate maturities.
   - Provides both liquidity and higher yields
   - Can be adjusted to express interest rate views

4. **Immunization**: Match duration of assets with duration of liabilities.
   - Protects against interest rate movements
   - Useful for institutional investors with defined liabilities

#### Python Implementation of Bond Portfolio Analytics

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class BondPortfolio:
    """Class for analyzing a portfolio of bonds."""
    
    def __init__(self, bonds=None):
        """
        Initialize bond portfolio.
        
        Parameters:
        bonds (list): List of dictionaries with bond information
                     Each bond should have: par, coupon_rate, ytm, years_to_maturity, 
                                           market_value, and optionally weight
        """
        self.bonds = bonds or []
        self._normalize_weights()
        self._calculate_portfolio_metrics()
    
    def _normalize_weights(self):
        """Normalize weights to sum to 1 if not provided or not summing to 1."""
        # Check if weights are provided
        has_weights = all('weight' in bond for bond in self.bonds)
        
        if not has_weights:
            # Assign weights based on market value
            total_market_value = sum(bond['market_value'] for bond in self.bonds)
            for bond in self.bonds:
                bond['weight'] = bond['market_value'] / total_market_value
        else:
            # Normalize provided weights
            total_weight = sum(bond['weight'] for bond in self.bonds)
            if abs(total_weight - 1.0) > 1e-6:  # Not approximately 1
                for bond in self.bonds:
                    bond['weight'] = bond['weight'] / total_weight
    
    def add_bond(self, bond):
        """Add a bond to the portfolio and recalculate metrics."""
        self.bonds.append(bond)
        self._normalize_weights()
        self._calculate_portfolio_metrics()
    
    def _calculate_bond_metrics(self, bond):
        """Calculate metrics for an individual bond."""
        # Calculate price if not provided
        if 'market_value' not in bond:
            bond['market_value'] = bond_price(
                bond['par'], bond['coupon_rate'], bond['ytm'], 
                bond['years_to_maturity'], bond.get('periods_per_year', 2)
            )
        
        # Calculate duration and convexity
        bond['macaulay_duration'] = bond_duration_macaulay(
            bond['par'], bond['coupon_rate'], bond['ytm'], 
            bond['years_to_maturity'], bond.get('periods_per_year', 2)
        )
        
        bond['modified_duration'] = bond_duration_modified(
            bond['macaulay_duration'], bond['ytm'], bond.get('periods_per_year', 2)
        )
        
        bond['convexity'] = bond_convexity(
            bond['par'], bond['coupon_rate'], bond['ytm'], 
            bond['years_to_maturity'], bond.get('periods_per_year', 2)
        )
        
        # Calculate yield metrics
        bond['current_yield'] = (bond['coupon_rate'] * bond['par']) / bond['market_value']
        
        return bond
    
    def _calculate_portfolio_metrics(self):
        """Calculate weighted metrics for the entire portfolio."""
        if not self.bonds:
            self.weighted_ytm = 0
            self.weighted_duration = 0
            self.weighted_convexity = 0
            self.weighted_current_yield = 0
            return
        
        # Calculate metrics for each bond
        for i, bond in enumerate(self.bonds):
            self.bonds[i] = self._calculate_bond_metrics(bond)
        
        # Calculate weighted portfolio metrics
        self.weighted_ytm = sum(bond['ytm'] * bond['weight'] for bond in self.bonds)
        self.weighted_duration = sum(bond['modified_duration'] * bond['weight'] for bond in self.bonds)
        self.weighted_convexity = sum(bond['convexity'] * bond['weight'] for bond in self.bonds)
        self.weighted_current_yield = sum(bond['current_yield'] * bond['weight'] for bond in self.bonds)
        self.total_market_value = sum(bond['market_value'] * bond['weight'] for bond in self.bonds)
    
    def simulate_yield_change(self, yield_change):
        """
        Simulate the impact of a yield change on the portfolio.
        
        Parameters:
        yield_change (float): Change in yields in decimal form
        
        Returns:
        dict: Results of the simulation
        """
        # Calculate price change using duration and convexity
        duration_effect = -self.weighted_duration * yield_change
        convexity_effect = 0.5 * self.weighted_convexity * (yield_change ** 2)
        pct_price_change = duration_effect + convexity_effect
        
        # Calculate new value
        new_value = self.total_market_value * (1 + pct_price_change)
        
        return {
            'original_value': self.total_market_value,
            'new_value': new_value,
            'dollar_change': new_value - self.total_market_value,
            'percent_change': pct_price_change * 100,
            'duration_effect': duration_effect * 100,
            'convexity_effect': convexity_effect * 100
        }
    
    def ladder_analysis(self):
        """
        Analyze the bond ladder structure of the portfolio.
        
        Returns:
        DataFrame: Analysis of the bond ladder
        """
        # Extract maturity and weight information
        maturities = [bond['years_to_maturity'] for bond in self.bonds]
        weights = [bond['weight'] for bond in self.bonds]
        market_values = [bond['market_value'] * bond['weight'] for bond in self.bonds]
        
        # Create ladder analysis DataFrame
        ladder_df = pd.DataFrame({
            'Years_to_Maturity': maturities,
            'Weight': weights,
            'Market_Value': market_values
        })
        
        # Group by maturity buckets
        ladder_df['Maturity_Bucket'] = pd.cut(
            ladder_df['Years_to_Maturity'],
            bins=[0, 1, 2, 3, 5, 7, 10, 20, 30, float('inf')],
            labels=['0-1', '1-2', '2-3', '3-5', '5-7', '7-10', '10-20', '20-30', '30+']
        )
        
        # Aggregate by bucket
        bucket_analysis = ladder_df.groupby('Maturity_Bucket').agg({
            'Weight': 'sum',
            'Market_Value': 'sum'
        }).reset_index()
        
        return bucket_analysis
    
    def interest_rate_risk_profile(self, yield_changes=None):
        """
        Generate interest rate risk profile for various yield changes.
        
        Parameters:
        yield_changes (list): List of yield changes to simulate
        
        Returns:
        DataFrame: Results of yield change simulations
        """
        if yield_changes is None:
            yield_changes = [-0.02, -0.01, -0.005, 0, 0.005, 0.01, 0.02]
        
        results = []
        for change in yield_changes:
            sim_result = self.simulate_yield_change(change)
            sim_result['yield_change'] = change * 100  # Convert to percentage
            results.append(sim_result)
        
        return pd.DataFrame(results)
    
    def plot_interest_rate_risk(self):
        """Plot the portfolio's response to interest rate changes."""
        # Generate data
        yield_changes = np.linspace(-0.03, 0.03, 100)
        price_changes = []
        
        for change in yield_changes:
            result = self.simulate_yield_change(change)
            price_changes.append(result['percent_change'])
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(yield_changes * 100, price_changes, 'b-', linewidth=2)
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        plt.title('Bond Portfolio Price Sensitivity to Interest Rate Changes')
        plt.xlabel('Change in Interest Rates (Percentage Points)')
        plt.ylabel('Portfolio Price Change (%)')
        plt.grid(True, alpha=0.3)
        
        # Add key points
        plt.scatter([yield_changes[0] * 100, 0, yield_changes[-1] * 100],
                   [price_changes[0], 0, price_changes[-1]], 
                   c=['g', 'k', 'r'], s=50)
        
        plt.annotate(f"{price_changes[0]:.2f}%", 
                    (yield_changes[0] * 100, price_changes[0]),
                    xytext=(-10, -20), textcoords='offset points')
        
        plt.annotate(f"{price_changes[-1]:.2f}%", 
                    (yield_changes[-1] * 100, price_changes[-1]),
                    xytext=(10, -20), textcoords='offset points')
        
        plt.tight_layout()
        return plt

# Example usage
corporate_bond = {
    'par': 1000,
    'coupon_rate': 0.04,  # 4%
    'ytm': 0.05,  # 5%
    'years_to_maturity': 10,
    'market_value': 920.76,
    'weight': 0.6
}

treasury_bond = {
    'par': 1000,
    'coupon_rate': 0.035,  # 3.5%
    'ytm': 0.045,  # 4.5%
    'years_to_maturity': 5,
    'market_value': 952.43,
    'weight': 0.4
}

# Create portfolio
portfolio = BondPortfolio([corporate_bond, treasury_bond])

# Display portfolio metrics
print(f"Portfolio Duration: {portfolio.weighted_duration:.2f}")
print(f"Portfolio Convexity: {portfolio.weighted_convexity:.2f}")
print(f"Portfolio YTM: {portfolio.weighted_ytm*100:.2f}%")
print(f"Portfolio Current Yield: {portfolio.weighted_current_yield*100:.2f}%")

# Analyze impact of interest rate changes
risk_profile = portfolio.interest_rate_risk_profile()
print("\nInterest Rate Risk Profile:")
print(risk_profile[['yield_change', 'percent_change', 'duration_effect', 'convexity_effect']])

# Analyze bond ladder structure
ladder = portfolio.ladder_analysis()
print("\nBond Ladder Analysis:")
print(ladder)

# Plot interest rate risk
portfolio.plot_interest_rate_risk()
plt.show()
```

### Credit Risk and Bond Ratings

In addition to interest rate risk, fixed income investors must consider credit risk—the risk that the issuer will default on payments. Bond ratings from agencies like S&P, Moody's, and Fitch provide a standardized assessment of creditworthiness.

#### Bond Rating Scales

| S&P/Fitch | Moody's | Category | Description |
|-----------|---------|----------|-------------|
| AAA       | Aaa     | Investment Grade | Highest quality, minimal risk |
| AA+/AA/AA-| Aa1/Aa2/Aa3 | Investment Grade | High quality, very low risk |
| A+/A/A-   | A1/A2/A3 | Investment Grade | Upper-medium grade, low risk |
| BBB+/BBB/BBB- | Baa1/Baa2/Baa3 | Investment Grade | Medium grade, moderate risk |
| BB+/BB/BB- | Ba1/Ba2/Ba3 | High Yield / Junk | Speculative, substantial risk |
| B+/B/B-   | B1/B2/B3 | High Yield / Junk | Highly speculative |
| CCC+/CCC/CCC- | Caa1/Caa2/Caa3 | High Yield / Junk | Poor quality, very high risk |
| CC        | Ca      | High Yield / Junk | Highly vulnerable to default |
| C         | C       | High Yield / Junk | Extremely vulnerable to default |
| D         | D       | Default | In default |

#### Credit Spreads

Credit spreads represent the additional yield investors demand for taking on credit risk:

$\text{Credit Spread} = \text{Corporate Bond Yield} - \text{Treasury Yield}$

These spreads typically widen during economic downturns and narrow during expansions.

### Fixed Income Portfolio Strategies

Several strategies can enhance fixed income portfolio performance:

1. **Credit Selection**: Identifying undervalued bonds with improving credit profiles.

2. **Sector Rotation**: Shifting allocations among Treasury, corporate, municipal, and securitized sectors based on relative value.

3. **Yield Curve Positioning**: Concentrating investments in yield curve segments expected to outperform.

4. **Duration Management**: Adjusting portfolio duration based on interest rate forecasts.

5. **Security Selection**: Identifying bonds with attractive structures, such as call protection or favorable covenants.

## Exercises

### Equity Analysis for Tech Companies

1. **Common and Preferred Stock Comparison**
   
   For the following tech companies—NVIDIA (NVDA), Intel (INTC), and Meta Platforms (META)—analyze their common stock characteristics:

   a) Using Excel, calculate and compare the following metrics:
      - P/E ratio
      - Dividend yield
      - Market capitalization
      - Historical price performance (5-year)
   
   b) Using Python, create a function to retrieve and analyze this data from an API
   
   c) Using an LLM, interpret these metrics and discuss the investment implications

2. **Equity Valuation Model Implementation**
   
   Value Tesla (TSLA) stock using multiple approaches:
   
   a) Using Excel, implement:
      - Gordon Growth Model
      - Two-stage Dividend Discount Model
      - P/E-based relative valuation
   
   b) Using Python, implement the same models and compare results
   
   c) Using an LLM, analyze the assumptions behind each model and explain why they yield different results

3. **Preferred Stock Analysis**
   
   Research and analyze a tech company's preferred stock:
   
   a) Find a technology company with preferred stock outstanding
   
   b) Using Excel, calculate its yield metrics
   
   c) Using Python, compare its risk-return profile to the company's common stock and bonds
   
   d) Using an LLM, explain why a company might issue preferred stock and who might invest in it

### Dividend Calculations and Yield Metrics

1. **Dividend Analysis**
   
   For Qualcomm (QCOM), Cisco (CSCO), and Oracle (ORCL):
   
   a) Using Excel, calculate:
      - Historical dividend growth rate
      - Dividend payout ratio
      - Dividend yield
      - Total return (price appreciation + dividends)
   
   b) Using Python, create visualizations of dividend growth over time
   
   c) Using an LLM, analyze each company's dividend policy and sustainability

2. **Dividend Reinvestment Calculator**
   
   Create a dividend reinvestment calculator:
   
   a) Using Excel, build a model that shows the impact of reinvesting dividends vs. taking cash
   
   b) Using Python, create an interactive version with visualization
   
   c) Using an LLM, explain the power of dividend reinvestment and compounding

3. **Ex-Dividend Date Trading Strategy**
   
   Research and analyze the ex-dividend date phenomenon:
   
   a) Using Excel, analyze stock price behavior around ex-dividend dates
   
   b) Using Python, test a trading strategy based on ex-dividend dates
   
   c) Using an LLM, explain the theoretical and practical aspects of ex-dividend date trading

### Bond Pricing with Excel, Python, and LLMs

1. **Corporate Bond Analysis**
   
   For a tech company corporate bond (e.g., Apple 3.85% 2043):
   
   a) Using Excel, calculate:
      - Current price
      - Yield to maturity
      - Duration and convexity
      - Interest rate sensitivity
   
   b) Using Python, implement the same calculations and verify the results
   
   c) Using an LLM, interpret these metrics and discuss the investment implications

2. **Bond Portfolio Construction**
   
   Create a diversified bond portfolio:
   
   a) Using Excel, build a model with at least 5 different bonds
   
   b) Using Python, calculate portfolio metrics (weighted duration, convexity, yield)
   
   c) Using an LLM, recommend an optimal allocation based on different interest rate scenarios

3. **Credit Analysis**
   
   Analyze credit risk for tech company bonds:
   
   a) Using Excel, compare yields and spreads across different credit ratings
   
   b) Using Python, analyze historical spread behavior during market stress
   
   c) Using an LLM, discuss the relationship between credit ratings, yields, and default risk

### Yield Curve Construction and Analysis

1. **Yield Curve Visualization**
   
   Using current market data:
   
   a) Using Excel, construct and visualize the Treasury yield curve
   
   b) Using Python, implement more sophisticated yield curve models
   
   c) Using an LLM, interpret the current yield curve shape and its economic implications

2. **Forward Rate Calculation**
   
   Calculate implied forward rates:
   
   a) Using Excel, derive 1-year forward rates from the yield curve
   
   b) Using Python, create a visualization of the forward curve
   
   c) Using an LLM, explain what forward rates imply about market expectations

3. **Yield Curve Trading Strategies**
   
   Research and analyze yield curve trading strategies:
   
   a) Using Excel, model bullet, barbell, and ladder strategies
   
   b) Using Python, backtest these strategies using historical data
   
   c) Using an LLM, explain which strategy might work best in different interest rate environments

By completing these exercises, you'll gain practical experience applying equity and fixed income concepts using all three computational approaches. The combination of Excel, Python, and LLMs provides a powerful toolkit for analyzing and interpreting financial securities, enhancing your ability to make informed investment decisions.
