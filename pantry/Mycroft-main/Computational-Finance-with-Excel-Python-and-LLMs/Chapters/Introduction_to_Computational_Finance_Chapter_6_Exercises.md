# Chapter 6 Exercises: Margin Accounts and Short Selling

## Exercise 1: Advanced Margin Account Analysis

**Problem:** You are a financial advisor helping a client understand the potential benefits and risks of using margin for an investment in Tesla (TSLA). Your client has $50,000 available to invest and is considering using margin to purchase additional shares. The current price of TSLA is $250 per share. The broker offers a margin loan at 7.5% annual interest rate, with a 50% initial margin requirement and 30% maintenance margin requirement.

**Tasks:**
1. Calculate the maximum number of TSLA shares your client can purchase using the full margin allowance
2. Determine the price at which a margin call would be triggered
3. Calculate the percentage price decline needed to trigger a margin call
4. Calculate the annual interest expense on the margin loan
5. Compare the returns on investment for different scenarios: 
   - Stock increases by 20% after 1 year
   - Stock decreases by 20% after 1 year 
   - Stock remains flat after 1 year
6. Determine the break-even price movement needed to compensate for the interest expense

**Excel Solution:**
```excel
'Inputs
Cash_Available = 50000
Stock_Price = 250
Initial_Margin_Req = 0.5
Maintenance_Margin_Req = 0.3
Annual_Interest_Rate = 0.075
Holding_Period_Years = 1

'1. Maximum Purchase Calculation
Max_Purchase_Value = Cash_Available / Initial_Margin_Req
Max_Shares = FLOOR(Max_Purchase_Value / Stock_Price, 1)
Actual_Purchase_Value = Max_Shares * Stock_Price
Margin_Loan = Actual_Purchase_Value - Cash_Available

'2. Margin Call Price
Margin_Call_Price = Margin_Loan / (Max_Shares * (1 - Maintenance_Margin_Req))

'3. Percentage Decline to Margin Call
Percentage_Decline = (Stock_Price - Margin_Call_Price) / Stock_Price

'4. Annual Interest Expense
Annual_Interest = Margin_Loan * Annual_Interest_Rate

'5. Return Comparison
'Scenario 1: 20% Increase
Final_Price_Up = Stock_Price * 1.2
Final_Value_Up = Max_Shares * Final_Price_Up
Equity_Up = Final_Value_Up - Margin_Loan
Profit_Up = Equity_Up - Cash_Available - Annual_Interest
ROI_Up = Profit_Up / Cash_Available
Non_Margin_Shares = FLOOR(Cash_Available / Stock_Price, 1)
Non_Margin_Profit_Up = Non_Margin_Shares * (Final_Price_Up - Stock_Price)
Non_Margin_ROI_Up = Non_Margin_Profit_Up / Cash_Available

'Scenario 2: 20% Decrease
Final_Price_Down = Stock_Price * 0.8
Final_Value_Down = Max_Shares * Final_Price_Down
Equity_Down = Final_Value_Down - Margin_Loan
Profit_Down = Equity_Down - Cash_Available - Annual_Interest
ROI_Down = Profit_Down / Cash_Available
Non_Margin_Profit_Down = Non_Margin_Shares * (Final_Price_Down - Stock_Price)
Non_Margin_ROI_Down = Non_Margin_Profit_Down / Cash_Available

'Scenario 3: Flat Price
Final_Value_Flat = Max_Shares * Stock_Price
Equity_Flat = Final_Value_Flat - Margin_Loan
Profit_Flat = Equity_Flat - Cash_Available - Annual_Interest
ROI_Flat = Profit_Flat / Cash_Available
Non_Margin_Profit_Flat = 0
Non_Margin_ROI_Flat = 0

'6. Break-even Price Movement
Break_Even_Increase = Annual_Interest / (Max_Shares * Stock_Price)
Break_Even_Price = Stock_Price * (1 + Break_Even_Increase)
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Input parameters
cash_available = 50000
stock_price = 250
initial_margin_req = 0.5
maintenance_margin_req = 0.3
annual_interest_rate = 0.075
holding_period_years = 1

# 1. Maximum purchase calculation
max_purchase_value = cash_available / initial_margin_req
max_shares = int(max_purchase_value / stock_price)
actual_purchase_value = max_shares * stock_price
margin_loan = actual_purchase_value - cash_available

# 2. Margin call price
margin_call_price = margin_loan / (max_shares * (1 - maintenance_margin_req))

# 3. Percentage decline to margin call
percentage_decline = (stock_price - margin_call_price) / stock_price

# 4. Annual interest expense
annual_interest = margin_loan * annual_interest_rate

# 5. Return comparison
# Non-margin position
non_margin_shares = int(cash_available / stock_price)
non_margin_investment = non_margin_shares * stock_price

# Define scenarios
scenarios = {
    "20% Increase": stock_price * 1.2,
    "No Change": stock_price,
    "20% Decrease": stock_price * 0.8
}

# Compare returns
comparison = []

for scenario_name, final_price in scenarios.items():
    # Margin position
    final_value = max_shares * final_price
    equity = final_value - margin_loan
    profit = equity - cash_available - annual_interest
    roi = profit / cash_available
    
    # Non-margin position
    non_margin_final_value = non_margin_shares * final_price
    non_margin_profit = non_margin_final_value - non_margin_investment
    non_margin_roi = non_margin_profit / cash_available
    
    comparison.append({
        "Scenario": scenario_name,
        "Final Price": final_price,
        "Margin ROI": roi,
        "Non-Margin ROI": non_margin_roi,
        "Leverage Effect": roi / non_margin_roi if non_margin_roi != 0 else np.nan
    })

comparison_df = pd.DataFrame(comparison)

# 6. Break-even price movement
break_even_increase = annual_interest / (max_shares * stock_price)
break_even_price = stock_price * (1 + break_even_increase)

# Print results
print(f"1. Maximum Purchase Analysis:")
print(f"   Maximum shares purchasable: {max_shares} shares")
print(f"   Total investment value: ${actual_purchase_value:,.2f}")
print(f"   Amount borrowed: ${margin_loan:,.2f}")
print(f"   Initial margin: {cash_available/actual_purchase_value:.2%}")

print(f"\n2. Margin Call Analysis:")
print(f"   Margin call price: ${margin_call_price:.2f}")
print(f"   Percentage decline to trigger margin call: {percentage_decline:.2%}")

print(f"\n3. Interest Expense:")
print(f"   Annual interest: ${annual_interest:,.2f}")
print(f"   Interest as percentage of investment: {annual_interest/actual_purchase_value:.2%}")

print(f"\n4. Break-even Analysis:")
print(f"   Required price increase to break even: {break_even_increase:.2%}")
print(f"   Break-even price: ${break_even_price:.2f}")

print("\n5. Return Comparison:")
print(comparison_df.to_string(index=False))

# Create visualization
price_range = np.linspace(stock_price * 0.5, stock_price * 1.5, 100)
margin_returns = []
non_margin_returns = []

for price in price_range:
    # Margin position
    final_value = max_shares * price
    equity = final_value - margin_loan
    profit = equity - cash_available - annual_interest
    roi = profit / cash_available
    margin_returns.append(roi)
    
    # Non-margin position
    non_margin_final_value = non_margin_shares * price
    non_margin_profit = non_margin_final_value - non_margin_investment
    non_margin_roi = non_margin_profit / cash_available
    non_margin_returns.append(non_margin_roi)

plt.figure(figsize=(10, 6))
plt.plot(price_range, np.array(margin_returns) * 100, 'b-', label='Margin')
plt.plot(price_range, np.array(non_margin_returns) * 100, 'g--', label='Non-Margin')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=stock_price, color='k', linestyle='--', alpha=0.3, label='Initial Price')
plt.axvline(x=margin_call_price, color='r', linestyle='--', alpha=0.7, label='Margin Call Price')
plt.axvline(x=break_even_price, color='orange', linestyle='--', alpha=0.7, label='Break-even Price')

plt.xlabel('Stock Price ($)')
plt.ylabel('Return (%)')
plt.title('Margin vs Non-Margin Returns')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('margin_analysis.png')
```

