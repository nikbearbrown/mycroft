# Chapter 5: Time Value of Money and Discounted Cash Flows

## 5.1 Present and Future Value Calculations

The time value of money is a fundamental concept in finance based on the principle that money available today is worth more than the same amount in the future due to its potential earning capacity. This section explores the mathematical relationships between present values (PV) and future values (FV) and their applications in financial decision-making.

### Basic Time Value Concepts

The relationship between present and future values is governed by compounding and discounting:

**Compounding** moves money forward in time:
- Future Value = Present Value × (1 + r)^t

**Discounting** moves money backward in time:
- Present Value = Future Value ÷ (1 + r)^t

Where:
- r = interest rate per period
- t = number of periods

### Future Value (FV) Calculation

Future value represents the value of a current asset at a specified date in the future, assuming a particular rate of return or interest rate.

**Formula**:
FV = PV × (1 + r)^t

**Excel Implementation**:
```excel
=PV*(1+r)^t

'Using Excel's FV function:
=FV(rate, nper, pmt, [pv], [type])
```

**Python Implementation**:
```python
def future_value(present_value, rate, periods):
    """
    Calculate future value of a present sum.
    
    Parameters:
    present_value (float): Initial investment
    rate (float): Interest rate per period (decimal)
    periods (int): Number of periods
    
    Returns:
    float: Future value
    """
    return present_value * (1 + rate) ** periods

# Example
initial_investment = 10000
annual_rate = 0.08
years = 5

fv = future_value(initial_investment, annual_rate, years)
print(f"Future value after {years} years: ${fv:.2f}")
```

### Present Value (PV) Calculation

Present value is the current worth of a future sum of money, given a specified rate of return. It's essentially the inverse of future value calculation.

**Formula**:
PV = FV ÷ (1 + r)^t

**Excel Implementation**:
```excel
=FV/(1+r)^t

'Using Excel's PV function:
=PV(rate, nper, pmt, [fv], [type])
```

**Python Implementation**:
```python
def present_value(future_value, rate, periods):
    """
    Calculate present value of a future sum.
    
    Parameters:
    future_value (float): Future amount
    rate (float): Discount rate per period (decimal)
    periods (int): Number of periods
    
    Returns:
    float: Present value
    """
    return future_value / (1 + rate) ** periods

# Example
future_amount = 15000
annual_rate = 0.07
years = 4

pv = present_value(future_amount, annual_rate, years)
print(f"Present value: ${pv:.2f}")
```

### Net Present Value (NPV)

NPV is used to determine the present value of an investment by the discounted sum of all cash flows received from the project.

**Formula**:
NPV = CF₀ + CF₁/(1+r)¹ + CF₂/(1+r)² + ... + CFₙ/(1+r)ⁿ

Where:
- CF₀ = Initial investment (usually negative)
- CFᵢ = Cash flow in period i
- r = Discount rate
- n = Total number of periods

**Excel Implementation**:
```excel
=NPV(rate, value1, [value2], ...) + CF₀
'Note: NPV function doesn't include the initial investment

'Alternative manual calculation:
=CF₀ + CF₁/(1+r)^1 + CF₂/(1+r)^2 + ... + CFₙ/(1+r)^n
```

**Python Implementation**:
```python
def npv(rate, cash_flows):
    """
    Calculate Net Present Value of a series of cash flows.
    
    Parameters:
    rate (float): Discount rate per period (decimal)
    cash_flows (list): Series of cash flows, where cash_flows[0] is the initial investment
    
    Returns:
    float: Net Present Value
    """
    npv_value = cash_flows[0]  # Initial investment
    
    for t, cf in enumerate(cash_flows[1:], 1):
        npv_value += cf / (1 + rate) ** t
        
    return npv_value

# Example
cash_flows = [-50000, 15000, 18000, 20000, 25000]  # Initial investment and subsequent cash flows
discount_rate = 0.10

investment_npv = npv(discount_rate, cash_flows)
print(f"NPV: ${investment_npv:.2f}")
```

### Internal Rate of Return (IRR)

IRR is the discount rate that makes the NPV of all cash flows equal to zero. It represents the annualized effective compounded return rate that can be earned on the invested capital.

**Formula**:
Find r such that: 0 = CF₀ + CF₁/(1+r)¹ + CF₂/(1+r)² + ... + CFₙ/(1+r)ⁿ

**Excel Implementation**:
```excel
=IRR(values, [guess])
'where values is the range containing cash flows, and guess is an optional starting point
```

**Python Implementation**:
```python
from scipy import optimize

def irr(cash_flows):
    """
    Calculate Internal Rate of Return of a series of cash flows.
    
    Parameters:
    cash_flows (list): Series of cash flows, where cash_flows[0] is the initial investment
    
    Returns:
    float: Internal Rate of Return
    """
    def npv_equation(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
    
    # Use numerical methods to find the root of the NPV equation
    return optimize.newton(npv_equation, 0.1)  # 0.1 is an initial guess

# Example
cash_flows = [-100000, 30000, 35000, 40000, 45000]  # Initial investment and subsequent cash flows

try:
    rate_of_return = irr(cash_flows)
    print(f"IRR: {rate_of_return:.2%}")
except:
    print("Could not calculate IRR. Check cash flows.")
```

## 5.2 Annuities and Perpetuities

Annuities and perpetuities are specific patterns of cash flows that are commonly encountered in finance. Understanding how to value these streams of payments is essential for various financial applications.

### Ordinary Annuities

An ordinary annuity is a series of equal payments made at the end of consecutive periods over a fixed duration.

#### Present Value of an Ordinary Annuity (PVA)

**Formula**:
PVA = PMT × [(1 - (1 + r)^(-n)) / r]

Where:
- PMT = Payment per period
- r = Interest rate per period
- n = Number of periods

**Excel Implementation**:
```excel
=PMT*(1-(1+r)^(-n))/r

'Using Excel's PV function for annuity:
=PV(rate, nper, pmt, [fv], [type])
'where type=0 for ordinary annuity (default)
```

