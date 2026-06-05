# Chapter 1 Exercises: The Corporation and Financial Markets

## Exercise 1: Corporate Structure Analysis with Python

**Problem:** As a financial analyst, you need to analyze and compare the ownership structures and board compositions of three major technology companies: Apple, Microsoft, and Amazon. You'll use Python to retrieve data, perform analysis, and visualize the results.

**Data Requirements:**
1. Ownership breakdown by category (institutional, insider, retail)
2. Top 10 institutional shareholders
3. Board composition (independent vs. non-independent)
4. Executive team structure

**Tasks:**

1. Write a Python script to scrape or retrieve ownership and governance data
2. Analyze the ownership concentration using the Herfindahl-Hirschman Index (HHI)
3. Compare board independence metrics
4. Create visualizations comparing key governance metrics
5. Evaluate potential agency conflicts based on ownership and governance

**Python Solution:**

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from bs4 import BeautifulSoup
import requests

# Task 1: Retrieve ownership and governance data
def get_ownership_data(ticker):
    """Retrieve ownership data for a given ticker"""
    stock = yf.Ticker(ticker)
    
    # Get major holders data
    major_holders = stock.major_holders
    
    # Get institutional holders
    institutional_holders = stock.institutional_holders
    
    # Get insider holders (in real implementation, you might need more sources)
    try:
        insider_holders = stock.insider_holders
    except:
        # Create dummy data for demonstration
        insider_holders = pd.DataFrame({
            'Name': ['CEO', 'CFO', 'CTO'],
            'Shares': [100000, 50000, 30000],
            'Value': [15000000, 7500000, 4500000]
        })
    
    return {
        'major_holders': major_holders,
        'institutional_holders': institutional_holders,
        'insider_holders': insider_holders
    }

# Task 2: Calculate Herfindahl-Hirschman Index (HHI)
def calculate_hhi(holders_df):
    """Calculate HHI for ownership concentration"""
    # Get total shares outstanding (in a real implementation, get this from API)
    total_shares = holders_df['Shares'].sum()
    
    # Calculate market share percentages
    market_shares = holders_df['Shares'] / total_shares * 100
    
    # Calculate HHI (sum of squared percentages)
    hhi = np.sum(market_shares ** 2)
    
    return hhi

# Task 3: Analyze board independence
def analyze_board(company_name, ticker):
    """Analyze board composition and independence"""
    # In a real implementation, you would scrape this data
    # For demonstration, we'll use dummy data
    
    boards = {
        'AAPL': {
            'total_directors': 8,
            'independent': 7,
            'avg_tenure': 6.5,
            'committees': {
                'Audit': {'members': 3, 'independent': 3},
                'Compensation': {'members': 4, 'independent': 4},
                'Nominating': {'members': 3, 'independent': 3}
            }
        },
        'MSFT': {
            'total_directors': 12,
            'independent': 11,
            'avg_tenure': 5.2,
            'committees': {
                'Audit': {'members': 4, 'independent': 4},
                'Compensation': {'members': 5, 'independent': 5},
                'Nominating': {'members': 4, 'independent': 4}
            }
        },
        'AMZN': {
            'total_directors': 10,
            'independent': 8,
            'avg_tenure': 4.8,
            'committees': {
                'Audit': {'members': 4, 'independent': 4},
                'Compensation': {'members': 3, 'independent': 3},
                'Nominating': {'members': 3, 'independent': 3}
            }
        }
    }
    
    board_data = boards.get(ticker, {})
    
    # Calculate independence percentage
    if board_data:
        board_data['independence_pct'] = board_data['independent'] / board_data['total_directors'] * 100
    
    return board_data

# Task 4: Create visualizations
def visualize_governance_comparison(companies, ownership_data, board_data):
    """Create visualizations comparing governance metrics"""
    # Set up the figure
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Ownership Distribution
    ax1 = fig.add_subplot(221)
    ownership_df = pd.DataFrame({
        company: [
            ownership_data[company]['major_holders'].iloc[0, 1] if len(ownership_data[company]['major_holders']) > 0 else 0,
            ownership_data[company]['major_holders'].iloc[1, 1] if len(ownership_data[company]['major_holders']) > 1 else 0,
            100 - float(ownership_data[company]['major_holders'].iloc[0, 1]) - 
                  float(ownership_data[company]['major_holders'].iloc[1, 1]) if len(ownership_data[company]['major_holders']) > 1 else 0
        ] for company in companies
    }, index=['Institutional', 'Insider', 'Retail'])
    
    ownership_df.plot(kind='bar', ax=ax1)
    ax1.set_title('Ownership Distribution')
    ax1.set_ylabel('Percentage (%)')
    ax1.set_ylim(0, 100)
    ax1.legend(title='Company')
    
    # 2. Board Independence
    ax2 = fig.add_subplot(222)
    independence_df = pd.DataFrame({
        'Independence': [board_data[company]['independence_pct'] for company in companies],
        'Non-Independence': [100 - board_data[company]['independence_pct'] for company in companies]
    }, index=companies)
    
    independence_df.plot(kind='bar', stacked=True, ax=ax2, color=['green', 'red'])
    ax2.set_title('Board Independence')
    ax2.set_ylabel('Percentage (%)')
    ax2.set_ylim(0, 100)
    ax2.legend(title='Status')
    
    # 3. Institutional Ownership Concentration
    ax3 = fig.add_subplot(223)
    hhi_values = [calculate_hhi(ownership_data[company]['institutional_holders']) for company in companies]
    sns.barplot(x=companies, y=hhi_values, ax=ax3)
    ax3.set_title('Ownership Concentration (HHI)')
    ax3.set_ylabel('HHI Value')
    
    # 4. Board Tenure
    ax4 = fig.add_subplot(224)
    tenure_values = [board_data[company]['avg_tenure'] for company in companies]
    sns.barplot(x=companies, y=tenure_values, ax=ax4)
    ax4.set_title('Average Board Tenure')
    ax4.set_ylabel('Years')
    
    plt.tight_layout()
    plt.savefig('governance_comparison.png')
    plt.show()

# Task 5: Evaluate potential agency conflicts
def evaluate_agency_conflicts(companies, ownership_data, board_data):
    """Evaluate potential agency conflicts based on ownership and governance"""
    results = []
    
    for company in companies:
        # Check ownership concentration
        institutional_pct = float(ownership_data[company]['major_holders'].iloc[0, 1]) if len(ownership_data[company]['major_holders']) > 0 else 0
        insider_pct = float(ownership_data[company]['major_holders'].iloc[1, 1]) if len(ownership_data[company]['major_holders']) > 1 else 0
        
        # Check board independence
        board_independence = board_data[company]['independence_pct']
        
        # Calculate top 5 institutional concentration
        top5_pct = ownership_data[company]['institutional_holders'].head(5)['% Out'].sum() if len(ownership_data[company]['institutional_holders']) >= 5 else 0
        
        # Evaluate potential conflicts
        conflicts = []
        
        if institutional_pct > 80:
            conflicts.append("High institutional ownership may lead to short-termism")
        
        if insider_pct < 5:
            conflicts.append("Low insider ownership may reduce management alignment with shareholders")
            
        if board_independence < 75:
            conflicts.append("Board may not be sufficiently independent to provide oversight")
            
        if top5_pct > 25:
            conflicts.append("Concentrated institutional ownership may lead to unbalanced influence")
            
        results.append({
            'Company': company,
            'Institutional Ownership': f"{institutional_pct:.1f}%",
            'Insider Ownership': f"{insider_pct:.1f}%",
            'Board Independence': f"{board_independence:.1f}%",
            'Top 5 Institutional Concentration': f"{top5_pct:.1f}%",
            'Potential Conflicts': conflicts
        })
    
    return pd.DataFrame(results)

# Main execution
def main():
    companies = ['AAPL', 'MSFT', 'AMZN']
    company_names = ['Apple', 'Microsoft', 'Amazon']
    
    # Get ownership data for each company
    ownership_data = {company: get_ownership_data(company) for company in companies}
    
    # Get board data for each company
    board_data = {company: analyze_board(name, company) for company, name in zip(companies, company_names)}
    
    # Visualize governance comparison
    visualize_governance_comparison(companies, ownership_data, board_data)
    
    # Evaluate agency conflicts
    agency_analysis = evaluate_agency_conflicts(companies, ownership_data, board_data)
    print(agency_analysis)

if __name__ == "__main__":
    main()
```

**Note:** The above code uses some dummy data for demonstration purposes. In a real implementation, you would need to retrieve the actual data from financial databases, company filings, or web scraping.

## Exercise 2: Market Data Visualization in Excel

**Problem:** You are preparing a market overview presentation for investors and need to create visualizations of key market indicators and sector performance. Using Excel, you'll create an interactive dashboard that allows users to compare different market segments and time periods.

**Data Requirements:**
1. Historical price data for major indices (S&P 500, Nasdaq, Dow Jones)
2. Sector performance data
3. Interest rates and yield curve data
4. Market volatility metrics

**Tasks:**
1. Set up data connections to retrieve market data
2. Create interactive charts for comparing index performance
3. Design a sector performance heatmap
4. Implement a yield curve visualization tool
5. Build a dashboard with dynamic time period selection

**Excel Solution:**

```excel
' This is the VBA code for the Excel solution

Option Explicit

Sub CreateMarketDashboard()
    ' Clear any existing worksheets except Data
    ClearWorksheets
    
    ' Create necessary worksheets
    CreateWorksheetStructure
    
    ' Import market data
    ImportMarketData
    
    ' Create index performance chart
    CreateIndexPerformanceChart
    
    ' Create sector heatmap
    CreateSectorHeatmap
    
    ' Create yield curve visualization
    CreateYieldCurveChart
    
    ' Create volatility chart
    CreateVolatilityChart
    
    ' Set up dashboard controls
    SetupDashboardControls
    
    ' Format dashboard
    FormatDashboard
    
    ' Set Dashboard as active sheet
    Sheets("Dashboard").Activate
    
    MsgBox "Market Dashboard created successfully!", vbInformation
End Sub

Sub ClearWorksheets()
    Dim ws As Worksheet
    
    Application.DisplayAlerts = False
    For Each ws In ThisWorkbook.Worksheets
        If ws.Name <> "Data" And ws.Name <> "Sheet1" Then
            ws.Delete
        End If
    Next ws
    Application.DisplayAlerts = True
    
    ' Rename Sheet1 if it exists
    On Error Resume Next
    Sheets("Sheet1").Name = "Data"
    On Error GoTo 0
End Sub

