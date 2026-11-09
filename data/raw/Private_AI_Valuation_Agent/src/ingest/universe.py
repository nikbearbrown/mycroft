"""Universe v1 name patterns and the private-position filter, in one place.

`universe_v1.json` is the frozen human record of *which companies* are in scope.
This module is the machine half: *how a row is recognised as one of them*, and
which rows are private positions at all. Both halves are versioned together --
changing a pattern here is a universe change and needs a new version boundary.

Three things are settled here, each measured against 2026Q2 rather than assumed:

  1. The filter is `FAIR_VALUE_LEVEL = '3'`, not the three-field AND in plan.md.
     docs/feasibility.md section 2: the plan's filter drops 5 of 6 managers,
     because filers use '000000000' as well as 'N/A' for a missing CUSIP and
     ARK and Capital Group report `IS_RESTRICTED_SECURITY = N` on restricted
     stock. Level 3 was the only field constant across all 19 verified rows.

  2. Name-match first, Level-3 confirm second. docs/feasibility.md section 5:
     filtering to private positions first yields ~694,000 rows a quarter, not
     the "few thousand" plan.md predicts, because 'N/A' is the generic no-CUSIP
     placeholder used by bonds, derivatives and cash. Matching the universe by
     name first cuts entity resolution's input to ~1,000 rows a quarter.

  3. Asset category is an allow-list, not a deny-list -- see ASSET_CATS below.
"""

# --------------------------------------------------------------------------
# Issuer-name patterns (SQL LIKE, matched against upper(ISSUER_NAME))
#
# Multiple patterns per company because filers spell the same issuer several
# ways. Every pattern below was checked against 2026Q2 for both what it catches
# and what it wrongly catches; the counts are in docs/worklog.md.
# --------------------------------------------------------------------------

UNIVERSE_PATTERNS = {
    # --- full members: marks, dispersion and propagation all published -----
    "Databricks, Inc.": ["%DATABRICKS%"],
    "Space Exploration Technologies Corp.": [
        "%SPACE EXPLORATION%",
        # 'SPACEX-CL A PP' and 'U First Capital Fund III LLC (SpaceX)' carry no
        # spelled-out name; %SPACE EXPLORATION% alone misses 5 rows in 2026Q2.
        "%SPACEX%",
    ],
    "Anthropic PBC": ["%ANTHROPIC%"],
    "OpenAI Group PBC": [
        "%OPENAI%",
        # BlackRock writes 'Open AI Group PBC' with a space. %OPENAI% alone
        # misses 7 rows in 2026Q2, five of them a whole manager's position.
        "%OPEN AI%",
    ],
    "Anduril Industries, Inc.": ["%ANDURIL%"],
    "Cerebras Systems Inc.": ["%CEREBRAS%"],
    # --- carried thin: marks published, dispersion/propagation suppressed --
    "Figure AI Inc.": [
        # NOT %FIGURE% -- 'Figure Technologies' is a fintech with 243 rows in
        # 2026Q2 and zero at Level 3. Different company, similar name.
        "%FIGURE AI%",
    ],
}

THIN_COVERAGE = {"Figure AI Inc."}

# Excluded from universe v1 but captured in the Parquet layer anyway, so that a
# v2 revisit never needs a re-download. Reasons are in universe_v1.json.
WATCHLIST_PATTERNS = {
    "X.AI Corp": ["%X.AI%"],
    "Perplexity AI, Inc.": ["%PERPLEXITY%"],
    "Groq, Inc.": ["%GROQ%"],
    "Scale AI, Inc.": ["%SCALE AI%"],
    # Kept deliberately as a live false-positive check, not as a candidate:
    # every %COHERE% row is Coherent Corp (public optics) or Cohere
    # Technologies (wireless), never Cohere Inc. the model company.
    "Cohere Inc. [FALSE POSITIVE]": ["%COHERE%"],
}

