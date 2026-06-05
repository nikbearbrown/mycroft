# Financial Metrics Agent

## Overview

This is a comprehensive SEC filing analysis system designed to extract, process, and analyze financial data from public company filings. The tool operates in two distinct phases to provide both quantitative financial metrics and qualitative narrative insights for investment analysis and financial research.

## Architecture

### Phase 1: Structured Financial Data Extraction ✅ **COMPLETE**
The first phase focuses on extracting structured financial metrics from SEC EDGAR filings using standardized XBRL data formats. This phase is fully implemented and operational.

### Phase 2: Narrative Content Analysis 🚧 **IN PROGRESS**
The second phase will extract and analyze narrative content from the HTML portions of SEC filings to provide qualitative insights, risk assessments, and contextual information.

## Components

### 1. SEC EDGAR Document Fetcher (`edgar_fetcher.py`)
**Purpose**: Raw document retrieval and filing management
- Fetches latest SEC filings for any public company by ticker symbol
- Retrieves company CIK numbers and metadata
- Downloads multiple filing types (10-K, 10-Q, 8-K, etc.)
- Handles rate limiting and SEC API compliance
- Saves documents locally for processing

**Key Features**:
- Company information lookup by ticker
- Bulk filing retrieval
- Form type filtering
- Document content extraction
- File management and organization

### 2. SEC Financial Analyzer (`financial_analyzer.py`)
**Purpose**: Structured financial data extraction and analysis
- Extracts standardized financial metrics from XBRL data
- Calculates key financial ratios and performance indicators
- Provides comprehensive financial analysis reports
- Exports data to multiple formats (JSON, CSV, DataFrame)

**Key Features**:
- **Revenue Metrics**: Total revenue, cost of revenue, gross profit
- **Profitability**: Operating income, net income, profit margins
- **Balance Sheet**: Assets, liabilities, shareholders' equity
- **Cash Flow**: Operating cash flow, capital expenditures, free cash flow
- **Financial Ratios**: ROA, ROE, debt-to-equity, profit margins
- **Historical Tracking**: Multi-period trend analysis

## Current Capabilities (Phase 1)

### Supported Financial Metrics
- **Income Statement**: Revenue, gross profit, operating income, net income, EPS
- **Balance Sheet**: Total assets, current assets, liabilities, shareholders' equity
- **Cash Flow**: Operating cash flow, capital expenditures, free cash flow
- **Key Ratios**: Gross margin, operating margin, net margin, ROA, ROE, debt-to-equity

### Supported Filing Types
- **10-K**: Annual reports
- **10-Q**: Quarterly reports  
- **8-K**: Current reports
- **DEF 14A**: Proxy statements
- **13F-HR**: Institutional investment manager holdings
- **SC 13G/D**: Beneficial ownership reports

### Export Formats
- **JSON**: Complete analysis reports with metadata
- **CSV**: Historical financial data for spreadsheet analysis
- **Pandas DataFrame**: For programmatic data analysis
- **Console Reports**: Formatted summary displays

## Installation & Setup

### Prerequisites
```bash
pip install sec-edgar-api pandas requests
```

### Required Configuration
- **User-Agent Header**: Must include your name and email address for SEC compliance
- **Rate Limiting**: Built-in delays to respect SEC server limits
- **CIK Caching**: Automatic ticker-to-CIK mapping and caching

## Usage Examples

### Basic Financial Analysis
```python
from financial_analyzer import SECFinancialAnalyzer

analyzer = SECFinancialAnalyzer(user_agent="Your Name your.email@example.com")
report = analyzer.create_comprehensive_report("AAPL")
analyzer.print_summary(report)
```

### Bulk Document Retrieval
```python
from edgar_fetcher import EDGARFetcher

fetcher = EDGARFetcher()
# Get all latest filings for a company
results = fetcher.fetch_all_latest_filings("NVDA", save_to_file=True)
```

### Data Export
```python
# Export to DataFrame for analysis
df = analyzer.export_to_dataframe(financial_data, "MSFT")
df.to_csv("msft_financial_data.csv", index=False)

# Save comprehensive report
import json
with open("company_report.json", 'w') as f:
    json.dump(report, f, indent=2, default=str)
```

## Development Status

### ✅ Completed (Phase 1)
- [x] SEC document retrieval system
- [x] XBRL financial data extraction
- [x] Financial ratio calculations
- [x] Multi-format data export
- [x] Comprehensive reporting
- [x] Error handling and logging
- [x] Rate limiting compliance

### 🚧 In Progress (Phase 2)
- [ ] HTML content parsing
- [ ] Narrative text extraction
- [ ] Natural language processing pipeline
- [ ] Risk factor categorization
- [ ] AI/technology mention detection
- [ ] Sentiment analysis implementation