Sub CreateWorksheetStructure()
    ' Check if Data sheet exists, if not create it
    On Error Resume Next
    If Sheets("Data").Name <> "Data" Then
        Worksheets.Add.Name = "Data"
    End If
    On Error GoTo 0
    
    ' Add other necessary sheets
    On Error Resume Next
    Worksheets.Add.Name = "Dashboard"
    Worksheets.Add.Name = "Index Performance"
    Worksheets.Add.Name = "Sector Performance"
    Worksheets.Add.Name = "Yield Curve"
    Worksheets.Add.Name = "Volatility"
    On Error GoTo 0
End Sub

Sub ImportMarketData()
    ' In a real implementation, you would use Power Query or other methods
    ' to import actual market data. For this exercise, we'll simulate it.
    
    Dim dataSheet As Worksheet
    Set dataSheet = Sheets("Data")
    
    ' Clear existing data
    dataSheet.Cells.Clear
    
    ' Create headers for index data
    dataSheet.Range("A1").Value = "Date"
    dataSheet.Range("B1").Value = "S&P 500"
    dataSheet.Range("C1").Value = "Nasdaq"
    dataSheet.Range("D1").Value = "Dow Jones"
    
    ' Create sample index data (last 12 months)
    Dim i As Integer
    Dim baseDate As Date
    baseDate = DateAdd("m", -12, Date)
    
    For i = 0 To 250 ' Simulate ~1 year of trading days
        dataSheet.Cells(i + 2, 1).Value = DateAdd("d", i, baseDate)
        
        ' Simulated S&P 500 data
        If i = 0 Then
            dataSheet.Cells(i + 2, 2).Value = 4000
        Else
            dataSheet.Cells(i + 2, 2).Value = dataSheet.Cells(i + 1, 2).Value * (1 + (Rnd() * 0.02 - 0.01))
        End If
        
        ' Simulated Nasdaq data
        If i = 0 Then
            dataSheet.Cells(i + 2, 3).Value = 12000
        Else
            dataSheet.Cells(i + 2, 3).Value = dataSheet.Cells(i + 1, 3).Value * (1 + (Rnd() * 0.025 - 0.01))
        End If
        
        ' Simulated Dow Jones data
        If i = 0 Then
            dataSheet.Cells(i + 2, 4).Value = 32000
        Else
            dataSheet.Cells(i + 2, 4).Value = dataSheet.Cells(i + 1, 4).Value * (1 + (Rnd() * 0.018 - 0.009))
        End If
    Next i
    
    ' Create sector performance data
    dataSheet.Range("F1").Value = "Sector"
    dataSheet.Range("G1").Value = "1-Month Return"
    dataSheet.Range("H1").Value = "3-Month Return"
    dataSheet.Range("I1").Value = "YTD Return"
    dataSheet.Range("J1").Value = "1-Year Return"
    
    Dim sectors As Variant
    sectors = Array("Technology", "Healthcare", "Financials", "Consumer Discretionary", _
                   "Communication Services", "Industrials", "Consumer Staples", _
                   "Energy", "Utilities", "Materials", "Real Estate")
    
    For i = 0 To UBound(sectors)
        dataSheet.Cells(i + 2, 6).Value = sectors(i)
        dataSheet.Cells(i + 2, 7).Value = Rnd() * 0.2 - 0.05 ' 1-month return (-5% to 15%)
        dataSheet.Cells(i + 2, 8).Value = Rnd() * 0.3 - 0.1 ' 3-month return (-10% to 20%)
        dataSheet.Cells(i + 2, 9).Value = Rnd() * 0.4 - 0.15 ' YTD return (-15% to 25%)
        dataSheet.Cells(i + 2, 10).Value = Rnd() * 0.5 - 0.2 ' 1-Year return (-20% to 30%)
    Next i
    
    ' Create yield curve data
    dataSheet.Range("L1").Value = "Maturity"
    dataSheet.Range("M1").Value = "Current Yield"
    dataSheet.Range("N1").Value = "1-Month Ago"
    dataSheet.Range("O1").Value = "1-Year Ago"
    
    Dim maturities As Variant
    maturities = Array("1-Month", "3-Month", "6-Month", "1-Year", "2-Year", "5-Year", "10-Year", "30-Year")
    
    ' Base yields (these would be real data in a real implementation)
    Dim currentYield As Double
    Dim lastMonthYield As Double
    Dim lastYearYield As Double
    
    For i = 0 To UBound(maturities)
        dataSheet.Cells(i + 2, 12).Value = maturities(i)
        
        ' Simulate an upward sloping yield curve
        Select Case i
            Case 0: currentYield = 3.75 + Rnd() * 0.25
            Case 1: currentYield = 3.8 + Rnd() * 0.3
            Case 2: currentYield = 3.9 + Rnd() * 0.35
            Case 3: currentYield = 4.0 + Rnd() * 0.4
            Case 4: currentYield = 4.2 + Rnd() * 0.4
            Case 5: currentYield = 4.3 + Rnd() * 0.5
            Case 6: currentYield = 4.4 + Rnd() * 0.5
            Case 7: currentYield = 4.5 + Rnd() * 0.6
        End Select
        
        dataSheet.Cells(i + 2, 13).Value = currentYield / 100 ' Current yield
        
        ' Last month's yields (slightly different)
        lastMonthYield = currentYield + (Rnd() * 0.4 - 0.2)
        dataSheet.Cells(i + 2, 14).Value = lastMonthYield / 100
        
        ' Last year's yields (lower, simulating rising rate environment)
        lastYearYield = currentYield - (1 + Rnd())
        dataSheet.Cells(i + 2, 15).Value = lastYearYield / 100
    Next i
    
    ' Create volatility data
    dataSheet.Range("Q1").Value = "Date"
    dataSheet.Range("R1").Value = "VIX"
    
    For i = 0 To 250 ' Simulate ~1 year of trading days
        dataSheet.Cells(i + 2, 17).Value = DateAdd("d", i, baseDate)
        
        ' Simulated VIX data
        If i = 0 Then
            dataSheet.Cells(i + 2, 18).Value = 20 + Rnd() * 5
        Else
            ' VIX tends to spike occasionally
            Dim randomSpike As Double
            randomSpike = Rnd()
            
            If randomSpike > 0.98 Then ' Occasional large spike
                dataSheet.Cells(i + 2, 18).Value = dataSheet.Cells(i + 1, 18).Value * (1 + (Rnd() * 0.3))
            ElseIf randomSpike > 0.9 Then ' More frequent small spikes
                dataSheet.Cells(i + 2, 18).Value = dataSheet.Cells(i + 1, 18).Value * (1 + (Rnd() * 0.1))
            Else
                ' Mean reversion toward ~20
                dataSheet.Cells(i + 2, 18).Value = dataSheet.Cells(i + 1, 18).Value + _
                    (20 - dataSheet.Cells(i + 1, 18).Value) * 0.05 + (Rnd() * 1 - 0.5)
            End If
            
            ' Ensure VIX doesn't go below 9 or above 80
            If dataSheet.Cells(i + 2, 18).Value < 9 Then
                dataSheet.Cells(i + 2, 18).Value = 9 + Rnd() * 2
            ElseIf dataSheet.Cells(i + 2, 18).Value > 80 Then
                dataSheet.Cells(i + 2, 18).Value = 80 - Rnd() * 5
            End If
        End If
    Next i
    
    ' Format data ranges as tables for easier reference
    dataSheet.Range("A1:D252").Select
    ActiveSheet.ListObjects.Add(xlSrcRange, Selection, , xlYes).Name = "IndexData"
    
    dataSheet.Range("F1:J13").Select
    ActiveSheet.ListObjects.Add(xlSrcRange, Selection, , xlYes).Name = "SectorData"
    
    dataSheet.Range("L1:O10").Select
    ActiveSheet.ListObjects.Add(xlSrcRange, Selection, , xlYes).Name = "YieldData"
    
    dataSheet.Range("Q1:R252").Select
    ActiveSheet.ListObjects.Add(xlSrcRange, Selection, , xlYes).Name = "VolatilityData"
    
    ' Format data appropriately
    dataSheet.Range("G2:J13").NumberFormat = "0.0%"
    dataSheet.Range("M2:O10").NumberFormat = "0.00%"
    
    ' Hide the data sheet
    dataSheet.Visible = xlSheetVeryHidden
End Sub

