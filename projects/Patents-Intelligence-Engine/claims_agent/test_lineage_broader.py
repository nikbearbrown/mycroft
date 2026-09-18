"""
test_lineage_broader.py — broadens LineageAgent testing to 2 genuinely
new, unseen patents, chosen for domain variety and likely different
citation profiles than our original NPL-heavy patent:
  - US-11983488-B1 — OpenAI, "Language Model for Text Generation &
    Editing" (granted May 14, 2024) — likely patent-heavy citations
  - US-2024160902-A1 — Shopify, "Similarity-Based Generative AI Output
    Filtering" (published May 16, 2024)

Real cost: 2 new exact-match lookups, ~$0.71 each (~$1.42 total).
"""
from google.cloud import bigquery
from lineage_agent import LineageAgent
import json

client = bigquery.Client(project="patent-intelligence-system")

patent_numbers = ["US-11983488-B1", "US-2024160902-A1"]

agent = LineageAgent()

for pub_number in patent_numbers:
    print("=" * 70)
    print(f"Querying: {pub_number}")
    print("=" * 70)

    query = """
    SELECT publication_number, citation
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
        print(f"No row found for {pub_number} — check the exact "
              f"publication number format (kind code may differ).\n")
        continue

    row = result[0]
    raw_rows = []
    for c in row.citation:
        if hasattr(c, "items"):
            raw_rows.append(dict(c.items()))
        else:
            raw_rows.append(dict(c))

    backward = agent.parse_backward_citations(row.publication_number, raw_rows)
    print(json.dumps(agent.summarize(backward), indent=2))
    print()
