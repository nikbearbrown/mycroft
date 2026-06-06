# Chapter 5: Time Value of Money and Discounted Cash Flows - Cheat Sheet

## 5.1 Present and Future Value Calculations

### Basic Time Value Concepts
**Definition**: Money today is worth more than the same amount in the future due to its earning potential

**Key Formulas**:
- **Future Value**: FV = PV × (1 + r)^t
- **Present Value**: PV = FV ÷ (1 + r)^t

Where:
- PV = Present value
- FV = Future value
- r = Interest rate per period
- t = Number of periods

**Excel Implementation**:
```excel
'Future Value
=PV*(1+r)^t
=FV(rate, nper, pmt, [pv], [type])

'Present Value
=FV/(1+r)^t
=PV(rate, nper, pmt, [fv], [type])
```

**Python Implementation**:
```python
def future_value(present_value, rate, periods):
    """Calculate future value of a present sum"""
    return present_value * (1 + rate) ** periods

def present_value(future_value, rate, periods):
    """Calculate present value of a future sum"""
    return future_value / (1 + rate) ** periods
```

### Net Present Value (NPV)
**Definition**: The sum of all discounted future cash flows, including the initial investment

**Formula**:
```
NPV = CF₀ + CF₁/(1+r)¹ + CF₂/(1+r)² + ... + CFₙ/(1+r)ⁿ
```

**Excel Implementation**:
```excel
=NPV(rate, value1, [value2], ...) + CF₀
'Note: Excel's NPV function doesn't include initial investment (CF₀)
```

**Python Implementation**:
```python
def npv(rate, cash_flows):
    """Calculate Net Present Value of a series of cash flows"""
    npv_value = cash_flows[0]  # Initial investment
    
    for t, cf in enumerate(cash_flows[1:], 1):
        npv_value += cf / (1 + rate) ** t
        
    return npv_value
```

### Internal Rate of Return (IRR)
**Definition**: The discount rate that makes the NPV of all cash flows equal to zero

**Formula**:
Find r such that: 0 = CF₀ + CF₁/(1+r)¹ + CF₂/(1+r)² + ... + CFₙ/(1+r)ⁿ

**Excel Implementation**:
```excel
=IRR(values, [guess])
```

**Python Implementation**:
```python
from scipy import optimize

def irr(cash_flows):
    """Calculate Internal Rate of Return"""
    def npv_equation(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
    
    return optimize.newton(npv_equation, 0.1)  # 0.1 is initial guess
```

## 5.2 Annuities and Perpetuities

### Ordinary Annuities
**Definition**: Series of equal payments made at the end of consecutive periods

#### Present Value of an Ordinary Annuity (PVA)
**Formula**:
```
PVA = PMT × [(1 - (1 + r)^(-n)) / r]
```

**Excel Implementation**:
```excel
=PMT*(1-(1+r)^(-n))/r
=PV(rate, nper, pmt, [fv], [type=0])
```

**Python Implementation**:
```python
def pv_ordinary_annuity(payment, rate, periods):
    """Calculate present value of an ordinary annuity"""
    return payment * ((1 - (1 + rate) ** -periods) / rate)
```

#### Future Value of an Ordinary Annuity (FVA)
**Formula**:
```
FVA = PMT × [((1 + r)^n - 1) / r]
```

**Excel Implementation**:
```excel
=PMT*((1+r)^n-1)/r
=FV(rate, nper, pmt, [pv], [type=0])
```

**Python Implementation**:
```python
def fv_ordinary_annuity(payment, rate, periods):
    """Calculate future value of an ordinary annuity"""
    return payment * ((1 + rate) ** periods - 1) / rate
```

### Annuities Due
**Definition**: Series of equal payments made at the beginning of consecutive periods

#### Present Value of an Annuity Due
**Formula**:
```
PV Annuity Due = PV Ordinary Annuity × (1 + r)
```

**Excel Implementation**:
```excel
=PMT*(1-(1+r)^(-n))/r*(1+r)
=PV(rate, nper, pmt, [fv], 1)
```

**Python Implementation**:
```python
def pv_annuity_due(payment, rate, periods):
    """Calculate present value of an annuity due"""
    return pv_ordinary_annuity(payment, rate, periods) * (1 + rate)
```

#### Future Value of an Annuity Due
**Formula**:
```
FV Annuity Due = FV Ordinary Annuity × (1 + r)
```

**Excel Implementation**:
```excel
=PMT*((1+r)^n-1)/r*(1+r)
=FV(rate, nper, pmt, [pv], 1)
```