Sub CreateIndexPerformanceChart()
    Dim perfSheet As Worksheet
    Set perfSheet = Sheets("Index Performance")
    
    ' Clear the sheet
    perfSheet.Cells.Clear
    
    ' Create a title
    perfSheet.Range("A1").Value = "Major Market Indices Performance"
    perfSheet.Range("A1").Font.Size = 16
    perfSheet.Range("A1").Font.Bold = True
    
    ' Create a normalized performance calculation
    perfSheet.Range("A3").Value = "Start Date:"
    perfSheet.Range("B3").Value = DateAdd("m", -3, Date) ' Default to 3 months
    
    perfSheet.Range("D3").Value = "End Date:"
    perfSheet.Range("E3").Value = Date
    
    perfSheet.Range("G3").Value = "Normalize Performance:"
    
    ' Add a checkbox for normalized performance
    Dim chkNormalize As CheckBox
    Set chkNormalize = perfSheet.CheckBoxes.Add(perfSheet.Range("H3").Left, _
                                               perfSheet.Range("H3").Top, 15, 15)
    chkNormalize.Caption = ""
    chkNormalize.Value = xlOn
    
    ' Create named range for date selections
    perfSheet.Range("B3").Name = "StartDate"
    perfSheet.Range("E3").Name = "EndDate"
    
    ' Format date cells
    perfSheet.Range("B3").NumberFormat = "mm/dd/yyyy"
    perfSheet.Range("E3").NumberFormat = "mm/dd/yyyy"
    
    ' Add a chart
    Dim cht As Chart
    Set cht = perfSheet.Shapes.AddChart2(201, xlLine, 50, 100, 800, 400).Chart
    
    ' Set the chart source data
    cht.SetSourceData Source:=Sheets("Data").Range("A1:D252")
    
    ' Add a title
    cht.ChartTitle.Text = "Market Indices Performance"
    
    ' Customize the chart
    With cht
        .HasLegend = True
        .Legend.Position = xlLegendPositionBottom
        
        .Axes(xlCategory, xlPrimary).HasTitle = True
        .Axes(xlCategory, xlPrimary).AxisTitle.Text = "Date"
        
        .Axes(xlValue, xlPrimary).HasTitle = True
        .Axes(xlValue, xlPrimary).AxisTitle.Text = "Price"
        
        ' Format x-axis to show dates
        .Axes(xlCategory).CategoryType = xlTimeScale
        .Axes(xlCategory).TickLabels.NumberFormat = "mm/dd/yyyy"
        
        ' Apply date filter
        .Axes(xlCategory).MinimumScale = DateAdd("m", -3, Date)
        .Axes(xlCategory).MaximumScale = Date
    End With
    
    ' Add controls to change the time period
    perfSheet.Range("A5").Value = "Time Period:"
    
    ' Create option buttons for time periods
    Dim optOneMonth As OptionButton
    Set optOneMonth = perfSheet.OptionButtons.Add(perfSheet.Range("B5").Left, _
                                                perfSheet.Range("B5").Top, 80, 20)
    optOneMonth.Caption = "1 Month"
    optOneMonth.GroupName = "TimePeriod"
    
    Dim optThreeMonth As OptionButton
    Set optThreeMonth = perfSheet.OptionButtons.Add(perfSheet.Range("C5").Left, _
                                                  perfSheet.Range("C5").Top, 80, 20)
    optThreeMonth.Caption = "3 Months"
    optThreeMonth.GroupName = "TimePeriod"
    optThreeMonth.Value = True
    
    Dim optSixMonth As OptionButton
    Set optSixMonth = perfSheet.OptionButtons.Add(perfSheet.Range("D5").Left, _
                                                perfSheet.Range("D5").Top, 80, 20)
    optSixMonth.Caption = "6 Months"
    optSixMonth.GroupName = "TimePeriod"
    
    Dim optOneYear As OptionButton
    Set optOneYear = perfSheet.OptionButtons.Add(perfSheet.Range("E5").Left, _
                                               perfSheet.Range("E5").Top, 80, 20)
    optOneYear.Caption = "1 Year"
    optOneYear.GroupName = "TimePeriod"
    
    Dim optYTD As OptionButton
    Set optYTD = perfSheet.OptionButtons.Add(perfSheet.Range("F5").Left, _
                                           perfSheet.Range("F5").Top, 80, 20)
    optYTD.Caption = "YTD"
    optYTD.GroupName = "TimePeriod"
    
    ' Create a button to update the chart
    Dim btnUpdate As Button
    Set btnUpdate = perfSheet.Buttons.Add(perfSheet.Range("G5").Left, _
                                         perfSheet.Range("G5").Top, 80, 20)
    btnUpdate.Caption = "Update Chart"
    btnUpdate.OnAction = "UpdateIndexChart"
    
    ' Add code to normalize the performance
    perfSheet.Range("J1").Value = "Helper Calculations - Do Not Modify"
    perfSheet.Range("J2").Value = "S&P 500 Base"
    perfSheet.Range("J3").Value = "Nasdaq Base"
    perfSheet.Range("J4").Value = "Dow Base"
    
    perfSheet.Range("K2").Formula = "=INDEX(Data!$B$2:$B$252, MATCH(StartDate, Data!$A$2:$A$252, 1))"
    perfSheet.Range("K3").Formula = "=INDEX(Data!$C$2:$C$252, MATCH(StartDate, Data!$A$2:$A$252, 1))"
    perfSheet.Range("K4").Formula = "=INDEX(Data!$D$2:$D$252, MATCH(StartDate, Data!$A$2:$A$252, 1))"
    
    ' Hide the helper calculations
    perfSheet.Range("J1:K4").Font.ColorIndex = 2 ' White text
    
    ' Create event handling for the controls
    ' This would be done in the class module in a real implementation
    ' For this exercise, we'll use the button to trigger updates
    
    ' Update the chart initially
    UpdateIndexChart
End Sub

Sub UpdateIndexChart()
    Dim perfSheet As Worksheet
    Set perfSheet = Sheets("Index Performance")
    
    ' Get the selected option button
    Dim timePeriod As String
    Dim i As Integer
    
    For i = 1 To perfSheet.OptionButtons.Count
        If perfSheet.OptionButtons(i).Value = xlOn Then
            timePeriod = perfSheet.OptionButtons(i).Caption
            Exit For
        End If
    Next i
    
    ' Set the start date based on the selected time period
    Select Case timePeriod
        Case "1 Month"
            perfSheet.Range("StartDate").Value = DateAdd("m", -1, Date)
        Case "3 Months"
            perfSheet.Range("StartDate").Value = DateAdd("m", -3, Date)
        Case "6 Months"
            perfSheet.Range("StartDate").Value = DateAdd("m", -6, Date)
        Case "1 Year"
            perfSheet.Range("StartDate").Value = DateAdd("yyyy", -1, Date)
        Case "YTD"
            perfSheet.Range("StartDate").Value = DateSerial(Year(Date), 1, 1)
    End Select
    
    ' Get the chart
    Dim cht As Chart
    Set cht = perfSheet.ChartObjects(1).Chart
    
    ' Update the chart's date range
    cht.Axes(xlCategory).MinimumScale = perfSheet.Range("StartDate").Value
    cht.Axes(xlCategory).MaximumScale = perfSheet.Range("EndDate").Value
    
    ' Check if normalization is on
    Dim normalizeOn As Boolean
    normalizeOn = (perfSheet.CheckBoxes(1).Value = xlOn)
    
    If normalizeOn Then
        ' Create a new data series for normalized performance
        Dim dataSheet As Worksheet
        Set dataSheet = Sheets("Data")
        
        ' Find the starting index
        Dim startIndex As Long
        startIndex = Application.Match(perfSheet.Range("StartDate").Value, dataSheet.Range("A2:A252"), 1) + 1
        
        ' Get the base values
        Dim spBase As Double, nasdaqBase As Double, dowBase As Double
        spBase = dataSheet.Cells(startIndex, 2).Value
        nasdaqBase = dataSheet.Cells(startIndex, 3).Value
        dowBase = dataSheet.Cells(startIndex, 4).Value
        
        ' Create the series formula
        Dim spSeries As String, nasdaqSeries As String, dowSeries As String
        
        spSeries = "=SERIES(""S&P 500"",Data!$A$" & startIndex & ":$A$252,Data!$B$" & startIndex & _
                   ":$B$252/Data!$B$" & startIndex & "*100,1)"
                   
        nasdaqSeries = "=SERIES(""Nasdaq"",Data!$A$" & startIndex & ":$A$252,Data!$C$" & startIndex & _
                       ":$C$252/Data!$C$" & startIndex & "*100,2)"
                       
        dowSeries = "=SERIES(""Dow Jones"",Data!$A$" & startIndex & ":$A$252,Data!$D$" & startIndex & _
                    ":$D$252/Data!$D$" & startIndex & "*100,3)"
        
        ' Delete existing series
        Do While cht.SeriesCollection.Count > 0
            cht.SeriesCollection(1).Delete
        Loop
        
        ' Add normalized series
        cht.SeriesCollection.Add spSeries
        cht.SeriesCollection.Add nasdaqSeries
        cht.SeriesCollection.Add dowSeries
        
        ' Update y-axis title
        cht.Axes(xlValue, xlPrimary).AxisTitle.Text = "Normalized Performance (Base=100)"
    Else
        ' Use the original data
        cht.SetSourceData Source:=Sheets("Data").Range("A1:D252")
        
        ' Update y-axis title
        cht.Axes(xlValue, xlPrimary).AxisTitle.Text = "Price"
    End If
    
    ' Update chart title
    cht.ChartTitle.Text = "Market Indices Performance: " & timePeriod
End Sub

Sub CreateSectorHeatmap()
    Dim sectorSheet As Worksheet
    Set sectorSheet = Sheets("Sector Performance")
    
    ' Clear the sheet
    sectorSheet.Cells.Clear
    
    ' Create a title
    sectorSheet.Range("A1").Value = "Sector Performance Heatmap"
    sectorSheet.Range("A1").Font.Size = 16
    sectorSheet.Range("A1").Font.Bold = True
    
    ' Copy sector data from the data sheet
    Sheets("Data").ListObjects("SectorData").Range.Copy
    sectorSheet.Range("A3").PasteSpecial xlPasteValues
    sectorSheet.Range("A3").PasteSpecial xlPasteFormats
    
    ' Format as a table
    sectorSheet.Range("A3:E14").Select
    ActiveSheet.ListObjects.Add(xlSrcRange, Selection, , xlYes).Name = "SectorPerformanceTable"
    
    ' Format as percentages
    sectorSheet.Range("B4:E14").NumberFormat = "0.00%"
    
    ' Add conditional formatting (heat map)
    Dim redTheme As Variant
    redTheme = Array(255, 0, 0) ' RGB values for negative returns
    
    Dim greenTheme As Variant
    greenTheme = Array(0, 255, 0) ' RGB values for positive returns
    
    ' Add conditional formatting to each time period
    AddHeatMapFormatting sectorSheet.Range("B4:B14"), redTheme, greenTheme
    AddHeatMapFormatting sectorSheet.Range("C4:C14"), redTheme, greenTheme
    AddHeatMapFormatting sectorSheet.Range("D4:D14"), redTheme, greenTheme
    AddHeatMapFormatting sectorSheet.Range("E4:E14"), redTheme, greenTheme
    
    ' Add time period selector
    sectorSheet.Range("G3").Value = "Select Time Period:"
    
    ' Add dropdown for time period selection
    Dim cmbTimePeriod As DropDown
    Set cmbTimePeriod = sectorSheet.DropDowns.Add(sectorSheet.Range("H3").Left, _
                                                sectorSheet.Range("H3").Top, 120, 20)
    With cmbTimePeriod
        .AddItem "1-Month Return"
        .AddItem "3-Month Return"
        .AddItem "YTD Return"
        .AddItem "1-Year Return"
        .ListIndex = 0 ' Default to 1-Month
    End With
    
    ' Add a button to create the bar chart
    Dim btnCreateChart As Button
    Set btnCreateChart = sectorSheet.Buttons.Add(sectorSheet.Range("I3").Left, _
                                                sectorSheet.Range("I3").Top, 120, 20)
    btnCreateChart.Caption = "Create Chart"
    btnCreateChart.OnAction = "CreateSectorBarChart"
    
    ' Create a place for the chart
    sectorSheet.Range("G5").Value = "Sector Performance Chart"
    sectorSheet.Range("G5").Font.Bold = True
End Sub

Sub AddHeatMapFormatting(rng As Range, redTheme As Variant, greenTheme As Variant)
    ' Add conditional formatting for a heatmap effect
    rng.FormatConditions.Delete
    
    ' Add a color scale conditional format
    rng.FormatConditions.AddColorScale ColorScaleType:=3
    
    ' Configure the color scale
    With rng.FormatConditions(1)
        .ColorScaleCriteria(1).Type = xlConditionValueLowestValue
        .ColorScaleCriteria(1).FormatColor.Color = RGB(redTheme(0), redTheme(1), redTheme(2))
        
        .ColorScaleCriteria(2).Type = xlConditionValueNumber
        .ColorScaleCriteria(2).Value = 0
        .ColorScaleCriteria(2).FormatColor.Color = RGB(255, 255, 255)
        
        .ColorScaleCriteria(3).Type = xlConditionValueHighestValue
        .ColorScaleCriteria(3).FormatColor.Color = RGB(greenTheme(0), greenTheme(1), greenTheme(2))
    End With
