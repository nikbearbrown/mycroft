import json
import csv
import io
from typing import List
from app.models.award import Award


def parse_awards(content: bytes, filename: str) -> List[Award]:
    """Parse raw bytes from a SAM.gov export into a list of Award objects."""
    if filename.endswith(".json"):
        return _parse_json(content)
    elif filename.endswith(".csv"):
        return _parse_csv(content)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def _parse_json(content: bytes) -> List[Award]:
    data = json.loads(content)
    records = data if isinstance(data, list) else data.get("results", [])
    return [Award(**_normalize(r)) for r in records]


def _parse_csv(content: bytes) -> List[Award]:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    return [Award(**_normalize(row)) for row in reader]


def _normalize(record: dict) -> dict:
    """Map SAM.gov field names to internal Award field names."""
    return {
        "award_id": record.get("award_id") or record.get("Award ID", ""),
        "recipient_name": record.get("recipient_name") or record.get("Recipient Name", ""),
        "awarding_agency": record.get("awarding_agency") or record.get("Awarding Agency", ""),
        "award_amount": float(record.get("award_amount") or record.get("Award Amount", 0) or 0),
        "award_date": record.get("award_date") or record.get("Award Date", ""),
        "description": record.get("description") or record.get("Description", ""),
        "naics_code": record.get("naics_code") or record.get("NAICS Code", ""),
        "place_of_performance": record.get("place_of_performance") or record.get("Place of Performance", ""),
    }