**Python Implementation**:
```python
def pv_ordinary_annuity(payment, rate, periods):
    """
    Calculate present value of an ordinary annuity.
    
    Parameters:
    payment (float): Payment per period
    rate (float): Interest rate per period (decimal)
    periods (int): Number of periods
    
    Returns:
    float: Present value
    """
    return payment * ((1 - (1 + rate) ** -periods) / rate)

# Example
annual_payment = 5000
annual_rate = 0.06
years = 10

pv = pv_ordinary_annuity(annual_payment, annual_rate, years)
print(f"Present value of ordinary annuity: ${pv:.2f}")
```

#### Future Value of an Ordinary Annuity (FVA)

**Formula**:
FVA = PMT × [((1 + r)^n - 1) / r]

**Excel Implementation**:
```excel
=PMT*((1+r)^n-1)/r

'Using Excel's FV function for annuity:
=FV(rate, nper, pmt, [pv], [type])
'where type=0 for ordinary annuity (default)
```

**Python Implementation**:
```python
def fv_ordinary_annuity(payment, rate, periods):
    """
    Calculate future value of an ordinary annuity.
    
    Parameters:
    payment (float): Payment per period
    rate (float): Interest rate per period (decimal)
    periods (int): Number of periods
    
    Returns:
    float: Future value
    """
    return payment * ((1 + rate) ** periods - 1) / rate

# Example
annual_deposit = 3000
annual_rate = 0.07
years = 15

fv = fv_ordinary_annuity(annual_deposit, annual_rate, years)
print(f"Future value of ordinary annuity: ${fv:.2f}")
```

### Annuities Due

An annuity due is a series of equal payments made at the beginning of consecutive periods over a fixed duration.

#### Present Value of an Annuity Due

**Formula**:
PV Annuity Due = PV Ordinary Annuity × (1 + r)

**Excel Implementation**:
```excel
=PMT*(1-(1+r)^(-n))/r*(1+r)

'Using Excel's PV function for annuity due:
=PV(rate, nper, pmt, [fv], 1)
'where type=1 for annuity due
```

**Python Implementation**:
```python
def pv_annuity_due(payment, rate, periods):
    """
    Calculate present value of an annuity due.
    
    Parameters:
    payment (float): Payment per period
    rate (float): Interest rate per period (decimal)
    periods (int): Number of periods
    
    Returns:
    float: Present value
    """
    return pv_ordinary_annuity(payment, rate, periods) * (1 + rate)

# Example
annual_payment = 5000
annual_rate = 0.06
years = 10

pv = pv_annuity_due(annual_payment, annual_rate, years)
print(f"Present value of annuity due: ${pv:.2f}")
```

#### Future Value of an Annuity Due

**Formula**:
FV Annuity Due = FV Ordinary Annuity × (1 + r)

**Excel Implementation**:
```excel
=PMT*((1+r)^n-1)/r*(1+r)

'Using Excel's FV function for annuity due:
=FV(rate, nper, pmt, [pv], 1)
'where type=1 for annuity due
```

**Python Implementation**:
```python
def fv_annuity_due(payment, rate, periods):
    """
    Calculate future value of an annuity due.
    
    Parameters:
    payment (float): Payment per period
    rate (float): Interest rate per period (decimal)
    periods (int): Number of periods
    
    Returns:
    float: Future value
    """
    return fv_ordinary_annuity(payment, rate, periods) * (1 + rate)

# Example
annual_deposit = 3000
annual_rate = 0.07
years = 15

fv = fv_annuity_due(annual_deposit, annual_rate, years)
print(f"Future value of annuity due: ${fv:.2f}")
```

### Perpetuities

A perpetuity is a series of equal payments that continue indefinitely.

#### Present Value of a Perpetuity

**Formula**:
PV Perpetuity = PMT / r

**Excel Implementation**:
```excel
=PMT/r
```

**Python Implementation**:
```python
def pv_perpetuity(payment, rate):
    """
    Calculate present value of a perpetuity.
    
    Parameters:
    payment (float): Payment per period
    rate (float): Interest rate per period (decimal)
    
    Returns:
    float: Present value
    """
    return payment / rate

# Example
annual_payment = 1000
annual_rate = 0.05

pv = pv_perpetuity(annual_payment, annual_rate)
print(f"Present value of perpetuity: ${pv:.2f}")
```

#### Growing Perpetuity

A growing perpetuity is a series of cash flows that grow at a constant rate indefinitely.

**Formula**:
PV Growing Perpetuity = PMT / (r - g)

Where:
- PMT = Initial payment
- r = Discount rate
- g = Growth rate (g < r)

**Excel Implementation**:
```excel
=PMT/(r-g)
```

**Python Implementation**:
```python
def pv_growing_perpetuity(payment, rate, growth_rate):
    """
    Calculate present value of a growing perpetuity.
    
    Parameters:
    payment (float): Initial payment
    rate (float): Discount rate per period (decimal)
    growth_rate (float): Growth rate per period (decimal)
    
    Returns:
    float: Present value
    """
    if growth_rate >= rate:
        raise ValueError("Growth rate must be less than discount rate")
    
    return payment / (rate - growth_rate)

# Example
annual_payment = 1000
annual_rate = 0.08
growth_rate = 0.03

try:
    pv = pv_growing_perpetuity(annual_payment, annual_rate, growth_rate)
    print(f"Present value of growing perpetuity: ${pv:.2f}")
except ValueError as e:
    print(f"Error: {e}")
```

## 5.3 Effective Annual Rates and Compounding

Understanding different compounding frequencies and their impact on investment returns is crucial for comparing investment opportunities accurately.

### Effective Annual Rate (EAR)

The effective annual rate represents the true annual interest rate when compounding occurs more than once per year.

**Formula**:
EAR = (1 + r/m)^m - 1

Where:
- r = Nominal annual interest rate
- m = Number of compounding periods per year

**Excel Implementation**:
```excel
=(1+r/m)^m-1

'Example for quarterly compounding:
=(1+0.08/4)^4-1
```

