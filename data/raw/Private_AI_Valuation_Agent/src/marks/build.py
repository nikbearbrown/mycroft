"""Build the marks panel: securities, then one mark per security/fund/period.

    price_per_share = value_usd / balance

That line is the whole project, and almost everything here exists because the
division is the easy part. The hard parts, in the order the data forced them:

1. **Amendments restate periods.** 16 `NPORT-P/A` filings cover the same
   (fund, period end) as an original. An amendment supersedes its original
   entirely; the original's holdings never become marks. Without that, the
   panel's own uniqueness constraint would reject the second filing and the
   choice of which one survives would be an accident of insert order.

2. **One security arrives on several lines.** A fund reporting the same
   security in several lots is ordinary. Those lines are summed -- Σvalue over
   Σbalance -- never averaged, and never deduplicated.

3. **Some of those lines are not the same security.** Inside a single filing,
   SpaceX common and preferred appear under the *same* issuer name and the
   *same* title, ten times apart. `asset_category` (EC/EP) separates them, so
   it is part of the security's identity here and not decoration. Where even
   that fails -- Neuberger Berman tags preferred as EC -- the lines disagree on
   price and the mark is recorded as **blended with no price at all**, because
   a price spanning two classes belongs to neither (plan.md, trap 2).

4. **Some titles are not share prices.** `CVT INT RIGHTS` prices per dollar of
   convertible right and `EV UNITS` per vehicle unit. The Week 4 class parser
   already knows; this module refuses to publish a price when it says so.

Nothing here adjusts a price. Splits are detected in src/marks/splits.py and
quarantined for a human, never corrected.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.resolve.normalize import parse_class  # noqa: E402

# Two lines of the same security whose prices differ by more than this are not
# the same security. 0.1% clears the fourth-decimal rounding that appears in
# five real line groups (73.5629 against 73.5630) and excludes the 1.79x OpenAI
# disagreement and the 10x SpaceX one.
BLEND_TOLERANCE = 0.001

# Filed asset categories, used only where the title carries no class at all.
# BlackRock files `ANTHROPIC PBC` with no class; without this every such row
# would be UNKNOWN and would merge with its own preferred sibling.
CATEGORY_CLASS = {"EC": "COM:UNSPECIFIED", "EP": "PFD:UNSPECIFIED"}

# One filing per (fund, period end). An amendment wins; between two amendments
# the later filing wins; between two filings on one day the later accession
# does. Deterministic, so a rebuild picks the same 1,496 filings every time.
EFFECTIVE_FILINGS = """
SELECT DISTINCT ON (fund_id, period_end)
       filing_id, fund_id, period_end, form_type
  FROM filings
 ORDER BY fund_id, period_end,
          CASE WHEN right(form_type, 2) = '/A' THEN 0 ELSE 1 END,
          filed_date DESC NULLS LAST,
          accession DESC
"""


# --------------------------------------------------------------------------
# securities
# --------------------------------------------------------------------------


def classify(title: str | None, asset_category: str | None) -> tuple[str, str]:
    """(class_normalized, price_basis) for one filed title.

    The asset category is a fallback, never an override: a title that says
    `SERIES F` is preferred whatever the filer tagged it, because ARK tags
    preferred as EC and the title is the more reliable of the two.
    """
    parsed = parse_class(title or "")
    label = parsed.label()
    if label == "UNKNOWN" and asset_category in CATEGORY_CLASS:
        label = CATEGORY_CLASS[asset_category]
    return label, parsed.basis


SECURITY_ROWS = """
WITH eff AS (%s)
SELECT m.company_id,
       r.title_of_issue,
       r.asset_category,
       bool_or(r.is_spv)                          AS is_spv,
       min(eff.period_end)                        AS first_seen,
       max(eff.period_end)                        AS last_seen,
       string_agg(DISTINCT f.family, ', ' ORDER BY f.family) AS filers,
       count(*)                                   AS lines
  FROM raw_holdings r
  JOIN eff             ON eff.filing_id = r.filing_id
  JOIN funds f         ON f.fund_id     = eff.fund_id
  JOIN match_decisions m ON m.raw_id    = r.raw_id
 WHERE m.company_id IS NOT NULL
 GROUP BY 1, 2, 3
 ORDER BY 1, 2, 3
