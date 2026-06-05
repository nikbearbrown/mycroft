#!/usr/bin/env python3
"""
SEC EDGAR Document Fetcher - Enhanced for n8n Integration
Fetches SEC filings and outputs standardized JSON for workflow processing.
"""

import requests
import json
import time
import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

class EDGARFetcher:
    def __init__(self, user_agent: str = "SEC Analyzer your.email@example.com"):
        self.headers = {
            'User-Agent': user_agent
        }
        self.base_url = "https://data.sec.gov/submissions/"
    
    def get_company_info(self, ticker: str) -> tuple:
        """Get company CIK and name from ticker."""
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        
        try:
            response = requests.get(tickers_url, headers=self.headers)
            response.raise_for_status()
            companies = response.json()
            
            for key, company in companies.items():
                if company['ticker'].upper() == ticker.upper():
                    cik = str(company['cik_str']).zfill(10)
                    company_name = company['title']
                    return cik, company_name
            
            return None, None
            
        except Exception as e:
            raise Exception(f"Error fetching company info: {e}")
    
    def get_filings(self, cik: str, form_types: List[str], max_per_type: int = 3) -> List[Dict]:
        """Get filtered filings list."""
        url = f"{self.base_url}CIK{cik}.json"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            filings = []
            recent_filings = data.get('filings', {}).get('recent', {})
            
            if recent_filings:
                forms = recent_filings.get('form', [])
                filing_dates = recent_filings.get('filingDate', [])
                accession_numbers = recent_filings.get('accessionNumber', [])
                primary_documents = recent_filings.get('primaryDocument', [])
                
                # Group by form type and limit
                by_type = defaultdict(list)
                
                for i, form in enumerate(forms):
                    if form in form_types and len(by_type[form]) < max_per_type:
                        filing_info = {
                            'form_type': form,
                            'filing_date': filing_dates[i],
                            'accession_number': accession_numbers[i],
                            'primary_document': primary_documents[i],
                            'html_url': self._build_html_url(cik, accession_numbers[i], primary_documents[i])
                        }
                        by_type[form].append(filing_info)
                        filings.append(filing_info)
                
                # Sort by filing date (most recent first)
                filings.sort(key=lambda x: x['filing_date'], reverse=True)
            
            return filings
            
        except Exception as e:
            raise Exception(f"Error fetching filings: {e}")
    
    def _build_html_url(self, cik: str, accession_number: str, primary_document: str) -> str:
        """Build URL for HTML version of filing."""
        acc_no_dashes = accession_number.replace('-', '')
        return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{primary_document}"
    
    def download_filing(self, filing: Dict[str, str], output_dir: str) -> Dict[str, Any]:
        """Download a single filing and return metadata."""
        try:
            time.sleep(0.1)  # SEC rate limiting
            
            response = requests.get(filing['html_url'], headers=self.headers)
            response.raise_for_status()
            
            # Create filename
            safe_form = filing['form_type'].replace('/', '_')
            filename = f"{safe_form}_{filing['filing_date']}_{filing['accession_number']}.html"
            filepath = os.path.join(output_dir, filename)
            
            # Save content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'form_type': filing['form_type'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'content_size': len(response.text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'form_type': filing['form_type'],
                'filing_date': filing['filing_date']
            }
    
    def fetch_all_filings(self, ticker: str, output_base_dir: str, 
                         form_types: List[str] = None, max_per_type: int = 2) -> Dict[str, Any]:
        """
        Main function to fetch all filings for a ticker.
        
        Returns standardized JSON output for n8n workflow.
        """
        if form_types is None:
            form_types = ['10-K', '10-Q', '8-K']
        
        try:
            # Get company info
            cik, company_name = self.get_company_info(ticker)
            if not cik:
                return {
                    'success': False,
                    'error': f'Ticker {ticker} not found in SEC database',
                    'ticker': ticker
                }
            
            # Create output directory
            output_dir = os.path.join(output_base_dir, f"{ticker.upper()}_SEC_filings")
            os.makedirs(output_dir, exist_ok=True)
            
            # Get filings list
            filings = self.get_filings(cik, form_types, max_per_type)
            if not filings:
                return {
                    'success': False,
                    'error': f'No filings found for {ticker}',
                    'ticker': ticker
                }
            
            # Download filings
            downloaded_files = []
            failed_downloads = []
            
            for filing in filings:
                result = self.download_filing(filing, output_dir)
                if result['success']:
                    downloaded_files.append(result)
                else:
                    failed_downloads.append(result)
            
            # Save metadata
            metadata = {
                'ticker': ticker.upper(),
                'company_name': company_name,
                'cik': cik,
                'download_timestamp': datetime.now().isoformat(),
                'form_types': form_types,
                'total_filings_found': len(filings),
                'successful_downloads': len(downloaded_files),
                'failed_downloads': len(failed_downloads)
            }
            
            metadata_file = os.path.join(output_dir, 'download_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Return standardized output
            return {
                'success': True,
                'ticker': ticker.upper(),
                'company_name': company_name,
                'cik': cik,
                'output_directory': output_dir,
                'metadata_file': metadata_file,
                'downloaded_files': downloaded_files,
                'failed_downloads': failed_downloads,
                'summary': {
                    'total_files': len(downloaded_files),
                    'total_size_chars': sum(f['content_size'] for f in downloaded_files),
                    'forms_by_type': {
                        form_type: len([f for f in downloaded_files if f['form_type'] == form_type])
                        for form_type in form_types
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ticker': ticker
            }

def main():
    """Command line interface for n8n integration."""
    parser = argparse.ArgumentParser(description='SEC EDGAR Fetcher for n8n')
    parser.add_argument('--ticker', required=True, help='Stock ticker symbol')
    parser.add_argument('--output-dir', default='/app/data', help='Output directory')
    parser.add_argument('--user-agent', required=True, help='User agent string')
    parser.add_argument('--forms', default='10-K,10-Q,8-K', help='Comma-separated form types')
    parser.add_argument('--max-per-type', type=int, default=2, help='Max filings per type')
    
    args = parser.parse_args()
    
    try:
        fetcher = EDGARFetcher(user_agent=args.user_agent)
        form_types = [f.strip() for f in args.forms.split(',')]
        
        result = fetcher.fetch_all_filings(
            ticker=args.ticker,
            output_base_dir=args.output_dir,
            form_types=form_types,
            max_per_type=args.max_per_type
        )
        
        # Output JSON for n8n to consume
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'ticker': args.ticker
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()