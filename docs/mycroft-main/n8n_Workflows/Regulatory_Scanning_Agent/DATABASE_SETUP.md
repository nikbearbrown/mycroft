# Mycroft Database Setup

> PostgreSQL database schema for the Mycroft Regulatory Intelligence System

## Quick Setup

```bash
# 1. Log in to PostgreSQL
sudo -u postgres psql

# 2. Create database and user
CREATE DATABASE mycroft_intelligence;
CREATE USER mycroft_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mycroft_intelligence TO mycroft_user;
\q

# 3. Connect and create table
psql -U mycroft_user -d mycroft_intelligence -h localhost
```

## Table Schema

```sql
CREATE TABLE regulatory_feeds (
    -- Identity
    id SERIAL PRIMARY KEY,
    
    -- Source Info
    source_feed VARCHAR(255) NOT NULL,  -- Which RSS feed (e.g., "SEC Press Releases")
    source VARCHAR(255) NOT NULL,        -- Original author/creator
    
    -- Document Content
    title TEXT NOT NULL,                 -- Document title
    link TEXT NOT NULL,                  -- URL to full document
    published TIMESTAMP NOT NULL,        -- When it was published
    content TEXT,                        -- Full text content
    
    -- Analysis Scores
    urgency_score INTEGER NOT NULL CHECK (urgency_score >= 1 AND urgency_score <= 10),
    impact_level VARCHAR(20) NOT NULL CHECK (impact_level IN ('Critical', 'High', 'Medium', 'Low')),
    
    -- Categorization (Stored as JSON)
    keyword_matches JSONB DEFAULT '{}',  -- Which keywords matched: {"crypto": true, "fraud": false}
    categories JSONB DEFAULT '[]',       -- Categories: ["enforcement", "crypto"]
    
    -- Metadata
    word_count INTEGER,                  -- Document length
    has_deadline BOOLEAN DEFAULT FALSE,  -- Contains compliance deadline?
    is_enforcement BOOLEAN DEFAULT FALSE, -- Enforcement action?
    
    -- Email Tracking
    email_sent BOOLEAN DEFAULT FALSE,    -- Has alert been sent?
    email_sent_at TIMESTAMP,             -- When was alert sent?
    
    -- Timestamps
    scraped_at TIMESTAMP NOT NULL,       -- When we collected it
    created_at TIMESTAMP DEFAULT NOW(),  -- When inserted to DB
    updated_at TIMESTAMP DEFAULT NOW()   -- Last modified
);
```

## The Key Feature: Smart Deduplication

**The unique constraint that makes everything work:**

```sql
CREATE UNIQUE INDEX idx_regulatory_feeds_title_date 
ON regulatory_feeds (title, DATE(published));
```

**Why this matters:**
- Same title + same date = duplicate document
- Google News changes URLs constantly, but title+date stays the same
- PostgreSQL automatically prevents duplicates
- No complex JavaScript filtering needed

## Required Indexes

```sql
-- Deduplication (MUST HAVE)
CREATE UNIQUE INDEX idx_regulatory_feeds_title_date 
ON regulatory_feeds (title, DATE(published));

-- Performance indexes
CREATE INDEX idx_regulatory_feeds_created_at ON regulatory_feeds(created_at DESC);
CREATE INDEX idx_regulatory_feeds_urgency ON regulatory_feeds(urgency_score DESC);
CREATE INDEX idx_regulatory_feeds_email_sent ON regulatory_feeds(email_sent, created_at DESC) WHERE email_sent = FALSE;

-- JSONB indexes for fast category searches
CREATE INDEX idx_regulatory_feeds_categories ON regulatory_feeds USING GIN (categories);
CREATE INDEX idx_regulatory_feeds_keyword_matches ON regulatory_feeds USING GIN (keyword_matches);
```

## Auto-Update Trigger