""" % EFFECTIVE_FILINGS

UPSERT_SECURITY = """
INSERT INTO securities (company_id, share_class_raw, class_normalized, filer_grammar,
                        is_spv, spv_opaque, notes, price_basis, asset_category,
                        first_seen, last_seen)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (company_id, class_normalized, share_class_raw) DO UPDATE
   SET filer_grammar = EXCLUDED.filer_grammar,
       is_spv        = securities.is_spv OR EXCLUDED.is_spv,
       spv_opaque    = securities.spv_opaque OR EXCLUDED.spv_opaque,
       price_basis   = EXCLUDED.price_basis,
       first_seen    = least(securities.first_seen, EXCLUDED.first_seen),
       last_seen     = greatest(securities.last_seen, EXCLUDED.last_seen)
RETURNING security_id
"""


MAP_SECURITY = """
INSERT INTO security_map (company_id, share_class_raw, asset_category, security_id)
VALUES (%s, %s, %s, %s)
ON CONFLICT (company_id, share_class_raw, asset_category)
DO UPDATE SET security_id = EXCLUDED.security_id
"""


def build_securities(conn) -> dict:
    """One row per (company, filed title, class), plus the lookup a filed line
    uses to find it.

    Three Databricks titles say "Series I" and are filed EC by one manager and
    EP by another. That is one security tagged two ways, not two securities, so
    the category does not enter the security's key -- it enters `security_map`,
    which is what the marks build joins on.
    """
    with conn.cursor() as cur:
        cur.execute(SECURITY_ROWS)
        rows = cur.fetchall()

        seen, bases, mapped = {}, {}, 0
        categories: dict = {}
        for company_id, title, category, is_spv, first, last, filers, _lines in rows:
            label, basis = classify(title, category)
            # An opaque SPV is one whose wrapper hides the underlying. The Week
            # 4 matcher already decided that; is_spv carries it forward and the
            # count is reported rather than the rows being dropped.
            opaque = bool(is_spv) and "ECONOMIC EXPOSURE" not in (title or "").upper()
            key = (company_id, label, title)
            categories.setdefault(key, set()).add(category or "")
            note = "filed as " + ", ".join(sorted(c or "no category"
                                                  for c in categories[key]))
            cur.execute(UPSERT_SECURITY, (
                company_id, title, label, filers, bool(is_spv), opaque, note,
                basis, ", ".join(sorted(categories[key])), first, last,
            ))
            security_id = cur.fetchone()[0]
            seen[key] = security_id
            bases[basis] = bases.get(basis, 0) + 1
            cur.execute(MAP_SECURITY, (company_id, title, category or "", security_id))
            mapped += 1
    conn.commit()
    return {"securities": len(seen), "line_groups": len(rows),
            "mapped": mapped, "by_basis": bases}


# --------------------------------------------------------------------------
# marks
# --------------------------------------------------------------------------

# Aggregation happens in SQL because the join is large and the database is
# remote; the arithmetic is a sum and a division, both of which Postgres does
# exactly on NUMERIC. The blended test compares the per-line prices before they
# are summed away.
INSERT_MARKS = """
WITH eff AS (%s),
line AS (
    SELECT s.security_id,
           s.company_id,
           eff.fund_id,
           eff.filing_id,
           eff.period_end,
           r.asset_category,
           r.currency,
           r.balance,
           r.value_usd,
           r.price_per_share,
           s.price_basis,
           s.is_spv,
           s.spv_opaque
      FROM raw_holdings r
      JOIN eff               ON eff.filing_id = r.filing_id
      JOIN match_decisions m ON m.raw_id      = r.raw_id
      JOIN security_map sm   ON sm.company_id      = m.company_id
                            AND sm.share_class_raw = r.title_of_issue
                            AND sm.asset_category  = coalesce(r.asset_category, '')
  JOIN securities s      ON s.security_id = sm.security_id
     WHERE m.company_id IS NOT NULL
),
grouped AS (
    SELECT security_id, company_id, fund_id, period_end,
           min(filing_id)                    AS filing_id,
           min(asset_category)               AS asset_category,
           min(currency)                     AS currency,
           count(*)                          AS lines,
           sum(balance)                      AS balance,
           sum(value_usd)                    AS value_usd,
           min(price_per_share)              AS price_min,
           max(price_per_share)              AS price_max,
           min(price_basis)                  AS price_basis,
           bool_or(is_spv)                   AS is_spv,
           bool_or(spv_opaque)               AS spv_opaque
      FROM line
     GROUP BY 1, 2, 3, 4
),
judged AS (
    SELECT g.*,
           (g.price_max IS NOT NULL AND g.price_min IS NOT NULL AND g.price_min > 0
            AND g.price_max / g.price_min > 1 + %%(tol)s)          AS is_blended,
           (g.balance IS NULL OR g.balance = 0)                    AS no_balance,
           (g.price_basis <> 'per_share')                          AS not_a_share
      FROM grouped g
)
INSERT INTO marks (security_id, company_id, fund_id, filing_id, period_end,
                   asset_category, currency, lines, balance, value_usd,
                   price_per_share, is_blended, price_min, price_max,
                   is_spv, spv_opaque, change_blocked, block_reason, run_id)