**Python Implementation**:
```python
def effective_annual_rate(nominal_rate, compounding_periods):
    """
    Calculate effective annual rate.
    
    Parameters:
    nominal_rate (float): Nominal annual interest rate (decimal)
    compounding_periods (int): Number of compounding periods per year
    
    Returns:
    float: Effective annual rate
    """
    return (1 + nominal_rate / compounding_periods) ** compounding_periods - 1

# Example
nominal_rate = 0.06  # 6% nominal rate
compounding_frequencies = [1, 2, 4, 12, 365]  # Annual, semi-annual, quarterly, monthly, daily

for freq in compounding_frequencies:
    ear = effective_annual_rate(nominal_rate, freq)
    print(f"Compounding {freq} times per year: EAR = {ear:.4%}")
```

### Continuous Compounding

When the number of compounding periods approaches infinity, we have continuous compounding.

**Formula**:
EAR with continuous compounding = e^r - 1

Where:
- r = Nominal annual interest rate
- e = Euler's number (approximately 2.71828)

**Excel Implementation**:
```excel
=EXP(r)-1

'Example for 8% continuous compounding:
=EXP(0.08)-1
```

**Python Implementation**:
```python
import math

def continuous_compounding_ear(nominal_rate):
    """
    Calculate effective annual rate with continuous compounding.
    
    Parameters:
    nominal_rate (float): Nominal annual interest rate (decimal)
    
    Returns:
    float: Effective annual rate
    """
    return math.exp(nominal_rate) - 1

# Example
nominal_rate = 0.06  # 6% nominal rate
ear = continuous_compounding_ear(nominal_rate)
print(f"Continuous compounding: EAR = {ear:.4%}")
```

### Present Value with Different Compounding Frequencies

**Formula**:
PV = FV × (1 + r/m)^(-m×t)

Where:
- r = Nominal annual interest rate
- m = Number of compounding periods per year
- t = Number of years

**Excel Implementation**:
```excel
=FV/(1+r/m)^(m*t)
```

**Python Implementation**:
```python
def present_value_compounding(future_value, nominal_rate, years, compounding_periods):
    """
    Calculate present value with different compounding frequencies.
    
    Parameters:
    future_value (float): Future value
    nominal_rate (float): Nominal annual interest rate (decimal)
    years (float): Number of years
    compounding_periods (int): Number of compounding periods per year
    
    Returns:
    float: Present value
    """
    return future_value / (1 + nominal_rate / compounding_periods) ** (compounding_periods * years)

# Example
future_value = 10000
nominal_rate = 0.07
years = 5
compounding_periods = 12  # Monthly compounding

pv = present_value_compounding(future_value, nominal_rate, years, compounding_periods)
print(f"Present value with monthly compounding: ${pv:.2f}")
```

### Continuous Discounting

**Formula**:
PV with continuous discounting = FV × e^(-r×t)

**Excel Implementation**:
```excel
=FV*EXP(-r*t)
```

**Python Implementation**:
```python
def present_value_continuous(future_value, nominal_rate, years):
    """
    Calculate present value with continuous discounting.
    
    Parameters:
    future_value (float): Future value
    nominal_rate (float): Nominal annual interest rate (decimal)
    years (float): Number of years
    
    Returns:
    float: Present value
    """
    return future_value * math.exp(-nominal_rate * years)

# Example
future_value = 10000
nominal_rate = 0.07
years = 5

pv = present_value_continuous(future_value, nominal_rate, years)
print(f"Present value with continuous discounting: ${pv:.2f}")
```

## 5.4 Loan Amortization and Payment Structures

Loan amortization involves gradually paying off a loan through regular payments that cover both principal and interest. This section examines different payment structures and how to analyze them.

### Calculating Loan Payments

For a fully amortizing loan, the payment is calculated such that the loan is completely paid off by the end of the term.

**Formula**:
PMT = PV × [r × (1 + r)^n] / [(1 + r)^n - 1]

Where:
- PMT = Payment per period
- PV = Loan principal (present value)
- r = Interest rate per period
- n = Total number of payments

**Excel Implementation**:
```excel
=PMT(rate, nper, pv, [fv], [type])
'where fv=0 for a fully amortizing loan
```

**Python Implementation**:
```python
def loan_payment(principal, rate, periods):
    """
    Calculate the payment for a fully amortizing loan.
    
    Parameters:
    principal (float): Loan amount
    rate (float): Interest rate per period (decimal)
    periods (int): Number of payment periods
    
    Returns:
    float: Payment amount per period
    """
    return principal * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)

# Example
loan_amount = 250000  # $250,000 mortgage
annual_rate = 0.045   # 4.5% annual interest rate
monthly_rate = annual_rate / 12
loan_years = 30
loan_months = loan_years * 12

monthly_payment = loan_payment(loan_amount, monthly_rate, loan_months)
print(f"Monthly mortgage payment: ${monthly_payment:.2f}")
```

### Amortization Schedule

An amortization schedule shows the breakdown of each payment into principal and interest components over the life of the loan.

**Excel Implementation**:
```excel
'Assuming cells are set up as follows:
'A1: Loan Amount
'A2: Annual Interest Rate
'A3: Loan Term in Years
'A4: Payment Frequency (per year)

'Calculate periodic interest rate
B1 = A2/A4

'Calculate total number of payments
B2 = A3*A4

'Calculate payment amount
B3 = PMT(B1,B2,A1)

'Set up amortization schedule (starting from row 7)
'Columns: Payment Number, Payment, Interest, Principal, Remaining Balance

'Row 7 (Payment 1)
A7 = 1
B7 = B3
C7 = A1*B1
D7 = B7-C7
E7 = A1-D7

'Row 8 (Payment 2)
A8 = A7+1
B8 = B3
C8 = E7*B1
D8 = B8-C8
E8 = E7-D8

'Continue pattern for remaining payments
```

