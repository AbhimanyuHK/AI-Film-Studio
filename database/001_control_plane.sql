-- AI Film Studio - Control Plane PostgreSQL schema
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS clients (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS films (
    film_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_films_client_id ON films(client_id);

CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL REFERENCES films(film_id) ON DELETE CASCADE,
    environment_id UUID NOT NULL,
    job_type VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_jobs_film_status ON jobs(film_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_queue ON jobs(status, scheduled_at);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome VARCHAR(16) NOT NULL,
    client_id UUID REFERENCES clients(client_id),
    film_id UUID REFERENCES films(film_id),
    environment_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_client_created ON audit_events(client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_film_created ON audit_events(film_id, created_at DESC);
