# Chapter 1: The Corporation and Financial Markets - Cheat Sheet

## 1.1 Corporate Structure and Governance

### Key Corporate Features
- **Separate Legal Entity**: Exists independently from owners
- **Limited Liability**: Owners' risk limited to investment
- **Transferable Ownership**: Shares freely transferable
- **Perpetual Existence**: Continues despite ownership changes
- **Centralized Management**: Professional managers run operations

### Board of Directors Metrics
```python
def calculate_board_independence(board_data):
    independence_ratio = board_data['independent_directors'] / board_data['total_directors']
    return independence_ratio
    
def analyze_board_diversity(board_data):
    gender_diversity = board_data['female_directors'] / board_data['total_directors']
    ethnic_diversity = board_data['minority_directors'] / board_data['total_directors']
    return {"gender_diversity": gender_diversity, "ethnic_diversity": ethnic_diversity}
```

### Governance Models
1. **Anglo-American**: Shareholder-centric
2. **Continental European**: Stakeholder-oriented
3. **Japanese**: Relationship-based

### Board Independence Excel Function
```excel
' Calculate board independence percentage
=COUNTIF(DirectorStatus,"Independent")/COUNT(DirectorStatus)

' Check for CEO/Chair split
=IF(CEO_Name=Chairman_Name,"Combined","Split")
```

### LLM Governance Analysis Prompt
```
Analyze the corporate governance of [Company] with focus on:
1. Board independence and committee structure
2. Executive compensation alignment with performance
3. Shareholder rights provisions
4. ESG governance integration

Compare to industry best practices and provide a governance quality score (1-10).
```

## 1.2 Financial Markets Overview

### Market Types
- **Primary Markets**: New securities issuance (IPOs, secondary offerings)
- **Secondary Markets**: Trading existing securities (exchanges, OTC)
- **Money Markets**: Short-term instruments (T-bills, commercial paper)
- **Capital Markets**: Long-term securities (stocks, bonds)
- **Derivatives Markets**: Contracts based on underlying assets (options, futures)

### Market Efficiency Levels
- **Weak Form**: Prices reflect all historical information
- **Semi-Strong Form**: Prices reflect all public information
- **Strong Form**: Prices reflect all information (public and private)

### Python Market Analysis
```python
import yfinance as yf
import pandas as pd

def calculate_market_metrics(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
    returns = data.pct_change().dropna()
    
    metrics = {
        'annualized_return': returns.mean() * 252 * 100,
        'volatility': returns.std() * (252 ** 0.5) * 100,
        'sharpe_ratio': returns.mean() / returns.std() * (252 ** 0.5)
    }
    
    return metrics
```

### Excel Market Data Analysis
```excel
' Calculate Annualized Return
=AVERAGE(DailyReturns)*252*100

' Calculate Volatility
=STDEV(DailyReturns)*SQRT(252)*100

' Calculate Sharpe Ratio
=AVERAGE(DailyReturns)/STDEV(DailyReturns)*SQRT(252)

' Calculate Beta
=COVARIANCE.P(StockReturns,MarketReturns)/VAR.P(MarketReturns)
```

### Market Efficiency Test in Excel
```excel
' Test for autocorrelation
Function TestWEMH(returns_range As Range) As Double
    TestWEMH = Application.WorksheetFunction.Correl( _
        Application.WorksheetFunction.Offset(returns_range, 1, 0, returns_range.Rows.Count - 1), _
        Application.WorksheetFunction.Offset(returns_range, 0, 0, returns_range.Rows.Count - 1))
End Function
```

## 1.3 The Financial Manager's Role

### Primary Functions
1. **Investment Decisions**: Project selection
2. **Financing Decisions**: Capital structure optimization
3. **Dividend Decisions**: Distribution policy
4. **Liquidity Management**: Working capital management
5. **Risk Management**: Identifying and mitigating risks

### Key Financial Metrics

| Category | Metric | Formula | Excel | Python |
|----------|--------|---------|-------|--------|
| **Profitability** | ROA | Net Income/Total Assets | `=B2/C2` | `net_income/total_assets` |
| | ROE | Net Income/Shareholders' Equity | `=B2/D2` | `net_income/equity` |
| | Operating Margin | Operating Income/Revenue | `=E2/F2` | `operating_income/revenue` |
| **Liquidity** | Current Ratio | Current Assets/Current Liabilities | `=G2/H2` | `current_assets/current_liabilities` |
| | Quick Ratio | (Current Assets-Inventory)/Current Liabilities | `=(G2-I2)/H2` | `(current_assets-inventory)/current_liabilities` |
| **Solvency** | Debt-to-Equity | Total Debt/Shareholders' Equity | `=J2/D2` | `total_debt/equity` |
| | Interest Coverage | EBIT/Interest Expense | `=K2/L2` | `ebit/interest_expense` |
| **Efficiency** | Asset Turnover | Revenue/Total Assets | `=F2/C2` | `revenue/total_assets` |
| | Inventory Turnover | COGS/Average Inventory | `=M2/AVG(I2:I3)` | `cogs/np.mean([inventory_t, inventory_t1])` |

