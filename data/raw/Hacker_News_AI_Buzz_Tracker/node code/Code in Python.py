# n8n code node: Code in Python  (structured JSON signal)
def func(_items):
    row = _items[0]["json"]
    lb = row.get("leaderboard", [])

    signal = {
        "source": "hacker_news_buzz",
        "schema_version": "1.0",
        "run_date": row.get("run_date"),
        "window_hours": row.get("window_hours", 24),
        "complete": row.get("complete", True),
        "entities": [
            {
                "entity": e.get("entity"),
                "ticker": e.get("ticker"),
                "buzz_score": e.get("buzzScore"),
                "velocity": e.get("velocity", 0),
                "breakout": e.get("breakout", False),
                "low_confidence": e.get("lowConfidence", False),
                "cold_start": e.get("coldStart", False),
            }
            for e in lb
        ],
    }
    return [{"json": signal}]


return func(_items)
