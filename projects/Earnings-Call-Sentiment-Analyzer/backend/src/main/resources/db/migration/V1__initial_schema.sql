CREATE TABLE transcripts (
    id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    quarter VARCHAR(20) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE analysis_jobs (
    id BIGSERIAL PRIMARY KEY,
    transcript_id BIGINT NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    message VARCHAR(500),
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analysis_jobs_transcript_id ON analysis_jobs(transcript_id);
CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);

CREATE TABLE transcript_chunks (
    id BIGSERIAL PRIMARY KEY,
    transcript_id BIGINT NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    section_name VARCHAR(50) NOT NULL,
    speaker_name VARCHAR(200),
    speaker_role VARCHAR(50) NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_order INTEGER NOT NULL
);

CREATE INDEX idx_transcript_chunks_transcript_id ON transcript_chunks(transcript_id);
CREATE UNIQUE INDEX uq_transcript_chunk_order ON transcript_chunks(transcript_id, chunk_order);

CREATE TABLE sentiment_results (
    id BIGSERIAL PRIMARY KEY,
    chunk_id BIGINT NOT NULL UNIQUE REFERENCES transcript_chunks(id) ON DELETE CASCADE,
    label VARCHAR(30) NOT NULL,
    positive_score DOUBLE PRECISION NOT NULL,
    neutral_score DOUBLE PRECISION NOT NULL,
    negative_score DOUBLE PRECISION NOT NULL,
    final_score DOUBLE PRECISION NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sentiment_summaries (
    id BIGSERIAL PRIMARY KEY,
    transcript_id BIGINT NOT NULL UNIQUE REFERENCES transcripts(id) ON DELETE CASCADE,
    overall_label VARCHAR(30) NOT NULL,
    overall_score DOUBLE PRECISION NOT NULL,
    prepared_remarks_score DOUBLE PRECISION,
    qa_score DOUBLE PRECISION,
    management_score DOUBLE PRECISION,
    analyst_score DOUBLE PRECISION,
    positive_chunk_count INTEGER NOT NULL,
    neutral_chunk_count INTEGER NOT NULL,
    negative_chunk_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
