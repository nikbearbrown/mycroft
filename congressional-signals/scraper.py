"""
scraper.py — Capitol Trades Selenium scraper
Outputs: data/trades.csv

Strategy (confirmed via DOM inspection):
  1. Paginate /politicians?page=N to get all politician profile IDs
  2. For each politician, paginate /politicians/{id}?page=N
  3. Each trade is a <TR class="border-b"> row inside a <table>
  4. Politician metadata (name, party, chamber, state) is in the page header
"""

import csv
import logging
import random
import re
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE = "https://www.capitoltrades.com"
DATA_DIR = Path(__file__).parent / "data"
OUTPUT = DATA_DIR / "trades.csv"

COLUMNS = [
    "politician",
    "party",
    "chamber",
    "state",
    "ticker",
    "asset_name",
    "trade_type",
    "transaction_date",
    "disclosure_date",
    "amount_range",
    "trade_url",
    "politician_id",
]

TRADE_ROW_SEL = "tr.border-b"
POLITICIAN_LINK_SEL = "a.index-card-link[href*='/politicians/']"


def make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)


def delay(lo: float = 1.5, hi: float = 3.0) -> None:
    time.sleep(random.uniform(lo, hi))


def clean_ticker(raw: str) -> str:
    raw = raw.strip().upper()
    return re.sub(r"[:.][A-Z]{2,4}$", "", raw)


def _text(el, selector: str, default: str = "") -> str:
    try:
        return el.find_element(By.CSS_SELECTOR, selector).text.strip()
    except NoSuchElementException:
        return default


def _attr(el, selector: str, attr: str) -> str:
    try:
        return el.find_element(By.CSS_SELECTOR, selector).get_attribute(attr) or ""
    except NoSuchElementException:
        return ""


def dismiss_cookie_banner(driver: webdriver.Chrome) -> None:
    for sel in [
        "button#onetrust-accept-btn-handler",
        "button[aria-label*='Accept']",
        "button[class*='accept']",
    ]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(0.5)
            return
        except NoSuchElementException:
            continue


# ─── Politician list ────────────────────────────────────────────────────────

def get_politician_ids(driver: webdriver.Chrome, wait: WebDriverWait, max_pages: int = 50) -> list[dict]:
    """
    Paginate /politicians?page=N and collect {id, name, party, chamber, state}.
    Politician rows are <li class="border-b">.
    """
    politicians: list[dict] = []
    seen_ids: set[str] = set()

    for page in range(max_pages):
        # Page 0 = /politicians (no param); page N = /politicians?page=N
        url = f"{BASE}/politicians" if page == 0 else f"{BASE}/politicians?page={page}"
        log.info("Politicians page %d -> %s", page, url)
        driver.get(url)
        time.sleep(6)  # Capitol Trades JS takes ~5-6s to hydrate

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, POLITICIAN_LINK_SEL)))
        except TimeoutException:
            log.info("No politician cards on page %d — done", page)
            break

        card_links = driver.find_elements(By.CSS_SELECTOR, POLITICIAN_LINK_SEL)
        if not card_links:
            break

        new_count = 0
        for link in card_links:
            try:
                href = link.get_attribute("href") or ""
                m = re.search(r"/politicians/([^/?]+)", href)
                if not m:
                    continue
                pol_id = m.group(1)
                if pol_id in seen_ids:
                    continue
                seen_ids.add(pol_id)

                name = _text(link, "h2") or _text(link, ".politician-name")
                # Extract party from parent article's CSS class (reliable; avoids picking up card body text)
                try:
                    article_class = driver.execute_script(
                        "return arguments[0].closest('article').className", link) or ""
                    party_m = re.search(r"\bparty--(\w+)", article_class)
                    party = party_m.group(1).capitalize() if party_m else ""
                except Exception:
                    party = ""
                # Chamber / state not reliably in listing-page DOM; will be blank
                chamber = ""
                state = ""

                politicians.append({
                    "id": pol_id,
                    "name": name,
                    "party": party,
                    "chamber": chamber,
                    "state": state,
                })
                new_count += 1
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        log.info("  Found %d new politicians (total %d)", new_count, len(politicians))
        if new_count == 0:
            log.info("No new politicians — stopping pagination")
            break
        delay()

    return politicians


