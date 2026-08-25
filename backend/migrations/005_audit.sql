CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome VARCHAR(16) NOT NULL,
    client_id UUID,
    film_id UUID,
    environment_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_film_created ON audit_events(film_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_client_created ON audit_events(client_id, created_at DESC);
