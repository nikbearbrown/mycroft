import csv
import os
from app.models.award import Award

_TRACKED_COMPANIES: set[str] = set()

_TRACKED_FILE = os.path.join(
    os.path.dirname(__file__),
    "../../../data/tracked_companies.csv",
)

_HIGH_VALUE_THRESHOLD = 10_000_000
_AI_NAICS_CODES = {"541511", "541512", "541519", "518210", "334111"}
_HIGH_PRIORITY_AGENCY_TYPES = {"DoD", "Intel"}


def _load_tracked_companies():
    global _TRACKED_COMPANIES
    if _TRACKED_COMPANIES:
        return
    try:
        with open(_TRACKED_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("company_name", "").strip().lower()
                if name:
                    _TRACKED_COMPANIES.add(name)
    except FileNotFoundError:
        pass


def score_award(award: Award) -> float:
    """
    Return a signal score between 0.0 and 1.0.

    Scoring components:
      - 0.40  recipient is a tracked company
      - 0.25  award amount >= $10M
      - 0.20  NAICS code is AI-related
      - 0.15  awarding agency type is DoD or Intel
    """
    _load_tracked_companies()
    score = 0.0

    recipient = (award.recipient_name or "").strip().lower()
    if any(tracked in recipient for tracked in _TRACKED_COMPANIES):
        score += 0.40

    if (award.award_amount or 0) >= _HIGH_VALUE_THRESHOLD:
        score += 0.25

    if (award.naics_code or "") in _AI_NAICS_CODES:
        score += 0.20

    if (award.agency_type or "") in _HIGH_PRIORITY_AGENCY_TYPES:
        score += 0.15

    return round(min(score, 1.0), 4)
