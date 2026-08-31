"""
test_connection.py — verify BigQuery access works, using a real, narrow,
single-patent query (not a wildcard scan) to stay safely within the
Sandbox free tier.
"""
from google.cloud import bigquery

client = bigquery.Client(project="patent-intelligence-system")

query = """
SELECT
    publication_number,
    claims_localized[0].text AS claims_text,
    claims_localized[0].language AS language
FROM `patents-public-data.patents.publications`
WHERE publication_number = 'US-11791319-B2'
LIMIT 1
"""

print("Running test query against a single, known patent...")
result = client.query(query).result()

for row in result:
    print("\nPublication number:", row.publication_number)
    print("Language:", row.language)
    print("Claims text (first 300 chars):")
    print(row.claims_text[:300] if row.claims_text else "(empty)")

print("\nConnection test succeeded.")