## Exercise 2: Short Selling Risk-Reward Analysis

**Problem:** You're considering short selling 300 shares of GameStop (GME), which is currently trading at $150 per share. Your broker requires 50% initial margin and 40% maintenance margin for this volatile stock. The annual stock borrow fee is 8%, and GME pays no dividend. You plan to hold the position for up to 3 months.

**Tasks:**
1. Calculate the initial margin requirement and total account value needed
2. Determine the proceeds from the short sale
3. Calculate the price at which a margin call would be triggered
4. Create a profit/loss table for various price scenarios ranging from $75 to $225
5. Calculate the return on investment for each price scenario
6. Analyze the maximum potential profit and unlimited loss characteristic of short selling
7. Calculate the impact of borrowing fees on overall returns

**Excel Solution:**
```excel
'Inputs
Stock_Price = 150
Shares = 300
Initial_Margin_Req = 0.5
Maintenance_Margin_Req = 0.4
Annual_Borrow_Fee = 0.08
Holding_Period_Months = 3

'1. Initial Margin and Account Value
Short_Sale_Proceeds = Stock_Price * Shares
Initial_Margin = Short_Sale_Proceeds * Initial_Margin_Req
Total_Account_Value = Short_Sale_Proceeds + Initial_Margin

'2. Short Sale Proceeds
'Already calculated: Short_Sale_Proceeds

'3. Margin Call Price
Margin_Call_Price = Stock_Price * (1 + Initial_Margin_Req / (1 - Maintenance_Margin_Req) - Initial_Margin_Req)

'4-5. Profit/Loss and ROI Table
'Create a table with scenario prices
Scenario_Prices = {75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225}

'For each scenario price, calculate:
'a. Market Value = Scenario_Price * Shares
'b. Borrowing Cost = Short_Sale_Proceeds * Annual_Borrow_Fee * (Holding_Period_Months / 12)
'c. Gross Profit = Short_Sale_Proceeds - Market_Value
'd. Net Profit = Gross_Profit - Borrowing_Cost
'e. ROI = Net_Profit / Initial_Margin
'f. Short Equity = Short_Sale_Proceeds + Initial_Margin - Market_Value
'g. Short Margin Percentage = Short_Equity / Market_Value

'6. Maximum Profit Calculation
Maximum_Theoretical_Profit = Short_Sale_Proceeds - Borrowing_Cost
Maximum_Profit_ROI = Maximum_Theoretical_Profit / Initial_Margin

'7. Borrowing Fee Impact
Borrowing_Cost = Short_Sale_Proceeds * Annual_Borrow_Fee * (Holding_Period_Months / 12)
Borrowing_Cost_Per_Share = Borrowing_Cost / Shares
Borrowing_Cost_Impact_Percent = Borrowing_Cost / Initial_Margin
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Input parameters
stock_price = 150
shares = 300
initial_margin_req = 0.5
maintenance_margin_req = 0.4
annual_borrow_fee = 0.08
holding_period_months = 3

# 1. Initial Margin and Account Value
short_sale_proceeds = stock_price * shares
initial_margin = short_sale_proceeds * initial_margin_req
total_account_value = short_sale_proceeds + initial_margin

# 2. Short Sale Proceeds (already calculated)

# 3. Margin Call Price
margin_call_price = stock_price * (1 + initial_margin_req / (1 - maintenance_margin_req) - initial_margin_req)

# 4-5. Profit/Loss and ROI Table
scenario_prices = np.arange(75, 226, 15)  # From $75 to $225 in $15 increments

# Calculate borrowing cost (same for all scenarios)
borrowing_cost = short_sale_proceeds * annual_borrow_fee * (holding_period_months / 12)

# Create results table
results = []

for scenario_price in scenario_prices:
    market_value = scenario_price * shares
    gross_profit = short_sale_proceeds - market_value
    net_profit = gross_profit - borrowing_cost
    roi = net_profit / initial_margin
    short_equity = short_sale_proceeds + initial_margin - market_value
    short_margin_percentage = short_equity / market_value
    
    # Margin call status
    if scenario_price >= margin_call_price:
        margin_status = "MARGIN CALL"
    else:
        margin_status = "OK"
    
    results.append({
        "Price": scenario_price,
        "Market Value": market_value,
        "Gross Profit": gross_profit,
        "Borrowing Cost": borrowing_cost,
        "Net Profit": net_profit,
        "ROI": roi,
        "Short Equity": short_equity,
        "Margin %": short_margin_percentage,
        "Status": margin_status
    })

results_df = pd.DataFrame(results)

# 6. Maximum Profit Calculation
maximum_theoretical_profit = short_sale_proceeds - borrowing_cost  # If price goes to zero
maximum_profit_roi = maximum_theoretical_profit / initial_margin

# 7. Borrowing Fee Impact
borrowing_cost_per_share = borrowing_cost / shares
borrowing_cost_impact_percent = borrowing_cost / initial_margin

# Print results
print(f"Short Selling Analysis for GME")
print(f"==============================")

print(f"\n1. Initial Position Requirements:")
print(f"   Short sale proceeds: ${short_sale_proceeds:,.2f}")
print(f"   Initial margin required: ${initial_margin:,.2f}")
print(f"   Total account value needed: ${total_account_value:,.2f}")

print(f"\n2. Margin Call Analysis:")
print(f"   Margin call price: ${margin_call_price:.2f}")
print(f"   Percentage increase to trigger margin call: {(margin_call_price/stock_price - 1):.2%}")

print(f"\n3. Borrowing Cost Impact:")
print(f"   Total borrowing cost (3 months): ${borrowing_cost:.2f}")
print(f"   Borrowing cost per share: ${borrowing_cost_per_share:.2f}")
print(f"   Borrowing cost as percentage of margin: {borrowing_cost_impact_percent:.2%}")

print(f"\n4. Maximum Profit Potential:")
print(f"   Maximum theoretical profit (if price goes to $0): ${maximum_theoretical_profit:,.2f}")
print(f"   Maximum ROI: {maximum_profit_roi:.2%}")

print(f"\n5. Profit/Loss Scenarios:")
pd.set_option('display.float_format', '${:.2f}'.format)
print(results_df[["Price", "Market Value", "Net Profit", "ROI", "Status"]].to_string(index=False))

# Create visualization
plt.figure(figsize=(12, 8))

# Plot 1: Profit/Loss vs Price
plt.subplot(2, 1, 1)
plt.plot(results_df["Price"], results_df["Net Profit"], 'r-', marker='o')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=stock_price, color='b', linestyle='--', label='Initial Price')
plt.axvline(x=margin_call_price, color='r', linestyle='--', label='Margin Call Price')
plt.xlabel('Stock Price ($)')
plt.ylabel('Net Profit ($)')
plt.title('Short Selling Profit/Loss by Price')
plt.grid(alpha=0.3)
plt.legend()

# Plot 2: ROI vs Price
plt.subplot(2, 1, 2)
plt.plot(results_df["Price"], results_df["ROI"] * 100, 'g-', marker='o')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=stock_price, color='b', linestyle='--', label='Initial Price')
plt.axvline(x=margin_call_price, color='r', linestyle='--', label='Margin Call Price')
plt.xlabel('Stock Price ($)')
plt.ylabel('Return on Investment (%)')
plt.title('Short Selling ROI by Price')
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('short_selling_analysis.png')
```

