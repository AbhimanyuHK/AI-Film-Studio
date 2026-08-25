-- Initial control-plane migration.
-- Apply this to PostgreSQL before enabling the production repository adapter.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS clients (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT clients_status_chk CHECK (status IN ('active', 'suspended', 'archived'))
);

CREATE TABLE IF NOT EXISTS films (
    film_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_languages TEXT[] NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT films_status_chk CHECK (status IN ('draft', 'provisioning', 'active', 'production', 'archived', 'destroying', 'destroyed', 'failed'))
);

CREATE TABLE IF NOT EXISTS film_environments (
    environment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL UNIQUE REFERENCES films(film_id) ON DELETE RESTRICT,
    provider TEXT NOT NULL DEFAULT 'aws',
    aws_account_id TEXT NOT NULL,
    aws_region TEXT NOT NULL,
    subdomain TEXT NOT NULL UNIQUE,
    terraform_state_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'provisioning',
    runtime_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT environment_provider_chk CHECK (provider = 'aws'),
    CONSTRAINT environment_status_chk CHECK (status IN ('provisioning', 'active', 'production', 'archived', 'destroying', 'destroyed', 'failed'))
);

CREATE TABLE IF NOT EXISTS deployments (
    deployment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id UUID NOT NULL REFERENCES film_environments(environment_id) ON DELETE RESTRICT,
    version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT deployment_status_chk CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'rolled_back'))
);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(client_id),
    film_id UUID REFERENCES films(film_id),
    environment_id UUID REFERENCES film_environments(environment_id),
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT audit_outcome_chk CHECK (outcome IN ('success', 'failure', 'denied'))
);

CREATE INDEX IF NOT EXISTS idx_films_client_id ON films(client_id);
CREATE INDEX IF NOT EXISTS idx_environments_film_id ON film_environments(film_id);
CREATE INDEX IF NOT EXISTS idx_deployments_environment_id ON deployments(environment_id);
CREATE INDEX IF NOT EXISTS idx_audit_film_id ON audit_events(film_id);
