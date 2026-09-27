"""
test_claims_agent.py — real end-to-end test of ClaimsAgent, using
US-10822628-B2 (already cached from earlier queries — free BigQuery
lookup). First runs structural-only (classify_independent=False, zero
API cost) to verify the wiring, then runs full classification on this
patent's 2 real independent claims.
"""
from google.cloud import bigquery
from claims_agent import ClaimsAgent
import json

client = bigquery.Client(project="patent-intelligence-system")

query = """
SELECT claims_localized[0].text AS claims_text
FROM `patents-public-data.patents.publications`
WHERE publication_number = @pub_number
LIMIT 1
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[bigquery.ScalarQueryParameter("pub_number", "STRING", "US-11197952-B2")]
)

print("Pulling claims text (should be free — cached from earlier)...")
result = list(client.query(query, job_config=job_config).result())
claims_text = result[0].claims_text

agent = ClaimsAgent()

print("\n--- Structural-only pass (no API cost) ---")
structural_reading = agent.read_claims(
    publication_number="US-11197952-B2",
    claims_text=claims_text,
    classify_independent=False,
)
print(agent.summarize(structural_reading))

print("\n--- Full pass with classification (1 independent claim, real API cost) ---")
full_reading = agent.read_claims(
    publication_number="US-11197952-B2",
    claims_text=claims_text,
    classify_independent=True,
)
print(json.dumps(agent.summarize(full_reading), indent=2))
