"""Assemble the golden-set sampling frame, with the evidence each label needs.

This does not label anything. It selects which issuer strings are worth a
human's judgment, and attaches to each one the facts that decide it, so that a
label is a reading of evidence rather than a guess about a name.

    python -m scripts.build_golden_candidates            # writes the frame
    python -m scripts.build_golden_candidates --stdout    # inspect it first

--------------------------------------------------------------------------
The unit of labelling
--------------------------------------------------------------------------
plan.md asks for 200-300 labelled holdings. The unit here is the distinct
(ISSUER_NAME, ISSUER_TITLE) pair instead, and each entry records how many
holdings it covers. The reason is that the 5,806 universe holdings contain only
231 distinct pairs: a random sample of 250 holdings would be roughly 95%
repeats of 'DATABRICKS INC' and would exercise the matcher on a few dozen
strings. Labelling the distinct strings covers every spelling the corpus
contains, and the holding counts let precision and recall be reported both
per-string (macro) and per-holding (micro). Both are in docs/entity_resolution.md.

--------------------------------------------------------------------------
Strata
--------------------------------------------------------------------------
S1  universe        every distinct pair the frozen Week 2 LIKE patterns select.
                    These decide precision: a wrong one is a false positive
                    already in the shipped data.
S2  near-miss       names in the 22M-row private layer that score >= 82 against
                    a universe token on partial_ratio but that the LIKE
                    patterns do NOT select. These decide recall: a company
                    hiding here is a miss nobody would otherwise see.

                    The sweep returns 347 such names, which would swamp the
                    sample -- 74 of them are one filer's internal security
                    codes ('XAIE-LMBK.AF' and 39 siblings), and labelling forty
                    of those measures nothing. Two rules cut it down, and the
                    second one is the important one:

                      (a) at most S2_PER_TOKEN names per near-miss token,
                          taken by holding volume, so every token's
                          neighbourhood is represented; and
                      (b) unconditionally, every near-miss name that matcher
                          v1 resolves to a company. Rule (b) means no claim
                          the matcher makes can escape being judged, which is
                          what makes the precision figure trustworthy rather
                          than a function of how the sample was drawn.

S3  hard cases      the five named in plan.md, pinned by literal and added to
                    the frame whether or not another stratum already caught
                    them. The opaque Fidelity SPVs reach the sample only this
                    way: they resemble nothing, which is exactly their point.

--------------------------------------------------------------------------
Evidence, and why price is the decisive field
--------------------------------------------------------------------------
For each candidate the frame carries a price-coincidence test against an
*anchor* series: the per-period consensus price computed only from holdings
whose identity is not in question, meaning rows carrying a registered issuer
LEI, or rows whose name is exactly the company's own name. The anchor never
depends on the fuzzy matcher being evaluated, so using it to label is not
circular.

This is what settles 'Anthropics Technology Ltd., Series G' -- a real UK
software company's name, filed by BlackRock, priced at 259.13640004 on the same
period end that six LEI-confirmed filers price Anthropic Series G at
259.1364. Ten significant figures is not a coincidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb
from rapidfuzz import fuzz, process

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.load import family_case_expr  # noqa: E402
from src.ingest.build_parquet import ALL_QUARTERS, PARQUET  # noqa: E402
from src.ingest.universe import ASSET_CATS  # noqa: E402
from src.resolve.match import (  # noqa: E402
    ALIASES,
    ISSUER_LEIS,
    like_pattern_company,
    resolve,
)
from src.resolve.normalize import (  # noqa: E402
    BASIS_PER_SHARE,
    normalise_name,
    parse_class,
)

OUT = ROOT / "docs" / "_golden_candidates.json"

# The tokens the near-miss sweep searches for. Deliberately the *spellings a
# company uses for itself*, not the frozen LIKE patterns -- searching with the
# patterns would only rediscover what the patterns already find.
NEAR_MISS_TOKENS = [
    "ANTHROPIC",
    "OPENAI",
    "OPEN AI",
    "DATABRICKS",
    "SPACEX",
    "SPACE EXPLORATION",
    "ANDURIL",
    "CEREBRAS",
    "FIGURE AI",
    "X.AI",
    "PERPLEXITY",
    "GROQ",
    "SCALE AI",
    "WORLD LABS",
]
NEAR_MISS_CUTOFF = 82
S2_PER_TOKEN = 4

# plan.md week 4: the cases the golden set exists to contain. Matched as
# substrings of the upper-cased issuer name so a respelling cannot drop them.
HARD_CASES = {
    "anthropic_variants": ["ANTHROPIC"],
    "opaque_spv": ["FSOIFD"],
    "ark_ec_tagged_preferred": ["OPENAI GROUP PBC SERIES C", "OPENAI GROUP PBC"],
    "spacex_10x": ["SPACE EXPLORATION", "SPACEX"],
    "world_labs_c_prime": ["WORLD LABS"],
}

PRICE_TOLERANCE = 0.005  # 0.5% -- wide enough for rounding, far short of 10x


def _views(con):
    priv = [(PARQUET / q / "private_holdings.parquet").as_posix() for q in ALL_QUARTERS]
    uni = [(PARQUET / q / "universe_holdings.parquet").as_posix() for q in ALL_QUARTERS]
    con.execute(f"CREATE VIEW p AS SELECT * FROM read_parquet([{','.join(map(repr, priv))}])")
    con.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet([{','.join(map(repr, uni))}])")


_EXACT_ALIAS_DENSE = {
    normalise_name(spelling).dense: company
    for company, spellings in ALIASES.items()
    for spelling in spellings
}


def _unimpeachable(name: str, lei) -> str | None:
    """The company this row names beyond dispute, or None.

    Two ways to be beyond dispute: a registered issuer LEI, or a name whose
    normalised key is exactly the company's own name. Neither uses the fuzzy
    scorer, which is what lets the resulting anchor be used to judge it.
    """
    if lei and len(lei.strip()) == 20 and lei.strip() in ISSUER_LEIS:
        return ISSUER_LEIS[lei.strip()]
    return _EXACT_ALIAS_DENSE.get(normalise_name(name).dense)


def _is_share_price(row) -> bool:
    """Is this row's price a per-share price at all?

    Two exclusions, both found by the anchor going wrong before this guard
    existed. Databricks' term loans are tagged LON and carry balance == value,
    so they price at exactly 1.00; with them in the anchor, every unrelated
    issuer priced at 1.00 'confirmed' as Databricks. And one Databricks row
    prices at -0.005, which made the ratio test pass for anything at all
    because the denominator was negative. An anchor is only as good as its
    instrument filter.
    """
    if row["price"] is None or row["price"] <= 0 or not row["period_end"]:
        return False
    if row["asset_cat"] is not None and row["asset_cat"] not in ASSET_CATS:
        return False
    return parse_class(row["issuer_title"], row["issuer_name"]).basis == BASIS_PER_SHARE


def anchor_series(rows) -> dict:
    """Consensus prices per (company, period_end), from unimpeachable rows."""
    anchor: dict = {}
    for row in rows:
        if not _is_share_price(row):
            continue
        company = _unimpeachable(row["issuer_name"], row["issuer_lei"])
        if not company:
            continue
        anchor.setdefault((company, row["period_end"]), set()).add(round(row["price"], 4))
    return anchor


def price_evidence(rows, anchor: dict) -> dict:
    """Which company's anchor prices does this string's own price series hit?"""
    hits: dict = {}
    priced = [r for r in rows if _is_share_price(r)]
    companies = sorted({c for c, _ in anchor})
    for row in priced:
        for company in companies:
            for anchor_price in anchor.get((company, row["period_end"]), ()):
                if abs(row["price"] - anchor_price) / anchor_price <= PRICE_TOLERANCE:
                    entry = hits.setdefault(company, {"periods": 0, "example": None})
                    entry["periods"] += 1
                    if entry["example"] is None:
                        entry["example"] = {
                            "period_end": row["period_end"],
                            "price": round(row["price"], 6),
                            "anchor_price": anchor_price,
                        }
                    break
    return {
        "rows_with_price": len(priced),
        "anchor_hits": {k: v for k, v in sorted(hits.items(), key=lambda x: -x[1]["periods"])},
    }


def describe(rows) -> dict:
    """Everything about one issuer string that a labeller needs to see."""
    prices = sorted(r["price"] for r in rows if r["price"] is not None)
    periods = sorted(r["period_end"] for r in rows if r["period_end"])
    leis = sorted({r["issuer_lei"] for r in rows if r["issuer_lei"] and len(r["issuer_lei"]) == 20})
    example = rows[0]
    return {
        "holdings": len(rows),
        "ciks": len({r["cik"] for r in rows}),
        "families": len({r["family"] for r in rows}),
        "family_names": " | ".join(sorted({r["family"] for r in rows if r["family"]}))[:200],
        "asset_cats": ",".join(sorted({r["asset_cat"] or "NULL" for r in rows})),
        "units": ",".join(sorted({r["unit"] or "NULL" for r in rows})),
        "period_first": periods[0] if periods else None,
        "period_last": periods[-1] if periods else None,
        "price_min": round(prices[0], 4) if prices else None,
        "price_median": round(prices[len(prices) // 2], 4) if prices else None,
        "price_max": round(prices[-1], 4) if prices else None,
        "leis": leis,
        "example_accession": example["accession"],
        "example_balance": example["balance"],
        "example_value": example["value"],
    }


def _select_names(con, verbose: bool) -> dict:
    """Which issuer names enter the frame, and under which strata."""
    selected: dict = {}  # upper name -> set of strata

    for name, in con.execute("SELECT DISTINCT upper(ISSUER_NAME) FROM u").fetchall():
        selected.setdefault(name, set()).add("S1_universe")

    # ---- the near-miss sweep over every distinct name in the private layer
    # ORDER BY is load-bearing, not tidiness: DuckDB's DISTINCT gives no ordering
    # guarantee, and process.extract() breaks equal scores by input position. An
    # unordered candidate list made the frame non-deterministic -- it rebuilt to
    # 322 strings instead of 323 -- and a golden set that does not rebuild
    # identically is not a fixture.
    names = [
        r[0]
        for r in con.execute(
            "SELECT DISTINCT upper(ISSUER_NAME) FROM p WHERE ISSUER_NAME IS NOT NULL ORDER BY 1"
        ).fetchall()
    ]
    near: dict = {}
    for token in NEAR_MISS_TOKENS:
        for hit, score, _ in process.extract(
            token, names, scorer=fuzz.partial_ratio, score_cutoff=NEAR_MISS_CUTOFF, limit=None
        ):
            if score > near.get(hit, (0.0, ""))[0]:
                near[hit] = (score, token)
    missed = {n: v for n, v in near.items() if like_pattern_company(n) is None}
    if verbose:
        print(f"near-miss sweep: {len(names):,} distinct names, {len(near)} score "
              f">= {NEAR_MISS_CUTOFF}, {len(missed)} of those unselected by the frozen patterns")

    volume = dict(
        con.execute(
            f"""SELECT upper(ISSUER_NAME), count(*) FROM p
                WHERE upper(ISSUER_NAME) IN ({','.join('?' * len(missed))})
                GROUP BY 1""",
            list(missed),
        ).fetchall()
    )

    # (a) the top S2_PER_TOKEN by holding volume for each near-miss token
    per_token: dict = {}
    for name, (_score, token) in missed.items():
        per_token.setdefault(token, []).append(name)
    for token in sorted(per_token):
        members = sorted(per_token[token], key=lambda n: (-volume.get(n, 0), n))
        for name in members[:S2_PER_TOKEN]:
            selected.setdefault(name, set()).add("S2_near_miss")

    # (b) every near-miss name matcher v1 claims, so no claim goes unjudged
    claimed = 0
    for name in missed:
        if resolve(name).resolved:
            selected.setdefault(name, set()).add("S2_near_miss")
            claimed += 1
    if verbose:
        print(f"  matcher v1 claims {claimed} of the {len(missed)} unselected names; "
              f"all are in the frame by rule (b)")

    # ---- S3: the plan's named hard cases, added unconditionally
    for tag, literals in HARD_CASES.items():
        for literal in literals:
            for name, in con.execute(
                "SELECT DISTINCT upper(ISSUER_NAME) FROM p WHERE upper(ISSUER_NAME) LIKE ?",
                [f"%{literal}%"],
            ).fetchall():
                selected.setdefault(name, set()).add(f"S3_{tag}")
    return selected


def build(verbose: bool = True) -> list:
    con = duckdb.connect()
    _views(con)
    selected = _select_names(con, verbose)

    # One scan for every row of every selected name. A few thousand rows, so
    # the anchor and the per-entry evidence are both computed in memory.
    fam = family_case_expr()
    raw = con.execute(
        f"""
        SELECT upper(ISSUER_NAME), upper(coalesce(ISSUER_TITLE,'')), ISSUER_LEI,
               CIK, {fam}, ASSET_CAT, UNIT, PERIOD_END, PRICE_PER_SHARE,
               ACCESSION_NUMBER, BALANCE, CURRENCY_VALUE
        FROM p WHERE upper(ISSUER_NAME) IN ({','.join('?' * len(selected))})
        """,
        list(selected),
    ).fetchall()
    rows = [
        {
            "issuer_name": r[0], "issuer_title": r[1], "issuer_lei": r[2], "cik": r[3],
            "family": r[4], "asset_cat": r[5], "unit": r[6],
            "period_end": str(r[7]) if r[7] else None,
            "price": float(r[8]) if r[8] is not None else None,
            "accession": r[9], "balance": r[10], "value": r[11],
        }
        for r in raw
    ]
    if verbose:
        print(f"{len(rows):,} holdings pulled for {len(selected)} selected names")

    anchor = anchor_series(rows)
    if verbose:
        print(f"anchor: {len(anchor)} (company, period) cells over "
              f"{len({c for c, _ in anchor})} companies, from unimpeachable rows only")

    by_pair: dict = {}
    for row in rows:
        by_pair.setdefault((row["issuer_name"], row["issuer_title"]), []).append(row)

    entries = []
    for (name, title), pair_rows in sorted(by_pair.items()):
        entries.append(
            {
                "id": f"g{len(entries) + 1:04d}",
                "issuer_name": name,
                "issuer_title": title,
                "strata": sorted(selected[name]),
                "like_pattern_says": like_pattern_company(name),
                "facts": describe(pair_rows),
                "evidence": price_evidence(pair_rows, anchor),
            }
        )

    if verbose:
        holdings = sum(e["facts"]["holdings"] for e in entries)
        print(f"\n{len(entries)} candidate issuer strings covering {holdings:,} holdings")
        for stratum in ("S1_universe", "S2_near_miss"):
            n = sum(1 for e in entries if stratum in e["strata"])
            print(f"  {stratum:26} {n:>4}")
        for tag in HARD_CASES:
            n = sum(1 for e in entries if f"S3_{tag}" in e["strata"])
            print(f"  S3_{tag:23} {n:>4}")
    return entries


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = ap.parse_args()
    entries = build()
    payload = {"generated_from": "data/parquet/*/{private,universe}_holdings.parquet",
               "quarters": ALL_QUARTERS, "entries": entries}
    if args.stdout:
        json.dump(payload, sys.stdout, indent=1)
    else:
        OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