**Python Implementation**:
```python
import pandas as pd

def create_amortization_schedule(principal, annual_rate, years, payments_per_year=12):
    """
    Create an amortization schedule for a loan.
    
    Parameters:
    principal (float): Loan amount
    annual_rate (float): Annual interest rate (decimal)
    years (int): Loan term in years
    payments_per_year (int): Number of payments per year
    
    Returns:
    DataFrame: Amortization schedule
    """
    # Calculate periodic interest rate and number of payments
    rate_per_period = annual_rate / payments_per_year
    total_periods = years * payments_per_year
    
    # Calculate payment amount
    payment = loan_payment(principal, rate_per_period, total_periods)
    
    # Initialize schedule
    schedule = []
    remaining_balance = principal
    
    for period in range(1, total_periods + 1):
        # Calculate interest for this period
        interest_payment = remaining_balance * rate_per_period
        
        # Calculate principal for this period
        principal_payment = payment - interest_payment
        
        # Update remaining balance
        remaining_balance -= principal_payment
        
        # Adjust for final payment rounding
        if period == total_periods:
            principal_payment += remaining_balance
            remaining_balance = 0
        
        # Add row to schedule
        schedule.append({
            'Payment': period,
            'Payment Amount': payment,
            'Interest': interest_payment,
            'Principal': principal_payment,
            'Remaining Balance': remaining_balance
        })
    
    return pd.DataFrame(schedule)

# Example
loan_amount = 200000
annual_rate = 0.04
loan_years = 15

schedule = create_amortization_schedule(loan_amount, annual_rate, loan_years)
print(schedule.head())
print("\nSummary:")
print(f"Total Payments: ${schedule['Payment Amount'].sum():.2f}")
print(f"Total Interest: ${schedule['Interest'].sum():.2f}")
```

### Alternative Payment Structures

#### Interest-Only Loans

With an interest-only loan, the borrower pays only the interest for a specified period, after which the loan either converts to an amortizing loan or requires a balloon payment.

**Excel Implementation**:
```excel
'Interest-only payment calculation
=PV*r

'Where:
'PV = Loan principal
'r = Interest rate per period
```

**Python Implementation**:
```python
def interest_only_payment(principal, rate):
    """
    Calculate interest-only payment.
    
    Parameters:
    principal (float): Loan amount
    rate (float): Interest rate per period (decimal)
    
    Returns:
    float: Interest-only payment amount
    """
    return principal * rate

# Example
loan_amount = 300000
annual_rate = 0.05
monthly_rate = annual_rate / 12

monthly_payment = interest_only_payment(loan_amount, monthly_rate)
print(f"Monthly interest-only payment: ${monthly_payment:.2f}")
```

#### Balloon Payments

A balloon payment is a large, lump-sum payment made at the end of a loan term. The loan payments are calculated as if the loan would amortize over a longer period, but the loan term is shorter, resulting in a large final payment.

**Excel Implementation**:
```excel
'Calculate regular payment based on a longer amortization period
Payment = PMT(rate, amortization_periods, pv)

'Calculate balloon payment (remaining balance after term ends)
Balloon = FV(rate, actual_periods, -Payment, pv)
```

**Python Implementation**:
```python
def balloon_loan_payments(principal, annual_rate, balloon_years, amortization_years, payments_per_year=12):
    """
    Calculate payments and balloon amount for a balloon loan.
    
    Parameters:
    principal (float): Loan amount
    annual_rate (float): Annual interest rate (decimal)
    balloon_years (int): Years until balloon payment
    amortization_years (int): Amortization period used for payment calculation
    payments_per_year (int): Number of payments per year
    
    Returns:
    tuple: (Regular payment amount, Balloon payment amount)
    """
    rate_per_period = annual_rate / payments_per_year
    amortization_periods = amortization_years * payments_per_year
    balloon_periods = balloon_years * payments_per_year
    
    # Calculate regular payment based on longer amortization
    payment = loan_payment(principal, rate_per_period, amortization_periods)
    
    # Create partial amortization schedule to find remaining balance
    remaining_balance = principal
    for period in range(1, balloon_periods + 1):
        interest_payment = remaining_balance * rate_per_period
        principal_payment = payment - interest_payment
        remaining_balance -= principal_payment
    
    # Balloon payment is the remaining balance
    balloon_payment = remaining_balance
    
    return payment, balloon_payment

# Example
loan_amount = 250000
annual_rate = 0.045
balloon_years = 7
amortization_years = 30

payment, balloon = balloon_loan_payments(loan_amount, annual_rate, balloon_years, amortization_years)
print(f"Regular payment: ${payment:.2f}")
print(f"Balloon payment after {balloon_years} years: ${balloon:.2f}")
```

#### Graduated Payment Mortgage (GPM)

A GPM starts with lower payments that gradually increase over time, typically at a fixed rate for a predetermined period.

