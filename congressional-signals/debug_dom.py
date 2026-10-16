"""
debug_dom.py — Save page HTML and probe many selectors to find trade rows.
Run this once, then inspect data/debug_page.html to update scraper.py.
"""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")
opts.add_argument("--window-size=1920,1080")
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=opts)
try:
    driver.get("https://capitoltrades.com/trades")
    time.sleep(5)  # let JS render fully

    # Dismiss cookie banner
    for sel in ["button#onetrust-accept-btn-handler", "button[aria-label*='Accept']"]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(1)
            break
        except:
            pass

    time.sleep(3)

    # Save full HTML
    html = driver.page_source
    out = DATA_DIR / "debug_page.html"
    out.write_text(html, encoding="utf-8")
    print(f"Saved HTML ({len(html):,} chars) -> {out}")

    # Probe many selectors
    probes = [
        "tr",
        "tbody tr",
        "table tr",
        "article",
        "[class*='trade']",
        "[class*='Trade']",
        "[class*='row']",
        "[class*='Row']",
        "li[class*='trade']",
        "div[class*='trade']",
        "[data-row-index]",
        "td",
        "[class*='politician']",
        "[class*='Politician']",
        "[class*='issuer']",
        "[class*='Issuer']",
        "[class*='ticker']",
        "[class*='Ticker']",
        "[class*='tx-type']",
        "[class*='TxType']",
        "time",
        "[datetime]",
    ]

    print("\n--- Selector probe results ---")
    for sel in probes:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            sample = els[0].get_attribute("class") or els[0].tag_name
            print(f"  {len(els):4d} × '{sel}'   (first class: {sample[:80]})")

    # Print outer HTML of first few potential row elements
    print("\n--- First <tr> elements (up to 5) ---")
    trs = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    for i, tr in enumerate(trs[:5]):
        print(f"\n  tr[{i}] classes={tr.get_attribute('class')}")
        print(f"  text snippet: {tr.text[:200]!r}")

    print("\n--- First [class*='trade'] elements (up to 5) ---")
    trade_els = driver.find_elements(By.CSS_SELECTOR, "[class*='trade']")
    for i, el in enumerate(trade_els[:5]):
        print(f"\n  [{i}] tag={el.tag_name} class={el.get_attribute('class')}")
        print(f"  text: {el.text[:200]!r}")

finally:
    driver.quit()

print("\nDone. Open data/debug_page.html in a browser or text editor to inspect the DOM.")
