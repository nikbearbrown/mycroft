import math

# --- calibration knobs (Week 3 deliverable; tune against fixtures)---
VOLUME_REF    = 30    # storyCount that earns ~full volume points
ENGAGEMENT_REF = 1000 # (points+comments) that earns ~full engagement points
FRONTPAGE_REF = 5     # frontPageCount that earns full front-page points

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def func(_items):
    out = []
    for item in _items:
        d = item["json"]
        m = d["rawMetrics"]
        story_count = m["storyCount"]
        engagement = m["totalPoints"] + m["totalComments"]
        fp_count = m["frontPageCount"]
        low_conf = d.get("lowConfidence", False)

        if low_conf:
            # Sparse-entity floor: absolute scale, not the cross-entity log scale.
            volume_score = 30.0 * clamp(story_count / 3.0)
            engagement_score = 30.0 * clamp(engagement / 50.0)
            front_page_score = 0.0
        else:
            volume_score = 30.0 * clamp(math.log1p(story_count) / math.log1p(VOLUME_REF))
            engagement_score = 30.0 * clamp(math.log1p(engagement) / math.log1p(ENGAGEMENT_REF))
            front_page_score = 20.0 * clamp(fp_count / FRONTPAGE_REF)

        # Cold-start: no prior snapshot yet (Week 4 wires the DB) -> uniform hard zero.
        # Week 4 formula: delta = today_buzz - yesterday_buzz
        # accel_score = 20 * clamp(delta / yesterday_buzz, -1.0, 2.0)
        # Zero-denominator guard: if yesterday_buzz == 0, accel_score = 0.0
        # Clamp is [-1.0, 2.0] per S0-10: negative velocit  y penalizes, positive rewards up to 200% growth.
        accel_score = 0.0

        buzz = round(volume_score + engagement_score + front_page_score + accel_score, 1)

        buzz_score = clamp(buzz, 0, 100)
        d["buzzScore"] = buzz_score
        d["scoreComponents"] = {
            "volume": round(volume_score, 1),
            "engagement": round(engagement_score, 1),
            "frontPage": round(front_page_score, 1),
            "acceleration": accel_score,
        }
        d["coldStart"] = True   # flipped to False in Week 4 once velocity has history
        d["breakout"] = buzz_score >= d.get("breakoutThreshold", 70)
        out.append({"json": d})

    # Ranked leaderboard, highest first.
    out.sort(key=lambda i: i["json"]["buzzScore"], reverse=True)
    return out

# return func(_items)