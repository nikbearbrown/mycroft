"""
test_multi_dependent.py — tests claims_parser against real patents known
to contain multi-dependent claims.

IMPORTANT: uses exact publication_number matches (=), never LIKE. A
LIKE wildcard on this table forces a full-column scan — one such query
was confirmed to cost 116.58 GB scanned (checked in BigQuery job
history), which is what actually exhausted the free monthly quota.
Exact matches on a known publication_number are cheap by comparison.
"""
from google.cloud import bigquery
from claims_parser import split_claims, summarize, flag_multi_dependency

client = bigquery.Client(project="patent-intelligence-system")

# Exact, confirmed publication numbers from earlier successful runs —
# never re-introduce a LIKE search here.
patent_numbers = ["US-10822628-B2", "US-11197952-B2", "US-10265458-B2"]

for pub_number in patent_numbers:
    print("=" * 60)
    print(f"Querying: {pub_number}")
    print("=" * 60)

    query = """
    SELECT
        publication_number,
        claims_localized[0].text AS claims_text
    FROM `patents-public-data.patents.publications`
    WHERE publication_number = @pub_number
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("pub_number", "STRING", pub_number)]
    )

    try:
        result = list(client.query(query, job_config=job_config).result())
    except Exception as e:
        print(f"Query failed: {e}\n")
        continue

    if not result:
        print(f"No match found for {pub_number}\n")
        continue

    row = result[0]
    full_text = row.claims_text

    if not full_text:
        print(f"Found {row.publication_number} but claims_text is empty\n")
        continue

    print(f"Found: {row.publication_number}")
    print(f"Claims text length: {len(full_text)} characters\n")

    claims = split_claims(full_text)
    print(f"Parsed {len(claims)} claim(s):\n")

    for c in claims:
        status = "INDEPENDENT" if c.is_independent else f"DEPENDENT on claim {c.references}"
        multi_ref_hint = "  [POSSIBLE MULTI-DEPENDENCY]" if flag_multi_dependency(c) else ""
        print(f"Claim {c.number} — {status}{multi_ref_hint}")

    print()
    print(summarize(claims))
    print()
