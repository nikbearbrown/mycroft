-- Table 1: User Interactions
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    response TEXT,
    topics_covered TEXT,
    knowledge_level VARCHAR(50),
    knowledge_gaps JSONB,
    prerequisites_needed JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Table 2: User Knowledge Profile
CREATE TABLE user_knowledge_profile (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    knowledge_level VARCHAR(50),
    strong_topics TEXT[],
    weak_topics JSONB,
    learning_pattern TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_timestamp ON user_interactions(timestamp);
CREATE INDEX idx_user_knowledge_profile_user_id ON user_knowledge_profile(user_id);