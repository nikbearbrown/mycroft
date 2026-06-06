from typing import List
from app.models.award import Award


def summarize_awards(awards: List[Award]) -> dict:
    """
    Generate an analyst-ready summary report from a processed list of awards.

    Returns aggregate stats and the top flagged signals.
    """
    if not awards:
        return {"total": 0, "flagged": [], "by_agency_type": {}, "total_value": 0}

    flagged = sorted(
        [a for a in awards if (a.signal_score or 0) >= 0.7],
        key=lambda a: a.signal_score or 0,
        reverse=True,
    )

    by_agency: dict[str, dict] = {}
    for award in awards:
        atype = award.agency_type or "Unknown"
        if atype not in by_agency:
            by_agency[atype] = {"count": 0, "total_value": 0.0}
        by_agency[atype]["count"] += 1
        by_agency[atype]["total_value"] += award.award_amount or 0

    return {
        "total": len(awards),
        "flagged_count": len(flagged),
        "total_value": sum(a.award_amount or 0 for a in awards),
        "by_agency_type": by_agency,
        "top_signals": [a.model_dump() for a in flagged[:10]],
    }
