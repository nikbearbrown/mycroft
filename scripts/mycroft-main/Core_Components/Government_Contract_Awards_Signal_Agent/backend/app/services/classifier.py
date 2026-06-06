import csv
import os
from app.models.award import Award

# List of (keyword_lower, agency_type) sorted longest-keyword-first so more
# specific entries win over broad ones (e.g. "defense intelligence agency"
# matches before "dept of defense").
_AGENCY_RULES: list[tuple[str, str]] = []

_MAPPING_FILE = os.path.join(
    os.path.dirname(__file__),
    "../../../data/agency_type_mapping.csv",
)


def _load_rules():
    global _AGENCY_RULES
    if _AGENCY_RULES:
        return
    rules = []
    try:
        with open(_MAPPING_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                keyword = row.get("agency_keyword", "").strip().lower()
                agency_type = row.get("agency_type", "").strip()
                if keyword and agency_type:
                    rules.append((keyword, agency_type))
    except FileNotFoundError:
        pass
    # longer keywords take priority (more specific match wins)
    _AGENCY_RULES = sorted(rules, key=lambda r: len(r[0]), reverse=True)


def classify_award(award: Award) -> str:
    """
    Return the agency type for an award by checking whether the awarding_agency
    path contains any known keyword (case-insensitive substring match).
    """
    _load_rules()
    haystack = (award.awarding_agency or "").lower()
    for keyword, agency_type in _AGENCY_RULES:
        if keyword in haystack:
            return agency_type
    return "Unknown"