**Python Implementation**:
```python
def graduated_payment_mortgage(principal, annual_rate, years, payments_per_year=12, 
                               initial_payment_reduction=0.2, graduation_years=5, annual_increase=0.05):
    """
    Calculate a graduated payment mortgage schedule.
    
    Parameters:
    principal (float): Loan amount
    annual_rate (float): Annual interest rate (decimal)
    years (int): Loan term in years
    payments_per_year (int): Number of payments per year
    initial_payment_reduction (float): Initial payment reduction percentage
    graduation_years (int): Years of graduated payments
    annual_increase (float): Annual increase in payment during graduation period
    
    Returns:
    DataFrame: Payment schedule
    """
    rate_per_period = annual_rate / payments_per_year
    total_periods = years * payments_per_year
    graduation_periods = graduation_years * payments_per_year
    
    # Calculate standard payment
    standard_payment = loan_payment(principal, rate_per_period, total_periods)
    
    # Calculate initial reduced payment
    initial_payment = standard_payment * (1 - initial_payment_reduction)
    
    # Initialize schedule
    schedule = []
    remaining_balance = principal
    
    for period in range(1, total_periods + 1):
        # Calculate payment for this period
        if period <= graduation_periods:
            # During graduation period, increase payment annually
            year = (period - 1) // payments_per_year
            payment = initial_payment * (1 + annual_increase) ** year
        else:
            # After graduation, payment is constant at the standard amount
            payment = standard_payment
        
        # Calculate interest for this period
        interest_payment = remaining_balance * rate_per_period
        
        # Calculate principal for this period (ensuring it doesn't exceed remaining balance)
        principal_payment = min(payment - interest_payment, remaining_balance)
        
        # If payment is insufficient to cover interest, add negative amortization
        if principal_payment < 0:
            interest_payment = payment
            principal_payment = 0
            remaining_balance += (interest_payment - payment)
        else:
            # Update remaining balance
            remaining_balance -= principal_payment
        
        # Add row to schedule
        schedule.append({
            'Payment': period,
            'Payment Amount': payment,
            'Interest': interest_payment,
            'Principal': principal_payment,
            'Remaining Balance': remaining_balance
        })
    
    return pd.DataFrame(schedule)

# Example
loan_amount = 300000
annual_rate = 0.045
loan_years = 30
initial_reduction = 0.3
graduation_years = 5
annual_increase = 0.1

schedule = graduated_payment_mortgage(loan_amount, annual_rate, loan_years, 
                                     initial_payment_reduction=initial_reduction,
                                     graduation_years=graduation_years,
                                     annual_increase=annual_increase)

# Print key information
print(f"Standard payment: ${loan_payment(loan_amount, annual_rate/12, loan_years*12):.2f}")
print(f"Initial payment: ${schedule.iloc[0]['Payment Amount']:.2f}")
print(f"Final graduated payment: ${schedule.iloc[graduation_years*12-1]['Payment Amount']:.2f}")
print(f"Total payments: ${schedule['Payment Amount'].sum():.2f}")
print(f"Total interest: ${schedule['Interest'].sum():.2f}")
```

## Exercises

### Bond Valuation for Tech Company Debt

**Problem:** You are analyzing a bond issued by a major technology company with the following characteristics:
- Par value: $1,000
- Coupon rate: 3.75% (semi-annual payments)
- Maturity: 10 years
- Current market yield: 4.25%

**Tasks:**
1. Calculate the price of the bond
2. Determine if the bond is trading at a premium or discount
3. Calculate the current yield
4. If the market yield increases to 5%, calculate the new bond price
5. Calculate the duration and convexity of the bond

**Excel Solution:**
```excel
'Inputs
Par_Value = 1000
Coupon_Rate = 0.0375
Maturity_Years = 10
Market_Yield = 0.0425
Periods_Per_Year = 2

'Bond price calculation
Periodic_Rate = Market_Yield / Periods_Per_Year
Periodic_Coupon = Coupon_Rate * Par_Value / Periods_Per_Year
Total_Periods = Maturity_Years * Periods_Per_Year

Bond_Price = PV(Periodic_Rate, Total_Periods, Periodic_Coupon, Par_Value)
'Result: $963.37

'Bond trading status
=IF(Bond_Price>Par_Value,"Premium",IF(Bond_Price<Par_Value,"Discount","Par"))
'Result: "Discount"

'Current yield
Current_Yield = (Coupon_Rate * Par_Value) / Bond_Price
'Result: 3.89%

'New bond price if yield increases to 5%
New_Yield = 0.05
New_Periodic_Rate = New_Yield / Periods_Per_Year
New_Bond_Price = PV(New_Periodic_Rate, Total_Periods, Periodic_Coupon, Par_Value)
'Result: $895.68

'Duration calculation
Duration = DURATION("1/1/2023", "1/1/2033", Coupon_Rate, Market_Yield, Periods_Per_Year, 1)
'Result: 8.01

'Modified duration
Modified_Duration = Duration / (1 + Periodic_Rate)
'Result: 7.78

'Convexity (approximate calculation)
Yield_Up = Market_Yield + 0.0001
Yield_Down = Market_Yield - 0.0001
Price_Up = PV(Yield_Up/Periods_Per_Year, Total_Periods, Periodic_Coupon, Par_Value)
Price_Down = PV(Yield_Down/Periods_Per_Year, Total_Periods, Periodic_Coupon, Par_Value)
Convexity = ((Price_Up + Price_Down - 2*Bond_Price) / Bond_Price) / (0.0001^2)
'Result: ~72
```

**Python Solution:**
```python
import numpy as np
from scipy import optimize

def bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """Calculate bond price"""
    periods = years_to_maturity * periods_per_year
    rate_per_period = ytm / periods_per_year
    coupon_per_period = (coupon_rate * par) / periods_per_year
    
    # Present value of coupon payments
    pv_coupons = coupon_per_period * ((1 - (1 + rate_per_period) ** -periods) / rate_per_period)
    
    # Present value of par value
    pv_par = par / (1 + rate_per_period) ** periods
    
    return pv_coupons + pv_par

def bond_duration(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """Calculate Macaulay duration of a bond"""
    periods = years_to_maturity * periods_per_year
    rate_per_period = ytm / periods_per_year
    coupon_per_period = (coupon_rate * par) / periods_per_year
    
    # Calculate bond price
    price = bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year)
    
    # Calculate weighted cash flows
    duration = 0
    for t in range(1, periods + 1):
        if t < periods:
            cf = coupon_per_period
        else:
            cf = coupon_per_period + par
            
        pv_cf = cf / (1 + rate_per_period) ** t
        duration += t * pv_cf
        
    # Divide by price and convert to years
    return (duration / price) / periods_per_year

def modified_duration(mac_duration, ytm, periods_per_year=2):
    """Calculate modified duration"""
    return mac_duration / (1 + ytm / periods_per_year)

def bond_convexity(par, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    """Calculate bond convexity"""
    # For simplicity, using numerical approximation
    delta = 0.0001
    price = bond_price(par, coupon_rate, ytm, years_to_maturity, periods_per_year)
    price_up = bond_price(par, coupon_rate, ytm + delta, years_to_maturity, periods_per_year)
    price_down = bond_price(par, coupon_rate, ytm - delta, years_to_maturity, periods_per_year)
    
    return (price_up + price_down - 2 * price) / (price * delta ** 2)

# Inputs
par_value = 1000
coupon_rate = 0.0375
years_to_maturity = 10
market_yield = 0.0425
periods_per_year = 2

# Calculate bond price
price = bond_price(par_value, coupon_rate, market_yield, years_to_maturity)
print(f"Bond price: ${price:.2f}")

# Determine if trading at premium or discount
if price > par_value:
    status = "Premium"
elif price < par_value:
    status = "Discount"
else:
    status = "Par"
print(f"Trading status: {status}")

# Calculate current yield
current_yield = (coupon_rate * par_value) / price
print(f"Current yield: {current_yield:.2%}")

# Calculate new price with higher yield
new_yield = 0.05
new_price = bond_price(par_value, coupon_rate, new_yield, years_to_maturity)
print(f"New bond price at 5% yield: ${new_price:.2f}")

# Calculate duration and convexity
mac_duration = bond_duration(par_value, coupon_rate, market_yield, years_to_maturity)
mod_duration = modified_duration(mac_duration, market_yield)
convexity = bond_convexity(par_value, coupon_rate, market_yield, years_to_maturity)

print(f"Macaulay duration: {mac_duration:.2f} years")
print(f"Modified duration: {mod_duration:.2f}")
print(f"Convexity: {convexity:.2f}")
```

