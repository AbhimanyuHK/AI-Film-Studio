-- AI Film Studio - production integrity and worker coordination
-- PostgreSQL control-plane hardening migration.

ALTER TABLE jobs
    ADD COLUMN IF NOT EXISTS worker_id TEXT,
    ADD COLUMN IF NOT EXISTS lease_until TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS idempotency_key TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS uq_jobs_idempotency
    ON jobs(film_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_jobs_claimable
    ON jobs(status, scheduled_at, lease_until);

CREATE INDEX IF NOT EXISTS idx_jobs_worker_lease
    ON jobs(worker_id, lease_until)
    WHERE worker_id IS NOT NULL;

ALTER TABLE jobs
    DROP CONSTRAINT IF EXISTS jobs_status_check;
ALTER TABLE jobs
    ADD CONSTRAINT jobs_status_check
    CHECK (status IN ('queued','running','retrying','completed','failed','cancelled'));

ALTER TABLE clients
    DROP CONSTRAINT IF EXISTS clients_status_check;
ALTER TABLE clients
    ADD CONSTRAINT clients_status_check
    CHECK (status IN ('active','suspended','archived'));

ALTER TABLE films
    DROP CONSTRAINT IF EXISTS films_status_check;
ALTER TABLE films
    ADD CONSTRAINT films_status_check
    CHECK (status IN ('draft','active','completed','archived'));

CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_clients_updated_at ON clients;
CREATE TRIGGER trg_clients_updated_at
BEFORE UPDATE ON clients
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_films_updated_at ON films;
CREATE TRIGGER trg_films_updated_at
BEFORE UPDATE ON films
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_jobs_updated_at ON jobs;
CREATE TRIGGER trg_jobs_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- Transactional worker claim pattern:
-- SELECT job rows FOR UPDATE SKIP LOCKED, then set worker_id/lease_until/status atomically.
