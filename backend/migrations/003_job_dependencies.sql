CREATE TABLE IF NOT EXISTS job_dependencies (
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    depends_on_job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, depends_on_job_id),
    CONSTRAINT job_dependency_no_self CHECK (job_id <> depends_on_job_id)
);

CREATE INDEX IF NOT EXISTS idx_job_dependencies_dependency ON job_dependencies(depends_on_job_id);