### Python Financial Dashboard
```python
def create_financial_dashboard(financial_data):
    # Calculate key metrics
    metrics = pd.DataFrame(index=financial_data.index)
    
    # Profitability
    metrics['ROA'] = financial_data['Net Income'] / financial_data['Total Assets']
    metrics['ROE'] = financial_data['Net Income'] / financial_data['Shareholders Equity']
    metrics['Operating Margin'] = financial_data['Operating Income'] / financial_data['Revenue']
    
    # Liquidity
    metrics['Current Ratio'] = financial_data['Current Assets'] / financial_data['Current Liabilities']
    metrics['Quick Ratio'] = (financial_data['Current Assets'] - financial_data['Inventory']) / financial_data['Current Liabilities']
    
    # Solvency
    metrics['Debt-to-Equity'] = financial_data['Total Debt'] / financial_data['Shareholders Equity']
    metrics['Interest Coverage'] = financial_data['EBIT'] / financial_data['Interest Expense']
    
    return metrics
```

### Financial Management LLM Prompt
```
Based on [Company]'s financial metrics:
- Revenue: $[X] million (growth: [Y]%)
- Operating margin: [Z]%
- ROE: [A]%
- Current ratio: [B]
- Debt-to-equity: [C]
- Free cash flow: $[D] million

Recommend optimal capital allocation priorities and identify financial risks.
```

## 1.4 Agency Relationships and Conflicts of Interest

### Principal-Agent Problem
Occurs when managers (agents) prioritize self-interest over shareholders' (principals') interests

### Agency Problems
1. **Effort Aversion**: Exerting less than optimal effort
2. **Perquisite Consumption**: Excessive executive benefits
3. **Empire Building**: Growth at expense of profitability
4. **Risk Aversion**: Avoiding positive-NPV risky projects
5. **Short-termism**: Focusing on short-term results

### Agency Cost Metrics
```python
def calculate_agency_costs(company_data):
    agency_metrics = {}
    
    # Asset utilization (lower = potentially higher agency costs)
    agency_metrics['Asset_Utilization'] = company_data['Revenue'] / company_data['Total_Assets']
    
    # Expense ratio (higher = potentially higher agency costs)
    agency_metrics['SGA_Ratio'] = company_data['SG&A_Expenses'] / company_data['Revenue']
    
    # Free cash flow to assets ratio (higher FCF with low growth = potential overretention)
    agency_metrics['FCF_to_Assets'] = company_data['Free_Cash_Flow'] / company_data['Total_Assets']
    
    return agency_metrics
```

### Excel Agency Cost Analysis
```excel
'Asset utilization ratio
=Revenue/TotalAssets

'SG&A to sales ratio
=SG&A/Revenue

'Free cash flow to assets
=FreeCashFlow/TotalAssets

'Executive compensation to net income
=ExecutiveCompensation/NetIncome
```

### Governance Mechanisms to Mitigate Agency Problems
1. **Board Oversight**: Independent directors monitor management
2. **Executive Compensation**: Performance-based pay aligns interests
3. **Shareholder Activism**: Engaged shareholders influence decisions
4. **Market for Corporate Control**: Takeover threat disciplines management
5. **Managerial Ownership**: Managers owning company shares

### Pay-Performance Alignment in Excel
```excel
'Calculate CEO pay-TSR correlation
=CORREL(CEOCompensation,TSR)

'Calculate compensation mix
=PerformanceBased/TotalCompensation
```

### LLM Agency Analysis Prompt
```
Analyze potential agency conflicts at [Company] based on:
1. Executive compensation structure (salary vs. performance-based)
2. Board independence and expertise
3. Ownership concentration
4. Financial indicators (FCF, growth opportunities, expense ratios)
5. Capital allocation decisions

Identify specific agency concerns and recommend governance improvements.
```

## Key Stakeholders
1. **Shareholders**: Provide equity capital
2. **Bondholders**: Provide debt capital
3. **Employees**: Provide human capital
4. **Customers**: Purchase products/services
5. **Suppliers**: Provide inputs/materials
6. **Communities**: Provide social license
7. **Government**: Provide regulatory framework