## Exercise 3: Margin Trading Strategy Comparison

**Problem:** You're developing a trading strategy guide for a group of retail investors interested in leveraged positions. You want to compare three approaches to leverage using a hypothetical $25,000 investment in the S&P 500 ETF (SPY), currently trading at $450 per share:

1. **Standard Margin Account**: 50% initial margin, 30% maintenance margin, 6.5% annual interest rate
2. **Portfolio Margin Account**: 15% initial margin, 10% maintenance margin, 7.5% annual interest rate (higher due to increased risk)
3. **Leveraged ETF**: 3x Leveraged S&P 500 ETF (no margin loan, but 0.95% expense ratio and daily rebalancing effects)

**Tasks:**
1. Calculate the maximum exposure possible with each strategy
2. Determine the effective leverage ratio for each approach
3. Calculate the margin call thresholds for the margin strategies
4. Model the performance of each strategy over 6 months under the following scenarios:
   - Bull market: Steady 2% monthly increase in S&P 500
   - Bear market: Steady 2% monthly decrease in S&P 500
   - Volatile market: +3%, -4%, +2%, -3%, +4%, -2% monthly changes
5. Calculate the total costs associated with each strategy
6. Analyze the advantages and disadvantages of each approach considering return potential, risk factors, and costs

**Excel Solution:**
```excel
'Inputs
Investment_Amount = 25000
SPY_Price = 450
Standard_Initial_Margin = 0.5
Standard_Maintenance_Margin = 0.3
Standard_Interest_Rate = 0.065
Portfolio_Initial_Margin = 0.15
Portfolio_Maintenance_Margin = 0.1
Portfolio_Interest_Rate = 0.075
Leveraged_ETF_Expense_Ratio = 0.0095
Holding_Period_Months = 6

'1. Maximum Exposure
Standard_Max_Exposure = Investment_Amount / Standard_Initial_Margin
Portfolio_Max_Exposure = Investment_Amount / Portfolio_Initial_Margin
Leveraged_ETF_Max_Exposure = Investment_Amount * 3  'For a 3x leveraged ETF

'2. Effective Leverage
Standard_Leverage = Standard_Max_Exposure / Investment_Amount
Portfolio_Leverage = Portfolio_Max_Exposure / Investment_Amount
Leveraged_ETF_Leverage = 3

'3. Margin Call Thresholds
Standard_Shares = FLOOR(Standard_Max_Exposure / SPY_Price, 1)
Standard_Actual_Exposure = Standard_Shares * SPY_Price
Standard_Borrowed = Standard_Actual_Exposure - Investment_Amount
Standard_Margin_Call_Price = Standard_Borrowed / (Standard_Shares * (1 - Standard_Maintenance_Margin))
Standard_Decline_To_Call = (SPY_Price - Standard_Margin_Call_Price) / SPY_Price

Portfolio_Shares = FLOOR(Portfolio_Max_Exposure / SPY_Price, 1)
Portfolio_Actual_Exposure = Portfolio_Shares * SPY_Price
Portfolio_Borrowed = Portfolio_Actual_Exposure - Investment_Amount
Portfolio_Margin_Call_Price = Portfolio_Borrowed / (Portfolio_Shares * (1 - Portfolio_Maintenance_Margin))
Portfolio_Decline_To_Call = (SPY_Price - Portfolio_Margin_Call_Price) / SPY_Price

'4. Performance Modeling
'We'll create tables for each market scenario and each strategy

'Bull Market: 2% monthly increase
Bull_Month1 = 0.02
Bull_Month2 = 0.02
Bull_Month3 = 0.02
Bull_Month4 = 0.02
Bull_Month5 = 0.02
Bull_Month6 = 0.02

'Bear Market: 2% monthly decrease
Bear_Month1 = -0.02
Bear_Month2 = -0.02
Bear_Month3 = -0.02
Bear_Month4 = -0.02
Bear_Month5 = -0.02
Bear_Month6 = -0.02

'Volatile Market
Volatile_Month1 = 0.03
Volatile_Month2 = -0.04
Volatile_Month3 = 0.02
Volatile_Month4 = -0.03
Volatile_Month5 = 0.04
Volatile_Month6 = -0.02

'For each scenario, calculate monthly and cumulative values for each strategy
'For Standard Margin
'Month 1 calculation example:
Standard_Bull_Month1_SPY = SPY_Price * (1 + Bull_Month1)
Standard_Bull_Month1_Value = Standard_Shares * Standard_Bull_Month1_SPY
Standard_Bull_Month1_Equity = Standard_Bull_Month1_Value - Standard_Borrowed
Standard_Bull_Month1_Monthly_Interest = Standard_Borrowed * Standard_Interest_Rate / 12
Standard_Bull_Month1_Net_Equity = Standard_Bull_Month1_Equity - Standard_Bull_Month1_Monthly_Interest
Standard_Bull_Month1_Return = (Standard_Bull_Month1_Net_Equity - Investment_Amount) / Investment_Amount

'Calculate similar values for all months and all scenarios
'Implement proper margin call logic if equity falls below maintenance requirement

'For Portfolio Margin
'Follow similar logic as Standard Margin with different parameters

'For Leveraged ETF
'Month 1 calculation example:
Leveraged_Bull_Month1_Return = Bull_Month1 * 3 - Leveraged_ETF_Expense_Ratio / 12
Leveraged_Bull_Month1_Value = Investment_Amount * (1 + Leveraged_Bull_Month1_Return)

'5. Total Costs
'Standard Margin
Standard_Bull_Total_Interest = SUM(Standard_Bull_Month1_Monthly_Interest:Standard_Bull_Month6_Monthly_Interest)
Standard_Bear_Total_Interest = SUM(Standard_Bear_Month1_Monthly_Interest:Standard_Bear_Month6_Monthly_Interest)
Standard_Volatile_Total_Interest = SUM(Standard_Volatile_Month1_Monthly_Interest:Standard_Volatile_Month6_Monthly_Interest)

'Portfolio Margin
Portfolio_Bull_Total_Interest = SUM(Portfolio_Bull_Month1_Monthly_Interest:Portfolio_Bull_Month6_Monthly_Interest)
Portfolio_Bear_Total_Interest = SUM(Portfolio_Bear_Month1_Monthly_Interest:Portfolio_Bear_Month6_Monthly_Interest)
Portfolio_Volatile_Total_Interest = SUM(Portfolio_Volatile_Month1_Monthly_Interest:Portfolio_Volatile_Month6_Monthly_Interest)

'Leveraged ETF
Leveraged_ETF_Bull_Expense = Investment_Amount * Leveraged_ETF_Expense_Ratio * (Holding_Period_Months / 12)
Leveraged_ETF_Bear_Expense = Investment_Amount * Leveraged_ETF_Expense_Ratio * (Holding_Period_Months / 12)
Leveraged_ETF_Volatile_Expense = Investment_Amount * Leveraged_ETF_Expense_Ratio * (Holding_Period_Months / 12)
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Input parameters
investment_amount = 25000
spy_price = 450
standard_initial_margin = 0.5
standard_maintenance_margin = 0.3
standard_interest_rate = 0.065
portfolio_initial_margin = 0.15
portfolio_maintenance_margin = 0.1
portfolio_interest_rate = 0.075
leveraged_etf_expense_ratio = 0.0095
holding_period_months = 6

# 1. Maximum Exposure
standard_max_exposure = investment_amount / standard_initial_margin
portfolio_max_exposure = investment_amount / portfolio_initial_margin
leveraged_etf_max_exposure = investment_amount * 3  # For a 3x leveraged ETF

# 2. Effective Leverage
standard_leverage = standard_max_exposure / investment_amount
portfolio_leverage = portfolio_max_exposure / investment_amount
leveraged_etf_leverage = 3

# 3. Margin Call Thresholds
standard_shares = int(standard_max_exposure / spy_price)
standard_actual_exposure = standard_shares * spy_price
standard_borrowed = standard_actual_exposure - investment_amount
standard_margin_call_price = standard_borrowed / (standard_shares * (1 - standard_maintenance_margin))
standard_decline_to_call = (spy_price - standard_margin_call_price) / spy_price

portfolio_shares = int(portfolio_max_exposure / spy_price)
portfolio_actual_exposure = portfolio_shares * spy_price
portfolio_borrowed = portfolio_actual_exposure - investment_amount
portfolio_margin_call_price = portfolio_borrowed / (portfolio_shares * (1 - portfolio_maintenance_margin))
portfolio_decline_to_call = (spy_price - portfolio_margin_call_price) / spy_price

# 4. Performance Modeling
# Define market scenarios
bull_market = [0.02, 0.02, 0.02, 0.02, 0.02, 0.02]
bear_market = [-0.02, -0.02, -0.02, -0.02, -0.02, -0.02]
volatile_market = [0.03, -0.04, 0.02, -0.03, 0.04, -0.02]

scenarios = {
    "Bull Market": bull_market,
    "Bear Market": bear_market,
    "Volatile Market": volatile_market
}

# Create a function to model the performance of each strategy
def model_performance(monthly_returns, strategy_params):
    """Model the performance of a trading strategy over time"""
    monthly_data = []
    cumulative_return = 0
    current_spy_price = spy_price
    current_equity = strategy_params['initial_investment']
    total_cost = 0
    
    if strategy_params['type'] == 'margin':
        # Margin account logic
        shares = strategy_params['shares']
        borrowed = strategy_params['borrowed']
        interest_rate = strategy_params['interest_rate']
        maintenance_margin = strategy_params['maintenance_margin']
        margin_call_triggered = False
        
        for month, monthly_return in enumerate(monthly_returns, 1):
            if not margin_call_triggered:
                # Update SPY price
                current_spy_price *= (1 + monthly_return)
                
                # Calculate new value and equity
                current_value = shares * current_spy_price
                current_equity_before_interest = current_value - borrowed
                
                # Calculate interest cost
                monthly_interest = borrowed * interest_rate / 12
                total_cost += monthly_interest
                
                # Deduct interest from equity
                current_equity = current_equity_before_interest - monthly_interest
                
                # Check for margin call
                margin_percentage = current_equity / current_value
                if margin_percentage < maintenance_margin:
                    margin_call_triggered = True
                    liquidation_value = current_equity  # Simplified liquidation
            else:
                # After margin call, assume liquidation and cash position
                monthly_interest = 0
                current_equity *= (1 + monthly_return)  # Just track as cash
            
            # Calculate monthly return on investment
            monthly_roi = (current_equity - strategy_params['initial_investment']) / strategy_params['initial_investment']
            
            monthly_data.append({
                'Month': month,
                'SPY Price': current_spy_price,
                'Account Value': current_value if not margin_call_triggered else current_equity,
                'Equity': current_equity,
                'Monthly Interest': monthly_interest,
                'Margin %': current_equity / current_value if not margin_call_triggered else 1.0,
                'Margin Call': margin_call_triggered,
                'ROI': monthly_roi
            })
    
    elif strategy_params['type'] == 'leveraged_etf':
        # Leveraged ETF logic
        leverage = strategy_params['leverage']
        expense_ratio = strategy_params['expense_ratio']
        
        for month, monthly_return in enumerate(monthly_returns, 1):
            # Calculate leveraged return (simplified without daily compounding effects)
            leveraged_return = monthly_return * leverage
            
            # Deduct monthly expense ratio
            monthly_expense = expense_ratio / 12
            total_cost += current_equity * monthly_expense
            
            # Update equity
            current_equity *= (1 + leveraged_return - monthly_expense)
            
            # Calculate monthly return on investment
            monthly_roi = (current_equity - strategy_params['initial_investment']) / strategy_params['initial_investment']
            
            monthly_data.append({
                'Month': month,
                'SPY Price': current_spy_price * (1 + monthly_return),  # Just for reference
                'Account Value': current_equity,
                'Equity': current_equity,
                'Monthly Expense': current_equity * monthly_expense,
                'ROI': monthly_roi
            })
    
    return pd.DataFrame(monthly_data), total_cost

# Define strategy parameters
strategies = {
    "Standard Margin": {
        'type': 'margin',
        'initial_investment': investment_amount,
        'shares': standard_shares,
        'borrowed': standard_borrowed,
        'interest_rate': standard_interest_rate,
        'maintenance_margin': standard_maintenance_margin
    },
    "Portfolio Margin": {
        'type': 'margin',
        'initial_investment': investment_amount,
        'shares': portfolio_shares,
        'borrowed': portfolio_borrowed,
        'interest_rate': portfolio_interest_rate,
        'maintenance_margin': portfolio_maintenance_margin
    },
    "Leveraged ETF": {
        'type': 'leveraged_etf',
        'initial_investment': investment_amount,
        'leverage': leveraged_etf_leverage,
        'expense_ratio': leveraged_etf_expense_ratio
    }
}

# Run simulations for all strategies and scenarios
results = {}
costs = {}

for scenario_name, monthly_returns in scenarios.items():
    scenario_results = {}
    scenario_costs = {}
    
    for strategy_name, strategy_params in strategies.items():
        monthly_data, total_cost = model_performance(monthly_returns, strategy_params)
        scenario_results[strategy_name] = monthly_data
        scenario_costs[strategy_name] = total_cost
    
    results[scenario_name] = scenario_results
    costs[scenario_name] = scenario_costs

# Print initial analysis
print("Margin Trading Strategy Comparison")
print("=================================")

print("\nInitial Setup:")
print(f"Investment Amount: ${investment_amount:,.2f}")
print(f"SPY Price: ${spy_price:.2f}")

print("\n1. Maximum Exposure:")
print(f"   Standard Margin: ${standard_actual_exposure:,.2f} ({standard_leverage:.2f}x leverage)")
print(f"   Portfolio Margin: ${portfolio_actual_exposure:,.2f} ({portfolio_leverage:.2f}x leverage)")
print(f"   Leveraged ETF: ${leveraged_etf_max_exposure:,.2f} ({leveraged_etf_leverage:.2f}x leverage)")

print("\n2. Margin Call Thresholds:")
print(f"   Standard Margin: ${standard_margin_call_price:.2f} ({standard_decline_to_call:.2%} decline)")
print(f"   Portfolio Margin: ${portfolio_margin_call_price:.2f} ({portfolio_decline_to_call:.2%} decline)")
print(f"   Leveraged ETF: N/A (no margin call)")

print("\n3. Total Costs Over 6 Months:")
for scenario_name, scenario_costs in costs.items():
    print(f"   {scenario_name}:")
    for strategy_name, cost in scenario_costs.items():
        print(f"      {strategy_name}: ${cost:.2f}")

# Print final performance
print("\n4. Final Performance (ROI):")
for scenario_name, scenario_results in results.items():
    print(f"   {scenario_name}:")
    for strategy_name, data in scenario_results.items():
        final_roi = data.iloc[-1]['ROI']
        margin_call = 'Yes' if 'Margin Call' in data.columns and data['Margin Call'].any() else 'No'
        print(f"      {strategy_name}: {final_roi:.2%} (Margin Call: {margin_call})")

# Create visualizations
for scenario_name, scenario_results in results.items():
    plt.figure(figsize=(12, 8))
    
    # Plot ROI over time
    for strategy_name, data in scenario_results.items():
        plt.plot(data['Month'], data['ROI'] * 100, marker='o', label=strategy_name)
    
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('Month')
    plt.ylabel('Return on Investment (%)')
    plt.title(f'Strategy Performance: {scenario_name}')
    plt.grid(alpha=0.3)
    plt.legend()
    
    plt.savefig(f'strategy_comparison_{scenario_name.replace(" ", "_").lower()}.png')
```