SELECT security_id, company_id, fund_id, filing_id, period_end,
       asset_category, currency, lines, balance, value_usd,
       CASE WHEN no_balance OR not_a_share OR is_blended THEN NULL
            ELSE value_usd / balance END,
       is_blended, price_min, price_max, is_spv, spv_opaque,
       (no_balance OR not_a_share OR is_blended),
       CASE WHEN no_balance  THEN 'no balance: a missing share count is not a zero price'
            WHEN not_a_share THEN 'not a share price: ' || price_basis
            WHEN is_blended  THEN 'blended lines: the price belongs to neither class'
            ELSE NULL END,
       %%(run_id)s
  FROM judged
ON CONFLICT (security_id, fund_id, period_end) DO NOTHING
""" % EFFECTIVE_FILINGS


def build_marks(conn, run_id: int | None = None) -> dict:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM marks")
        cur.execute(INSERT_MARKS, {"tol": BLEND_TOLERANCE, "run_id": run_id})
        inserted = cur.rowcount
        cur.execute("""
            SELECT count(*)                                        AS marks,
                   count(*) FILTER (WHERE price_per_share IS NOT NULL) AS priced,
                   count(*) FILTER (WHERE is_blended)              AS blended,
                   count(*) FILTER (WHERE change_blocked)          AS blocked,
                   count(*) FILTER (WHERE spv_opaque)              AS opaque_spv,
                   sum(lines)                                      AS lines
              FROM marks
        """)
        marks, priced, blended, blocked, opaque, lines = cur.fetchone()
    conn.commit()
    return {"inserted": inserted, "marks": marks, "priced": priced,
            "blended": blended, "blocked": blocked, "opaque_spv": opaque,
            "lines_aggregated": int(lines or 0)}


def coverage(conn) -> dict:
    """Every resolved holding must land in exactly one mark, or be explained."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM raw_holdings")
        holdings = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM match_decisions WHERE company_id IS NULL")
        rejected = cur.fetchone()[0]
        cur.execute("""
            WITH eff AS (%s)
            SELECT count(*) FROM raw_holdings r
             WHERE NOT EXISTS (SELECT 1 FROM eff WHERE eff.filing_id = r.filing_id)
        """ % EFFECTIVE_FILINGS)
        superseded = cur.fetchone()[0]
        cur.execute("SELECT coalesce(sum(lines), 0) FROM marks")
        aggregated = int(cur.fetchone()[0])
    return {"holdings": holdings, "rejected_not_in_universe": rejected,
            "superseded_by_amendment": superseded, "lines_in_marks": aggregated,
            "reconciles": holdings == rejected + superseded + aggregated}
