from bs4 import BeautifulSoup
import datetime
import logging
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('capitol_trades.log'),
        logging.StreamHandler()
    ]
)


class Config:
    """Configuration settings for the Capitol Trades scraper."""
    
    RECENT_DAYS = 45
    MIN_TRADE_SIZE = 5000
    USE_MAX_RANGE = True
    
    URL = "https://www.capitoltrades.com/trades"
    TRADES_CHECKED_FILE = "trades_checked.txt"
    DATE_LOG_FILE = "date_log.txt"
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT_TIMEOUT = 10
    PAGES_TO_SCRAPE = 7


class TradeExtractor:
    """Handles extraction and parsing of trade data from HTML elements."""
    
    @staticmethod
    def parse_trade_size(size_str: Optional[str]) -> Optional[List[int]]:
        """Convert trade size string (e.g., '1K-15K') to numeric range [1000, 15000]."""
        if not size_str or size_str == "N/A":
            return None
        
        try:
            size_str = size_str.strip()
            
            if '<' in size_str:
                return [0, 1000]
            
            parts = size_str.replace('–', '-').replace('—', '-').split('-')
            if len(parts) != 2:
                return None
            
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            result = []
            
            for part in parts:
                part = part.strip()
                numeric = ''.join(c for c in part if c.isdigit() or c == '.')
                suffix = ''.join(c for c in part if c.isalpha())
                
                if not numeric or suffix not in multipliers:
                    return None
                
                value = float(numeric) * multipliers[suffix]
                result.append(int(value))
            
            return result
        except Exception as e:
            logging.debug(f"Error parsing trade size '{size_str}': {e}")
            return None
    
    @staticmethod
    def parse_filed_after(filed_str: Optional[str]) -> Optional[int]:
        """Extract number of days from filing delay string."""
        if not filed_str:
            return None
        
        try:
            digits = ''.join(c for c in filed_str if c.isdigit())
            return int(digits) if digits else None
        except Exception as e:
            logging.debug(f"Error parsing filed_after '{filed_str}': {e}")
            return None