## Exercise 4: Regulatory Impact Analysis on Margin Trading

**Problem:** You work for a financial policy research institute and have been asked to analyze how changes in margin requirements impact market stability and investor behavior. You'll examine three historical periods of regulatory changes and their effects:

1. **1929 Pre-Crash Period**: No federal margin requirements (some brokers required as little as 10% margin)
2. **1974 Oil Crisis Period**: 65% initial margin requirement (temporarily raised from 50%)
3. **Current Period (2025)**: 50% initial margin requirement with portfolio margin options

The analysis will focus on a hypothetical portfolio of $100,000 invested in a diversified basket of stocks representing the market.

**Tasks:**
1. Calculate the maximum leverage possible under each regulatory regime
2. Model how different margin requirements would affect portfolio drawdowns during market crashes:
   - 1929 Crash: -89% over 34 months
   - 1973-1974 Bear Market: -48% over 21 months
   - 2008 Financial Crisis: -57% over 17 months
3. Analyze how many investors would face margin calls under each scenario
4. Calculate the forced selling volume that would result from margin calls
5. Assess the impact of portfolio margin systems compared to standard Reg T margin
6. Create policy recommendations based on the analysis

**Excel Solution:**
```excel
'Inputs
Portfolio_Value = 100000
Current_Initial_Margin = 0.5
Current_Maintenance_Margin = 0.3
Pre1929_Initial_Margin = 0.1
Pre1929_Maintenance_Margin = 0.05
Oil_Crisis_Initial_Margin = 0.65
Oil_Crisis_Maintenance_Margin = 0.4
Portfolio_Margin_Initial = 0.15
Portfolio_Margin_Maintenance = 0.1

'Crash Scenarios
Crash_1929_Drawdown = 0.89
Crash_1929_Months = 34
Crash_1974_Drawdown = 0.48
Crash_1974_Months = 21
Crash_2008_Drawdown = 0.57
Crash_2008_Months = 17

'1. Maximum Leverage
Pre1929_Max_Leverage = 1 / Pre1929_Initial_Margin
Oil_Crisis_Max_Leverage = 1 / Oil_Crisis_Initial_Margin
Current_Max_Leverage = 1 / Current_Initial_Margin
Portfolio_Margin_Max_Leverage = 1 / Portfolio_Margin_Initial

'2. Crash Scenario Modeling
'We'll model each crash scenario with each regulatory regime
'For each month, calculate the portfolio value, equity, and margin percentage
'Check if margin call would be triggered

'Define monthly percentage declines for each crash (simplified as linear)
Crash_1929_Monthly_Decline = Crash_1929_Drawdown / Crash_1929_Months
Crash_1974_Monthly_Decline = Crash_1974_Drawdown / Crash_1974_Months
Crash_2008_Monthly_Decline = Crash_2008_Drawdown / Crash_2008_Months

'For each regulatory regime and crash scenario, track:
'- Portfolio value each month
'- Equity each month
'- Margin percentage each month
'- Whether a margin call is triggered
'- Month when margin call occurs
'- Equity remaining after liquidation

'3-4. Margin Call Analysis
'Assuming a normal distribution of investors with different entry points
'Calculate percentage of investors facing margin calls under each regime
'Calculate forced selling volume (using a simple model of partial liquidation)

'5. Portfolio Margin vs Reg T Analysis
'Compare drawdowns and margin call thresholds
'Calculate risk metrics for each approach
```

