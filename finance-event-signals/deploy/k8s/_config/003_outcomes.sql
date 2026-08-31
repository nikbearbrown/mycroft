-- Week 4: grading. One row per attempted grading of an actionable signal.
-- A row with correct IS NULL and grading_note set is an honest "not yet gradeable" —
-- never a guessed value (P3).

CREATE TABLE IF NOT EXISTS signal_outcomes (
    signal_id           TEXT PRIMARY KEY REFERENCES signals (signal_id),
    ticker               TEXT,
    predicted_direction  TEXT,               -- copied from signals.direction at grading time
    price_at_publish     DOUBLE PRECISION,
    price_after          DOUBLE PRECISION,
    pct_move             DOUBLE PRECISION,
    realized_direction   TEXT,               -- up | down | flat | NULL (ungradeable)
    holding_days         INT,
    priced_at_date       DATE,               -- date of the price_at_publish bar
    priced_after_date    DATE,               -- date of the price_after bar
    correct              BOOLEAN,            -- NULL = ungradeable, never a guess
    grading_note         TEXT,               -- e.g. "insufficient time elapsed", "no ticker"
    graded_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS signal_outcomes_correct_idx ON signal_outcomes (correct);