End Sub

Sub CreateSectorBarChart()
    Dim sectorSheet As Worksheet
    Set sectorSheet = Sheets("Sector Performance")
    
    ' Determine the selected time period
    Dim selectedPeriod As String
    Dim columnIndex As Integer
    
    selectedPeriod = sectorSheet.DropDowns(1).List(sectorSheet.DropDowns(1).ListIndex)
    
    ' Map the selected period to the corresponding column
    Select Case selectedPeriod
        Case "1-Month Return"
            columnIndex = 2
        Case "3-Month Return"
            columnIndex = 3
        Case "YTD Return"
            columnIndex = 4
        Case "1-Year Return"
            columnIndex = 5
    End Select
    
    ' Delete existing chart if there is one
    On Error Resume Next
    sectorSheet.ChartObjects("SectorBarChart").Delete
    On Error GoTo 0
    
    ' Create a chart for the selected time period
    Dim chartRange As Range
    Set chartRange = sectorSheet.Range("A3:A14," & sectorSheet.Cells(3, columnIndex).Address & ":" & _
                                      sectorSheet.Cells(14, columnIndex).Address)
    
    Dim cht As ChartObject
    Set cht = sectorSheet.ChartObjects.Add(sectorSheet.Range("G6").Left, sectorSheet.Range("G6").Top, 500, 300)
    cht.Name = "SectorBarChart"
    
    ' Set up the chart
    With cht.Chart
        .SetSourceData Source:=chartRange
        .ChartType = xlBarClustered
        .HasTitle = True
        .ChartTitle.Text = "Sector Performance: " & selectedPeriod
        
        ' Sort the data from highest to lowest
        .Sort.SortFields.Add Key:=.SeriesCollection(1).Values, Order:=xlDescending
        .Sort.Apply
        
        ' Format the bars with gradient based on values
        .SeriesCollection(1).Format.Fill.Visible = msoTrue
        .SeriesCollection(1).Format.Fill.Type = msoFillGradient
        
        ' Add data labels
        .SeriesCollection(1).HasDataLabels = True
        .SeriesCollection(1).DataLabels.NumberFormat = "0.00%"
        .SeriesCollection(1).DataLabels.Position = xlLabelPositionOutsideEnd
        
        ' Remove the legend
        .HasLegend = False
        
        ' Format the value axis
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = selectedPeriod
        .Axes(xlValue).MajorGridlines.Format.Line.Visible = msoTrue
        .Axes(xlValue).MajorGridlines.Format.Line.ForeColor.RGB = RGB(200, 200, 200)
        .Axes(xlValue).NumberFormat = "0.00%"
        
        ' Add a zero line for reference
        .Axes(xlValue).DisplayUnit = xlNone
        .Axes(xlValue).CrossesAt = 0
        .Axes(xlValue).Crosses = xlCustom
        
        ' Format colors based on positive/negative values
        For Each pt In .SeriesCollection(1).Points
            If pt.Value < 0 Then
                pt.Format.Fill.ForeColor.RGB = RGB(255, 150, 150)
            Else
                pt.Format.Fill.ForeColor.RGB = RGB(150, 255, 150)
            End If
        Next pt
    End With
End Sub

Sub CreateYieldCurveChart()
    Dim yieldSheet As Worksheet
    Set yieldSheet = Sheets("Yield Curve")
    
    ' Clear the sheet
    yieldSheet.Cells.Clear
    
    ' Create a title
    yieldSheet.Range("A1").Value = "Yield Curve Analysis"
    yieldSheet.Range("A1").Font.Size = 16
    yieldSheet.Range("A1").Font.Bold = True
    
    ' Copy yield curve data from the data sheet
    Sheets("Data").ListObjects("YieldData").Range.Copy
    yieldSheet.Range("A3").PasteSpecial xlPasteValues
    yieldSheet.Range("A3").PasteSpecial xlPasteFormats
    
    ' Format as a table
    yieldSheet.Range("A3:D11").Select
    ActiveSheet.ListObjects.Add(xlSrcRange, Selection, , xlYes).Name = "YieldCurveTable"
    
    ' Format as percentages
    yieldSheet.Range("B4:D11").NumberFormat = "0.00%"
    
    ' Create a yield curve chart
    Dim cht As Chart
    Set cht = yieldSheet.Shapes.AddChart2(201, xlLine, 50, 200, 800, 400).Chart
    
    ' Set up the chart
    With cht
        .SetSourceData Source:=yieldSheet.Range("A3:D11")
        .ChartType = xlLine
        
        .HasTitle = True
        .ChartTitle.Text = "Treasury Yield Curve Comparison"
        
        .HasLegend = True
        .Legend.Position = xlLegendPositionBottom
        
        .Axes(xlCategory, xlPrimary).HasTitle = True
        .Axes(xlCategory, xlPrimary).AxisTitle.Text = "Maturity"
        
        .Axes(xlValue, xlPrimary).HasTitle = True
        .Axes(xlValue, xlPrimary).AxisTitle.Text = "Yield"
        .Axes(xlValue, xlPrimary).NumberFormat = "0.00%"
        
        ' Add series names
        .SeriesCollection(1).Name = "Current Yield"
        .SeriesCollection(2).Name = "1-Month Ago"
        .SeriesCollection(3).Name = "1-Year Ago"
        
        ' Format the series
        .SeriesCollection(1).Format.Line.ForeColor.RGB = RGB(0, 112, 192)
        .SeriesCollection(1).Format.Line.Weight = 3
        
        .SeriesCollection(2).Format.Line.ForeColor.RGB = RGB(112, 48, 160)
        .SeriesCollection(2).Format.Line.Weight = 2
        
        .SeriesCollection(3).Format.Line.ForeColor.RGB = RGB(192, 0, 0)
        .SeriesCollection(3).Format.Line.Weight = 2
        
        ' Add markers
        .SeriesCollection(1).MarkerStyle = xlMarkerStyleCircle
        .SeriesCollection(1).MarkerSize = 8
        
        .SeriesCollection(2).MarkerStyle = xlMarkerStyleDiamond
        .SeriesCollection(2).MarkerSize = 8
        
        .SeriesCollection(3).MarkerStyle = xlMarkerStyleSquare
        .SeriesCollection(3).MarkerSize = 8
        
        ' Add gridlines
        .Axes(xlValue).MajorGridlines.Format.Line.Visible = msoTrue
        .Axes(xlValue).MajorGridlines.Format.Line.ForeColor.RGB = RGB(200, 200, 200)
    End With
    
    ' Add yield curve analysis
    yieldSheet.Range("A15").Value = "Yield Curve Analysis:"
    yieldSheet.Range("A15").Font.Bold = True
    
    yieldSheet.Range("A16").Value = "Current 10Y-2Y Spread:"
    yieldSheet.Range("B16").Formula = "=INDEX(YieldCurveTable[Current Yield],MATCH(""10-Year"",YieldCurveTable[Maturity],0))-INDEX(YieldCurveTable[Current Yield],MATCH(""2-Year"",YieldCurveTable[Maturity],0))"
    yieldSheet.Range("B16").NumberFormat = "0.00%"
    
    yieldSheet.Range("A17").Value = "1-Month Ago 10Y-2Y Spread:"
    yieldSheet.Range("B17").Formula = "=INDEX(YieldCurveTable[1-Month Ago],MATCH(""10-Year"",YieldCurveTable[Maturity],0))-INDEX(YieldCurveTable[1-Month Ago],MATCH(""2-Year"",YieldCurveTable[Maturity],0))"
    yieldSheet.Range("B17").NumberFormat = "0.00%"
    
    yieldSheet.Range("A18").Value = "1-Year Ago 10Y-2Y Spread:"
    yieldSheet.Range("B18").Formula = "=INDEX(YieldCurveTable[1-Year Ago],MATCH(""10-Year"",YieldCurveTable[Maturity],0))-INDEX(YieldCurveTable[1-Year Ago],MATCH(""2-Year"",YieldCurveTable[Maturity],0))"
    yieldSheet.Range("B18").NumberFormat = "0.00%"
    
    yieldSheet.Range("A20").Value = "Curve Status:"
    yieldSheet.Range("B20").Formula = "=IF(B16<0,""Inverted"",""Normal"")"
    
    ' Add conditional formatting to the curve status
    With yieldSheet.Range("B20").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""Inverted""")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    With yieldSheet.Range("B20").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""Normal""")
        .Font.Color = RGB(0, 128, 0)
        .Font.Bold = True
    End With
    
    ' Add a yield curve inversion warning
    yieldSheet.Range("A22").Value = "Yield Curve Inversion Warning:"
    yieldSheet.Range("B22").Formula = "=IF(B16<0,""WARNING: Yield curve is inverted (10Y-2Y spread is negative). This has historically preceded recessions."",""Yield curve is normal (10Y-2Y spread is positive)."")"
    yieldSheet.Range("B22").WrapText = True
    yieldSheet.Range("B22").RowHeight = 40
    
    With yieldSheet.Range("B22").FormatConditions.Add(Type:=xlCellValue, Operator:=xlContains, Formula1:="""WARNING""")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    With yieldSheet.Range("B22").FormatConditions.Add(Type:=xlCellValue, Operator:=xlContains, Formula1:="""normal""")
        .Font.Color = RGB(0, 128, 0)
    End With
End Sub