**Python Solution:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Input parameters
portfolio_value = 100000
current_initial_margin = 0.5
current_maintenance_margin = 0.3
pre1929_initial_margin = 0.1
pre1929_maintenance_margin = 0.05
oil_crisis_initial_margin = 0.65
oil_crisis_maintenance_margin = 0.4
portfolio_margin_initial = 0.15
portfolio_margin_maintenance = 0.1

# Crash scenarios
crash_scenarios = {
    "1929 Crash": {"drawdown": 0.89, "months": 34},
    "1973-74 Bear Market": {"drawdown": 0.48, "months": 21},
    "2008 Financial Crisis": {"drawdown": 0.57, "months": 17}
}

# Regulatory regimes
regimes = {
    "Pre-1929": {"initial_margin": pre1929_initial_margin, "maintenance_margin": pre1929_maintenance_margin},
    "1974 Oil Crisis": {"initial_margin": oil_crisis_initial_margin, "maintenance_margin": oil_crisis_maintenance_margin},
    "Current (Reg T)": {"initial_margin": current_initial_margin, "maintenance_margin": current_maintenance_margin},
    "Portfolio Margin": {"initial_margin": portfolio_margin_initial, "maintenance_margin": portfolio_margin_maintenance}
}

# 1. Calculate maximum leverage for each regime
for regime_name, regime_params in regimes.items():
    regimes[regime_name]["max_leverage"] = 1 / regime_params["initial_margin"]

