"""Central configuration — everything the pipeline needs to be reproducible.

Paths follow Mycroft's data-layer convention: raw SEC responses and generated
outputs live under the repo-root ``data/`` tree in a per-recipe subfolder, kept
distinct from source data. The SEC-required User-Agent, base URLs, and polite
rate limiting also live here.
"""
from __future__ import annotations

import os
from pathlib import Path

# --- Paths -----------------------------------------------------------------
# config.py -> secfma -> sec-filings-financial-metrics -> scripts -> <repo root>
BASE_DIR = Path(__file__).resolve().parents[3]
RECIPE = "sec-filings-financial-metrics"
RAW_DIR = BASE_DIR / "data" / "raw" / RECIPE          # cached, unmodified SEC responses
VERIFIED_DIR = BASE_DIR / "data" / "verified" / RECIPE  # pipeline outputs
for _d in (RAW_DIR, VERIFIED_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- SEC access ------------------------------------------------------------
# The SEC *requires* a descriptive User-Agent with a contact email and asks
# clients to stay under ~10 requests/second. Override via SEC_USER_AGENT.
USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "Mycroft SEC Filings Metrics Agent - Asavari Shejwal (shejwal.a@northeastern.edu)",
)
MIN_REQUEST_INTERVAL = float(os.environ.get("SEC_MIN_REQUEST_INTERVAL", "0.15"))  # seconds

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik10}.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"
COMPANY_CONCEPT_URL = (
    "https://data.sec.gov/api/xbrl/companyconcept/CIK{cik10}/{taxonomy}/{tag}.json"
)

# Forms we care about for financial metrics.
DEFAULT_FORMS = ("10-K", "10-Q")

# How long a cached raw file is considered fresh (hours). <= 0 means always reuse.
CACHE_TTL_HOURS = float(os.environ.get("SEC_CACHE_TTL_HOURS", "24"))
