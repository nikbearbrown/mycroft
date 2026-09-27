"""
inspect_independent_claims.py — pulls every independent claim across
our four real, already-tested patents, and prints basic structural
stats (word count, limitation count) side by side. This is a research
step, not the classifier itself — we look at real data before deciding
what heuristic rules might actually distinguish broad vs. narrow scope.
"""
from google.cloud import bigquery
from claims_parser import split_claims

client = bigquery.Client(project="patent-intelligence-system")

patent_numbers = [
    "US-11791319-B2",
    "US-10822628-B2",
    "US-11197952-B2",
    "US-10265458-B2",
]

for pub_number in patent_numbers:
    query = f"""
    SELECT claims_localized[0].text AS claims_text
    FROM `patents-public-data.patents.publications`
    WHERE publication_number = '{pub_number}'
    LIMIT 1
    """
    result = list(client.query(query).result())
    if not result or not result[0].claims_text:
        print(f"{pub_number}: no claims text found\n")
        continue

    claims = split_claims(result[0].claims_text)
    independents = [c for c in claims if c.is_independent]

    print("=" * 70)
    print(f"{pub_number} — {len(independents)} independent claim(s)")
    print("=" * 70)

    for c in independents:
        word_count = len(c.text.split())
        # crude limitation count: count "wherein", "comprising", ";" as rough proxies
        limitation_markers = c.text.lower().count("wherein") + c.text.count(";")
        opens_with_method = c.text.strip().lower().startswith(("a method", "the method"))

        print(f"\nClaim {c.number}:")
        print(f"  word count: {word_count}")
        print(f"  limitation markers (wherein/semicolons): {limitation_markers}")
        print(f"  opens as method claim: {opens_with_method}")
        print(f"  first 150 chars: {c.text[:150]}...")

    print()