**Python Implementation**:
```python
def fv_annuity_due(payment, rate, periods):
    """Calculate future value of an annuity due"""
    return fv_ordinary_annuity(payment, rate, periods) * (1 + rate)
```

### Perpetuities
**Definition**: Series of equal payments that continue indefinitely

#### Present Value of a Perpetuity
**Formula**:
```
PV Perpetuity = PMT / r
```

**Excel Implementation**:
```excel
=PMT/r
```

**Python Implementation**:
```python
def pv_perpetuity(payment, rate):
    """Calculate present value of a perpetuity"""
    return payment / rate
```

#### Growing Perpetuity
**Formula**:
```
PV Growing Perpetuity = PMT / (r - g)
```
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
    """Calculate present value of a growing perpetuity"""
    if growth_rate >= rate:
        raise ValueError("Growth rate must be less than discount rate")
    
    return payment / (rate - growth_rate)
```

## 5.3 Effective Annual Rates and Compounding

### Effective Annual Rate (EAR)
**Definition**: True annual interest rate when compounding occurs more than once per year

**Formula**:
```
EAR = (1 + r/m)^m - 1
```
Where:
- r = Nominal annual interest rate
- m = Number of compounding periods per year

**Excel Implementation**:
```excel
=(1+r/m)^m-1
```

**Python Implementation**:
```python
def effective_annual_rate(nominal_rate, compounding_periods):
    """Calculate effective annual rate"""
    return (1 + nominal_rate / compounding_periods) ** compounding_periods - 1
```

### Continuous Compounding
**Formula**:
```
EAR with continuous compounding = e^r - 1
```

**Excel Implementation**:
```excel
=EXP(r)-1
```

**Python Implementation**:
```python
import math

def continuous_compounding_ear(nominal_rate):
    """Calculate EAR with continuous compounding"""
    return math.exp(nominal_rate) - 1
```

### Present Value with Different Compounding Frequencies
**Formula**:
```
PV = FV × (1 + r/m)^(-m×t)
```

**Excel Implementation**:
```excel
=FV/(1+r/m)^(m*t)
```

**Python Implementation**:
```python
def present_value_compounding(future_value, nominal_rate, years, compounding_periods):
    """Calculate present value with different compounding frequencies"""
    return future_value / (1 + nominal_rate / compounding_periods) ** (compounding_periods * years)
```

### Continuous Discounting
**Formula**:
```
PV with continuous discounting = FV × e^(-r×t)
```

**Excel Implementation**:
```excel
=FV*EXP(-r*t)
```

**Python Implementation**:
```python
def present_value_continuous(future_value, nominal_rate, years):
    """Calculate present value with continuous discounting"""
    return future_value * math.exp(-nominal_rate * years)
```

## 5.4 Loan Amortization and Payment Structures

### Calculating Loan Payments
**Definition**: Regular payment that fully pays off a loan by the end of the term

**Formula**:
```
PMT = PV × [r × (1 + r)^n] / [(1 + r)^n - 1]
```

**Excel Implementation**:
```excel
=PMT(rate, nper, pv, [fv], [type])
```

**Python Implementation**:
```python
def loan_payment(principal, rate, periods):
    """Calculate payment for a fully amortizing loan"""
    return principal * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)
```

### Amortization Schedule
**Components**:
- Payment number
- Payment amount
- Interest portion
- Principal portion
- Remaining balance

**Excel Implementation**:
```excel
'For each payment row:
'Interest payment
=Previous_Balance*Rate

'Principal payment
=Payment_Amount-Interest_Payment

'Remaining balance
=Previous_Balance-Principal_Payment
```

**Python Implementation**:
```python
def create_amortization_schedule(principal, annual_rate, years, payments_per_year=12):
    """Create an amortization schedule for a loan"""
    rate_per_period = annual_rate / payments_per_year
    total_periods = years * payments_per_year
    payment = loan_payment(principal, rate_per_period, total_periods)
    
    schedule = []
    remaining_balance = principal
    
    for period in range(1, total_periods + 1):
        interest_payment = remaining_balance * rate_per_period
        principal_payment = payment - interest_payment
        remaining_balance -= principal_payment
        
        schedule.append({
            'Payment': period,
            'Payment Amount': payment,
            'Interest': interest_payment,
            'Principal': principal_payment,
            'Remaining Balance': remaining_balance
        })
    
    return schedule
