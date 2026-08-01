# n8n code node: Computer Buzz Score
import math

# --- calibration knobs (Week 3 deliverable; tune against fixtures)---
VOLUME_REF    = 30    # storyCount that earns ~full volume points
ENGAGEMENT_REF = 1000 # (points+comments) that earns ~full engagement points
FRONTPAGE_REF = 5     # frontPageCount that earns full front-page points

# --- Week 4 acceleration bounds (per plan.md / S0-10) ---
ACCEL_MIN = -1.0      # full negative velocity floor (score dropped to ~0 or below)
ACCEL_MAX = 2.0       # cap reward at +200% growth vs the prior run


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def base_of(entry):
    """Reconstruct an entry's non-acceleration score from its stored components.

    Yesterday's snapshot stores scoreComponents; the acceleration part is
    excluded so today's velocity is measured against yesterday's *base*, not a
    figure that already contained yesterday's own acceleration (avoids compounding).
    """
    c = entry.get("scoreComponents", {}) or {}
    return c.get("volume", 0) + c.get("engagement", 0) + c.get("frontPage", 0)


def split_inputs(_items):
    """Separate the single previous-run item (has a 'leaderboard' key) from the
    current per-entity metric items. Returns (prev_leaderboard, current_items)."""
    prev_leaderboard = []
    current = []
    for item in _items:
        d = item.get("json", {})
        if "leaderboard" in d:
            # The DB read row merged in before this node.
            prev_leaderboard = d.get("leaderboard") or []
        elif "rawMetrics" in d:
            current.append(d)
    return prev_leaderboard, current


def func(_items):
    prev_leaderboard, current = split_inputs(_items)
    prev_by_entity = {e.get("entity"): e for e in prev_leaderboard if e.get("entity")}

    out = []
    for d in current:
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

        today_base = volume_score + engagement_score + front_page_score

        # --- Acceleration vs the previous run (Week 4) ---
        prev = prev_by_entity.get(d["entity"])
        if prev is None:
            # Cold start: entity unseen (first run, or newly added at a version boundary).
            accel_score = 0.0
            cold_start = True
        else:
            yesterday_base = base_of(prev)
            if yesterday_base <= 0:
                # Zero-denominator guard: no meaningful baseline to grow from.
                accel_score = 0.0
            else:
                delta = today_base - yesterday_base
                accel_score = 20.0 * clamp(delta / yesterday_base, ACCEL_MIN, ACCEL_MAX)
            cold_start = False

        buzz = round(today_base + accel_score, 1)

        buzz_score = clamp(buzz, 0, 100)
        d["buzzScore"] = buzz_score
        d["scoreComponents"] = {
            "volume": round(volume_score, 1),
            "engagement": round(engagement_score, 1),
            "frontPage": round(front_page_score, 1),
            "acceleration": round(accel_score, 1),
        }
        d["velocity"] = round(accel_score, 1)   # exposed for the digest / JSON signal
        d["coldStart"] = cold_start
        d["breakout"] = buzz_score >= d.get("breakoutThreshold", 70)
        out.append({"json": d})

    # Ranked leaderboard, highest first.
    out.sort(key=lambda i: i["json"]["buzzScore"], reverse=True)
    return out


return func(_items)