# 2. Model crash scenarios
def model_crash(scenario, regime, investor_entry_points=None):
    """
    Model a market crash under specific regulatory regime
    
    Parameters:
    scenario (dict): Crash scenario parameters
    regime (dict): Regulatory regime parameters
    investor_entry_points (list): Optional list of market levels where investors entered
    
    Returns:
    dict: Results of the simulation
    """
    monthly_decline = scenario["drawdown"] / scenario["months"]
    
    # Initialize tracking variables
    market_levels = []
    margin_percentages = []
    margin_calls = []
    
    # Start at 100% (pre-crash)
    current_market_level = 1.0
    
    # Calculate initial position
    max_exposure = portfolio_value / regime["initial_margin"]
    initial_borrowed = max_exposure - portfolio_value
    
    for month in range(scenario["months"] + 1):  # +1 to include starting point
        market_levels.append(current_market_level)
        
        # Calculate current portfolio value and equity
        current_portfolio_value = max_exposure * current_market_level
        current_equity = current_portfolio_value - initial_borrowed
        current_margin_percentage = current_equity / current_portfolio_value
        
        margin_percentages.append(current_margin_percentage)
        
        # Check for margin call
        margin_call = current_margin_percentage < regime["maintenance_margin"]
        margin_calls.append(margin_call)
        
        # Update market level for next month
        current_market_level *= (1 - monthly_decline)
    
    # Calculate investor impact if entry points provided
    investor_impact = None
    if investor_entry_points is not None:
        investor_impact = []
        for entry_point in investor_entry_points:
            # Adjust values based on entry point
            adjusted_market_levels = [level / entry_point for level in market_levels]
            
            # Find if and when margin call occurs
            margin_call_month = None
            for month, (level, margin) in enumerate(zip(adjusted_market_levels, margin_percentages)):
                if margin < regime["maintenance_margin"]:
                    margin_call_month = month
                    break
            
            investor_impact.append({
                "entry_point": entry_point,
                "margin_call": margin_call_month is not None,
                "margin_call_month": margin_call_month,
                "final_equity_percentage": adjusted_market_levels[-1] - (1 - regime["initial_margin"])
            })
    
    return {
        "market_levels": market_levels,
        "margin_percentages": margin_percentages,
        "margin_calls": margin_calls,
        "first_margin_call_month": next((i for i, call in enumerate(margin_calls) if call), None),
        "investor_impact": investor_impact
    }

