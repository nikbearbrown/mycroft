"""
patent_reader.py — a real, callable CLI wiring ClaimsAgent and
LineageAgent together for the first time. Takes a real publication
number, runs both agents, and prints a combined reading.

Usage:
    .venv/bin/python patent_reader.py US-11791319-B2
    .venv/bin/python patent_reader.py US-11791319-B2 --no-classify

Uses the same exact-match, parameterized query pattern as every other
script in this project — safe against the real cost we documented in
the README (cached queries are free; only genuinely new patent
numbers cost the real ~$0.71).
"""
import sys
import json
import argparse

from google.cloud import bigquery
from claims_agent import ClaimsAgent
from lineage_agent import LineageAgent


def fetch_patent_row(client: bigquery.Client, pub_number: str):
    query = """
    SELECT publication_number, claims_localized[0].text AS claims_text, citation
    FROM `patents-public-data.patents.publications`
    WHERE publication_number = @pub_number
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("pub_number", "STRING", pub_number)]
    )
    result = list(client.query(query, job_config=job_config).result())
    return result[0] if result else None


def main():
    parser = argparse.ArgumentParser(
        description="Read a patent's claims and citation lineage."
    )
    parser.add_argument("publication_number", help="e.g. US-11791319-B2")
    parser.add_argument(
        "--no-classify", action="store_true",
        help="skip the Claude API call for protection-scope classification "
             "(faster, zero API cost — structural claims reading + lineage only)"
    )
    args = parser.parse_args()

    client = bigquery.Client(project="patent-intelligence-system")

    print(f"Fetching {args.publication_number}...")
    row = fetch_patent_row(client, args.publication_number)

    if row is None:
        print(f"No row found for {args.publication_number}. "
              f"Check the exact publication number format (kind code, dashes).")
        sys.exit(1)

    result = {"publication_number": row.publication_number}

    if row.claims_text:
        claims_agent = ClaimsAgent()
        claims_reading = claims_agent.read_claims(
            publication_number=row.publication_number,
            claims_text=row.claims_text,
            classify_independent=not args.no_classify,
        )
        result["claims"] = claims_agent.summarize(claims_reading)
    else:
        result["claims"] = None
        print("Warning: no claims_text found for this patent.")

    if row.citation:
        lineage_agent = LineageAgent()
        raw_rows = []
        for c in row.citation:
            raw_rows.append(dict(c.items()) if hasattr(c, "items") else dict(c))
        backward = lineage_agent.parse_backward_citations(row.publication_number, raw_rows)
        result["lineage"] = lineage_agent.summarize(backward)
    else:
        result["lineage"] = {"total_citations": 0}

    print()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