class TradeChecker:
    """Manages persistence of checked trades to avoid duplicate processing."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        try:
            open(self.filepath, 'a').close()
        except Exception as e:
            logging.error(f"Error creating trades file: {e}")
    
    def load_checked_ids(self) -> set:
        try:
            with open(self.filepath, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            logging.error(f"Error loading checked trades: {e}")
            return set()
    
    def mark_as_checked(self, trade_id: str):
        try:
            with open(self.filepath, 'a') as f:
                f.write(f"{trade_id}\n")
        except Exception as e:
            logging.error(f"Error marking trade as checked: {e}")


class CapitolTradesScraperSelenium:
    """
    Selenium-based scraper for Capitol Trades website.
    
    Scrapes congressional stock trades and filters based on user-defined criteria
    including filing delay, trade size, and ticker availability.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.extractor = TradeExtractor()
        self.checker = TradeChecker(config.TRADES_CHECKED_FILE)
        self.driver = None
        self.current_page = 1
    
    def setup_driver(self):
        """Initialize headless Chrome WebDriver."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            logging.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Error setting up WebDriver: {e}")
            return False
    
    def fetch_page(self, page_num: int = 1) -> Optional[BeautifulSoup]:
        """Fetch and parse a specific page from Capitol Trades."""
        try:
            if page_num == 1:
                url = self.config.URL
            else:
                url = f"{self.config.URL}?page={page_num}"
            
            logging.info(f"Fetching page {page_num}: {url}")
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, self.config.ELEMENT_WAIT_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            time.sleep(3)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            
            self.current_page = page_num
            self.log_run(f"Success - Page {page_num}")
            return soup
        
        except TimeoutException:
            logging.error(f"Timeout waiting for page {page_num} to load")
            return None
        except Exception as e:
            logging.error(f"Error fetching page {page_num}: {e}")
            return None
    
    def has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if additional pages are available."""
        try:
            next_button = soup.find('a', string=lambda x: x and 'next' in x.lower())
            if next_button and not next_button.get('disabled'):
                return True
            
            pagination = soup.find('div', class_=lambda x: x and 'pagination' in str(x).lower())
            if pagination:
                page_links = pagination.find_all('a')
                if page_links:
                    return True
            
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]
                if len(rows) == 0:
                    return False
            
            return True
        
        except Exception as e:
            logging.debug(f"Error checking for next page: {e}")
            return False
    
    def log_run(self, status: str):
        try:
            with open(self.config.DATE_LOG_FILE, 'a') as f:
                f.write(f"{datetime.datetime.now()} - Status: {status}\n")
        except Exception as e:
            logging.error(f"Error logging run: {e}")
    
    def extract_trade_from_row(self, row) -> Optional[Dict]:
        """Extract all relevant trade information from a table row."""
        try:
            cells = row.find_all('td')
            
            if len(cells) < 9:
                return None
            
            politician_cell = cells[0]
            politician_link = politician_cell.find('a')
            politician_name = politician_link.text.strip() if politician_link else None
            
            party_text = politician_cell.get_text()
            if 'Republican' in party_text:
                party = 'Republican'
            elif 'Democrat' in party_text:
                party = 'Democrat'
            else:
                party = 'Unknown'
            
            issuer_cell = cells[1]
            issuer_link = issuer_cell.find('a')
            trade_issue = issuer_link.text.strip() if issuer_link else None
            
            trade_ticker = "N/A"
            if issuer_link:
                full_text = issuer_cell.get_text(separator='\n')
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                
                if len(lines) >= 2:
                    potential_ticker = lines[1]
                    if potential_ticker and potential_ticker != trade_issue:
                        trade_ticker = potential_ticker
            
            if trade_ticker == "N/A":
                for text in issuer_cell.stripped_strings:
                    text = text.strip()
                    if text == trade_issue:
                        continue
                    if text and (':' in text or (text.isupper() and len(text) <= 6)):
                        trade_ticker = text
                        break
            
            published = cells[2].text.strip()
            traded_date = cells[3].text.strip()
            
            filed_after_str = cells[4].text.strip()
            filed_after = self.extractor.parse_filed_after(filed_after_str)
            
            owner = cells[5].text.strip()
            transaction_type = cells[6].text.strip()
            
            trade_size_str = cells[7].text.strip()
            trade_size = self.extractor.parse_trade_size(trade_size_str)
            
            price = cells[8].text.strip()
            
            detail_link = row.find('a', href=lambda x: x and '/trades/' in x)
            if detail_link:
                href = detail_link.get('href')
                trade_id = ''.join(c for c in href if c.isdigit())
                trade_link = f"https://www.capitoltrades.com{href}"
            else:
                return None
            
            return {
                'trade_id': trade_id,
                'trade_link': trade_link,
                'politician': politician_name,
                'party': party,
                'trade_issue': trade_issue,
                'trade_ticker': trade_ticker,
                'published': published,
                'traded_date': traded_date,
                'filed_after': filed_after,
                'owner': owner,
                'transaction_type': transaction_type,
                'trade_size': trade_size,
                'price': price
            }
        
        except Exception as e:
            logging.debug(f"Error extracting trade from row: {e}")
            return None
    
    def meets_criteria(self, trade_data: Dict) -> bool:
        """Check if trade meets all filtering criteria."""
        try:
            if trade_data['filed_after'] is None:
                return False
            
            if trade_data['filed_after'] >= self.config.RECENT_DAYS:
                return False
            
            if trade_data['trade_size'] is None:
                return False
            
            range_idx = 1 if self.config.USE_MAX_RANGE else 0
            trade_size_value = trade_data['trade_size'][range_idx]
            
            if trade_size_value < self.config.MIN_TRADE_SIZE:
                return False
            
            ticker = trade_data['trade_ticker']
            if not ticker or ticker == "N/A" or ticker.strip() == "":
                return False
            
            return True
        
        except Exception as e:
            logging.debug(f"Error checking criteria: {e}")
            return False
    
    def process_page(self, soup: BeautifulSoup, checked_ids: set) -> List[Dict]:
        """Process all trades on a single page and return matching trades."""
        filtered_trades = []
        
        table = soup.find('table')
        if not table:
            logging.error("Could not find trades table")
            return filtered_trades
        
        rows = table.find_all('tr')[1:]
        logging.info(f"Found {len(rows)} trades on page {self.current_page}")
        
        for idx, row in enumerate(rows):
            trade_data = self.extract_trade_from_row(row)
            
            if not trade_data:
                continue
            
            trade_id = trade_data['trade_id']
            
            if trade_id in checked_ids:
                logging.debug(f"Trade {trade_id} already checked, skipping")
                continue
            
            if self.meets_criteria(trade_data):
                logging.info(f"✓ Trade {trade_id} matches: {trade_data['politician']} - {trade_data['trade_issue']}")
                filtered_trades.append(trade_data)
                self.checker.mark_as_checked(trade_id)
            else:
                logging.debug(f"✗ Trade {trade_id} does not meet criteria")
        
        return filtered_trades
    
    def format_output(self, trades: List[Dict]) -> str:
        """Format filtered trades into a readable report."""
        if not trades:
            return "No trades matched the criteria"
        
        output = f"\n{'='*80}\n"
        output += f"Found {len(trades)} trade(s) matching criteria\n"
        output += f"{'='*80}\n\n"
        
        for i, trade in enumerate(trades, 1):
            output += f"Trade #{i}\n"
            output += f"{'─'*60}\n"
            output += f"Politician: {trade['politician']} ({trade['party']})\n"
            output += f"Transaction: {trade['transaction_type']}\n"
            output += f"Company: {trade['trade_issue']} ({trade['trade_ticker']})\n"
            output += f"Size: ${trade['trade_size'][0]:,} - ${trade['trade_size'][1]:,}\n"
            output += f"Filed After: {trade['filed_after']} days\n"
            output += f"Traded: {trade['traded_date']}\n"
            output += f"Published: {trade['published']}\n"
            output += f"Price: {trade['price']}\n"
            output += f"Link: {trade['trade_link']}\n"
            output += "\n"
        
        return output
    
    def run(self) -> List[Dict]:
        """
        Main execution method with pagination support.
        
        Returns:
            List of trades matching the filtering criteria.
        """
        logging.info("="*80)
        logging.info("Starting Capitol Trades scraper")
        logging.info("="*80)
        logging.info(f"Configuration:")
        logging.info(f"  - RECENT_DAYS: {self.config.RECENT_DAYS}")
        logging.info(f"  - MIN_TRADE_SIZE: ${self.config.MIN_TRADE_SIZE:,}")
        logging.info(f"  - USE_MAX_RANGE: {self.config.USE_MAX_RANGE}")
        logging.info(f"  - PAGES_TO_SCRAPE: {self.config.PAGES_TO_SCRAPE}")
        logging.info("="*80)
        
        all_filtered_trades = []
        
        try:
            if not self.setup_driver():
                return []
            
            checked_ids = self.checker.load_checked_ids()
            logging.info(f"Loaded {len(checked_ids)} previously checked trades")
            
            page_num = 1
            pages_scraped = 0
            
            while pages_scraped < self.config.PAGES_TO_SCRAPE:
                logging.info(f"\n{'#'*80}")
                logging.info(f"Scraping page {page_num} ({pages_scraped + 1}/{self.config.PAGES_TO_SCRAPE})")
                logging.info(f"{'#'*80}")
                
                soup = self.fetch_page(page_num)
                if not soup:
                    logging.error(f"Failed to fetch page {page_num}, stopping")
                    break
                
                page_trades = self.process_page(soup, checked_ids)
                all_filtered_trades.extend(page_trades)
                
                logging.info(f"Page {page_num} complete: Found {len(page_trades)} matching trades")
                
                pages_scraped += 1
                
                if pages_scraped < self.config.PAGES_TO_SCRAPE:
                    if not self.has_next_page(soup):
                        logging.info("No more pages available")
                        break
                    
                    page_num += 1
                    time.sleep(2)
            
            logging.info(f"\n{'='*80}")
            logging.info(f"SCRAPING COMPLETE")
            logging.info(f"Total pages scraped: {pages_scraped}")
            logging.info(f"Total matching trades found: {len(all_filtered_trades)}")
            logging.info(f"{'='*80}")
            
            return all_filtered_trades
        
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("WebDriver closed")


def main():
    try:
        config = Config()
        scraper = CapitolTradesScraperSelenium(config)
        
        filtered_trades = scraper.run()
        
        output = scraper.format_output(filtered_trades)
        print(output)
        
        if filtered_trades:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"filtered_trades_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(output)
            logging.info(f"Results saved to {filename}")
        
        return filtered_trades
    
    except Exception as e:
        logging.error(f"Fatal error in main: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    main()