# ─── Trade rows ─────────────────────────────────────────────────────────────

def _parse_date_cell(td) -> str:
    """
    Extract ISO date from a table cell whose date is split across two divs:
      <div class="text-size-3 font-medium">11 May</div>
      <div class="text-size-2 text-txt-dimmer">2026</div>
    Returns YYYY-MM-DD or empty string.
    """
    try:
        day_mon = td.find_element(By.CSS_SELECTOR, ".text-size-3").text.strip()
        year    = td.find_element(By.CSS_SELECTOR, ".text-size-2").text.strip()
        if day_mon and year and year.isdigit():
            from datetime import datetime as _dt
            return _dt.strptime(f"{day_mon} {year}", "%d %b %Y").strftime("%Y-%m-%d")
    except Exception:
        pass
    return ""


def parse_trade_row(tr, politician: dict) -> dict | None:
    """
    Parse a <TR class="border-b"> trade row on a politician's page.
    Column order (confirmed from DOM):
      td[0] = issuer (name + ticker)
      td[1] = disclosure date  (split-div format: "11 May" / "2026")
      td[2] = transaction date (split-div format: "6 May"  / "2026")
      td[3] = reporting gap
      td[4+] = trade type, amount, link
    """
    # Get all <td> cells in this row
    tds = []
    try:
        tds = tr.find_elements(By.CSS_SELECTOR, "td")
    except Exception:
        pass

    # Dates — from td[1] (disclosure) and td[2] (transaction)
    disclosure_date  = _parse_date_cell(tds[1]) if len(tds) > 1 else ""
    transaction_date = _parse_date_cell(tds[2]) if len(tds) > 2 else ""

    # Trade type
    trade_type = _text(tr, ".tx-type")

    # Issuer
    asset_name = _text(tr, "h3.issuer-name") or _text(tr, ".issuer-name")
    ticker = clean_ticker(_text(tr, ".issuer-ticker"))

    # Amount — td[5] contains "100K•250K"; normalise bullet/dash separator
    amount = ""
    if len(tds) > 5:
        amount = tds[5].text.strip()
    if not amount:
        amount = _text(tr, "span.trade-size") or _text(tr, ".trade-size")
    # Replace bullet (U+25CF) and en-dash (U+2013) with plain hyphen
    amount = amount.replace("●", "-").replace("–", "-").replace("—", "-")

    # Trade URL (arrow link)
    trade_url = ""
    try:
        links = tr.find_elements(By.CSS_SELECTOR, "a[href*='/trades/']")
        for l in links:
            href = l.get_attribute("href") or ""
            if "/trades/" in href:
                trade_url = href
                break
    except Exception:
        pass

    if not ticker and not asset_name:
        return None  # skip blank rows

    return {
        "politician": politician["name"],
        "party": politician["party"],
        "chamber": politician["chamber"],
        "state": politician["state"],
        "ticker": ticker,
        "asset_name": asset_name,
        "trade_type": trade_type,
        "transaction_date": transaction_date,
        "disclosure_date": disclosure_date,
        "amount_range": amount,
        "trade_url": trade_url,
        "politician_id": politician["id"],
    }


def scrape_politician_trades(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    politician: dict,
    max_pages: int = 50,
) -> list[dict]:
    """Paginate a politician's trade table and return all trade records."""
    trades: list[dict] = []
    pol_id = politician["id"]

    for page in range(1, max_pages + 1):  # pages start at 1; ?page=0 is empty
        url = f"{BASE}/politicians/{pol_id}?page={page}"
        driver.get(url)
        time.sleep(5)

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, TRADE_ROW_SEL)))
        except TimeoutException:
            break

        rows = driver.find_elements(By.CSS_SELECTOR, TRADE_ROW_SEL)
        if not rows:
            break

        page_trades = []
        for row in rows:
            try:
                t = parse_trade_row(row, politician)
                if t:
                    page_trades.append(t)
            except StaleElementReferenceException:
                continue

        if not page_trades:
            break

        trades.extend(page_trades)
        log.info("    %s page %d: %d trades", pol_id, page, len(page_trades))
        delay(0.8, 1.5)

    return trades