### Investment Analysis for ASML and INTC

**Problem:** You are considering investing in the semiconductor industry and have narrowed your choices to ASML Holding (ASML) and Intel Corporation (INTC). You've gathered the following information:

**ASML:**
- Current stock price: $675
- Expected annual dividend: $6.50
- Expected dividend growth rate: 15% for 5 years, then 5% perpetually
- Required rate of return: 12%

**INTC:**
- Current stock price: $48
- Expected annual dividend: $1.45
- Expected dividend growth rate: 5% perpetually
- Required rate of return: 10%

**Tasks:**
1. Calculate the intrinsic value of both stocks using appropriate dividend discount models
2. Determine which stock appears more undervalued
3. If you have $10,000 to invest, how should you allocate it between these two stocks?
4. Calculate the expected future value of your investment after 10 years

**Excel Solution:**
```excel
'ASML Valuation (Two-stage DDM)
ASML_Price = 675
ASML_Dividend = 6.5
ASML_Growth_1 = 0.15
ASML_Growth_2 = 0.05
ASML_Required_Return = 0.12
ASML_Years_Stage_1 = 5

'Calculate PV of dividends during high-growth phase
ASML_D1 = ASML_Dividend * (1 + ASML_Growth_1)
ASML_D2 = ASML_D1 * (1 + ASML_Growth_1)
ASML_D3 = ASML_D2 * (1 + ASML_Growth_1)
ASML_D4 = ASML_D3 * (1 + ASML_Growth_1)
ASML_D5 = ASML_D4 * (1 + ASML_Growth_1)

ASML_PV_D1 = ASML_D1 / (1 + ASML_Required_Return)
ASML_PV_D2 = ASML_D2 / (1 + ASML_Required_Return)^2
ASML_PV_D3 = ASML_D3 / (1 + ASML_Required_Return)^3
ASML_PV_D4 = ASML_D4 / (1 + ASML_Required_Return)^4
ASML_PV_D5 = ASML_D5 / (1 + ASML_Required_Return)^5

ASML_PV_High_Growth = SUM(ASML_PV_D1:ASML_PV_D5)

'Calculate terminal value and its present value
ASML_D6 = ASML_D5 * (1 + ASML_Growth_2)
ASML_Terminal_Value = ASML_D6 / (ASML_Required_Return - ASML_Growth_2)
ASML_PV_Terminal = ASML_Terminal_Value / (1 + ASML_Required_Return)^5

'Calculate intrinsic value
ASML_Intrinsic_Value = ASML_PV_High_Growth + ASML_PV_Terminal
'Result: $706.82

'INTC Valuation (Gordon Growth Model)
INTC_Price = 48
INTC_Dividend = 1.45
INTC_Growth = 0.05
INTC_Required_Return = 0.1

INTC_D1 = INTC_Dividend * (1 + INTC_Growth)
INTC_Intrinsic_Value = INTC_D1 / (INTC_Required_Return - INTC_Growth)
'Result: $30.45

'Undervaluation percentage
ASML_Undervaluation = (ASML_Intrinsic_Value - ASML_Price) / ASML_Price
'Result: 4.71%

INTC_Undervaluation = (INTC_Intrinsic_Value - INTC_Price) / INTC_Price
'Result: -36.56% (overvalued)

'Investment allocation based on relative undervaluation
'Since INTC appears overvalued, allocate all to ASML
ASML_Allocation = 10000
INTC_Allocation = 0

'Calculate expected future value (10 years)
ASML_Annual_Return = 0.12  'Required return
ASML_FV = ASML_Allocation * (1 + ASML_Annual_Return)^10
'Result: $31,058.48
```

