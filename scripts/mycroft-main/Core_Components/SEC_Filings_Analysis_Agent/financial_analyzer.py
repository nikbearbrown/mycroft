#!/usr/bin/env python3
"""
SEC Financial Analyzer - Enhanced for n8n Integration
Uses sec-edgar-api to extract financial metrics and calculate ratios.
"""

import json
import sys
import argparse
import os
import warnings
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sec_edgar_api import EdgarClient

warnings.filterwarnings('ignore')
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('sec_edgar_api').setLevel(logging.ERROR)

class SECFinancialAnalyzer:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent
        self.edgar = EdgarClient(user_agent=user_agent)
        self.ticker_to_cik_cache = {}
    
    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Convert ticker to CIK."""
        if ticker in self.ticker_to_cik_cache:
            return self.ticker_to_cik_cache[ticker]
        
        try:
            import requests
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(tickers_url, headers=headers)
            response.raise_for_status()
            companies = response.json()
            
            for key, company in companies.items():
                if company['ticker'].upper() == ticker.upper():
                    cik = str(company['cik_str']).zfill(10)
                    self.ticker_to_cik_cache[ticker] = cik
                    return cik
            
            return None
            
        except Exception as e:
            raise Exception(f"Error looking up CIK for {ticker}: {e}")
    
    def get_company_facts(self, ticker: str) -> Dict[str, Any]:
        """Get company facts from SEC API."""
        try:
            cik = self.get_cik_from_ticker(ticker)
            if not cik:
                raise Exception(f"Could not find CIK for ticker {ticker}")
            
            company_facts = self.edgar.get_company_facts(cik)
            return company_facts
            
        except Exception as e:
            raise Exception(f"Error fetching company facts for {ticker}: {e}")
    
    def extract_financial_metrics(self, company_facts: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Extract key financial metrics from company facts."""
        if not company_facts or 'facts' not in company_facts:
            return {}
        
        us_gaap = company_facts.get('facts', {}).get('us-gaap', {})
        financial_data = {}
        
        # Enhanced metrics mapping for better coverage
        metrics_mapping = {
            'revenue': ['Revenues', 'SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
            'cost_of_revenue': ['CostOfRevenue', 'CostOfGoodsAndServicesSold'],
            'gross_profit': ['GrossProfit'],
            'research_development': ['ResearchAndDevelopmentExpense'],
            'operating_income': ['OperatingIncomeLoss'],
            'net_income': ['NetIncomeLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic'],
            'earnings_per_share_basic': ['EarningsPerShareBasic'],
            'earnings_per_share_diluted': ['EarningsPerShareDiluted'],
            'cash_and_equivalents': ['CashAndCashEquivalentsAtCarryingValue'],
            'total_current_assets': ['AssetsCurrent'],
            'total_assets': ['Assets'],
            'current_liabilities': ['LiabilitiesCurrent'],
            'long_term_debt': ['LongTermDebt', 'LongTermDebtNoncurrent'],
            'total_liabilities': ['Liabilities'],
            'shareholders_equity': ['StockholdersEquity'],
            'operating_cash_flow': ['NetCashProvidedByUsedInOperatingActivities'],
            'capital_expenditures': ['PaymentsToAcquirePropertyPlantAndEquipment'],
            'shares_outstanding': ['CommonStocksIncludingAdditionalPaidInCapitalSharesOutstanding'],
            'book_value_per_share': ['BookValuePerShare']
        }
        
        for metric_name, possible_keys in metrics_mapping.items():
            metric_data = self._extract_metric_data(us_gaap, possible_keys)
            if metric_data:
                financial_data[metric_name] = metric_data
        
        return financial_data
    
    def _extract_metric_data(self, us_gaap: Dict, possible_keys: List[str]) -> List[Dict]:
        """Extract data for a specific metric."""
        for key in possible_keys:
            if key in us_gaap:
                usd_data = us_gaap[key].get('units', {}).get('USD', [])
                if usd_data:
                    cleaned_data = []
                    for item in usd_data:
                        if 'val' not in item:
                            continue
                        
                        data_point = {
                            'value': item['val'],
                            'period_end': item.get('end'),
                            'fiscal_year': item.get('fy'),
                            'fiscal_period': item.get('fp'),
                            'form': item.get('form'),
                            'filed_date': item.get('filed')
                        }
                        cleaned_data.append(data_point)
                    
                    # Sort by period end date
                    cleaned_data.sort(key=lambda x: x.get('period_end', ''), reverse=True)
                    return cleaned_data[:10]  # Return last 10 periods
        
        return []
    
    def get_latest_data(self, financial_data: Dict[str, List[Dict]], form_type: str = '10-K') -> Dict[str, Any]:
        """Get latest data for a specific form type."""
        latest_data = {}
        
        for metric_name, metric_data in financial_data.items():
            for data_point in metric_data:
                if data_point.get('form') == form_type and data_point.get('value') is not None:
                    latest_data[metric_name] = data_point
                    break
        
        return latest_data
    
    def calculate_ratios(self, annual_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate financial ratios from annual data."""
        ratios = {}
        
        def get_value(metric_name: str) -> float:
            return annual_data.get(metric_name, {}).get('value', 0) or 0
        
        # Extract values
        revenue = get_value('revenue')
        gross_profit = get_value('gross_profit')
        operating_income = get_value('operating_income')
        net_income = get_value('net_income')
        total_assets = get_value('total_assets')
        shareholders_equity = get_value('shareholders_equity')
        total_liabilities = get_value('total_liabilities')
        operating_cash_flow = get_value('operating_cash_flow')
        current_assets = get_value('total_current_assets')
        current_liabilities = get_value('current_liabilities')
        
        # Calculate ratios
        if revenue > 0:
            if gross_profit > 0:
                ratios['gross_margin_pct'] = (gross_profit / revenue) * 100
            if operating_income != 0:
                ratios['operating_margin_pct'] = (operating_income / revenue) * 100
            if net_income != 0:
                ratios['net_margin_pct'] = (net_income / revenue) * 100
        
        # Profitability ratios
        if total_assets > 0 and net_income != 0:
            ratios['return_on_assets_pct'] = (net_income / total_assets) * 100
        
        if shareholders_equity > 0 and net_income != 0:
            ratios['return_on_equity_pct'] = (net_income / shareholders_equity) * 100
        
        # Leverage ratios
        if shareholders_equity > 0:
            ratios['debt_to_equity'] = total_liabilities / shareholders_equity
        
        if total_assets > 0:
            ratios['debt_to_assets'] = total_liabilities / total_assets
        
        # Liquidity ratios
        if current_liabilities > 0:
            ratios['current_ratio'] = current_assets / current_liabilities
        
        # Cash flow ratios
        if operating_cash_flow > 0 and current_liabilities > 0:
            ratios['operating_cash_flow_ratio'] = operating_cash_flow / current_liabilities
        
        return ratios
    
    def create_financial_analysis(self, ticker: str, output_dir: str) -> Dict[str, Any]:
        """
        Create comprehensive financial analysis.
        
        Returns standardized JSON output for n8n.
        """
        try:
            # Get company facts
            company_facts = self.get_company_facts(ticker)
            if not company_facts:
                raise Exception("Could not retrieve company facts")
            
            # Extract financial metrics
            financial_data = self.extract_financial_metrics(company_facts)
            if not financial_data:
                raise Exception("Could not extract financial data")
            
            # Get latest annual and quarterly data
            latest_annual = self.get_latest_data(financial_data, '10-K')
            latest_quarterly = self.get_latest_data(financial_data, '10-Q')
            
            # Calculate ratios
            financial_ratios = self.calculate_ratios(latest_annual)
            
            # Company information
            company_info = {
                'ticker': ticker.upper(),
                'company_name': company_facts.get('entityName', 'N/A'),
                'cik': company_facts.get('cik', 'N/A'),
                'sic': company_facts.get('sic', 'N/A'),
                'sic_description': company_facts.get('sicDescription', 'N/A'),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Build complete report
            report = {
                'success': True,
                'ticker': ticker.upper(),
                'company_info': company_info,
                'latest_annual_metrics': latest_annual,
                'latest_quarterly_metrics': latest_quarterly,
                'financial_ratios': financial_ratios,
                'historical_data_summary': {
                    metric: len(data) for metric, data in financial_data.items()
                },
                'key_insights': self._generate_key_insights(latest_annual, financial_ratios)
            }
            
            # Save detailed data to file
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{ticker}_financial_analysis.json")
                
                detailed_report = report.copy()
                detailed_report['full_historical_data'] = financial_data
                
                with open(output_file, 'w') as f:
                    json.dump(detailed_report, f, indent=2, default=str)
                
                report['output_file'] = output_file
            
            return report
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ticker': ticker
            }
    
    def _generate_key_insights(self, annual_data: Dict[str, Any], ratios: Dict[str, float]) -> List[str]:
        """Generate key financial insights."""
        insights = []
        
        # Revenue insight
        if 'revenue' in annual_data:
            revenue_val = annual_data['revenue']['value']
            insights.append(f"Latest annual revenue: ${revenue_val:,.0f}")
        
        # Profitability insights
        if 'net_margin_pct' in ratios:
            margin = ratios['net_margin_pct']
            if margin > 20:
                insights.append(f"Strong profitability with {margin:.1f}% net margin")
            elif margin > 10:
                insights.append(f"Healthy profitability with {margin:.1f}% net margin")
            elif margin > 0:
                insights.append(f"Modest profitability with {margin:.1f}% net margin")
            else:
                insights.append(f"Negative net margin of {margin:.1f}%")
        
        # Financial health
        if 'debt_to_equity' in ratios:
            de_ratio = ratios['debt_to_equity']
            if de_ratio < 0.3:
                insights.append("Conservative debt levels")
            elif de_ratio > 1.0:
                insights.append("High leverage - monitor debt levels")
        
        if 'current_ratio' in ratios:
            cr = ratios['current_ratio']
            if cr > 2.0:
                insights.append("Strong liquidity position")
            elif cr < 1.0:
                insights.append("Potential liquidity concerns")
        
        return insights

def main():
    """Command line interface for n8n."""
    parser = argparse.ArgumentParser(description='SEC Financial Analyzer for n8n')
    parser.add_argument('--ticker', required=True, help='Stock ticker symbol')
    parser.add_argument('--user-agent', help='User agent string', default='Humanitarian AI hr@humanitariansai.com')
    parser.add_argument('--output-dir', default='./data', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        analyzer = SECFinancialAnalyzer(user_agent=args.user_agent)
        result = analyzer.create_financial_analysis(args.ticker, args.output_dir)
        
        # Output JSON for n8n
        output = json.dumps(result, default=str, ensure_ascii=False)
        print(output)
        sys.stdout.flush()
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'ticker': args.ticker
        }
        print(json.dumps(error_output, ensure_ascii=False))
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()