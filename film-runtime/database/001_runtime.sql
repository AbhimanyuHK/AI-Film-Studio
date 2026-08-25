CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS film_metadata (
  film_id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS characters (
  character_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS scenes (
  scene_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scene_number INTEGER NOT NULL,
  title TEXT,
  description TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS shots (
  shot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scene_id UUID NOT NULL REFERENCES scenes(scene_id) ON DELETE CASCADE,
  shot_number INTEGER NOT NULL,
  prompt TEXT,
  status VARCHAR(32) NOT NULL DEFAULT 'planned',
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS production_jobs (
  job_id VARCHAR(128) PRIMARY KEY,
  operation VARCHAR(128) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  result JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS film_assets (
  asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_type VARCHAR(64) NOT NULL,
  object_key TEXT NOT NULL,
  content_type VARCHAR(128),
  checksum TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
  chunk_id VARCHAR(256) PRIMARY KEY,
  source TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_chunks(source);