# ─── Main ────────────────────────────────────────────────────────────────────

BROWSER_RESTART_EVERY = 25  # restart Chrome every N politicians to prevent memory issues


def scrape(max_politician_pages: int = 50, max_trade_pages: int = 50) -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    done_ids = load_done_ids()
    if done_ids:
        log.info("Resuming — %d politicians already done", len(done_ids))

    driver = make_driver()
    wait = WebDriverWait(driver, 45)
    total_trades = 0

    try:
        driver.get(BASE)
        delay(2, 3)
        dismiss_cookie_banner(driver)

        # Step 1: collect all politician IDs
        log.info("=== Step 1: Collecting politician IDs ===")
        politicians = get_politician_ids(driver, wait, max_pages=max_politician_pages)
        log.info("Total politicians found: %d", len(politicians))

        # Step 2: scrape each politician's trades (skip already-done ones)
        log.info("=== Step 2: Scraping individual trades ===")
        for i, pol in enumerate(politicians, 1):
            pol_id = pol["id"]
            if pol_id in done_ids:
                log.info("[%d/%d] Skipping %s (already done)", i, len(politicians), pol["name"])
                continue

            log.info("[%d/%d] %s (%s)", i, len(politicians), pol["name"], pol_id)

            # Restart browser periodically to prevent memory exhaustion
            if (i - 1) % BROWSER_RESTART_EVERY == 0 and i > 1:
                log.info("Restarting browser to free memory...")
                driver.quit()
                driver = make_driver()
                wait = WebDriverWait(driver, 45)

            pol_trades = scrape_politician_trades(driver, wait, pol, max_pages=max_trade_pages)

            if pol_trades:
                append_trades(pol_trades)
                total_trades += len(pol_trades)

            mark_done(pol_id)
            log.info("  -> %d trades | Total so far: %d", len(pol_trades), total_trades)
            delay()

    except KeyboardInterrupt:
        log.info("Interrupted — progress saved via checkpointing")
    except Exception as e:
        log.error("Unexpected error: %s — progress saved via checkpointing", e)
        raise
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return []  # data written incrementally; caller reads from OUTPUT


CHECKPOINT = DATA_DIR / "scraper_checkpoint.txt"


def load_done_ids() -> set[str]:
    """Return set of politician IDs already scraped (from checkpoint file)."""
    if not CHECKPOINT.exists():
        return set()
    return set(CHECKPOINT.read_text(encoding="utf-8").splitlines())


def mark_done(pol_id: str) -> None:
    with open(CHECKPOINT, "a", encoding="utf-8") as f:
        f.write(pol_id + "\n")


def _ascii_safe(s: str) -> str:
    # Strip newlines/tabs so CSV fields stay single-line; normalize to ASCII
    s = s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    s = s.encode('ascii', errors='replace').decode('ascii')
    return ' '.join(s.split())


def append_trades(trades: list[dict]) -> None:
    """Append trades to CSV, writing header only if file doesn't exist yet."""
    # Normalize all string fields to ASCII-safe before writing
    clean = []
    for t in trades:
        clean.append({k: _ascii_safe(str(v)) if isinstance(v, str) else v for k, v in t.items()})

    write_header = not OUTPUT.exists() or OUTPUT.stat().st_size == 0
    with open(OUTPUT, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        if write_header:
            writer.writeheader()
        writer.writerows(clean)


def save(trades: list[dict]) -> None:
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(trades)
    log.info("Saved %d rows -> %s", len(trades), OUTPUT)


if __name__ == "__main__":
    scrape(max_politician_pages=50, max_trade_pages=50)
    if OUTPUT.exists() and OUTPUT.stat().st_size > 0:
        import pandas as pd
        n = len(pd.read_csv(OUTPUT))
        log.info("Done. %d trades saved -> %s", n, OUTPUT)
        log.info("Run enricher.py next.")
    else:
        log.error("No trades collected.")
