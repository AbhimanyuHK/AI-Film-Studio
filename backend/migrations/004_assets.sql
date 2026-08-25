CREATE TABLE IF NOT EXISTS assets (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL REFERENCES films(film_id) ON DELETE RESTRICT,
    environment_id UUID NOT NULL REFERENCES film_environments(environment_id) ON DELETE RESTRICT,
    object_key TEXT NOT NULL,
    asset_type VARCHAR(64) NOT NULL,
    content_type VARCHAR(255) NOT NULL,
    size_bytes BIGINT,
    checksum VARCHAR(128),
    version INTEGER NOT NULL DEFAULT 1,
    metadata JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_asset_film_object_key UNIQUE (film_id, object_key)
);
CREATE INDEX IF NOT EXISTS idx_assets_film_type ON assets(film_id, asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_environment ON assets(environment_id);
