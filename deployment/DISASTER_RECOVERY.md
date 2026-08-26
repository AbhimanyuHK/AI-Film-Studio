# Disaster Recovery Runbook

## Recovery targets

- PostgreSQL: restore from the latest automated snapshot or point-in-time recovery.
- S3: restore/versioned artifacts from the film bucket; never disable versioning.
- Jobs: stale leases are reclaimed by workers; interrupted jobs are retried according to policy.
- Secrets: restore from AWS Secrets Manager; rotate service tokens after an incident.

## Recovery order

1. Restore the AWS networking and IAM foundation with Terraform.
2. Restore PostgreSQL and apply database migrations in order.
3. Restore S3 access and verify bucket encryption/public-access blocking.
4. Restore SQS/job processing and dead-letter handling.
5. Deploy backend, workers, film-runtime and AI Engine.
6. Run `/health` checks for every service.
7. Run `deployment/smoke_test.py` against staging.
8. Verify a production job can be created, claimed, executed and completed.
9. Verify artifact retrieval from S3.
10. Rotate compromised credentials and record the incident.

## Validation

Do not declare recovery complete until:

- database connectivity is healthy;
- workers can claim a job;
- AI Engine authentication succeeds;
- film scope isolation succeeds;
- generated artifacts are written to the correct film prefix;
- frontend can retrieve job status.
