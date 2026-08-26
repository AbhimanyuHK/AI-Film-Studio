Troubleshooting
===============

Service will not start
----------------------

Check environment variables, database connectivity, port conflicts, dependency installation, and container logs.

Job remains queued
------------------

Check that workers are running, the worker can connect to PostgreSQL, the job is not blocked by unmet dependencies, and the queue/lease configuration is correct.

Job repeatedly fails
--------------------

Inspect the persisted error and worker logs. Confirm provider credentials, model availability, request limits, and network access. Do not increase retries for permanent validation failures.

AI model not found
------------------

Confirm ``MODEL_PROVIDER`` and the relevant model environment variable. Verify that the model is installed/available at the configured provider and that the model identifier is present in the approved registry.

S3 access failure
-----------------

Check IAM role permissions, bucket/region configuration, object key scope, and whether the workload is running in a subnet with the required AWS network path.

Cross-film access denied
------------------------

Verify client, film, and environment identifiers. The Film Runtime intentionally rejects scope mismatches.

Terraform failure
-----------------

Run ``terraform fmt`` and ``terraform validate`` first. Then inspect the plan for missing variables, unavailable AWS resources, IAM permissions, quotas, or state-lock problems.

Production incident
-------------------

Follow the operations and rollback procedures. Avoid making ad-hoc production database edits unless the incident procedure explicitly requires them.
