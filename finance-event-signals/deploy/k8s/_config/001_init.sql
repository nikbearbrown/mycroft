-- Week 1 schema. The verified store: one row per ingested event.
-- Later weeks add: signals, gate_decisions, signal_outcomes, accuracy_scorecard.

CREATE TABLE IF NOT EXISTS events (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_key     TEXT        NOT NULL UNIQUE,   -- dedup key: EDGAR accession no, or atom entry id
    source        TEXT        NOT NULL,          -- 'edgar_fts' | 'edgar_atom' | 'fred' | 'manual'
    form          TEXT,                          -- e.g. '8-K'
    event_type    TEXT,                          -- classified later (Week 2); NULL for now
    ticker        TEXT,
    cik           TEXT,
    company       TEXT,
    title         TEXT,
    url           TEXT,
    published_at  TIMESTAMPTZ,
    fetched_at    TIMESTAMPTZ,
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    signal_status TEXT,                          -- 'stub' in Week 1
    raw           JSONB       NOT NULL
);

CREATE INDEX IF NOT EXISTS events_source_idx       ON events (source);
CREATE INDEX IF NOT EXISTS events_published_at_idx ON events (published_at DESC);
CREATE INDEX IF NOT EXISTS events_cik_idx          ON events (cik);
