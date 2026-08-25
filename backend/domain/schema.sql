-- AI Film Studio control-plane schema
-- This database contains control metadata only. Film production content belongs
-- to the isolated film environment and must not be stored here.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE clients (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE films (
    film_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id),
    name TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_languages TEXT[] NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'provisioning', 'active', 'production', 'archived', 'destroying', 'destroyed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE film_environments (
    environment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL UNIQUE REFERENCES films(film_id),
    provider TEXT NOT NULL DEFAULT 'aws' CHECK (provider IN ('aws')),
    aws_account_id TEXT NOT NULL,
    aws_region TEXT NOT NULL,
    subdomain TEXT NOT NULL UNIQUE,
    terraform_state_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'provisioning' CHECK (status IN ('provisioning', 'active', 'production', 'archived', 'destroying', 'destroyed', 'failed')),
    runtime_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE deployments (
    deployment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id UUID NOT NULL REFERENCES film_environments(environment_id),
    version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'rolled_back')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(client_id),
    film_id UUID REFERENCES films(film_id),
    environment_id UUID REFERENCES film_environments(environment_id),
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'failure', 'denied')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_films_client_id ON films(client_id);
CREATE INDEX idx_deployments_environment_id ON deployments(environment_id);
CREATE INDEX idx_audit_events_film_id ON audit_events(film_id);
