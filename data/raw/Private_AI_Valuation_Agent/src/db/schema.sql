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

-- ================================================================ WEEK 6 ====
-- Resolution graph and human review queue.
--
-- Deviation from plan.md, logged in docs/worklog.md and logs/RUN_LOG.md:
--   plan.md gives match_decisions "unique (raw_id)" AND says decisions are
--   "keyed so the same ambiguity is never presented twice". Those two cannot
--   both hold in one table. The 5,806 universe holdings are only 231 distinct
--   (issuer_name, title_of_issue) pairs, so a queue keyed by raw_id would ask
--   the same question up to 85 times -- the Databricks spelling count.
--   Resolution: match_decisions keeps unique (raw_id) exactly as specified and
--   is the per-holding audit trail; review_decisions is keyed by the ambiguity
--   and is what the queue reads before it interrupts a human. One human answer
--   fans out to every holding that shares its key.

-- ------------------------------------------------------------- companies ----
-- The canonical layer. Seeded from universe_v1.json (frozen, Week 1) plus the
-- watchlist names the adjudicator is allowed to return. universe_version is
-- carried so a later v2 boundary is visible as a discontinuity, not a silent
-- edit.
CREATE TABLE IF NOT EXISTS companies (
    company_id       BIGSERIAL PRIMARY KEY,
    canonical_name   TEXT NOT NULL,
    status           TEXT,          -- full | thin | watchlist
    lei              TEXT,
    universe_version INT,
    notes            TEXT,
    UNIQUE (canonical_name)
);

-- ------------------------------------------------------------ securities ----
-- Week 7 populates this from adjudicated share classes. Created now because
-- match_decisions.security_id references it and plan.md declares it nullable.
CREATE TABLE IF NOT EXISTS securities (
    security_id      BIGSERIAL PRIMARY KEY,
    company_id       BIGINT REFERENCES companies (company_id),
    share_class_raw  TEXT,
    class_normalized TEXT,
    filer_grammar    TEXT,
    is_spv           BOOLEAN,
    spv_opaque       BOOLEAN,
    notes            TEXT,
    UNIQUE (company_id, class_normalized, share_class_raw)
);