Sub CreateVolatilityChart()
    Dim volSheet As Worksheet
    Set volSheet = Sheets("Volatility")
    
    ' Clear the sheet
    volSheet.Cells.Clear
    
    ' Create a title
    volSheet.Range("A1").Value = "Market Volatility Analysis"
    volSheet.Range("A1").Font.Size = 16
    volSheet.Range("A1").Font.Bold = True
    
    ' Create time period selections
    volSheet.Range("A3").Value = "Time Period:"
    
    ' Create option buttons for time periods
    Dim optOneMonth As OptionButton
    Set optOneMonth = volSheet.OptionButtons.Add(volSheet.Range("B3").Left, _
                                              volSheet.Range("B3").Top, 80, 20)
    optOneMonth.Caption = "1 Month"
    optOneMonth.GroupName = "VolTimePeriod"
    
    Dim optThreeMonth As OptionButton
    Set optThreeMonth = volSheet.OptionButtons.Add(volSheet.Range("C3").Left, _
                                                volSheet.Range("C3").Top, 80, 20)
    optThreeMonth.Caption = "3 Months"
    optThreeMonth.GroupName = "VolTimePeriod"
    optThreeMonth.Value = True
    
    Dim optSixMonth As OptionButton
    Set optSixMonth = volSheet.OptionButtons.Add(volSheet.Range("D3").Left, _
                                              volSheet.Range("D3").Top, 80, 20)
    optSixMonth.Caption = "6 Months"
    optSixMonth.GroupName = "VolTimePeriod"
    
    Dim optOneYear As OptionButton
    Set optOneYear = volSheet.OptionButtons.Add(volSheet.Range("E3").Left, _
                                             volSheet.Range("E3").Top, 80, 20)
    optOneYear.Caption = "1 Year"
    optOneYear.GroupName = "VolTimePeriod"
    
    ' Create a button to update the chart
    Dim btnUpdate As Button
    Set btnUpdate = volSheet.Buttons.Add(volSheet.Range("F3").Left, _
                                        volSheet.Range("F3").Top, 80, 20)
    btnUpdate.Caption = "Update Chart"
    btnUpdate.OnAction = "UpdateVolatilityChart"
    
    ' Create named ranges for date selections
    volSheet.Range("H3").Name = "VolStartDate"
    volSheet.Range("VolStartDate").Value = DateAdd("m", -3, Date) ' Default to 3 months
    volSheet.Range("H3").NumberFormat = "mm/dd/yyyy"
    volSheet.Range("H3").Locked = True
    
    ' Create the VIX chart
    Dim cht As Chart
    Set cht = volSheet.Shapes.AddChart2(201, xlAreaStacked, 50, 100, 800, 300).Chart
    
    ' Set up the chart
    With cht
        .SetSourceData Source:=Sheets("Data").Range("Q1:R252")
        .ChartType = xlLine
        
        .HasTitle = True
        .ChartTitle.Text = "CBOE Volatility Index (VIX) - Last 3 Months"
        
        .Axes(xlCategory, xlPrimary).HasTitle = True
        .Axes(xlCategory, xlPrimary).AxisTitle.Text = "Date"
        .Axes(xlCategory).CategoryType = xlTimeScale
        .Axes(xlCategory).TickLabels.NumberFormat = "mm/dd/yyyy"
        
        .Axes(xlValue, xlPrimary).HasTitle = True
        .Axes(xlValue, xlPrimary).AxisTitle.Text = "VIX"
        
        ' Apply date filter
        .Axes(xlCategory).MinimumScale = DateAdd("m", -3, Date)
        .Axes(xlCategory).MaximumScale = Date
        
        ' Format the series
        .SeriesCollection(1).Name = "VIX"
        .SeriesCollection(1).Format.Line.ForeColor.RGB = RGB(192, 0, 0)
        .SeriesCollection(1).Format.Line.Weight = 2
        
        ' Remove legend
        .HasLegend = False
        
        ' Add horizontal line at VIX = 20 (threshold for high volatility)
        Dim serThreshold As Series
        Set serThreshold = .SeriesCollection.NewSeries
        serThreshold.Name = "Volatility Threshold"
        serThreshold.Values = Array(20, 20)
        serThreshold.XValues = Array(.Axes(xlCategory).MinimumScale, .Axes(xlCategory).MaximumScale)
        serThreshold.Format.Line.ForeColor.RGB = RGB(0, 112, 192)
        serThreshold.Format.Line.DashStyle = msoLineDash
        serThreshold.Format.Line.Weight = 1.5
        
        ' Add gridlines
        .Axes(xlValue).MajorGridlines.Format.Line.Visible = msoTrue
        .Axes(xlValue).MajorGridlines.Format.Line.ForeColor.RGB = RGB(200, 200, 200)
        
        ' Set the y-axis scale to start at 0
        .Axes(xlValue).MinimumScale = 0
    End With
    
    ' Create volatility statistics
    volSheet.Range("A18").Value = "Volatility Statistics"
    volSheet.Range("A18").Font.Bold = True
    
    volSheet.Range("A19").Value = "Current VIX Value:"
    volSheet.Range("B19").Formula = "=INDEX(Data!$R$2:$R$252, MATCH(MAX(Data!$Q$2:$Q$252), Data!$Q$2:$Q$252, 0))"
    
    volSheet.Range("A20").Value = "Average VIX (Selected Period):"
    volSheet.Range("B20").Formula = "=AVERAGEIFS(Data!$R$2:$R$252, Data!$Q$2:$Q$252, "">=VolStartDate"", Data!$Q$2:$Q$252, ""<=TODAY()"")"
    
    volSheet.Range("A21").Value = "Maximum VIX (Selected Period):"
    volSheet.Range("B21").Formula = "=MAXIFS(Data!$R$2:$R$252, Data!$Q$2:$Q$252, "">=VolStartDate"", Data!$Q$2:$Q$252, ""<=TODAY()"")"
    
    volSheet.Range("A22").Value = "Minimum VIX (Selected Period):"
    volSheet.Range("B22").Formula = "=MINIFS(Data!$R$2:$R$252, Data!$Q$2:$Q$252, "">=VolStartDate"", Data!$Q$2:$Q$252, ""<=TODAY()"")"
    
    volSheet.Range("A23").Value = "Volatility Regime:"
    volSheet.Range("B23").Formula = "=IF(B19<15,""Low Volatility"",IF(B19<25,""Moderate Volatility"",""High Volatility""))"
    
    ' Add conditional formatting to the volatility regime
    With volSheet.Range("B23").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""Low Volatility""")
        .Font.Color = RGB(0, 128, 0)
        .Font.Bold = True
    End With
    
    With volSheet.Range("B23").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""Moderate Volatility""")
        .Font.Color = RGB(255, 153, 0)
        .Font.Bold = True
    End With
    
    With volSheet.Range("B23").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""High Volatility""")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    ' Update the chart
    UpdateVolatilityChart
End Sub

Sub UpdateVolatilityChart()
    Dim volSheet As Worksheet
    Set volSheet = Sheets("Volatility")
    
    ' Get the selected option button
    Dim timePeriod As String
    Dim i As Integer
    
    For i = 1 To volSheet.OptionButtons.Count
        If volSheet.OptionButtons(i).Value = xlOn Then
            timePeriod = volSheet.OptionButtons(i).Caption
            Exit For
        End If
    Next i
    
    ' Set the start date based on the selected time period
    Select Case timePeriod
        Case "1 Month"
            volSheet.Range("VolStartDate").Value = DateAdd("m", -1, Date)
        Case "3 Months"
            volSheet.Range("VolStartDate").Value = DateAdd("m", -3, Date)
        Case "6 Months"
            volSheet.Range("VolStartDate").Value = DateAdd("m", -6, Date)
        Case "1 Year"
            volSheet.Range("VolStartDate").Value = DateAdd("yyyy", -1, Date)
    End Select
    
    ' Get the chart
    Dim cht As Chart
    Set cht = volSheet.ChartObjects(1).Chart
    
    ' Update the chart's date range
    cht.Axes(xlCategory).MinimumScale = volSheet.Range("VolStartDate").Value
    cht.Axes(xlCategory).MaximumScale = Date
    
    ' Update the threshold line
    cht.SeriesCollection(2).XValues = Array(cht.Axes(xlCategory).MinimumScale, cht.Axes(xlCategory).MaximumScale)
    
    ' Update chart title
    cht.ChartTitle.Text = "CBOE Volatility Index (VIX) - Last " & timePeriod
    
    ' Update the threshold line to fit the new date range
    Dim serThreshold As Series
    Set serThreshold = cht.SeriesCollection(2)
    serThreshold.XValues = Array(cht.Axes(xlCategory).MinimumScale, cht.Axes(xlCategory).MaximumScale)
End Sub

Sub SetupDashboardControls()
    Dim dashSheet As Worksheet
    Set dashSheet = Sheets("Dashboard")
    
    ' Clear the sheet
    dashSheet.Cells.Clear
    
    ' Create a title
    dashSheet.Range("A1").Value = "Financial Markets Dashboard"
    dashSheet.Range("A1").Font.Size = 20
    dashSheet.Range("A1").Font.Bold = True
    
    ' Add date
    dashSheet.Range("A2").Value = "Last Updated:"
    dashSheet.Range("B2").Formula = "=TODAY()"
    dashSheet.Range("B2").NumberFormat = "mmmm d, yyyy"
    
    ' Create navigation buttons
    dashSheet.Range("A4").Value = "Navigation:"
    
    ' Index Performance Button
    Dim btnIndex As Button
    Set btnIndex = dashSheet.Buttons.Add(dashSheet.Range("B4").Left, _
                                        dashSheet.Range("B4").Top, 150, 25)
    btnIndex.Caption = "Index Performance"
    btnIndex.OnAction = "NavigateToSheet"
    
    ' Sector Performance Button
    Dim btnSector As Button
    Set btnSector = dashSheet.Buttons.Add(dashSheet.Range("D4").Left, _
                                        dashSheet.Range("D4").Top, 150, 25)
    btnSector.Caption = "Sector Performance"
    btnSector.OnAction = "NavigateToSheet"
    
    ' Yield Curve Button
    Dim btnYield As Button
    Set btnYield = dashSheet.Buttons.Add(dashSheet.Range("F4").Left, _
                                        dashSheet.Range("F4").Top, 150, 25)
    btnYield.Caption = "Yield Curve"
    btnYield.OnAction = "NavigateToSheet"
    
    ' Volatility Button
    Dim btnVolatility As Button
    Set btnVolatility = dashSheet.Buttons.Add(dashSheet.Range("H4").Left, _
                                             dashSheet.Range("H4").Top, 150, 25)
    btnVolatility.Caption = "Volatility"
    btnVolatility.OnAction = "NavigateToSheet"
    
    ' Create dashboard sections
    dashSheet.Range("A6").Value = "Market Overview"
    dashSheet.Range("A6").Font.Size = 14
    dashSheet.Range("A6").Font.Bold = True
    
    ' Add market summary metrics
    dashSheet.Range("A8").Value = "Index"
    dashSheet.Range("B8").Value = "Last"
    dashSheet.Range("C8").Value = "Daily Change"
    dashSheet.Range("D8").Value = "YTD Return"
    
    ' Format header row
    dashSheet.Range("A8:D8").Font.Bold = True
    dashSheet.Range("A8:D8").Interior.Color = RGB(200, 200, 200)
    
    ' Add data rows
    dashSheet.Range("A9").Value = "S&P 500"
    dashSheet.Range("A10").Value = "Nasdaq"
    dashSheet.Range("A11").Value = "Dow Jones"
    
    ' Get the last values from the data sheet
    dashSheet.Range("B9").Formula = "=INDEX(Data!$B$2:$B$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0))"
    dashSheet.Range("B10").Formula = "=INDEX(Data!$C$2:$C$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0))"
    dashSheet.Range("B11").Formula = "=INDEX(Data!$D$2:$D$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0))"
    
    ' Calculate daily changes
    dashSheet.Range("C9").Formula = "=(INDEX(Data!$B$2:$B$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0)) / INDEX(Data!$B$2:$B$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0) - 1) - 1)"
    dashSheet.Range("C10").Formula = "=(INDEX(Data!$C$2:$C$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0)) / INDEX(Data!$C$2:$C$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0) - 1) - 1)"
    dashSheet.Range("C11").Formula = "=(INDEX(Data!$D$2:$D$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0)) / INDEX(Data!$D$2:$D$252, MATCH(MAX(Data!$A$2:$A$252), Data!$A$2:$A$252, 0) - 1) - 1)"
    
    ' Calculate YTD returns
    dashSheet.Range("D9").Formula = "=(INDEX(Data!$B$2:$B$252, MATCH(MAX(Data!
    
  ```excel
    ' Format C9:D11 as percentages
    dashSheet.Range("C9:D11").NumberFormat = "0.00%"
    
    ' Add conditional formatting for daily changes
    With dashSheet.Range("C9:C11").FormatConditions.Add(Type:=xlCellValue, Operator:=xlLess, Formula1:="0")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    With dashSheet.Range("C9:C11").FormatConditions.Add(Type:=xlCellValue, Operator:=xlGreater, Formula1:="0")
        .Font.Color = RGB(0, 128, 0)
        .Font.Bold = True
    End With
    
    With dashSheet.Range("D9:D11").FormatConditions.Add(Type:=xlCellValue, Operator:=xlLess, Formula1:="0")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    With dashSheet.Range("D9:D11").FormatConditions.Add(Type:=xlCellValue, Operator:=xlGreater, Formula1:="0")
        .Font.Color = RGB(0, 128, 0)
        .Font.Bold = True
    End With
    
    ' Add sector performance summary
    dashSheet.Range("A13").Value = "Top Performing Sectors (YTD)"
    dashSheet.Range("A13").Font.Bold = True
    
    dashSheet.Range("A14").Formula = "=INDEX(Data!$F$2:$F$13, MATCH(LARGE(Data!$I$2:$I$13, 1), Data!$I$2:$I$13, 0))"
    dashSheet.Range("B14").Formula = "=LARGE(Data!$I$2:$I$13, 1)"
    dashSheet.Range("A15").Formula = "=INDEX(Data!$F$2:$F$13, MATCH(LARGE(Data!$I$2:$I$13, 2), Data!$I$2:$I$13, 0))"
    dashSheet.Range("B15").Formula = "=LARGE(Data!$I$2:$I$13, 2)"
    dashSheet.Range("A16").Formula = "=INDEX(Data!$F$2:$F$13, MATCH(LARGE(Data!$I$2:$I$13, 3), Data!$I$2:$I$13, 0))"
    dashSheet.Range("B16").Formula = "=LARGE(Data!$I$2:$I$13, 3)"
    
    dashSheet.Range("B14:B16").NumberFormat = "0.00%"
    dashSheet.Range("B14:B16").Font.Color = RGB(0, 128, 0)
    
    dashSheet.Range("C13").Value = "Worst Performing Sectors (YTD)"
    dashSheet.Range("C13").Font.Bold = True
    
    dashSheet.Range("C14").Formula = "=INDEX(Data!$F$2:$F$13, MATCH(SMALL(Data!$I$2:$I$13, 1), Data!$I$2:$I$13, 0))"
    dashSheet.Range("D14").Formula = "=SMALL(Data!$I$2:$I$13, 1)"
    dashSheet.Range("C15").Formula = "=INDEX(Data!$F$2:$F$13, MATCH(SMALL(Data!$I$2:$I$13, 2), Data!$I$2:$I$13, 0))"
    dashSheet.Range("D15").Formula = "=SMALL(Data!$I$2:$I$13, 2)"
    dashSheet.Range("C16").Formula = "=INDEX(Data!$F$2:$F$13, MATCH(SMALL(Data!$I$2:$I$13, 3), Data!$I$2:$I$13, 0))"
    dashSheet.Range("D16").Formula = "=SMALL(Data!$I$2:$I$13, 3)"
    
    dashSheet.Range("D14:D16").NumberFormat = "0.00%"
    dashSheet.Range("D14:D16").Font.Color = RGB(255, 0, 0)
    
    ' Add yield curve summary
    dashSheet.Range("A18").Value = "Yield Curve Status:"
    dashSheet.Range("A18").Font.Bold = True
    
    ' Calculate 10Y-2Y spread
    dashSheet.Range("B18").Formula = "=INDEX(Data!$M$2:$M$10, MATCH(""10-Year"", Data!$L$2:$L$10, 0)) - INDEX(Data!$M$2:$M$10, MATCH(""2-Year"", Data!$L$2:$L$10, 0))"
    dashSheet.Range("B18").NumberFormat = "0.00%"
    
    dashSheet.Range("C18").Formula = "=IF(B18<0, ""INVERTED"", ""NORMAL"")"
    
    With dashSheet.Range("C18").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""INVERTED""")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    With dashSheet.Range("C18").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""NORMAL""")
        .Font.Color = RGB(0, 128, 0)
        .Font.Bold = True
    End With
    
    ' Add volatility summary
    dashSheet.Range("A19").Value = "Current VIX:"
    dashSheet.Range("A19").Font.Bold = True
    
    dashSheet.Range("B19").Formula = "=INDEX(Data!$R$2:$R$252, MATCH(MAX(Data!$Q$2:$Q$252), Data!$Q$2:$Q$252, 0))"
    
    dashSheet.Range("C19").Formula = "=IF(B19<15, ""LOW VOLATILITY"", IF(B19<25, ""MODERATE VOLATILITY"", ""HIGH VOLATILITY""))"
    
    With dashSheet.Range("C19").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""LOW VOLATILITY""")
        .Font.Color = RGB(0, 128, 0)
        .Font.Bold = True
    End With
    
    With dashSheet.Range("C19").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""MODERATE VOLATILITY""")
        .Font.Color = RGB(255, 153, 0)
        .Font.Bold = True
    End With
    
    With dashSheet.Range("C19").FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="""HIGH VOLATILITY""")
        .Font.Color = RGB(255, 0, 0)
        .Font.Bold = True
    End With
    
    ' Add charts to dashboard
    ' Index performance chart
    dashSheet.Range("F6").Value = "Index Performance (Last 3 Months)"
    dashSheet.Range("F6").Font.Size = 14
    dashSheet.Range("F6").Font.Bold = True
    
    ' Create a chart for the index performance
    Dim indexChart As ChartObject
    Set indexChart = dashSheet.ChartObjects.Add(dashSheet.Range("F7").Left, dashSheet.Range("F7").Top, 400, 250)
    
    With indexChart.Chart
        ' Set the source data
        .SetSourceData Source:=Sheets("Data").Range("A1:D252")
        .ChartType = xlLine
        
        ' Filter for the last 3 months
        .Axes(xlCategory).CategoryType = xlTimeScale
        .Axes(xlCategory).TickLabels.NumberFormat = "mm/dd/yyyy"
        .Axes(xlCategory).MinimumScale = DateAdd("m", -3, Date)
        .Axes(xlCategory).MaximumScale = Date
        
        ' Normalize the data to start at 100
        Dim startIndex As Long
        startIndex = Application.Match(DateAdd("m", -3, Date), Sheets("Data").Range("A2:A252"), 1) + 1
        
        Dim spBase As Double, nasdaqBase As Double, dowBase As Double
        spBase = Sheets("Data").Cells(startIndex, 2).Value
        nasdaqBase = Sheets("Data").Cells(startIndex, 3).Value
        dowBase = Sheets("Data").Cells(startIndex, 4).Value
        
        ' Clear existing series
        Do While .SeriesCollection.Count > 0
            .SeriesCollection(1).Delete
        Loop
        
        ' Add normalized series
        Dim spSeries As String, nasdaqSeries As String, dowSeries As String
        
        spSeries = "=SERIES(""S&P 500"",Data!$A$" & startIndex & ":$A$252,Data!$B$" & startIndex & _
                  ":$B$252/Data!$B$" & startIndex & "*100,1)"
                  
        nasdaqSeries = "=SERIES(""Nasdaq"",Data!$A$" & startIndex & ":$A$252,Data!$C$" & startIndex & _
                      ":$C$252/Data!$C$" & startIndex & "*100,2)"
                      
        dowSeries = "=SERIES(""Dow Jones"",Data!$A$" & startIndex & ":$A$252,Data!$D$" & startIndex & _
                   ":$D$252/Data!$D$" & startIndex & "*100,3)"
        
        ' Add normalized series
        .SeriesCollection.Add spSeries
        .SeriesCollection.Add nasdaqSeries
        .SeriesCollection.Add dowSeries
        
        ' Format the chart
        .HasTitle = False
        .HasLegend = True
        .Legend.Position = xlLegendPositionBottom
        
        .Axes(xlValue, xlPrimary).HasTitle = True
        .Axes(xlValue, xlPrimary).AxisTitle.Text = "Normalized Value (Base=100)"
        
        ' Add gridlines
        .Axes(xlValue).MajorGridlines.Format.Line.Visible = msoTrue
        .Axes(xlValue).MajorGridlines.Format.Line.ForeColor.RGB = RGB(200, 200, 200)
    End With
    
    ' Sector performance heatmap
    dashSheet.Range("F22").Value = "Sector Performance (YTD)"
    dashSheet.Range("F22").Font.Size = 14
    dashSheet.Range("F22").Font.Bold = True
    
    ' Create a chart for the sector performance
    Dim sectorChart As ChartObject
    Set sectorChart = dashSheet.ChartObjects.Add(dashSheet.Range("F23").Left, dashSheet.Range("F23").Top, 400, 250)
    
    With sectorChart.Chart
        ' Create a bar chart of YTD sector returns
        .SetSourceData Source:=Sheets("Data").Range("F1:F13,I1:I13")
        .ChartType = xlBarClustered
        
        ' Format the chart
        .HasTitle = False
        .HasLegend = False
        
        ' Sort the data from highest to lowest
        .Sort.SortFields.Add Key:=.SeriesCollection(1).Values, Order:=xlDescending
        .Sort.Apply
        
        ' Add data labels
        .SeriesCollection(1).HasDataLabels = True
        .SeriesCollection(1).DataLabels.NumberFormat = "0.00%"
        .SeriesCollection(1).DataLabels.Position = xlLabelPositionOutsideEnd
        
        ' Format the bars with color based on positive/negative
        For Each pt In .SeriesCollection(1).Points
            If pt.Value < 0 Then
                pt.Format.Fill.ForeColor.RGB = RGB(255, 150, 150)
            Else
                pt.Format.Fill.ForeColor.RGB = RGB(150, 255, 150)
            End If
        Next pt
        
        ' Format the value axis
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "YTD Return"
        .Axes(xlValue).MajorGridlines.Format.Line.Visible = msoTrue
        .Axes(xlValue).MajorGridlines.Format.Line.ForeColor.RGB = RGB(200, 200, 200)
        .Axes(xlValue).NumberFormat = "0.00%"
        
        ' Add a zero line for reference
        .Axes(xlValue).DisplayUnit = xlNone
        .Axes(xlValue).CrossesAt = 0
        .Axes(xlValue).Crosses = xlCustom
    End With
End Sub

Sub FormatDashboard()
    Dim dashSheet As Worksheet
    Set dashSheet = Sheets("Dashboard")
    
    ' Format the title area
    dashSheet.Range("A1:J1").Merge
    dashSheet.Range("A1").HorizontalAlignment = xlCenter
    dashSheet.Range("A1").Font.Size = 20
    dashSheet.Range("A1").Font.Bold = True
    dashSheet.Range("A1").Font.Name = "Calibri"
    dashSheet.Range("A1").Font.Color = RGB(31, 78, 120)
    
    ' Add a horizontal line under the title
    dashSheet.Range("A2:J2").Borders(xlEdgeBottom).LineStyle = xlContinuous
    dashSheet.Range("A2:J2").Borders(xlEdgeBottom).Weight = xlMedium
    dashSheet.Range("A2:J2").Borders(xlEdgeBottom).Color = RGB(31, 78, 120)
    
    ' Format the navigation area
    dashSheet.Range("A4").Font.Bold = True
    
    ' Format the market overview header
    dashSheet.Range("A6:D6").Merge
    dashSheet.Range("A6").Font.Size = 14
    dashSheet.Range("A6").Font.Bold = True
    dashSheet.Range("A6").Font.Name = "Calibri"
    dashSheet.Range("A6").Font.Color = RGB(31, 78, 120)
    
    ' Format index table
    dashSheet.Range("A8:D8").Interior.Color = RGB(217, 225, 242)
    dashSheet.Range("A8:D8").Font.Bold = True
    dashSheet.Range("A8:D11").Borders.LineStyle = xlContinuous
    dashSheet.Range("A8:D11").Borders.Weight = xlThin
    dashSheet.Range("A8:D8").Borders(xlEdgeBottom).Weight = xlMedium
    
    ' Format sector performance headers
    dashSheet.Range("A13").Font.Bold = True
    dashSheet.Range("C13").Font.Bold = True
    
    ' Format yield curve and volatility sections
    dashSheet.Range("A18:A19").Font.Bold = True
    
    ' Format chart headers
    dashSheet.Range("F6").Font.Size = 14
    dashSheet.Range("F6").Font.Bold = True
    dashSheet.Range("F6").Font.Name = "Calibri"
    dashSheet.Range("F6").Font.Color = RGB(31, 78, 120)
    
    dashSheet.Range("F22").Font.Size = 14
    dashSheet.Range("F22").Font.Bold = True
    dashSheet.Range("F22").Font.Name = "Calibri"
    dashSheet.Range("F22").Font.Color = RGB(31, 78, 120)
    
    ' Adjust column widths
    dashSheet.Columns("A:J").AutoFit
    
    ' Add alternate row shading to the index table
    dashSheet.Range("A9:D9").Interior.Color = RGB(242, 242, 242)
    dashSheet.Range("A11:D11").Interior.Color = RGB(242, 242, 242)
End Sub

Sub NavigateToSheet()
    Dim btn As Button
    Set btn = ActiveSheet.Buttons(Application.Caller)
    
    ' Navigate to the sheet based on the button caption
    Sheets(btn.Caption).Activate
End Sub

' Main execution function
Sub Main()
    CreateMarketDashboard
End Sub
```

## Exercise 3: LLM-Based Corporate Governance Research

**Problem:** As a corporate finance analyst, you've been tasked with conducting a comprehensive governance analysis of technology companies to identify best practices and potential risks. You'll use Large Language Models to assist in your research, analysis, and report generation.

**Requirements:**
1. Research governance structures of major technology companies
2. Identify governance trends and risks specific to the technology sector
3. Analyze the relationship between governance practices and financial performance
4. Generate a comprehensive report with actionable insights
5. Create an executive summary dashboard

**Tasks:**
1. Develop effective prompts to extract governance information from LLMs
2. Create a systematic approach to governance evaluation
3. Design a scoring methodology for comparing governance practices
4. Generate visualization recommendations based on governance data
5. Produce a template for governance reports that can be customized per company

**LLM-Based Solution:**

**Step 1: Develop Structured Research Prompts**

Below are the key prompts designed to extract specific governance information from LLMs. Each prompt is structured to yield standardized outputs that can be combined into a comprehensive analysis.

**Prompt 1: Board Structure Analysis**
```
Analyze the board structure of [Company] using the following framework:

1. Board composition:
   - Total number of directors
   - Independence percentage
   - Gender diversity ratio
   - Ethnic/racial diversity representation
   - Average age
   - Average tenure

2. Committee structure:
   - Audit committee: size, independence, financial expertise presence
   - Compensation committee: size, independence, potential conflicts
   - Nominating/Governance committee: size, independence, process transparency
   - Technology/Cybersecurity committee (if applicable): size, relevant expertise

3. Leadership structure:
   - CEO/Chair split or combined
   - If combined, presence of lead independent director
   - Former CEO on board
   - Key governance gatekeepers (committee chairs)

4. Director qualifications:
   - Relevant industry experience percentage
   - Financial expertise representation
   - International experience
   - Technology expertise
   - Risk management background

Present your findings in a structured table format with a "Governance Risk" rating (Low, Medium, High) for each category based on current best practices. Include 2-3 sentences explaining the most significant strengths and weaknesses.
```

**Prompt 2: Executive Compensation Analysis**
```
Evaluate the executive compensation structure of [Company] based on the following criteria:

1. Pay components breakdown:
   - Base salary as % of total compensation
   - Annual incentive (cash bonus) as % of total
   - Long-term incentives as % of total
   - Perquisites and other compensation as % of total

2. Performance metrics:
   - Financial metrics used (specify)
   - Non-financial metrics used (specify)
   - ESG-related metrics inclusion
   - Relative performance benchmarks
   - Absolute performance thresholds

3. Pay-performance alignment:
   - 3-year TSR vs. CEO compensation growth
   - Performance metrics alignment with strategic objectives
   - Discretionary adjustments frequency and rationale
   - Clawback provisions and implementation
   - Realized vs. realizable pay discrepancies

4. Governance features:
   - Stock ownership guidelines
   - Hedging/pledging policies
   - Golden parachutes
   - Change-in-control provisions
   - Post-employment consulting arrangements

Provide a concise assessment of the compensation structure's alignment with shareholder interests, its effectiveness in incentivizing long-term value creation, and any potential governance risks. Include a comparison with 2-3 industry peers on key metrics.
```

**Prompt 3: Shareholder Rights Analysis**
```
Assess the shareholder rights and governance mechanisms at [Company] covering:

1. Voting structure:
   - One share, one vote or dual-class structure
   - If dual-class, voting power disparity
   - Cumulative voting availability
   - Proxy access provisions
   - Majority voting standard for director elections

2. Anti-takeover provisions:
   - Poison pill (details and trigger threshold)
   - Classified/staggered board
   - Supermajority voting requirements
   - Blank check preferred stock authorization
   - Limitations on calling special meetings

3. Shareholder engagement:
   - Responsiveness to shareholder proposals
   - Engagement policy and disclosure
   - Historical implementation of approved proposals
   - Frequency and transparency of engagement reporting
   - Virtual meeting practices and shareholder access

4. Share repurchase and dividend policy:
   - Historical patterns
   - Decision-making process transparency
   - Alignment with capital allocation strategy
   - Insider transactions around repurchase announcements
   - Potential conflicts of interest

Create a "Shareholder Rights Score" from 1-10 (10 being strongest rights) with justification. Identify the three most significant governance risks from a shareholder perspective and explain their potential impact on long-term value.
```

**Prompt 4: ESG Governance Integration**
```
Evaluate how [Company] integrates ESG oversight into its governance structure:

1. Board-level ESG oversight:
   - Dedicated sustainability/ESG committee existence
   - ESG responsibilities within existing committees
   - Board expertise in material ESG issues
   - Frequency of ESG discussions at board level
   - Board diversity as ESG governance factor

2. Management ESG structure:
   - Chief Sustainability Officer or equivalent position
   - ESG reporting lines
   - Integration with risk management function
   - Executive compensation ties to ESG metrics
   - Middle management accountability mechanisms

3. ESG disclosure practices:
   - Frameworks used (SASB, GRI, TCFD, etc.)
   - Assurance/verification of ESG data
   - Materiality assessment process
   - Stakeholder input mechanisms
   - Climate scenario analysis

4. ESG controversy management:
   - Historical ESG controversies
   - Response effectiveness
   - Governance changes implemented post-controversy
   - Whistleblower protection mechanisms
   - Supply chain governance oversight

Provide an assessment of the company's ESG governance maturity level (Beginning, Developing, Advanced, Leading) with specific recommendations for improvement. Include examples of best practices from industry peers that could be adopted.
```

**Step 2: Create a Governance Evaluation Framework**

**Corporate Governance Scoring Methodology**

Using LLM-generated data from the research prompts, the following comprehensive governance evaluation framework provides a standardized approach to compare companies:

```
# Corporate Governance Evaluation Framework

## Scoring Categories and Weights

### 1. Board Structure and Independence (30%)
   - Board Independence Score (10%)
   - Board Diversity Score (5%)
   - Committee Structure Score (10%)
   - Board Leadership Score (5%)

### 2. Executive Compensation (25%)
   - Pay-Performance Alignment Score (10%)
   - Incentive Structure Score (5%)
   - Compensation Governance Score (5%)
   - Disclosure Quality Score (5%)

### 3. Shareholder Rights (25%)
   - Voting Rights Score (10%)
   - Anti-takeover Defenses Score (5%)
   - Shareholder Engagement Score (5%)
   - Capital Allocation Governance Score (5%)

### 4. ESG Governance (20%)
   - ESG Oversight Structure Score (5%)
   - ESG Management Integration Score (5%)
   - ESG Disclosure Practices Score (5%)
   - ESG Risk Management Score (5%)

## Scoring Methodology

Each subcategory is scored on a scale of 1-5, where:
1 = Significant governance concerns; practices substantially below industry standards
2 = Some governance concerns; practices somewhat below industry standards
3 = Acceptable governance; practices meet industry standards
4 = Strong governance; practices exceed industry standards
5 = Excellent governance; practices represent industry best practice

## Overall Governance Rating Scale

90-100%: Exemplary Governance
80-89%: Strong Governance
70-79%: Good Governance
60-69%: Satisfactory Governance
50-59%: Needs Improvement
Below 50%: Significant Concerns
```

**Prompt to Generate Governance Score Calculations:**
```
Based on the governance data collected for [Company], calculate a comprehensive governance score using the following methodology:

1. Board Structure and Independence (30% of total):
   - Board Independence: [Calculate score 1-5] × 2 = [weighted score]
   - Board Diversity: [Calculate score 1-5] = [weighted score]
   - Committee Structure: [Calculate score 1-5] × 2 = [weighted score]
   - Board Leadership: [Calculate score 1-5] = [weighted score]
   Subtotal: [sum of weighted scores] / 30 × 100 = [percentage]

2. Executive Compensation (25% of total):
   - Pay-Performance Alignment: [Calculate score 1-5] × 2 = [weighted score]
   - Incentive Structure: [Calculate score 1-5] = [weighted score]
   - Compensation Governance: [Calculate score 1-5] = [weighted score]
   - Disclosure Quality: [Calculate score 1-5] = [weighted score]
   Subtotal: [sum of weighted scores] / 25 × 100 = [percentage]

3. Shareholder Rights (25% of total):
   - Voting Rights: [Calculate score 1-5] × 2 = [weighted score]
   - Anti-takeover Defenses: [Calculate score 1-5] = [weighted score]
   - Shareholder Engagement: [Calculate score 1-5] = [weighted score]
   - Capital Allocation Governance: [Calculate score 1-5] = [weighted score]
   Subtotal: [sum of weighted scores] / 25 × 100 = [percentage]

4. ESG Governance (20% of total):
   - ESG Oversight Structure: [Calculate score 1-5] = [weighted score]
   - ESG Management Integration: [Calculate score 1-5] = [weighted score]
   - ESG Disclosure Practices: [Calculate score 1-5] = [weighted score]
   - ESG Risk Management: [Calculate score 1-5] = [weighted score]
   Subtotal: [sum of weighted scores] / 20 × 100 = [percentage]

Total Governance Score = [weighted sum of all categories] = [percentage]
Governance Rating = [corresponding rating based on percentage]

For each category, provide a 1-2 sentence justification for the score given.
```

**Step 3: Governance-Financial Performance Analysis Framework**

Use this prompt to analyze the relationship between governance practices and financial performance:

```
Analyze the relationship between corporate governance practices and financial performance for [Company] over the past 5 years:

1. Compile the following financial metrics:
   - Total Shareholder Return (1-year, 3-year, 5-year)
   - Return on Invested Capital (ROIC)
   - Operating Margin
   - Revenue Growth
   - Earnings Growth
   - Stock Price Volatility (beta)
   - Valuation Multiples (P/E, EV/EBITDA) relative to peers

2. Identify significant governance changes over the 5-year period:
   - Board composition changes
   - Executive compensation structure modifications
   - Shareholder rights alterations
   - ESG governance developments

3. Analyze potential correlations:
   - Map governance changes against financial performance inflection points
   - Compare governance scores with industry peer performance
   - Identify governance factors most closely associated with outperformance or underperformance
   - Assess whether governance improvements preceded financial improvements

4. Develop a hypothesis about the governance-performance relationship specific to this company, including:
   - The 2-3 most impactful governance factors for this specific company
   - Potential confounding variables or alternative explanations
   - Industry-specific governance considerations
   - Recommendations for governance changes that could improve financial performance

Present your analysis in both narrative form and with a visual timeline that maps governance changes against performance metrics.
```

**Step 4: Comprehensive Governance Report Template**

Use the following prompt to generate a comprehensive governance report template:

```
Create a comprehensive corporate governance report for [Company] following this structure:

# Corporate Governance Assessment: [Company]

## Executive Summary (1 page)
- Overall Governance Rating: [Rating]
- Key Governance Strengths: [Bullet points]
- Key Governance Concerns: [Bullet points]
- Priority Recommendations: [Bullet points]
- Governance-Performance Relationship: [Brief summary]

## 1. Board Structure and Effectiveness (3-4 pages)
### 1.1 Board Composition and Independence
### 1.2 Board Diversity Analysis
### 1.3 Committee Structure and Effectiveness
### 1.4 Director Qualifications and Expertise
### 1.5 Board Evaluation Processes
### 1.6 Succession Planning

## 2. Executive Compensation (3-4 pages)
### 2.1 Compensation Philosophy and Strategy
### 2.2 Pay Structure Analysis
### 2.3 Performance Metrics Evaluation
### 2.4 Pay-Performance Alignment Assessment
### 2.5 Peer Group Benchmarking
### 2.6 Compensation Risk Analysis

## 3. Shareholder Rights and Engagement (2-3 pages)
### 3.1 Voting Structure Analysis
### 3.2 Anti-takeover Provisions Assessment
### 3.3 Shareholder Engagement Practices
### 3.4 Shareholder Proposal History and Response
### 3.5 Capital Allocation Governance

## 4. ESG Governance Integration (2-3 pages)
### 4.1 Board ESG Oversight Structure
### 4.2 Management ESG Responsibilities
### 4.3 ESG Disclosure Evaluation
### 4.4 ESG Risk Management Framework
### 4.5 ESG Controversy Response Mechanisms

## 5. Governance-Financial Performance Analysis (2-3 pages)
### 5.1 Historical Performance Overview
### 5.2 Governance-Performance Correlation Analysis
### 5.3 Peer Comparison Analysis
### 5.4 Impact of Specific Governance Changes

## 6. Recommendations (2 pages)
### 6.1 Short-term Governance Improvements (0-12 months)
### 6.2 Medium-term Governance Enhancements (1-3 years)
### 6.3 Long-term Governance Evolution (3+ years)
### 6.4 Implementation Roadmap

## Appendices
### A. Governance Scoring Methodology
### B. Detailed Peer Comparison Data
### C. Governance Change Timeline
### D. Director Skill Matrix
### E. Shareholder Proposal History (5 years)

Include data visualizations for:
1. Board composition (independence, diversity, tenure)
2. Pay mix and performance alignment
3. Governance score radar chart vs. peers
4. Governance changes and financial performance timeline
5. Shareholder proposal subjects and voting results

For each section, provide specific, actionable insights rather than generic observations.
```

**Step 5: Executive Dashboard Template**

Use this prompt to generate an executive dashboard concept:

```
Design an executive dashboard that visually summarizes the key governance findings for [Company]. The dashboard should:

1. Present a one-page overview of critical governance metrics and insights
2. Be accessible to board members and senior executives
3. Highlight both strengths and areas for improvement
4. Include comparative peer data where relevant
5. Present information in a visually engaging format

Include the following elements:

1. Overall Governance Score and Rating with year-over-year trend
2. Board Composition Snapshot:
   - Independence ratio (visual)
   - Diversity metrics (visual)
   - Expertise coverage (visual)
   - Tenure distribution (visual)

3. Key Governance Risk Indicators:
   - Color-coded risk levels (Low, Medium, High)
   - Governance risk trend arrows (improving/declining)
   - Priority areas for board attention

4. Performance Correlation Highlights:
   - TSR vs. Governance Score
   - Key governance-performance relationships

5. Peer Comparison Radar Chart:
   - Comparing key governance dimensions against 3-5 peers

6. Governance Improvement Roadmap:
   - Timeline visualization of recommended improvements
   - Expected impact of improvements
   - Implementation complexity indicators

Provide a mockup description of this dashboard including layout recommendations, chart types, color schemes, and data presentation approaches. Include specific metrics and data points that would be most impactful for executive decision-making.
```

**Using LLMs for Continuous Governance Monitoring**

Create a system that leverages LLMs for ongoing governance monitoring with this prompt:

```
Design a systematic approach to use LLMs for continuous corporate governance monitoring. The system should:

1. Monitor sources of governance information:
   - SEC filings (10-K, DEF 14A, 8-K)
   - Press releases
   - Media coverage
   - Analyst reports
   - Shareholder activist campaigns

2. Identify significant governance events:
   - Board changes
   - Executive transitions
   - Shareholder proposal submissions
   - Compensation structure changes
   - Regulatory investigations or settlements
   - ESG controversies

3. Generate alerts for governance changes that:
   - Substantially alter the governance score
   - Indicate increased governance risk
   - Create potential conflicts of interest
   - Deviate from stated governance policies
   - Lag emerging best practices

4. Provide contextual analysis for governance changes:
   - Comparison to industry trends
   - Potential impact on governance score
   - Strategic implications
   - Investor relations considerations
   - Recommended responses

Design a workflow that integrates LLM analysis with human expertise, including:
1. Data collection processes
2. Prompt templates for standard analyses
3. Alert thresholds and escalation criteria
4. Reporting formats and frequency
5. Action recommendation framework

The system should prioritize accuracy, timeliness, and actionability while minimizing false positives and information overload.
```

**Governance Analysis Implementation Plan**

This implementation plan outlines how to operationalize the LLM-based governance research approach:

1. **Data Collection Phase (Weeks 1-2)**
   - Compile list of target companies
   - Gather baseline governance data from public sources
   - Prepare company-specific variables for prompt templates
   - Create data storage structure for governance findings

2. **LLM Analysis Phase (Weeks 3-4)**
   - Execute structured prompts for each company
   - Validate critical findings against primary sources
   - Standardize outputs for cross-company comparison
   - Generate company-specific governance scores

3. **Insight Development Phase (Weeks 5-6)**
   - Analyze governance-performance relationships
   - Identify sector-specific governance trends
   - Develop actionable recommendations
   - Create visualization templates

4. **Reporting Phase (Weeks 7-8)**
   - Generate comprehensive governance reports
   - Develop executive dashboards
   - Prepare presentation materials
   - Create implementation roadmaps for governance improvements

5. **Continuous Monitoring Setup (Week 9-10)**
   - Implement LLM-based governance monitoring system
   - Establish alert thresholds
   - Create governance change detection prompts
   - Develop update protocols for ongoing monitoring

The approach can be scaled across multiple companies and adapted for different sectors by modifying prompt templates to account for industry-specific governance factors.  