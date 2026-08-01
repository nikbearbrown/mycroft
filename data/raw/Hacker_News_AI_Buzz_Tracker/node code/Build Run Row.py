# n8n code node: Build Run Row
def func(_items):
    leaderboard = [i["json"] for i in _items]           # already sorted by score
    run_date = leaderboard[0].get("runDate") if leaderboard else None
    raw_metrics = {i["entity"]: i["rawMetrics"] for i in leaderboard}
    return [{"json": {
        "run_date": run_date,
        "window_hours": 24,
        "leaderboard": leaderboard,
        "raw_metrics": raw_metrics,
        "complete": len(leaderboard) == len(_items) and len(leaderboard) > 0,
        "watchlist_version": "v1"
    }}]


return func(_items)
