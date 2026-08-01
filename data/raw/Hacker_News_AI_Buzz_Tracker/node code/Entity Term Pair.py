# n8n code node: Entity Term Pair
res = []
for item in _items:
    for query in item["json"]["queryTerms"]:
        res.append({
            "entity": item["json"]["entity"],
            "term": query,
            "queryTerm": f'"{query}"',
            "sinceUnix": item["json"]["sinceUnix"],
            "ticker": item["json"]["ticker"],
            "frontPagePoints": item["json"]["frontPagePoints"],
            "breakoutThreshold": item["json"]["breakoutThreshold"],
        })

return res