# Generate investor entry points (normally distributed around 1.0)
np.random.seed(42)  # For reproducibility
num_investors = 1000
mean_entry = 1.0
std_dev = 0.15  # Standard deviation of entry points
investor_entry_points = np.random.normal(mean_entry, std_dev, num_investors)

# Run simulations for all combinations
results = {}

for scenario_name, scenario in crash_scenarios.items():
    regime_results = {}
    
    for regime_name, regime in regimes.items():
        regime_results[regime_name] = model_crash(scenario, regime, investor_entry_points)
    
    results[scenario_name] = regime_results

# 3-4. Analyze margin calls and forced selling
margin_call_analysis = {}

for scenario_name, regime_results in results.items():
    scenario_analysis = {}
    
    for regime_name, crash_result in regime_results.items():
        if crash_result["investor_impact"] is not None:
            # Calculate percentage of investors with margin calls
            margin_called = sum(1 for investor in crash_result["investor_impact"] if investor["margin_call"])
            margin_call_percentage = margin_called / num_investors
            
            # Estimate forced selling volume (simplified)
            # Assume investors need to restore margin to initial requirement
            forced_selling = 0
            for investor in crash_result["investor_impact"]:
                if investor["margin_call"]:
                    # Simplified calculation of forced selling as percentage of portfolio
                    forced_selling += portfolio_value  # Simplified assumption
            
            scenario_analysis[regime_name] = {
                "margin_call_percentage": margin_call_percentage,
                "forced_selling_volume": forced_selling,
                "first_margin_call_month": crash_result["first_margin_call_month"]
            }
    
    margin_call_analysis[scenario_name] = scenario_analysis

