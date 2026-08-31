-- scripts/init_db.sql
-- Agentic AML Compliance Workflow — Database Initialization
--
-- Run automatically by docker-compose.yml on first startup.
-- To run manually:
--   psql $DATABASE_URL -f scripts/init_db.sql
--
-- Creates four tables:
--   audit_log          — append-only workflow audit record
--   human_review_queue — pending compliance officer reviews
--   escalation_queue   — pending senior compliance officer reviews
--   sar_assessments    — SAR assessment records for BSA Officer

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ─────────────────────────────────────────────────────────────
-- AUDIT LOG
-- Append-only. No UPDATE or DELETE allowed.
-- Cryptographic hash stored at workflow close (seal).
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS audit_log (
    id             BIGSERIAL       NOT NULL,
    trade_id       UUID            NOT NULL,
    event_type     VARCHAR(100)    NOT NULL,
    content        JSONB           NOT NULL,
    created_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_audit_log_trade_id
    ON audit_log (trade_id, created_at);

-- Row-level security: INSERT only, no UPDATE or DELETE
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_log_insert_only
    ON audit_log
    FOR INSERT
    WITH CHECK (true);

-- Revoke UPDATE and DELETE from the application role
-- [DEV] Replace 'pipeline' with your database application role name
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pipeline') THEN
        REVOKE UPDATE, DELETE ON audit_log FROM pipeline;
    END IF;
END
$$;

-- Cryptographic seals (one row per completed workflow)
CREATE TABLE IF NOT EXISTS audit_log_seals (
    trade_id       UUID            PRIMARY KEY,
    record_hash    VARCHAR(64)     NOT NULL,   -- SHA-256 hex digest
    sealed_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────
-- HUMAN REVIEW QUEUE
-- Stores pending exception reports waiting for compliance officer review.
-- Must be durable: survives process restarts.
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS human_review_queue (
    id             UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_id       UUID            NOT NULL,
    report         TEXT            NOT NULL,       -- The formatted exception report
    status         VARCHAR(50)     NOT NULL DEFAULT 'PENDING',
    -- Status values: PENDING → IN_REVIEW → RESOLVED
    created_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Decision fields (populated when officer submits)
    approved       BOOLEAN,
    officer_id     VARCHAR(100),
    rationale      TEXT,
    action         VARCHAR(50),    -- "escalate" or "reject" when approved=false
    decided_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_human_review_queue_trade_id
    ON human_review_queue (trade_id);

CREATE INDEX IF NOT EXISTS idx_human_review_queue_status
    ON human_review_queue (status, created_at);


-- ─────────────────────────────────────────────────────────────
-- ESCALATION QUEUE
-- Stores trades escalated from the autonomous pipeline or by a
-- compliance officer decision. Routes to senior compliance teams.
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS escalation_queue (
    id             UUID            PRIMARY KEY,   -- EscalationPackage.escalation_id
    trade_id       UUID            NOT NULL,
    package        JSONB           NOT NULL,      -- Full EscalationPackage JSON
    status         VARCHAR(50)     NOT NULL DEFAULT 'PENDING',
    -- Status values: PENDING → IN_REVIEW → RESOLVED
    assigned_team  VARCHAR(100),
    priority       VARCHAR(20),    -- LOW / MEDIUM / HIGH / CRITICAL
    created_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Decision fields (populated when senior officer submits)
    outcome        VARCHAR(50),    -- APPROVED / BLOCKED / ESCALATE_FURTHER
    officer_id     VARCHAR(100),
    rationale      TEXT,
    decided_at     TIMESTAMPTZ,

    -- For ESCALATE_FURTHER: links to the next escalation record
    further_escalation_id UUID
);

CREATE INDEX IF NOT EXISTS idx_escalation_queue_trade_id
    ON escalation_queue (trade_id);

CREATE INDEX IF NOT EXISTS idx_escalation_queue_status_team
    ON escalation_queue (status, assigned_team, priority, created_at);


-- ─────────────────────────────────────────────────────────────
-- SAR ASSESSMENTS
-- Records created when a trade is blocked and the BSA Officer must
-- evaluate whether a SAR filing is warranted.
-- This system creates the assessment — it never files the SAR.
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sar_assessments (
    id                  UUID            PRIMARY KEY,   -- SARAssessment.assessment_id
    trade_id            UUID            NOT NULL,
    counterparty_lei    VARCHAR(20)     NOT NULL,
    counterparty_name   TEXT            NOT NULL,
    flag_type           VARCHAR(100)    NOT NULL,
    trade_value_usd     TEXT            NOT NULL,
    block_reason        TEXT            NOT NULL,
    agent_outputs       JSONB           NOT NULL,
    escalation_source   VARCHAR(100),
    status              VARCHAR(50)     NOT NULL DEFAULT 'PENDING_BSO_REVIEW',
    -- Status values: PENDING_BSO_REVIEW → UNDER_REVIEW → SAR_FILED / NO_SAR_REQUIRED / ESCALATED_TO_LEGAL
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sar_assessments_trade_id
    ON sar_assessments (trade_id);

CREATE INDEX IF NOT EXISTS idx_sar_assessments_status
    ON sar_assessments (status, created_at);

CREATE INDEX IF NOT EXISTS idx_sar_assessments_lei
    ON sar_assessments (counterparty_lei);