**Python Solution:**
```python
def two_stage_ddm(current_dividend, high_growth_rate, stable_growth_rate, 
                 required_return, high_growth_years):
    """Calculate stock value using two-stage DDM"""
    # Present value of dividends during high-growth phase
    pv_high_growth = 0
    dividend = current_dividend
    
    for year in range(1, high_growth_years + 1):
        dividend *= (1 + high_growth_rate)
        pv_high_growth += dividend / (1 + required_return) ** year
    
    # Terminal value using Gordon Growth Model
    terminal_dividend = dividend * (1 + stable_growth_rate)
    terminal_value = terminal_dividend / (required_return - stable_growth_rate)
    
    # Present value of terminal value
    pv_terminal = terminal_value / (1 + required_return) ** high_growth_years
    
    return pv_high_growth + pv_terminal

def gordon_growth_model(next_dividend, required_return, growth_rate):
    """Calculate stock value using Gordon Growth Model"""
    return next_dividend / (required_return - growth_rate)

def future_value(present_value, rate, years):
    """Calculate future value"""
    return present_value * (1 + rate) ** years

# ASML inputs
asml_price = 675
asml_dividend = 6.50
asml_growth_1 = 0.15
asml_growth_2 = 0.05
asml_required_return = 0.12
asml_high_growth_years = 5

# INTC inputs
intc_price = 48
intc_dividend = 1.45
intc_growth = 0.05
intc_required_return = 0.10

# Calculate intrinsic values
asml_value = two_stage_ddm(asml_dividend, asml_growth_1, asml_growth_2, 
                          asml_required_return, asml_high_growth_years)

intc_next_dividend = intc_dividend * (1 + intc_growth)
intc_value = gordon_growth_model(intc_next_dividend, intc_required_return, intc_growth)

# Calculate undervaluation percentages
asml_undervaluation = (asml_value - asml_price) / asml_price
intc_undervaluation = (intc_value - intc_price) / intc_price

# Determine optimal allocation
investment_amount = 10000

if asml_undervaluation > intc_undervaluation:
    if asml_undervaluation > 0:
        asml_allocation = investment_amount
        intc_allocation = 0
    else:
        asml_allocation = 0
        intc_allocation = 0  # Hold cash if both overvalued
else:
    if intc_undervaluation > 0:
        asml_allocation = 0
        intc_allocation = investment_amount
    else:
        asml_allocation = 0
        intc_allocation = 0  # Hold cash if both overvalued

# Calculate future value
asml_shares = asml_allocation / asml_price
intc_shares = intc_allocation / intc_price

asml_future_value = future_value(asml_allocation, asml_required_return, 10)
intc_future_value = future_value(intc_allocation, intc_required_return, 10)
total_future_value = asml_future_value + intc_future_value

# Display results
print(f"ASML intrinsic value: ${asml_value:.2f}")
print(f"INTC intrinsic value: ${intc_value:.2f}")
print(f"ASML undervaluation: {asml_undervaluation:.2%}")
print(f"INTC undervaluation: {intc_undervaluation:.2%}")
print("\nRecommended allocation:")
print(f"ASML: ${asml_allocation:.2f} ({asml_shares:.2f} shares)")
print(f"INTC: ${intc_allocation:.2f} ({intc_shares:.2f} shares)")
print(f"\nExpected future value after 10 years: ${total_future_value:.2f}")
```

### Retirement Planning Calculations

**Problem:** You are 35 years old and planning for retirement at age 65. You currently have $50,000 in your retirement account and can save $6,000 per year. You want to determine how much you'll have at retirement and whether it will be sufficient.

**Assumptions:**
- Expected annual return: 7%
- Inflation rate: 2.5%
- Current annual expenses: $60,000
- Desired retirement income: 80% of inflation-adjusted pre-retirement expenses
- Life expectancy: 90 years

**Tasks:**
1. Calculate the future value of your current savings at retirement
2. Calculate the future value of your annual contributions at retirement
3. Determine your total retirement portfolio value
4. Calculate your inflation-adjusted annual expenses at retirement
5. Determine the withdrawal rate needed to sustain your retirement income
6. Assess whether your retirement savings will be sufficient

**Excel Solution:**
```excel
'Inputs
Current_Age = 35
Retirement_Age = 65
Life_Expectancy = 90
Current_Savings = 50000
Annual_Contribution = 6000
Expected_Return = 0.07
Inflation_Rate = 0.025
Current_Expenses = 60000
Replacement_Ratio = 0.8

'Calculations
Years_Until_Retirement = Retirement_Age - Current_Age
Retirement_Duration = Life_Expectancy - Retirement_Age

'Future value of current savings
FV_Current_Savings = Current_Savings * (1 + Expected_Return)^Years_Until_Retirement
'Result: $381,473.52

'Future value of annual contributions
FV_Contributions = Annual_Contribution * ((1 + Expected_Return)^Years_Until_Retirement - 1) / Expected_Return
'Result: $598,905.48

'Total retirement portfolio
Total_Portfolio = FV_Current_Savings + FV_Contributions
'Result: $980,379.00

'Inflation-adjusted annual expenses at retirement
Retirement_Expenses = Current_Expenses * (1 + Inflation_Rate)^Years_Until_Retirement * Replacement_Ratio
'Result: $103,145.98

'Required withdrawal rate
Withdrawal_Rate = Retirement_Expenses / Total_Portfolio
'Result: 10.52%

'Sustainable withdrawal rate (4% rule)
Sustainable_Annual_Withdrawal = Total_Portfolio * 0.04
'Result: $39,215.16

'Shortfall or surplus
Annual_Shortfall = Retirement_Expenses - Sustainable_Annual_Withdrawal
'Result: $63,930.82 (shortfall)

'Additional savings needed
Additional_Monthly_Savings = PMT(Expected_Return/12, Years_Until_Retirement*12, 0, -Annual_Shortfall/0.04)
'Result: $1,217.53
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def future_value(present_value, rate, years):
    """Calculate future value of a lump sum"""
    return present_value * (1 + rate) ** years

def future_value_annuity(payment, rate, years):
    """Calculate future value of an annuity"""
    return payment * ((1 + rate) ** years - 1) / rate

def sustainable_withdrawal(portfolio, rate, years):
    """Calculate sustainable annual withdrawal"""
    if rate == 0:
        return portfolio / years
    return portfolio * rate / (1 - (1 + rate) ** -years)

# Inputs
current_age = 35
retirement_age = 65
life_expectancy = 90
current_savings = 50000
annual_contribution = 6000
expected_return = 0.07
inflation_rate = 0.025
current_expenses = 60000
replacement_ratio = 0.8

# Derived values
years_until_retirement = retirement_age - current_age
retirement_duration = life_expectancy - retirement_age
real_return = (1 + expected_return) / (1 + inflation_rate) - 1

# Calculate retirement portfolio
fv_current_savings = future_value(current_savings, expected_return, years_until_retirement)
fv_contributions = future_value_annuity(annual_contribution, expected_return, years_until_retirement)
total_portfolio = fv_current_savings + fv_contributions

# Calculate retirement needs
retirement_expenses_nominal = current_expenses * (1 + inflation_rate) ** years_until_retirement * replacement_ratio
retirement_expenses_real = current_expenses * replacement_ratio

# Assess sustainability
withdrawal_rate = retirement_expenses_nominal / total_portfolio
sustainable_withdrawal_amount = total_portfolio * 0.04  # Using 4% rule
shortfall = retirement_expenses_nominal - sustainable_withdrawal_amount

# Additional monthly savings needed
if shortfall > 0:
    pmt_rate = (1 + expected_return) ** (1/12) - 1
    additional_monthly_savings = np.pmt(pmt_rate, years_until_retirement * 12, 0, -shortfall / 0.04)
else:
    additional_monthly_savings = 0

# Generate retirement forecast
years = list(range(current_age, life_expectancy + 1))
portfolio_values = []
expenses = []

# Build portfolio until retirement
portfolio = current_savings
for age in range(current_age, retirement_age):
    portfolio_values.append(portfolio)
    expenses.append(0)
    portfolio = portfolio * (1 + expected_return) + annual_contribution

# Withdraw during retirement
for age in range(retirement_age, life_expectancy + 1):
    portfolio_values.append(portfolio)
    expense = retirement_expenses_nominal * ((1 + inflation_rate) ** (age - retirement_age))
    expenses.append(expense)
    portfolio = max(0, portfolio * (1 + expected_return) - expense)

# Create and display results
results = pd.DataFrame({
    'Age': years,
    'Portfolio Value': portfolio_values,
    'Withdrawals': expenses
})

# Display summary
print("Retirement Planning Summary")
print(f"Years until retirement: {years_until_retirement}")
print(f"Future value of current savings: ${fv_current_savings:.2f}")
print(f"Future value of annual contributions: ${fv_contributions:.2f}")
print(f"Total retirement portfolio: ${total_portfolio:.2f}")
print(f"Annual expenses at retirement (nominal): ${retirement_expenses_nominal:.2f}")
print(f"Required withdrawal rate: {withdrawal_rate:.2%}")
print(f"Sustainable withdrawal (4% rule): ${sustainable_withdrawal_amount:.2f}")

if shortfall > 0:
    print(f"SHORTFALL: ${shortfall:.2f} per year")
    print(f"Additional monthly savings needed: ${additional_monthly_savings:.2f}")
else:
    surplus = -shortfall
    print(f"SURPLUS: ${surplus:.2f} per year")

# Plot portfolio projection
plt.figure(figsize=(10, 6))
plt.plot(results['Age'], results['Portfolio Value'], label='Portfolio Value')
plt.axvline(x=retirement_age, color='r', linestyle='--', label='Retirement Age')
plt.xlabel('Age')
plt.ylabel('Portfolio Value ($)')
plt.title('Retirement Portfolio Projection')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()
```

