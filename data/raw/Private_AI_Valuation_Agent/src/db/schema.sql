-- Private AI Valuation Agent -- Week 2 schema (funds, filings, raw_holdings, runs).
--
-- Follows the storage schema in plan.md, with the deviations noted below. Safe
-- to run more than once: every statement is IF NOT EXISTS, and the loader
-- upserts on the natural keys declared here.
--
-- Deviation from plan.md, logged in docs/worklog.md:
--   plan.md's raw_holdings is "one row per disclosed private position", which
--   measures at ~694,000 rows a quarter (docs/feasibility.md section 5) -- 9.7M
--   rows over 14 quarters, past what a Supabase free tier holds. So the full
--   private layer lives in data/parquet/*/private_holdings.parquet, which is
--   re-runnable and queryable with DuckDB, and raw_holdings carries the
--   universe-matched subset (~1,000/quarter) that resolution and marks consume.
--   The append-only invariant is unchanged and applies to both layers.

-- ---------------------------------------------------------------- funds ----
CREATE TABLE IF NOT EXISTS funds (
    fund_id     BIGSERIAL PRIMARY KEY,
    cik         TEXT NOT NULL,
    series_id   TEXT,
    fund_name   TEXT,
    family      TEXT,
    first_seen  DATE,
    last_seen   DATE,
    -- A fund is a series within a registrant. series_id is nullable in the
    -- source, so COALESCE to '' keeps the unique constraint usable.
    UNIQUE (cik, series_id)
);

CREATE INDEX IF NOT EXISTS funds_family_idx ON funds (family);

-- -------------------------------------------------------------- filings ----
CREATE TABLE IF NOT EXISTS filings (
    filing_id    BIGSERIAL PRIMARY KEY,
    fund_id      BIGINT REFERENCES funds (fund_id),
    accession    TEXT NOT NULL,
    form_type    TEXT,
    period_end   DATE,
    filed_date   DATE,
    net_assets   NUMERIC,
    source_url   TEXT,
    UNIQUE (accession)
);

CREATE INDEX IF NOT EXISTS filings_period_idx ON filings (period_end);
CREATE INDEX IF NOT EXISTS filings_fund_idx   ON filings (fund_id);

-- --------------------------------------------------------- raw_holdings ----
-- Immutable. Resolution never edits a row here; it writes to match_decisions
-- (Week 6). The pipeline is therefore fully re-runnable from raw, and a
-- matcher bug is always recoverable.
CREATE TABLE IF NOT EXISTS raw_holdings (
    raw_id            BIGSERIAL PRIMARY KEY,
    filing_id         BIGINT REFERENCES filings (filing_id),
    holding_id        TEXT,
    issuer_name       TEXT,
    title_of_issue    TEXT,
    cusip             TEXT,
    lei               TEXT,
    balance           NUMERIC,
    units             TEXT,
    currency          TEXT,
    value_usd         NUMERIC,
    pct_net_assets    NUMERIC,
    asset_category    TEXT,
    issuer_category   TEXT,
    is_restricted     BOOLEAN,
    fair_value_level  INT,
    -- price_per_share is stored, not derived on read, so that the arithmetic
    -- is done once at ingest under one null rule. NULL where balance is 0 or
    -- absent: a missing share count is not a zero price.
    price_per_share   NUMERIC,
    -- Provisional company label from the frozen name patterns in
    -- src/ingest/universe.py. NOT a resolution decision -- Week 5/6 supersede
    -- it and record their reasoning in match_decisions.
    company_provisional TEXT,
    is_spv            BOOLEAN,
    source_quarter    TEXT,
    ingested_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (filing_id, holding_id)
);

CREATE INDEX IF NOT EXISTS raw_company_idx ON raw_holdings (company_provisional);
CREATE INDEX IF NOT EXISTS raw_issuer_idx  ON raw_holdings (issuer_name);
CREATE INDEX IF NOT EXISTS raw_filing_idx  ON raw_holdings (filing_id);

-- ------------------------------------------------------------------ runs ----
-- One row per ingest. complete = false marks a partial run, and a partial run
-- is never the prior-period baseline for re-mark detection.
CREATE TABLE IF NOT EXISTS runs (
    run_id            BIGSERIAL PRIMARY KEY,
    started_at        TIMESTAMPTZ DEFAULT now(),
    completed_at      TIMESTAMPTZ,
    periods_ingested  TEXT[],
    rows_scanned      BIGINT,
    rows_private      BIGINT,
    rows_universe     BIGINT,
    rows_null_price   INT,
    excluded_by_cat   INT,
    spv_count         INT,
    complete          BOOLEAN DEFAULT FALSE,
    notes             TEXT
);
