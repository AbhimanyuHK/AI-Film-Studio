-- AI Film Studio - environments, deployments and job dependency graph
-- Applies after 001_control_plane.sql and 003_integrity_and_worker.sql.

ALTER TABLE films
    ADD COLUMN IF NOT EXISTS source_language VARCHAR(20) NOT NULL DEFAULT 'en',
    ADD COLUMN IF NOT EXISTS target_languages JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE TABLE IF NOT EXISTS film_environments (
    environment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL UNIQUE REFERENCES films(film_id) ON DELETE CASCADE,
    provider VARCHAR(32) NOT NULL DEFAULT 'aws',
    aws_account_id VARCHAR(20) NOT NULL,
    aws_region VARCHAR(32) NOT NULL,
    subdomain VARCHAR(63) NOT NULL UNIQUE,
    terraform_state_key TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'provisioning',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_film_environments_film ON film_environments(film_id);

CREATE TABLE IF NOT EXISTS deployments (
    deployment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id UUID NOT NULL REFERENCES film_environments(environment_id) ON DELETE CASCADE,
    version VARCHAR(100) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_deployments_environment ON deployments(environment_id, created_at DESC);

CREATE TABLE IF NOT EXISTS job_dependencies (
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    depends_on_job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, depends_on_job_id),
    CONSTRAINT job_dependencies_no_self CHECK (job_id <> depends_on_job_id)
);

CREATE INDEX IF NOT EXISTS idx_job_dependencies_dependency ON job_dependencies(depends_on_job_id);

DROP TRIGGER IF EXISTS trg_film_environments_updated_at ON film_environments;
CREATE TRIGGER trg_film_environments_updated_at
BEFORE UPDATE ON film_environments
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_deployments_updated_at ON deployments;
CREATE TRIGGER trg_deployments_updated_at
BEFORE UPDATE ON deployments
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- Recover jobs whose worker lease expired. A later worker claim can safely retry them.
CREATE OR REPLACE FUNCTION recover_expired_job_leases()
RETURNS INTEGER AS $$
DECLARE recovered INTEGER;
BEGIN
    UPDATE jobs
    SET status = CASE WHEN attempts < max_attempts THEN 'retrying' ELSE 'failed' END,
        worker_id = NULL,
        lease_until = NULL,
        error_code = 'worker_lease_expired',
        retry_count = retry_count + 1,
        updated_at = now()
    WHERE status = 'running'
      AND lease_until IS NOT NULL
      AND lease_until < now();
    GET DIAGNOSTICS recovered = ROW_COUNT;
    RETURN recovered;
END;
$$ LANGUAGE plpgsql;
