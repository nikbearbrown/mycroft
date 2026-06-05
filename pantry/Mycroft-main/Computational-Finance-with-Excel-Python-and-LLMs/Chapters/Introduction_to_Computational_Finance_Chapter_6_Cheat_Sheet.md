# Chapter 6: Investment Process - Margin Accounts and Short Selling

## 6.1 Margin Account Mechanics

### Basic Margin Concepts

**Key Components:**
- **Equity** = Total Value of Securities - Borrowed Amount (Debit Balance)
- **Margin Loan** = Total Value of Securities - Equity
- **Margin Percentage** = Equity / Total Value of Securities

**Excel Implementation:**
```excel
'Calculate Equity
=TotalSecuritiesValue-MarginLoan

'Calculate Margin Percentage
=Equity/TotalSecuritiesValue
```

**Python Implementation:**
```python
def calculate_margin_metrics(total_securities_value, margin_loan):
    equity = total_securities_value - margin_loan
    margin_percentage = equity / total_securities_value
    leverage_ratio = total_securities_value / equity
    
    return {
        'equity': equity,
        'margin_percentage': margin_percentage,
        'leverage_ratio': leverage_ratio
    }
```

### Margin Interest

```
Annual Interest Cost = Average Loan Balance × Interest Rate
```

**Excel Implementation:**
```excel
'Calculate interest cost
=AverageLoanBalance*AnnualInterestRate*DaysOutstanding/365
```

**Python Implementation:**
```python
def calculate_margin_interest(loan_amount, annual_rate, days):
    return loan_amount * annual_rate * days / 365
```

## 6.2 Initial and Maintenance Margin Requirements

### Initial Margin Requirements

- **Regulation T**: Standard initial margin = 50%
- **Maximum Purchase Power**:
  ```
  Maximum Purchase = Cash / Initial Margin Requirement
  ```

**Excel Implementation:**
```excel
'Calculate maximum purchase power
=CashDeposit/InitialMarginRequirement
```

**Python Implementation:**
```python
def max_purchase_power(cash_deposit, initial_margin_requirement):
    return cash_deposit / initial_margin_requirement
```

### Maintenance Margin Requirements

- **FINRA minimum**: 25%
- **Broker requirements**: Typically 30-40%

**Margin Call Threshold:**
Triggered when: `Equity / Market Value < Maintenance Margin Requirement`

**Margin Call Price:**
```
Margin Call Price = Loan Amount / (Shares × (1 - Maintenance Margin))
```

**Excel Implementation:**
```excel
'Calculate margin call price
=LoanAmount/(Shares*(1-MaintenanceMargin))
```

**Python Implementation:**
```python
def margin_call_price(loan_amount, shares, maintenance_margin):
    return loan_amount / (shares * (1 - maintenance_margin))
```

## 6.3 Short Selling Procedures and Risks

### Short Position Metrics

- **Short Equity** = Proceeds from Short Sale + Initial Margin - (Current Price × Shares)
- **Short Margin Percentage** = Short Equity / (Current Price × Shares)

**Excel Implementation:**
```excel
'Calculate short equity
=ShortSaleProceeds+InitialMargin-(CurrentPrice*Shares)

'Calculate short margin percentage
=ShortEquity/(CurrentPrice*Shares)
```

**Python Implementation:**
```python
def calculate_short_position(short_sale_proceeds, initial_margin, current_price, shares):
    market_value = current_price * shares
    short_equity = short_sale_proceeds + initial_margin - market_value
    short_margin_percentage = short_equity / market_value
    
    return {
        'short_equity': short_equity,
        'short_margin_percentage': short_margin_percentage
    }
```

### Short Selling Returns

**Return Formula:**
```
Return = (Initial Price - Final Price) / Initial Margin
```

**Return Including Costs:**
```
Return = (Initial Price - Final Price - Borrowing Costs - Dividends Paid) / Initial Margin
```

**Excel Implementation:**
```excel
'Calculate short selling return
=(InitialPrice-FinalPrice)/InitialMargin

'Including costs
=(InitialPrice-FinalPrice-BorrowingCosts-DividendsPaid)/InitialMargin
```

**Python Implementation:**
```python
def short_selling_return(initial_price, final_price, initial_margin, 
                        borrowing_costs=0, dividends_paid=0):
    gross_profit = initial_price - final_price
    net_profit = gross_profit - borrowing_costs - dividends_paid
    return net_profit / initial_margin
```

### Short Selling Risks

| Risk Type | Description |
|-----------|-------------|
| **Unlimited Loss** | Prices can rise indefinitely, unlike long positions limited to 100% loss |
| **Short Squeeze** | Heavily shorted stock rises sharply, forcing short sellers to cover |
| **Buy-In Risk** | Lender can recall shares at any time |
| **Dividend Payments** | Short seller must pay dividends issued during short position |
| **Borrowing Costs** | Fees for borrowing shares (annualized rate) |

## 6.4 Regulatory Considerations

### Regulation T

- Sets initial margin requirement at 50%
- Applies to both long and short positions
- Establishes payment timing requirements

### FINRA Rule 4210

- Establishes minimum maintenance margin of 25%
- Defines special requirements for certain securities
- Outlines procedures for margin calls

### SEC Regulation SHO

- Requires "locate" of shares before short selling
- Includes "close-out" requirements for failure to deliver
- Implemented temporary short sale restrictions during market stress

## Decision Tools and Formulas

| Calculation | Formula | Purpose |
|-------------|---------|---------|
| **Long Position Leverage** | Total Securities Value / Equity | Measures amplification of returns |
| **Break-even Price Change** | Interest Rate × Leverage Ratio | Required price increase to cover interest |
| **Short Position Break-even** | (Borrowing Fee + Dividends) / Initial Price | Required price decrease to cover costs |
| **Margin Call Buffer** | Current Margin % - Maintenance Margin % | Cushion before margin call |

## Quick Reference: Margin Examples

| Scenario | Starting Point | Result |
|----------|----------------|--------|
| **$10K cash, 50% margin** | Can buy $20K in securities | Initial margin = 50% |
| **Stock falls 20%** | $20K → $16K value, $10K loan | New margin = 37.5% |
| **Maintenance margin 30%** | Margin call at 30% | Triggered at $14.29K value |
| **$10K short at $50/share** | 200 shares short, $5K initial margin | Margin call at $72.92/share |

## Common Calculations Walkthrough

### Long Position Example

```python
# Initial setup
cash = 10000
share_price = 50
shares = 300  # Buy 300 shares
initial_margin_req = 0.5
maintenance_margin = 0.3

# Position metrics
position_value = share_price * shares  # $15,000
loan_amount = position_value - cash  # $5,000
initial_margin = cash / position_value  # 66.7%

# Margin call calculation
margin_call_price = loan_amount / (shares * (1 - maintenance_margin))  # $23.81
```

### Short Position Example

```python
# Initial setup
cash = 10000  # Initial margin deposit
share_price = 50
shares = 200  # Short 200 shares
initial_margin_req = 0.5
maintenance_margin = 0.3

# Position metrics
short_value = share_price * shares  # $10,000
short_proceeds = short_value  # $10,000

# Margin call calculation
margin_call_price = share_price * (1 + initial_margin_req / (1 - maintenance_margin) - initial_margin_req)  # $72.92
```