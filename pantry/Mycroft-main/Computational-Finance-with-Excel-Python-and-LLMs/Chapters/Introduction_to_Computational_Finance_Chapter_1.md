# Chapter 1: Introduction to Computational Finance

## 1.1 The Convergence of Excel, Python, and LLMs in Finance

Finance has always been at the forefront of computational innovation. From the earliest spreadsheets to today's sophisticated machine learning models, financial professionals have leveraged technology to gain insights, manage risk, and create value. We now stand at a fascinating intersection where three powerful computational approaches converge to transform financial analysis:

**Excel**: The ubiquitous spreadsheet software that revolutionized financial modeling in the 1980s remains the most widely used tool in finance today. With its intuitive interface, extensive financial functions, and visualization capabilities, Excel offers accessibility and transparency that make it indispensable for practitioners at all levels.

**Python**: As financial models have grown more complex, Python has emerged as the programming language of choice for quantitative finance. Its readable syntax, vast ecosystem of specialized libraries (NumPy, pandas, scikit-learn, etc.), and scalability make it ideal for handling large datasets and implementing sophisticated algorithms.

**Large Language Models (LLMs)**: The newest frontier in computational finance, LLMs like ChatGPT, Claude, and Gemini represent a paradigm shift in how we interact with financial data and concepts. These AI assistants can translate natural language into code, explain complex financial ideas, and even help develop and debug financial models.

### The Power of Complementary Approaches

Each of these tools offers distinct advantages and limitations:

| Tool | Strengths | Limitations |
|------|-----------|-------------|
| **Excel** | - Intuitive visual interface<br>- Ubiquitous in business<br>- Transparency in calculations<br>- Low barrier to entry | - Performance issues with large datasets<br>- Limited reproducibility<br>- Challenges in version control<br>- Potential for formula errors |
| **Python** | - Powerful data manipulation<br>- Advanced statistical capabilities<br>- Reproducible workflows<br>- Scalability to large datasets | - Steeper learning curve<br>- Less visual/interactive<br>- Requires programming knowledge<br>- Development overhead |
| **LLMs** | - Natural language interface<br>- Knowledge integration<br>- Code generation<br>- Explanatory capabilities | - Potential for hallucinations<br>- Limited computational capabilities<br>- Less transparent reasoning<br>- May lack domain-specific knowledge |

Rather than viewing these as competing approaches, modern financial analysts recognize the value in using them together as complementary tools. This trilateral approach allows practitioners to:

1. **Prototype rapidly** in Excel, where ideas can be visually explored
2. **Scale efficiently** with Python when dealing with larger datasets or more complex models
3. **Augment understanding** with LLMs to explain concepts, generate code, and validate approaches

### Real-World Application: Analyzing Tesla Stock

Consider a simple example: analyzing Tesla (TSLA) stock returns. Let's see how each approach might tackle this task:

**Excel Approach**:
- Download historical price data into a spreadsheet
- Create formulas to calculate daily returns
- Build a dashboard with summary statistics and charts
- Visually identify patterns and outliers

**Python Approach**:
- Use pandas to retrieve and process the historical data
- Implement statistical measures like Sharpe ratio and maximum drawdown
- Apply advanced techniques like GARCH modeling for volatility
- Create reproducible notebooks with embedded visualizations

**LLM Approach**:
- Ask for explanations of Tesla's historical performance
- Request code generation for specific analyses
- Validate interpretation of statistical findings
- Generate natural language reports of the analysis

By combining these approaches, an analyst can work more efficiently, gain deeper insights, and communicate results more effectively than would be possible with any single tool.

In this textbook, we embrace this convergence by teaching financial concepts through all three lenses. For every problem we encounter, we will demonstrate how to solve it using Excel, Python, and LLMs, highlighting the strengths of each approach while acknowledging their limitations.

## 1.2 Setting Up Your Computational Environment

To follow along with the examples and exercises in this book, you'll need to set up appropriate computational environments for Excel, Python, and LLMs. This section provides guidance on creating an effective workspace for financial analysis using all three approaches.

### Excel Setup

