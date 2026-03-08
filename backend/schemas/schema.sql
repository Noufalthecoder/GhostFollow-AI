-- PostgreSQL / Supabase schema

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    customer_name VARCHAR(120) NOT NULL,
    customer_email VARCHAR(255),
    subject VARCHAR(255),
    last_message TEXT NOT NULL,
    conversation_context TEXT NOT NULL,
    last_message_time TIMESTAMP NOT NULL,
    ghosted_status BOOLEAN NOT NULL DEFAULT FALSE,
    followup_sent BOOLEAN NOT NULL DEFAULT FALSE,
    ai_reasoning TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS followups (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    generated_message TEXT NOT NULL,
    sent_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'queued'
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER,
    step VARCHAR(120) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'info',
    details TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_ghosted_status ON conversations(ghosted_status);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_time ON conversations(last_message_time);
CREATE INDEX IF NOT EXISTS idx_followups_conversation_id ON followups(conversation_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);