```sql
-- Automatically update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_regulatory_feeds_updated_at
BEFORE UPDATE ON regulatory_feeds
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

## Field Explanations

### Why JSONB for Categories?

**Instead of this (complex):**
```sql
-- Would require 3 tables and JOINs
CREATE TABLE categories (id, name);
CREATE TABLE document_categories (doc_id, category_id);
```

**We use this (simple):**
```sql
categories JSONB  -- Store ["enforcement", "crypto", "securities"]
```

**Benefits:**
- One table, no JOINs needed
- Add new categories without schema changes
- Fast queries with GIN indexes
- Flexible structure

**Query examples:**
```sql
-- Find documents with 'crypto' category
SELECT * FROM regulatory_feeds WHERE categories @> '["crypto"]';

-- Find documents with crypto OR enforcement
SELECT * FROM regulatory_feeds WHERE categories ?| ARRAY['crypto', 'enforcement'];
```

### Why Timestamp Without Timezone?

```sql
published TIMESTAMP WITHOUT TIME ZONE
```

All RSS feeds report in UTC/GMT, so we don't need timezone complexity. Makes date math simpler:

```sql
-- Last 7 days
SELECT * FROM regulatory_feeds WHERE published > NOW() - INTERVAL '7 days';

-- Group by date
SELECT DATE(published), COUNT(*) FROM regulatory_feeds GROUP BY DATE(published);
```

### Why Check Constraints?

```sql
urgency_score INTEGER CHECK (urgency_score >= 1 AND urgency_score <= 10)
impact_level VARCHAR(20) CHECK (impact_level IN ('Critical', 'High', 'Medium', 'Low'))
```

**Database rejects invalid data automatically:**
- Can't insert urgency_score = 15 (rejected)
- Can't insert impact_level = "Super High" (rejected)
- No need for application-level validation

## Using with n8n

**In your INSERT query, use:**

```sql
INSERT INTO regulatory_feeds (
  source_feed, source, title, link, published, content,
  urgency_score, impact_level, keyword_matches, categories,
  word_count, has_deadline, is_enforcement, scraped_at
) VALUES (
  '{{ $json.source_feed }}',
  '{{ $json.source }}',
  '{{ $json.title }}',
  '{{ $json.link }}',
  '{{ $json.published }}',
  '{{ $json.content }}',
  {{ $json.urgency_score }},
  '{{ $json.impact_level }}',
  '{{ $json.keyword_matches_str }}'::jsonb,
  '{{ $json.categories_str }}'::jsonb,
  {{ $json.word_count }},
  {{ $json.has_deadline }},
  {{ $json.is_enforcement }},
  '{{ $json.scraped_at }}'
)
ON CONFLICT (title, DATE(published)) DO NOTHING
RETURNING *;
```

**The magic part:** `ON CONFLICT DO NOTHING RETURNING *`
- Tries to insert
- If duplicate (same title+date), skips it
- Returns ONLY successfully inserted rows
- Zero JavaScript filtering needed!

## Common Queries

```sql
-- Get today's high priority items
SELECT * FROM regulatory_feeds
WHERE created_at >= CURRENT_DATE
  AND urgency_score > 7
ORDER BY urgency_score DESC;

-- Find crypto enforcement actions
SELECT * FROM regulatory_feeds
WHERE categories @> '["crypto"]'
  AND is_enforcement = TRUE;

-- Unsent email alerts
SELECT * FROM regulatory_feeds
WHERE email_sent = FALSE
  AND urgency_score > 7
  AND created_at >= NOW() - INTERVAL '1 day';
```

## Backup

```bash
# Backup
pg_dump -U mycroft_user -d mycroft_intelligence -F c -f "backup.dump"

# Restore
pg_restore -U mycroft_user -d mycroft_intelligence -v "backup.dump"
```

## Troubleshooting

**"Duplicate key violation" error:**
- This is GOOD - it means duplicates are being prevented
- Make sure your n8n query uses `ON CONFLICT DO NOTHING`

**Can't connect:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Reset password
sudo -u postgres psql
ALTER USER mycroft_user WITH PASSWORD 'new_password';
```

**Slow queries:**
```sql
-- Check if indexes exist
\di

-- Rebuild indexes
REINDEX TABLE regulatory_feeds;
```

---

**Database Version:** PostgreSQL 12+  
**Author:** Darshan Rajopadhye  
**Contact:** rajopadhye.d@northeastern.edu