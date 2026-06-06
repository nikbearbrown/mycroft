# SEC Filing Metrics and AI Analysis Guide

## Overview

This guide provides a comprehensive reference for financial metrics available in different SEC filing types and outlines the manual text processing required for AI-specific analysis.

---

## Financial Metrics by Filing Type

### 10-K Annual Report

The 10-K is the most comprehensive annual filing and contains the complete set of financial statements and metrics.

#### Income Statement Metrics
| Metric | XBRL Tag | Description | Frequency |
|--------|----------|-------------|-----------|
| Revenue | `Revenues`, `SalesRevenueNet` | Total company revenue | Annual |
| Cost of Revenue | `CostOfRevenue`, `CostOfGoodsAndServicesSold` | Direct costs of producing goods/services | Annual |
| Gross Profit | `GrossProfit` | Revenue minus cost of revenue | Annual |
| Research & Development | `ResearchAndDevelopmentExpense` | R&D spending | Annual |
| Operating Income | `OperatingIncomeLoss` | Profit from core operations | Annual |
| Net Income | `NetIncomeLoss` | Bottom-line profit after all expenses | Annual |
| Earnings Per Share | `EarningsPerShareBasic`, `EarningsPerShareDiluted` | Per-share earnings | Annual |

#### Balance Sheet Metrics
| Metric | XBRL Tag | Description | Point-in-Time |
|--------|----------|-------------|---------------|
| Cash & Equivalents | `CashAndCashEquivalentsAtCarryingValue` | Liquid assets | Year-end |
| Short-term Investments | `ShortTermInvestments` | Marketable securities | Year-end |
| Accounts Receivable | `AccountsReceivableNetCurrent` | Money owed by customers | Year-end |
| Total Current Assets | `AssetsCurrent` | Assets convertible to cash within 1 year | Year-end |
| Total Assets | `Assets` | All company assets | Year-end |
| Goodwill | `Goodwill` | Intangible asset from acquisitions | Year-end |
| Intangible Assets | `IntangibleAssetsNetExcludingGoodwill` | Patents, trademarks, etc. | Year-end |
| Current Liabilities | `LiabilitiesCurrent` | Short-term obligations | Year-end |
| Long-term Debt | `LongTermDebt` | Debt due after 1 year | Year-end |
| Total Liabilities | `Liabilities` | All company obligations | Year-end |
| Shareholders' Equity | `StockholdersEquity` | Owner's stake in company | Year-end |

#### Cash Flow Metrics
| Metric | XBRL Tag | Description | Frequency |
|--------|----------|-------------|-----------|
| Operating Cash Flow | `NetCashProvidedByUsedInOperatingActivities` | Cash from core operations | Annual |
| Capital Expenditures | `PaymentsToAcquirePropertyPlantAndEquipment` | Investment in fixed assets | Annual |
| Free Cash Flow | `FreeCashFlow` | Operating cash flow minus capex | Annual |

### 10-Q Quarterly Report

The 10-Q provides quarterly updates with similar metrics but for shorter periods.

#### Available Metrics
- **Same structure as 10-K** but for quarterly periods
- **Year-to-date cumulative** figures for income statement items
- **Point-in-time** figures for balance sheet items
- **Quarterly cash flow** information

#### Key Differences from 10-K
- Less detailed footnotes and analysis
- May have fewer supplementary metrics
- Interim periods may show seasonal variations
- Some annual-only disclosures are missing

### 8-K Current Report

8-K filings are event-driven and contain limited structured financial data.

#### Typical Metrics (when applicable)
- **Material agreements** - contract values, terms
- **Acquisitions/Dispositions** - transaction amounts
- **Executive compensation** - specific compensation figures
- **Earnings announcements** - preliminary financial results

#### Limitations
- **No standardized financial statements**
- **Event-specific information only**
- **Limited XBRL tagging**
- **Requires manual text analysis for most data**

---

## Calculated Financial Ratios

The following ratios are automatically calculated from the extracted metrics:

### Profitability Ratios
| Ratio | Formula | Source Metrics |
|-------|---------|----------------|
| Gross Margin | (Gross Profit / Revenue) × 100 | 10-K, 10-Q |
| Operating Margin | (Operating Income / Revenue) × 100 | 10-K, 10-Q |
| Net Margin | (Net Income / Revenue) × 100 | 10-K, 10-Q |

### Return Ratios
| Ratio | Formula | Source Metrics |
|-------|---------|----------------|
| Return on Assets (ROA) | (Net Income / Total Assets) × 100 | 10-K, 10-Q |
| Return on Equity (ROE) | (Net Income / Shareholders' Equity) × 100 | 10-K, 10-Q |

### Leverage Ratios
| Ratio | Formula | Source Metrics |
|-------|---------|----------------|
| Debt-to-Equity | Total Liabilities / Shareholders' Equity | 10-K, 10-Q |

---



## AI-Specific Analysis: Manual Text Processing Requirements

Since structured XBRL data doesn't contain AI-specific information, comprehensive AI analysis requires processing the full text of SEC filings. Here's what needs to be manually extracted:

### 1. Business Description Section (Item 1 in 10-K)

### 2. Risk Factors Section (Item 1A in 10-K)

### 3. Management Discussion & Analysis (Item 7 in 10-K)
