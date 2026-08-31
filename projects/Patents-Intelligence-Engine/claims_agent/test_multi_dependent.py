"""
test_multi_dependent.py — tests claims_parser against real patents likely
to contain multi-dependent claims (e.g. "claim 1 or 2", "claims 1-3"),
based on real patent numbers found via search: US10822628, US11197952,
US10265458.

Publication numbers need to be in the BigQuery format (US-XXXXXXX-B2 or
similar) — this script searches by base number since we don't know the
exact kind-code suffix, rather than guessing it.
"""
from google.cloud import bigquery
from claims_parser import split_claims, summarize

client = bigquery.Client(project="patent-intelligence-system")

candidate_numbers = ["10822628", "11197952", "10265458"]

for base_number in candidate_numbers:
    print("=" * 60)
    print(f"Searching for patent number containing: {base_number}")
    print("=" * 60)

    query = f"""
    SELECT
        publication_number,
        claims_localized[0].text AS claims_text
    FROM `patents-public-data.patents.publications`
    WHERE publication_number LIKE 'US-{base_number}%'
    LIMIT 1
    """

    try:
        result = list(client.query(query).result())
    except Exception as e:
        print(f"Query failed: {e}\n")
        continue

    if not result:
        print(f"No match found for {base_number}\n")
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
        multi_ref_hint = ""
        if not c.is_independent and (" or " in c.text[:150].lower() or "-" in c.text[:80]):
            multi_ref_hint = "  [POSSIBLE MULTI-DEPENDENCY — CHECK MANUALLY]"
        print(f"Claim {c.number} — {status}{multi_ref_hint}")

    print()
    print(summarize(claims))
    print()