**Requirements**:
- Microsoft Excel (2016 or newer recommended)
- Optional: Power Query for data import capabilities
- Optional: Analysis ToolPak add-in for advanced statistical analyses

**Setup Steps**:
1. **Enable the Analysis ToolPak**:
   - File → Options → Add-ins → Manage Excel Add-ins → Go
   - Check "Analysis ToolPak" and "Solver Add-in"
   - Click OK

2. **Configure Financial Formatting**:
   - Create custom number formats for percentages, currencies, and dates
   - Example format for percentages with 2 decimal places: `0.00%;-0.00%;0.00%`

3. **Optimize Calculation Settings**:
   - For large workbooks: Formulas → Calculation Options → Manual
   - For most analyses: Formulas → Calculation Options → Automatic

### Python Setup

**Requirements**:
- Python 3.8 or newer
- Anaconda distribution (recommended for scientific computing)
- Key libraries: pandas, numpy, matplotlib, scipy, scikit-learn, yfinance

**Setup Steps**:
1. **Install Anaconda**:
   - Download from [anaconda.com](https://www.anaconda.com/products/individual)
   - Follow installation instructions for your operating system

2. **Create a Computational Finance Environment**:
   ```bash
   conda create -n compfin python=3.10
   conda activate compfin
   conda install pandas numpy matplotlib scipy scikit-learn jupyter
   pip install yfinance pandas-datareader fredapi
   ```

3. **Set Up Jupyter Notebook**:
   - From the activated environment, run:
   ```bash
   jupyter notebook
   ```
   - Create a folder for your financial analysis projects

4. **Optional: Install IDE**:
   - VS Code or PyCharm are excellent choices for Python development
   - Install appropriate extensions for Python and Jupyter support

### LLM Setup

**Requirements**:
- Internet access for web-based LLMs
- API access (optional for programmatic integration)

**Setup Options**:
1. **Web Interfaces**:
   - Create accounts on platforms hosting the LLMs you plan to use:
     - OpenAI's ChatGPT: [chat.openai.com](https://chat.openai.com)
     - Anthropic's Claude: [claude.ai](https://claude.ai)
     - Google's Gemini: [gemini.google.com](https://gemini.google.com)

2. **API Access** (for programmatic use):
   - Obtain API keys from the respective providers
   - Install client libraries:
   ```bash
   pip install openai anthropic google-generativeai
   ```

3. **LLM in Notebooks**:
   - Libraries like LangChain can help integrate LLMs into Jupyter notebooks
   ```bash
   pip install langchain
   ```

### Data Sources Setup

1. **Free Financial Data Sources**:
   - Yahoo Finance (accessible via `yfinance` Python library)
   - Alpha Vantage (free API with registration)
   - FRED (Federal Reserve Economic Data)

2. **API Connections**:
   - Register for free API keys where needed
   - Store API keys securely (using environment variables)

3. **Sample Datasets**:
   - Download the companion datasets for this textbook from our website
   - Include historical data for the tech stocks we'll analyze throughout the book

### Integrated Environment Example

Here's a simple Python script to test your setup, which retrieves recent Tesla stock data:

```python
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Get Tesla stock data for the past year
tsla = yf.download('TSLA', period='1y')

# Calculate daily returns
tsla['Return'] = tsla['Adj Close'].pct_change()

# Display summary statistics
print(tsla['Return'].describe())

# Plot the closing prices
plt.figure(figsize=(10, 6))
plt.plot(tsla['Adj Close'])
plt.title('Tesla Stock Price - Past Year')
plt.ylabel('Price ($)')
plt.grid(True)
plt.show()
```

If this script runs successfully, your Python environment is properly configured for financial analysis.

## 1.3 The Triangulation Methodology for LLM Accuracy

While Large Language Models (LLMs) offer remarkable capabilities for financial analysis, they can sometimes produce incorrect information with high confidence—a phenomenon known as "hallucination." This is particularly concerning in finance, where accuracy is paramount. To address this challenge, we introduce the triangulation methodology, a systematic approach to enhance the reliability of LLM-generated financial insights.

### Understanding LLM Limitations in Finance

Before diving into triangulation, it's important to understand why LLMs might struggle with financial data:

1. **Training Data Limitations**: LLMs may have been trained on outdated financial information or limited examples of specialized financial concepts.

2. **Mathematical Precision**: Finance requires exact calculations, while LLMs sometimes approximate or make arithmetic errors.

3. **Context Window Constraints**: Complex financial analyses may exceed the context window of LLMs, leading to incomplete reasoning.

4. **Overconfidence**: LLMs can present speculative information with unwarranted certainty, especially in domains like market prediction.

### The Triangulation Framework

Triangulation in financial LLM applications involves three key components:

1. **Multi-Model Verification**: Consulting multiple LLMs (ChatGPT, Claude, and Gemini) on the same financial question.

2. **Cross-Source Validation**: Comparing LLM outputs with authoritative financial sources and computational results from Excel or Python.

3. **Consistency Checking**: Evaluating internal consistency of LLM responses through follow-up questions and alternative formulations.

### Implementing Triangulation

Here's a practical approach to implementing triangulation for financial analyses:

#### Step 1: Question Formulation
Begin with a clear, precise financial question. For complex queries, break them down into component parts.

**Example**: "What was Tesla's beta over the past 3 years, and what does it imply about the stock's risk profile?"

#### Step 2: Multi-Model Consultation
Submit the identical question to multiple LLMs and record their responses.

| LLM | Response on Tesla's Beta |
|-----|--------------------------|
| ChatGPT | "Tesla's 3-year beta is approximately 1.65, indicating the stock is more volatile than the market..." |
| Claude | "Based on the most recent data, Tesla has a beta of around 1.8 over the past 3 years, suggesting higher volatility..." |
| Gemini | "Tesla's beta over the last 3 years has ranged from 1.5 to 2.0, currently standing at about 1.7..." |

#### Step 3: Consensus and Divergence Analysis
Identify areas of agreement and disagreement among the LLMs.

**Consensus**: All models agree Tesla's beta is greater than 1, indicating higher volatility than the market.
**Divergence**: The exact beta value varies from 1.65 to 1.8 across models.

#### Step 4: Verification with Computational Tools
Calculate the actual value using Excel or Python to verify the LLM claims.

```python
import yfinance as yf
import numpy as np

# Download data
tesla = yf.download('TSLA', period='3y')
market = yf.download('^GSPC', period='3y')  # S&P 500

# Calculate returns
tesla['Returns'] = tesla['Adj Close'].pct_change()
market['Returns'] = market['Adj Close'].pct_change()

# Remove NaN values
clean_data = pd.concat([tesla['Returns'], market['Returns']], axis=1).dropna()
clean_data.columns = ['Tesla', 'Market']

# Calculate beta
covariance = np.cov(clean_data['Tesla'], clean_data['Market'])[0,1]
market_variance = np.var(clean_data['Market'])
beta = covariance / market_variance

print(f"Tesla's 3-year beta: {beta:.2f}")
```

#### Step 5: Synthesize and Refine
Combine insights from all sources, giving priority to computationally verified information.

**Final Conclusion**: "Tesla's 3-year beta is 1.72 (verified by calculation), confirming the LLM consensus that the stock exhibits higher volatility than the market. This aligns with Tesla's position as a growth-oriented technology company in the automotive sector."

### Mathematical Basis for Triangulation

The triangulation approach is not just intuitively appealing but has a mathematical foundation. If we assume that each LLM has an independent probability *p* of being correct on a given financial question (where *p* > 0.5), then the probability of getting the correct answer by taking the majority vote from three models is:

P(correct) = p³ + 3p²(1-p)

For example, if individual LLMs are correct 80% of the time, the triangulation approach yields the correct answer with approximately 96% probability—a substantial improvement in reliability.

### Triangulation Prompt Templates

To facilitate consistent triangulation, we recommend using standardized prompt templates when consulting LLMs:

**Basic Triangulation Prompt**:
```
I'm seeking to validate financial information about [specific financial topic]. 
Please provide:
1. The [specific calculation or information] for [financial instrument]
2. The methodology you would use to calculate this
3. Any assumptions or limitations in your response
4. Your confidence level in this information (low/medium/high)
5. What sources would you recommend to verify this information
```

**Advanced Cross-Verification Prompt**:
```
I've received the following information from different sources about [financial topic]:
- Source 1 states: [information from first source]
- Source 2 states: [information from second source]
- My calculation shows: [your calculation result]

These [agree/disagree]. Please help me understand:
1. The most likely correct answer and why
2. Potential reasons for the discrepancy
3. How I could definitively resolve this question
```

By systematically applying this triangulation methodology throughout this textbook, we'll demonstrate how to leverage the power of LLMs while minimizing their limitations, particularly for critical financial calculations and analyses.

## 1.4 Working with Financial Data

Financial data serves as the foundation for all computational finance applications. Understanding how to acquire, process, and analyze financial data is essential for effective financial modeling and decision-making. This section covers the key aspects of working with financial data across our three computational platforms.

### Types of Financial Data

Financial data comes in various forms, each serving different analytical purposes:

1. **Market Data**:
   - **Price data**: Historical and real-time asset prices (stocks, bonds, derivatives)
   - **Volume data**: Trading volumes indicating market activity
   - **Volatility metrics**: Measures of price variation and risk

2. **Fundamental Data**:
   - **Financial statements**: Balance sheets, income statements, cash flow statements
   - **Ratios and metrics**: P/E ratios, dividend yields, profit margins
   - **Economic indicators**: GDP, unemployment rates, inflation figures

3. **Alternative Data**:
   - **Sentiment data**: Social media mentions, news sentiment
   - **Satellite imagery**: For retail traffic, shipping, agricultural yields
   - **Credit card transactions**: Consumer spending patterns

4. **Derived Data**:
   - **Technical indicators**: Moving averages, RSI, MACD
   - **Factor exposures**: Sensitivity to market, size, value factors
   - **Risk metrics**: VaR, expected shortfall, stress test results

### Data Acquisition Methods

#### Excel Data Acquisition

Excel offers several methods for obtaining financial data:

1. **Data Connections**:
   - Data tab → Get Data → From Web
   - Connect to financial websites or APIs that provide data in tabular format
   - Refresh connections to update data automatically

2. **Add-ins and Extensions**:
   - Stock Connector add-in for real-time and historical market data
   - Bloomberg Excel add-in (requires Bloomberg Terminal subscription)
   - Refinitiv Eikon Excel add-in (requires subscription)

3. **Manual Import**:
   - Download CSV files from financial websites
   - Data tab → From Text/CSV to import data
   - Copy-paste from financial websites (less recommended due to potential errors)

#### Python Data Acquisition

Python provides powerful libraries for financial data retrieval:

1. **yfinance** (Yahoo Finance):
   ```python
   import yfinance as yf
   
   # Download historical data for specified tickers
   data = yf.download(['TSLA', 'NVDA', 'AMD', 'META'], 
                      start='2020-01-01', 
                      end='2023-12-31')
   ```

2. **pandas-datareader** (multiple sources):
   ```python
   import pandas_datareader as pdr
   
   # Get data from FRED (Federal Reserve Economic Data)
   inflation = pdr.get_data_fred('CPIAUCSL', start='2010-01-01')
   ```

3. **API-based retrieval**:
   ```python
   import requests
   import pandas as pd
   
   # Example using Alpha Vantage API
   api_key = 'YOUR_API_KEY'
   url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey={api_key}&outputsize=full'
   r = requests.get(url)
   data = r.json()
   
   # Convert to DataFrame
   df = pd.DataFrame(data['Time Series (Daily)']).T
   ```

#### LLM-Assisted Data Acquisition

LLMs can help with data acquisition in several ways:

1. **Code Generation**:
   - Request code snippets for specific data retrieval tasks
   - Get guidance on API parameters and options

2. **Data Source Recommendations**:
   - Ask for appropriate data sources for specific financial analyses
   - Get information about data quality and limitations

3. **Troubleshooting**:
   - Help with debugging data retrieval issues
   - Suggesting alternative approaches when primary methods fail

### Data Cleaning and Preparation

#### Common Data Issues in Finance

1. **Missing Values**: Gaps in time series due to non-trading days or reporting lags
2. **Outliers**: Extreme values from market events or data errors
3. **Look-ahead Bias**: Using information that wouldn't have been available at the time
4. **Survivorship Bias**: Analyzing only companies that survived to the present
5. **Temporal Misalignment**: Mismatched timestamps across different data sources

#### Excel Data Cleaning

1. **Handling Missing Data**:
   - Use IF(ISNA()) to detect and replace missing values
   - Conditional formatting to highlight gaps
   - AVERAGEIF for simple imputation

2. **Outlier Detection**:
   - Use quartile functions and IQR method
   ```
   =IF(C2>QUARTILE(C$2:C$100,3)+1.5*(QUARTILE(C$2:C$100,3)-QUARTILE(C$2:C$100,1)),"Outlier","Normal")
   ```

3. **Date Standardization**:
   - Convert text dates to Excel date format using DATEVALUE()
   - Align dates using WORKDAY() to handle business days

#### Python Data Cleaning

1. **Handling Missing Data**:
   ```python
   # Detect missing values
   missing_values = df.isna().sum()
   
   # Fill missing values (various methods)
   df_filled = df.fillna(method='ffill')  # Forward fill
   df_filled = df.fillna(df.mean())       # Mean imputation
   ```

2. **Outlier Treatment**:
   ```python
   # Detect outliers using IQR
   Q1 = df['Returns'].quantile(0.25)
   Q3 = df['Returns'].quantile(0.75)
   IQR = Q3 - Q1
   
   # Filter outliers
   df_filtered = df[~((df['Returns'] < (Q1 - 1.5 * IQR)) | 
                      (df['Returns'] > (Q3 + 1.5 * IQR)))]
   ```

3. **Time Series Alignment**:
   ```python
   # Ensure consistent date frequency
   df_resampled = df.asfreq('B')  # Business day frequency
   
   # Align multiple time series
   aligned_df = pd.concat([series1, series2], axis=1).dropna()
   ```

#### LLM-Assisted Data Cleaning

LLMs can provide guidance on data cleaning strategies:

1. **Problem Identification**:
   - Analyzing data characteristics to identify potential issues
   - Suggesting appropriate cleaning methods based on data patterns

2. **Code Generation**:
   - Creating custom data cleaning functions for specific issues
   - Adapting general cleaning methods to financial data contexts

3. **Interpretation Assistance**:
   - Explaining the implications of data issues for financial analyses
   - Evaluating the potential impact of different cleaning approaches

### Data Analysis and Visualization

Effective analysis and visualization are crucial for extracting insights from financial data.

#### Excel Analysis and Visualization

1. **Basic Statistical Analysis**:
   - Descriptive statistics using functions like AVERAGE, STDEV.P, CORREL
   - Data Analysis ToolPak for regression, histograms, and more

2. **Financial Functions**:
   - NPV, IRR, XIRR for cash flow analysis
   - PRICE, YIELD, DURATION for bond calculations
   - STOCKHISTORY for historical stock data (Excel 365)

3. **Visualization**:
   - Line charts for time series data
   - Scatter plots for correlation analysis
   - Combo charts for comparing multiple metrics

#### Python Analysis and Visualization

1. **Statistical Analysis**:
   ```python
   # Basic statistics
   returns_stats = df['Returns'].describe()
   
   # Correlation analysis
   correlation_matrix = df[['TSLA', 'NVDA', 'AMD', 'META']].corr()
   
   # Time series analysis
   from statsmodels.tsa.stattools import adfuller
   adf_result = adfuller(df['TSLA'])  # Test for stationarity
   ```

2. **Financial Analysis**:
   ```python
   # Calculate daily returns
   df['Returns'] = df['Adj Close'].pct_change()
   
   # Calculate rolling volatility (20-day)
   df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
   
   # Calculate Sharpe ratio
   risk_free_rate = 0.03  # 3%
   sharpe_ratio = (df['Returns'].mean() * 252 - risk_free_rate) / (df['Returns'].std() * np.sqrt(252))
   ```

3. **Visualization**:
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns
   
   # Price chart
   plt.figure(figsize=(12, 6))
   plt.plot(df.index, df['Adj Close'])
   plt.title('Stock Price')
   plt.ylabel('Price ($)')
   plt.grid(True)
   
   # Returns distribution
   plt.figure(figsize=(10, 6))
   sns.histplot(df['Returns'].dropna(), kde=True)
   plt.title('Returns Distribution')
   
   # Correlation heatmap
   plt.figure(figsize=(8, 6))
   sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
   plt.title('Correlation Matrix')
   ```

#### LLM-Assisted Analysis and Visualization

LLMs can enhance data analysis and visualization in several ways:

1. **Analysis Strategy**:
   - Suggesting appropriate analytical techniques for specific financial questions
   - Providing step-by-step guidance for complex analyses

2. **Visualization Recommendations**:
   - Recommending the most effective chart types for different financial data
   - Providing code for customized visualizations

3. **Interpretation**:
   - Explaining the significance of statistical findings
   - Contextualizing results within financial theory and market conditions

### Case Study: Tech Stock Analysis

Let's conclude this section with a simple case study that demonstrates the process of working with financial data across our three platforms. We'll analyze the performance of four tech stocks: Tesla (TSLA), NVIDIA (NVDA), AMD, and Meta (META).

#### Excel Implementation

1. **Data Acquisition**:
   - Create a new workbook with sheets for each stock and summary analysis
   - Use Data → Get Data → From Web to import historical prices from a financial website
   - Alternatively, download CSV files and import them

2. **Data Processing**:
   - Calculate daily returns: `=(C3-C2)/C2` and copy down
   - Calculate statistics: average return, standard deviation, minimum, maximum
   - Create a correlation table using CORREL function

3. **Visualization**:
   - Create a line chart of price performance with all four stocks
   - Create a chart comparing volatility (standard deviation of returns)
   - Create a correlation heatmap using conditional formatting

#### Python Implementation

```python
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Get data for tech stocks
tickers = ['TSLA', 'NVDA', 'AMD', 'META']
start_date = '2022-01-01'
end_date = '2023-12-31'

# Download data
data = yf.download(tickers, start=start_date, end=end_date)

# Extract adjusted closing prices
prices = data['Adj Close']

# Calculate daily returns
returns = prices.pct_change().dropna()

# Calculate statistics
stats = pd.DataFrame({
    'Mean Return': returns.mean(),
    'Volatility': returns.std(),
    'Min Return': returns.min(),
    'Max Return': returns.max()
})
stats['Annualized Return'] = stats['Mean Return'] * 252
stats['Annualized Volatility'] = stats['Volatility'] * np.sqrt(252)
stats['Sharpe Ratio'] = stats['Annualized Return'] / stats['Annualized Volatility']

# Calculate correlation
correlation = returns.corr()

# Visualizations
plt.figure(figsize=(12, 6))
(prices / prices.iloc[0] * 100).plot()
plt.title('Price Performance (Indexed to 100)')
plt.ylabel('Price Index')
plt.grid(True)
plt.legend()
plt.savefig('tech_stocks_performance.png')

plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Matrix')
plt.savefig('tech_stocks_correlation.png')

# Display results
print(stats)
print("\nCorrelation Matrix:")
print(correlation)
```

#### LLM-Assisted Analysis

**Prompt to LLM**:
```
I've analyzed the performance of tech stocks (TSLA, NVDA, AMD, META) from 2022-2023 and found the following:
- NVDA had the highest returns but also high volatility
- TSLA and META showed moderate correlation (0.45)
- AMD had the largest single-day drop (-14%)

What additional analyses would you recommend to better understand these stocks? Please provide specific Python code examples for any advanced analyses you suggest.
```

This case study demonstrates how each platform can contribute to financial data analysis, from Excel's accessibility to Python's analytical power to LLMs' guidance and interpretation.

By mastering data acquisition, cleaning, and analysis across all three platforms, you'll be well-equipped to tackle the more advanced financial modeling techniques covered in subsequent chapters.

---

## Exercises

### Conceptual Review Questions

1. **Explain the complementary strengths of Excel, Python, and LLMs in computational finance. When would you choose one over the others?**

2. **What is the triangulation methodology for LLMs, and why is it particularly important in financial analysis?**

3. **Describe three common data issues in financial datasets and their potential impact on analysis results.**

4. **What are the advantages and disadvantages of using web-based financial data sources compared to subscription-based professional data services?**

5. **How has the rise of LLMs changed the workflow of financial analysts? Identify three specific tasks that are transformed by this technology.**

### Basic Financial Calculations with Excel, Python, and LLMs

1. **Total Return Calculation**
   
   Calculate the total return for an investment in NVIDIA (NVDA) stock from January 1, 2023, to December 31, 2023, including dividends.
   
   a) Implement in Excel
   b) Implement in Python
   c) Generate a solution using an LLM (ChatGPT, Claude, or Gemini)
   d) Compare the three approaches and identify any discrepancies

2. **Risk and Return Metrics**
   
   For Tesla (TSLA) stock over the past 2 years:
   
   a) Calculate the annualized return and volatility using Excel
   b) Calculate the same metrics using Python
   c) Ask an LLM to explain the significance of these metrics for Tesla
   d) Use the triangulation methodology to evaluate the LLM's explanation

3. **Portfolio Allocation**
   
   Create a portfolio with the following allocation: 30% TSLA, 25% NVDA, 20% AMD, 15% META, and 10% ASML.
   
   a) Calculate the expected return and risk of this portfolio using Excel
   b) Implement the same calculation in Python
   c) Ask an LLM to suggest an improved allocation that might increase return or reduce risk
   d) Verify the LLM's suggestion by recalculating the portfolio metrics

### Data Retrieval and Manipulation for Tech Stocks

1. **Historical Data Retrieval**
   
   Retrieve 5 years of historical price data for Intel (INTC) and Taiwan Semiconductor (TSM).
   
   a) Use Excel's data connection or import features
   b) Use Python's yfinance or pandas-datareader
   c) Ask an LLM to generate the necessary code and explain any trends
   d) Visualize the price performance using all three methods

2. **Data Cleaning Challenge**
   
   The provided dataset `tech_stocks_messy.csv` contains price data for multiple tech stocks with various issues: missing values, outliers, and date misalignments.
   
   a) Clean the dataset using Excel formulas and functions
   b) Clean the same dataset using Python
   c) Ask an LLM to identify potential issues and generate cleaning code
   d) Compare the results of the three cleaning approaches

3. **Technical Indicator Implementation**
   
   Implement the following technical indicators for ServiceNow (NOW) stock:
   - 20-day and 50-day Simple Moving Averages
   - Relative Strength Index (RSI)
   - Moving Average Convergence Divergence (MACD)
   
   a) Calculate these indicators in Excel
   b) Implement them in Python
   c) Ask an LLM to explain the significance of the indicator values
   d) Create visualizations showing the indicators alongside price data

### LLM Triangulation for Financial Definitions

1. **Beta Coefficient Analysis**
   
   a) Ask ChatGPT, Claude, and Gemini to explain the beta coefficient of a stock and how to interpret it
   b) Compare their responses, noting similarities and differences
   c) Calculate the actual beta for Moderna (MRNA) using both Excel and Python
   d) Analyze which LLM provided the most accurate and complete explanation

2. **Efficient Market Hypothesis**
   
   a) Ask the three LLMs to explain the Efficient Market Hypothesis and its implications for investors
   b) Identify any contradictions or inconsistencies in their explanations
   c) Formulate a follow-up question that tests the depth of their understanding
   d) Synthesize a comprehensive explanation based on the triangulated responses

3. **Financial Ratio Interpretation**
   
   a) Calculate the following ratios for Qualcomm (QCOM) using financial statement data:
      - Price-to-Earnings (P/E) ratio
      - Debt-to-Equity ratio
      - Return on Equity (ROE)
   
   b) Ask each LLM to interpret these ratios in the context of Qualcomm's industry
   c) Compare their interpretations with industry benchmarks
   d) Evaluate which LLM provides the most insightful and accurate analysis

---

By completing these exercises, you'll gain practical experience with all three computational approaches and develop a strong foundation for the more advanced topics covered in subsequent chapters. The triangulation methodology will help you critically evaluate LLM outputs, while the hands-on implementations in Excel and Python will build your technical skills in computational finance.