### LLM-Based Analysis of Payment Structures

**Problem:** You are considering different mortgage options for a $400,000 home purchase:

**Option 1: Traditional 30-year fixed-rate mortgage**
- Interest rate: 6.25%
- 30-year term
- Fixed monthly payments

**Option 2: 7/1 ARM (Adjustable Rate Mortgage)**
- Initial interest rate: 5.5% (fixed for 7 years)
- After 7 years, rate adjusts annually (assume it increases to 7% and stays there)
- 30-year term

**Option 3: 15-year fixed-rate mortgage**
- Interest rate: 5.75%
- 15-year term
- Fixed monthly payments

**Tasks:**
1. Calculate monthly payments for each option
2. Create amortization schedules showing principal and interest breakdown
3. Compare total interest paid over the life of each loan
4. Perform a break-even analysis to determine how long you need to stay in the home for each option
5. Use an LLM to interpret the results and provide a recommendation based on different scenarios

**Excel/Python Solution:**
This part would involve calculations and data preparation. The LLM interpretation would follow.

**LLM Interpretation:**

"# Mortgage Option Analysis

Based on the calculations for your $400,000 home purchase options, here's my analysis:

## Monthly Payment Comparison

| Mortgage Option | Monthly Payment | Total Interest Paid |
|----------------|-----------------|---------------------|
| 30-year fixed (6.25%) | $2,462.87 | $486,633.20 |
| 7/1 ARM (5.5%/7%) | $2,271.16 (first 7 years) <br> $2,531.25 (after) | $456,744.58 |
| 15-year fixed (5.75%) | $3,316.49 | $196,968.20 |

## Break-Even Analysis
- If you stay in the home less than 7 years, the 7/1 ARM offers the lowest total cost
- Between 7-10 years, the 7/1 ARM and 30-year fixed are comparable
- Beyond 10 years, the 15-year fixed becomes increasingly advantageous despite higher monthly payments

## Recommendation Based on Time Horizon

**If planning to stay less than 7 years:**
The 7/1 ARM is clearly the best choice, saving approximately $191 per month compared to the 30-year fixed. Over 7 years, this amounts to savings of approximately $16,044 in payments and additional equity buildup of about $9,500.

**If planning to stay 7-15 years:**
This depends on your financial situation. The 15-year fixed builds equity much faster and saves nearly $290,000 in interest compared to the 30-year fixed, but requires about $854 more in monthly payments. If you can afford the higher payment, the 15-year option will leave you mortgage-free much sooner and at a substantially lower total cost.

**If planning to stay more than 15 years:**
The 15-year fixed is mathematically superior, resulting in complete ownership 15 years earlier and saving nearly $290,000 in interest payments compared to the 30-year option.

## Risk Considerations
- The 7/1 ARM carries interest rate risk after 7 years, which could result in payments higher than projected
- Fixed-rate options provide payment certainty for budget planning
- Higher payments on the 15-year mortgage reduce financial flexibility for other goals

## Final Recommendation
If maximizing financial efficiency is your primary goal and you can comfortably afford the higher payment, the 15-year mortgage is the clear winner in almost all scenarios except very short-term homeownership. However, if you need to maximize monthly cash flow flexibility or are uncertain about future income stability, the 30-year fixed provides the best balance of certainty and affordability.

For the best of both worlds, you might consider taking the 30-year mortgage but making voluntary additional principal payments when your budget allows. This gives you the flexibility of lower required payments with the option to accelerate payoff and reduce total interest."