```

### Alternative Payment Structures

#### Interest-Only Loans
**Formula**:
```
Interest-only payment = PV × r
```

**Excel Implementation**:
```excel
=PV*r
```

**Python Implementation**:
```python
def interest_only_payment(principal, rate):
    """Calculate interest-only payment"""
    return principal * rate
```

#### Balloon Payments
**Definition**: Large lump-sum payment at the end of a loan term

**Excel Implementation**:
```excel
'Regular payment (based on longer amortization)
=PMT(rate, amortization_periods, pv)

'Balloon payment (remaining balance)
=FV(rate, actual_periods, -Payment, pv)
```

**Python Implementation**:
```python
def balloon_loan_payments(principal, annual_rate, balloon_years, amortization_years, payments_per_year=12):
    """Calculate payments and balloon amount for a balloon loan"""
    rate_per_period = annual_rate / payments_per_year
    amortization_periods = amortization_years * payments_per_year
    balloon_periods = balloon_years * payments_per_year
    
    # Calculate regular payment based on longer amortization
    payment = loan_payment(principal, rate_per_period, amortization_periods)
    
    # Calculate remaining balance at balloon date
    remaining_balance = principal
    for period in range(1, balloon_periods + 1):
        interest_payment = remaining_balance * rate_per_period
        principal_payment = payment - interest_payment
        remaining_balance -= principal_payment
    
    return payment, remaining_balance
```

#### Graduated Payment Mortgage (GPM)
**Definition**: Loan with payments that start lower and increase over time

**Key Characteristics**:
- Initial payment reduction (e.g., 20-30%)
- Gradual payment increases (e.g., 3-7% annually)
- Graduation period (e.g., 5-10 years)
- May involve negative amortization in early years

**Python Implementation**:
```python
def graduated_payment_mortgage(principal, annual_rate, years, payments_per_year=12,
                              initial_payment_reduction=0.2, graduation_years=5, 
                              annual_increase=0.05):
    """Calculate a graduated payment mortgage schedule"""
    rate_per_period = annual_rate / payments_per_year
    total_periods = years * payments_per_year
    graduation_periods = graduation_years * payments_per_year
    
    # Calculate standard payment
    standard_payment = loan_payment(principal, rate_per_period, total_periods)
    
    # Calculate initial reduced payment
    initial_payment = standard_payment * (1 - initial_payment_reduction)
    
    # Create schedule with graduated payments
    schedule = []
    remaining_balance = principal
    
    for period in range(1, total_periods + 1):
        if period <= graduation_periods:
            year = (period - 1) // payments_per_year
            payment = initial_payment * (1 + annual_increase) ** year
        else:
            payment = standard_payment
            
        interest_payment = remaining_balance * rate_per_period
        principal_payment = payment - interest_payment
        remaining_balance -= principal_payment
        
        schedule.append({
            'Payment': period,
            'Payment Amount': payment,
            'Interest': interest_payment,
            'Principal': principal_payment,
            'Remaining Balance': remaining_balance
        })
    
    return schedule
```

### Time Value Applications

| Application | Key Formulas | Description |
|-------------|--------------|-------------|
| **Retirement Planning** | FV = PV(1+r)^t + PMT×[(1+r)^t-1]/r | Calculate future value of current savings plus periodic contributions |
| **Mortgage Analysis** | PMT = PV×[r×(1+r)^n]/[(1+r)^n-1] | Calculate monthly payment for home loan |
| **Education Funding** | PV = FV×(1+r)^(-t) | Calculate amount needed today to fund future education costs |
| **Capital Budgeting** | NPV = Σ[CF_t/(1+r)^t] | Evaluate investment projects based on discounted cash flows |
| **Bond Valuation** | P = Σ[C/(1+r)^t] + F/(1+r)^n | Price a bond based on coupon payments and face value |

### Decision Rules

| Metric | Decision Rule | Excel | Python Function |
|--------|---------------|-------|-----------------|
| **Net Present Value (NPV)** | Accept if NPV > 0 | `=NPV(rate,values)+CF0` | `npv(rate, cash_flows)` |
| **Internal Rate of Return (IRR)** | Accept if IRR > required return | `=IRR(values)` | `irr(cash_flows)` |
| **Payback Period** | Accept if < target period | Custom calculation | Custom calculation |
| **Profitability Index (PI)** | Accept if PI > 1 | `=NPV(r,CF1:CFn)/(-CF0)` | `(npv(r,CF) - CF[0])/(-CF[0])` |
</artifact>
