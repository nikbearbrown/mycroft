"""
test_real_parse.py — pulls the FULL claims text for a real patent from
BigQuery and runs it through claims_parser.py. This is the real test —
test_connection.py only showed the first 300 characters.
"""
from google.cloud import bigquery
from claims_parser import split_claims, summarize

client = bigquery.Client(project="patent-intelligence-system")

query = """
SELECT
    publication_number,
    claims_localized[0].text AS claims_text
FROM `patents-public-data.patents.publications`
WHERE publication_number = 'US-11791319-B2'
LIMIT 1
"""

print("Pulling full claims text...")
result = list(client.query(query).result())

if not result:
    print("No rows returned.")
else:
    row = result[0]
    full_text = row.claims_text

    print(f"Total claims text length: {len(full_text)} characters\n")
    print("=" * 60)
    print("FULL RAW TEXT (for manual inspection):")
    print("=" * 60)
    print(full_text)
    print("=" * 60)

    claims = split_claims(full_text)

    print(f"\nParsed {len(claims)} claim(s):\n")
    for c in claims:
        status = "INDEPENDENT" if c.is_independent else f"DEPENDENT on claim {c.references}"
        print(f"Claim {c.number} — {status}")
        print(f"  {c.text[:120]}...")
        print()

    print(summarize(claims))