# Print results
print("Regulatory Impact Analysis on Margin Trading")
print("===========================================")

print("\n1. Maximum Leverage by Regulatory Regime:")
for regime_name, regime in regimes.items():
    print(f"   {regime_name}: {regime['max_leverage']:.2f}x leverage")

print("\n2. Market Crash Impact Analysis:")
for scenario_name, regime_results in margin_call_analysis.items():
    print(f"\n   {scenario_name}:")
    for regime_name, analysis in regime_results.items():
        margin_call_month = analysis["first_margin_call_month"]
        margin_call_timing = f"Month {margin_call_month}" if margin_call_month is not None else "No margin call"
        
        print(f"      {regime_name}:")
        print(f"         Margin Call Timing: {margin_call_timing}")
        print(f"         % of Investors Facing Margin Calls: {analysis['margin_call_percentage']:.2%}")
        print(f"         Estimated Forced Selling: ${analysis['forced_selling_volume']:,.2f}")

print("\n3. Portfolio Margin vs. Reg T Comparison:")
for scenario_name in crash_scenarios:
    reg_t_result = margin_call_analysis[scenario_name]["Current (Reg T)"]
    portfolio_result = margin_call_analysis[scenario_name]["Portfolio Margin"]
    
    reg_t_month = reg_t_result["first_margin_call_month"]
    portfolio_month = portfolio_result["first_margin_call_month"]
    
    margin_call_difference = "N/A"
    if reg_t_month is not None and portfolio_month is not None:
        margin_call_difference = f"{portfolio_month - reg_t_month} months earlier" if portfolio_month < reg_t_month else f"{reg_t_month - portfolio_month} months later"
    
    print(f"   {scenario_name}:")
    print(f"      Difference in Margin Call Timing: {margin_call_difference}")
    print(f"      Difference in Affected Investors: {portfolio_result['margin_call_percentage'] - reg_t_result['margin_call_percentage']:.2%}")
    print(f"      Difference in Forced Selling: ${portfolio_result['forced_selling_volume'] - reg_t_result['forced_selling_volume']:,.2f}")

# Create visualizations
plt.figure(figsize=(15, 10))

# Plot 1: Market levels during crashes
plt.subplot(2, 2, 1)
for scenario_name, scenario in crash_scenarios.items():
    months = list(range(scenario["months"] + 1))
    market_levels = results[scenario_name]["Current (Reg T)"]["market_levels"]
    plt.plot(months, market_levels, label=scenario_name)

plt.xlabel('Month')
plt.ylabel('Market Level (% of Pre-Crash)')
plt.title('Market Drawdowns in Historical Crashes')
plt.grid(alpha=0.3)
plt.legend()

# Plot 2: Margin Percentages for 1929 Crash
plt.subplot(2, 2, 2)
scenario_name = "1929 Crash"
months = list(range(crash_scenarios[scenario_name]["months"] + 1))

for regime_name, regime_result in results[scenario_name].items():
    plt.plot(months, regime_result["margin_percentages"], label=regime_name)

plt.axhline(y=current_maintenance_margin, color='r', linestyle='--', label='Current Maintenance Requirement')
plt.xlabel('Month')
plt.ylabel('Margin Percentage')
plt.title('Margin Percentages During 1929 Crash')
plt.grid(alpha=0.3)
plt.legend()

# Plot 3: Percentage of Investors Facing Margin Calls
plt.subplot(2, 2, 3)
scenarios = list(crash_scenarios.keys())
x = np.arange(len(scenarios))
width = 0.2
multiplier = 0

for regime_name, regime in regimes.items():
    margin_call_percentages = [margin_call_analysis[scenario][regime_name]["margin_call_percentage"] for scenario in scenarios]
    offset = width * multiplier
    plt.bar(x + offset, [p * 100 for p in margin_call_percentages], width, label=regime_name)
    multiplier += 1

plt.xlabel('Crash Scenario')
plt.ylabel('% of Investors')
plt.title('Investors Facing Margin Calls')
plt.xticks(x + width, scenarios)
plt.grid(alpha=0.3)
plt.legend()

# Plot 4: Distribution of Investor Entry Points
plt.subplot(2, 2, 4)
plt.hist(investor_entry_points, bins=30, alpha=0.7)
plt.axvline(x=1.0, color='r', linestyle='--', label='Market Peak')
plt.xlabel('Entry Point (Relative to Peak)')
plt.ylabel('Number of Investors')
plt.title('Distribution of Investor Entry Points')
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('regulatory_impact_analysis.png')

# Create policy recommendations based on analysis
print("\n4. Policy Recommendations:")
print("   1. Consider dynamic margin requirements that adjust with market volatility")
print("   2. Implement early warning systems for investors approaching margin limits")
print("   3. Evaluate staged liquidation procedures to reduce market impact of forced selling")
print("   4. Consider portfolio-based risk assessment rather than flat margin requirements")
print("   5. Require increased investor education on margin risks before account approval")
```

These exercises provide comprehensive, practical applications of the margin trading and short selling concepts covered in Chapter 6. They progress from basic calculations to complex scenario analyses and policy implications, giving students a thorough understanding of both the mechanics and strategic considerations of leveraged investing.