-- Week 2: the signal model + the human gate.

ALTER TABLE events ADD COLUMN IF NOT EXISTS ticker TEXT;
CREATE INDEX IF NOT EXISTS events_ticker_idx ON events (ticker);

-- One row per material-event read. A withheld read is still a row
-- (status='withheld') so the review queue shows the agent looked and declined.
CREATE TABLE IF NOT EXISTS signals (
    signal_id       TEXT PRIMARY KEY,          -- deterministic: 'sig_' || event_key  (idempotent)
    event_key       TEXT NOT NULL UNIQUE REFERENCES events (event_key),
    status          TEXT NOT NULL,             -- pending_review | withheld | actionable | rejected
    event_type      TEXT,
    direction       TEXT,                      -- up | down | unclear | NULL
    magnitude       TEXT,                      -- small | medium | large | NULL
    confidence      DOUBLE PRECISION,
    rationale       TEXT,
    withheld_reason TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS signals_status_idx ON signals (status);

-- The phase gate. One decision per signal (Week 2). Nothing reaches
-- events.actionable without a row here.
CREATE TABLE IF NOT EXISTS gate_decisions (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    signal_id  TEXT NOT NULL UNIQUE REFERENCES signals (signal_id),
    reviewer   TEXT NOT NULL,
    verdict    TEXT NOT NULL,                  -- actionable | reject
    note       TEXT,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Reviewer-facing view: the signal plus its event context.
CREATE OR REPLACE VIEW signal_review AS
SELECT s.signal_id, s.status, s.event_type, s.direction, s.magnitude, s.confidence,
       s.rationale, s.withheld_reason, s.created_at,
       e.event_key, e.ticker, e.company, e.title, e.url, e.published_at, e.form,
       g.reviewer, g.verdict, g.note, g.decided_at
FROM signals s
JOIN events e ON e.event_key = s.event_key
LEFT JOIN gate_decisions g ON g.signal_id = s.signal_id;