-- ------------------------------------------------------ review_decisions ----
-- One row per ambiguity, not per holding. decision_key is the case- and
-- whitespace-normalised (issuer_name || title_of_issue) pair, stored as
-- readable text rather than a hash so a human can audit it in place (P5).
--
-- verdict is what was decided, company_id is what it was decided to be:
--   company        -> this ambiguity is that company
--   not_in_universe-> deliberately not one of ours
--   unresolved     -> the reviewer could not tell; stays in the queue report,
--                     never silently dropped
CREATE TABLE IF NOT EXISTS review_decisions (
    decision_key     TEXT PRIMARY KEY,
    issuer_name      TEXT NOT NULL,
    title_of_issue   TEXT,
    verdict          TEXT NOT NULL,
    company_id       BIGINT REFERENCES companies (company_id),
    class_normalized TEXT,
    trigger          TEXT,          -- why it reached a human
    reviewer         TEXT NOT NULL, -- a name. "auto" is not a reviewer.
    rationale        TEXT NOT NULL,
    holdings_covered INT,
    thread_id        TEXT,
    decided_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS review_verdict_idx ON review_decisions (verdict);

-- ------------------------------------------------------- match_decisions ----
-- The audit trail: exactly one row per resolved holding, per plan.md.
-- method records who decided, and 'human' rows carry the reviewer's name.
CREATE TABLE IF NOT EXISTS match_decisions (
    decision_id   BIGSERIAL PRIMARY KEY,
    raw_id        BIGINT REFERENCES raw_holdings (raw_id),
    security_id   BIGINT REFERENCES securities (security_id),
    company_id    BIGINT REFERENCES companies (company_id),
    method        TEXT NOT NULL,   -- lei | alias | spv | fuzzy | llm | human | reused | rejected
    confidence    NUMERIC,
    model         TEXT,
    reviewer      TEXT,
    rationale     TEXT,
    -- The grouping identity of the question, NOT a reference to
    -- review_decisions. An auto-accepted holding has a decision_key and no
    -- human decision, so a foreign key here rejects exactly the rows that
    -- never needed a reviewer. Only the human answers live in
    -- review_decisions, and match_decisions.method = 'human' | 'reused' is
    -- what says one was consulted.
    decision_key  TEXT,
    trigger       TEXT,
    run_id        BIGINT REFERENCES runs (run_id),
    decided_at    TIMESTAMPTZ DEFAULT now(),
    UNIQUE (raw_id)
);

CREATE INDEX IF NOT EXISTS match_method_idx  ON match_decisions (method);
CREATE INDEX IF NOT EXISTS match_company_idx ON match_decisions (company_id);
CREATE INDEX IF NOT EXISTS match_key_idx     ON match_decisions (decision_key);

-- ================================================================ WEEK 7 ====
-- The marks panel and the split detector.

-- ----------------------------------------------------------------- marks ----
-- One row per (security, fund, period end). plan.md's columns, plus six that
-- the data forced and that are logged as deviations in docs/marks_panel.md:
--
--   asset_category  part of the line-group identity, not decoration. Within a
--                   single filing, SpaceX common and preferred arrive under the
--                   *same* issuer name and title, ten times apart; EC/EP is the
--                   only thing separating them.
--   lines           how many raw holding lines were aggregated into this mark.
--                   A fund reporting one security across several lots is normal
--                   and must be summed, not deduplicated.
--   is_blended      the lines disagreed on price beyond rounding. No price is
--                   published for a blended mark: plan.md's rule is that a
--                   price spanning two classes "belongs to neither".
--   price_min/max   what the disagreeing lines actually said, so the exception
--                   is auditable instead of just suppressed.
--   currency        everything is USD today (5,806 of 5,806). Recorded so the
--                   guard is visible rather than assumed.
--   change_blocked  the quarantine, stated rather than implied by two other
--                   columns. A blocked mark never enters a change series.
CREATE TABLE IF NOT EXISTS marks (
    mark_id                BIGSERIAL PRIMARY KEY,
    security_id            BIGINT REFERENCES securities (security_id),
    company_id             BIGINT REFERENCES companies (company_id),
    fund_id                BIGINT REFERENCES funds (fund_id),
    filing_id              BIGINT REFERENCES filings (filing_id),
    period_end             DATE NOT NULL,
    asset_category         TEXT,
    currency               TEXT,
    lines                  INT,
    balance                NUMERIC,
    value_usd              NUMERIC,
    price_per_share        NUMERIC,
    is_blended             BOOLEAN DEFAULT FALSE,
    price_min              NUMERIC,
    price_max              NUMERIC,
    is_spv                 BOOLEAN DEFAULT FALSE,
    spv_opaque             BOOLEAN DEFAULT FALSE,
    -- re-mark detection
    prior_period_end       DATE,
    prior_price_per_share  NUMERIC,
    is_remark              BOOLEAN,
    -- split detection: suspected by machine, adjudicated only by a human
    split_suspected        BOOLEAN DEFAULT FALSE,
    split_ratio            NUMERIC,
    split_reason           TEXT,
    split_adjudicated      BOOLEAN DEFAULT FALSE,
    split_adjudication     TEXT,
    -- the quarantine
    change_blocked         BOOLEAN DEFAULT FALSE,
    block_reason           TEXT,
    confidence             NUMERIC,
    run_id                 BIGINT REFERENCES runs (run_id),
    built_at               TIMESTAMPTZ DEFAULT now(),
    UNIQUE (security_id, fund_id, period_end)
);

CREATE INDEX IF NOT EXISTS marks_company_idx ON marks (company_id, period_end);
CREATE INDEX IF NOT EXISTS marks_period_idx  ON marks (period_end);
CREATE INDEX IF NOT EXISTS marks_split_idx   ON marks (split_suspected)
    WHERE split_suspected;
CREATE INDEX IF NOT EXISTS marks_blocked_idx ON marks (change_blocked)
    WHERE change_blocked;

-- securities gains the price basis. The share-class parser already decides
-- whether a title describes a share at all -- `CVT INT RIGHTS` and `EV UNITS`
-- price per dollar or per vehicle unit, not per share -- and a marks panel that
-- forgets that publishes $1.00 as a price.
ALTER TABLE securities ADD COLUMN IF NOT EXISTS price_basis TEXT;
ALTER TABLE securities ADD COLUMN IF NOT EXISTS asset_category TEXT;
ALTER TABLE securities ADD COLUMN IF NOT EXISTS first_seen DATE;
ALTER TABLE securities ADD COLUMN IF NOT EXISTS last_seen DATE;

-- How a filed line finds its security. Three Databricks titles say "Series F"
-- (preferred by title) and are filed as EC by some managers and EP by others:
-- one security, two category tags. Keying securities on the category would
-- split it in two; ignoring the category would merge SpaceX common with SpaceX
-- preferred, which arrive under an identical title. So identity stays on
-- (company, title, class) and the category is carried in this lookup.
CREATE TABLE IF NOT EXISTS security_map (
    company_id      BIGINT NOT NULL REFERENCES companies (company_id),
    share_class_raw TEXT NOT NULL,
    asset_category  TEXT NOT NULL,   -- '' where the filer gave none
    security_id     BIGINT NOT NULL REFERENCES securities (security_id),
    PRIMARY KEY (company_id, share_class_raw, asset_category)
);

-- A security whose series contains an unadjudicated suspected split somewhere.
-- Distinct from change_blocked, deliberately. plan.md's invariant is per mark:
-- "A mark with split_suspected = true and split_adjudicated = false never
-- enters a change calculation." Blocking the whole series instead would have
-- quarantined 90 further marks -- ARK's entire Anthropic series among them --
-- for a break that a change between two other periods never crosses. The flag
-- warns; only the step itself is blocked.
ALTER TABLE marks ADD COLUMN IF NOT EXISTS series_flagged BOOLEAN DEFAULT FALSE;

-- The factor a human says to divide by, which is NOT the ratio the detector
-- measured. ARK's Perplexity step has a ratio of 11.93 because a 10:1 split
-- and a 16% markdown happened in the same period: shares went 6,081 -> 60,810
-- while value fell from 4,226,522.43 to 3,542,758.43. Week 8 must adjust by
-- **10** and leave the markdown alone. Adjusting by 11.93 would erase a real
-- price move, which is the mirror image of the mistake the detector exists to
-- prevent.
ALTER TABLE marks ADD COLUMN IF NOT EXISTS split_factor NUMERIC;

-- ================================================================ WEEK 8 ====
-- The separate lane for the event study: universe-company holdings at a fair
-- value level OTHER than 3.
--
-- Deliberately not part of raw_holdings. That table is the Level 3 private
-- layer, 5,806 rows reconcile against it through match_decisions and marks,
-- and widening its filter would silently redefine the re-mark rate, the
-- dispersion and the panel. Nothing downstream of raw_holdings reads this.
--
-- Empty today, and that is the finding: every universe-company row in the
-- fourteen quarters on disk is Level 3. Cerebras went public after the
-- archive's last period end (2026-04-30), so its Level 1 marks are in 2026Q3,
-- which the SEC has not published.
CREATE TABLE IF NOT EXISTS public_observations (
    observation_id      BIGSERIAL PRIMARY KEY,
    source_quarter      TEXT,
    accession           TEXT NOT NULL,
    period_end          TEXT,          -- as filed, e.g. '29-MAY-2026'
    registrant          TEXT,
    issuer_name         TEXT NOT NULL,
    title_of_issue      TEXT,
    cusip               TEXT,
    fair_value_level    TEXT NOT NULL,
    is_restricted       TEXT,
    asset_category      TEXT,
    currency            TEXT,
    balance             NUMERIC,
    value_usd           NUMERIC,
    price_per_share     NUMERIC,
    company_provisional TEXT,
    ingested_at         TIMESTAMPTZ DEFAULT now(),
    UNIQUE (accession, issuer_name, title_of_issue, fair_value_level, balance)
);

CREATE INDEX IF NOT EXISTS public_obs_company_idx
    ON public_observations (company_provisional, fair_value_level);
