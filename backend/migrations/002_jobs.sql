CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL REFERENCES films(film_id) ON DELETE RESTRICT,
    environment_id UUID NOT NULL REFERENCES film_environments(environment_id) ON DELETE RESTRICT,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    payload JSONB NOT NULL DEFAULT '{}',
    result JSONB,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT jobs_status_chk CHECK (status IN ('queued','running','succeeded','failed','cancelled','retrying')),
    CONSTRAINT jobs_attempts_chk CHECK (attempts >= 0 AND max_attempts > 0 AND attempts <= max_attempts)
);

CREATE INDEX IF NOT EXISTS idx_jobs_film_status ON jobs(film_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_environment_status ON jobs(environment_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_queue ON jobs(status, scheduled_at);