# --------------------------------------------------------------------------
# Asset categories
#
# An allow-list, because the deny-list is open-ended and a missed debt category
# silently corrupts a price series. Verified on 2026Q2 universe Level-3 rows:
#
#   EP     533   preferred -- the bulk of real marks
#   EC     337   common
#   OTHER   31   real marks too: 'ANTHROPIC' 964,742 sh / $249,999,768.80 =
#                $259.1364, the same price six managers agree on. Also where
#                the transparent SPVs live. Dropping OTHER would lose real data.
#   LON     10   Databricks term loans and delayed draws -- balance equals
#                value, so price_per_share would be ~1.00 and meaningless.
#   STIV     6   short-term investment vehicles, not equity.
#
# NULL is allowed through: the field is nullable and a null category is not
# evidence of debt. Rows excluded here are counted in the reconciliation rather
# than dropped silently.
# --------------------------------------------------------------------------

ASSET_CATS = ("EC", "EP", "OTHER")

# --------------------------------------------------------------------------
# SQL fragments
# --------------------------------------------------------------------------

PRIVATE_FILTER = "FAIR_VALUE_LEVEL = '3'"

# The wider net written to the Parquet layer: every Level 3 row that also looks
# like it lacks a real CUSIP or is flagged restricted. Broader than the universe
# on purpose -- it is the re-runnable raw layer, and a universe v2 has to be
# answerable from it without re-downloading 6 GB.
PARQUET_NET = f"""
    {PRIVATE_FILTER}
    AND (ISSUER_CUSIP IN ('N/A', '000000000', '0', '')
         OR ISSUER_CUSIP IS NULL
         OR IS_RESTRICTED_SECURITY = 'Y')
"""

# Recognises SPV wrappers: ARK's 'U First Capital Fund III LLC (SpaceX)',
# T. Rowe's 'AESTAS LLC dba OPENAI LLC', and the '(invested in ...)' /
# '(economic exposure to ...)' forms. Transparent SPVs still resolve to the
# underlying company; opaque ones (Fidelity's FSOIFD*) never match a pattern
# at all and so never reach here.
SPV_EXPR = """
    (upper(ISSUER_NAME) LIKE '%(INVESTED IN %'
     OR upper(ISSUER_NAME) LIKE '%(ECONOMIC EXPOSURE%'
     OR upper(ISSUER_NAME) LIKE '% LLC (%'
     OR upper(ISSUER_NAME) LIKE '% LP (%'
     OR upper(ISSUER_NAME) LIKE '% DBA %')
"""


def _like_clause(patterns, column="upper(ISSUER_NAME)"):
    return "(" + " OR ".join(f"{column} LIKE '{p}'" for p in patterns) + ")"


def company_case_expr(column="upper(ISSUER_NAME)"):
    """A CASE expression mapping an issuer name to its canonical company.

    First match wins, so pattern order matters within a company but not
    between them -- the patterns are disjoint across companies by construction.
    """
    arms = []
    for canonical, patterns in UNIVERSE_PATTERNS.items():
        arms.append(f"WHEN {_like_clause(patterns, column)} THEN '{canonical}'")
    for canonical, patterns in WATCHLIST_PATTERNS.items():
        arms.append(f"WHEN {_like_clause(patterns, column)} THEN '{canonical}'")
    return "CASE " + " ".join(arms) + " ELSE NULL END"


def universe_match_expr(column="upper(ISSUER_NAME)", include_watchlist=False):
    """Boolean SQL: does this row's issuer name belong to the universe?"""
    groups = dict(UNIVERSE_PATTERNS)
    if include_watchlist:
        groups.update(WATCHLIST_PATTERNS)
    every = [p for patterns in groups.values() for p in patterns]
    return _like_clause(every, column)


def status_of(canonical_name):
    """'full', 'thin', or 'watchlist' -- what may be published for a company."""
    if canonical_name in THIN_COVERAGE:
        return "thin"
    if canonical_name in UNIVERSE_PATTERNS:
        return "full"
    return "watchlist"
