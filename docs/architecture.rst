Architecture
============

Service boundaries
------------------

The platform intentionally separates responsibilities.

+----------------+--------------------------------------------------+
| Component      | Responsibility                                   |
+================+==================================================+
| Frontend       | UI, job status, film/project interaction         |
+----------------+--------------------------------------------------+
| Backend        | API, auth, control plane, job creation           |
+----------------+--------------------------------------------------+
| Database       | Durable state, films, jobs, environments         |
+----------------+--------------------------------------------------+
| Workers        | Async execution, leases, retries, dispatch      |
+----------------+--------------------------------------------------+
| Film Runtime   | Film isolation, context, film assets             |
+----------------+--------------------------------------------------+
| AI Engine      | AI workflow and provider/model execution         |
+----------------+--------------------------------------------------+
| S3             | Large binary assets and generated artifacts      |
+----------------+--------------------------------------------------+

Request lifecycle
-----------------

1. The frontend calls the backend API.
2. The backend authenticates and authorizes the request.
3. A durable job is created in PostgreSQL.
4. A worker claims the job using a database lock/lease.
5. The worker dispatches execution to the appropriate film runtime.
6. Film Runtime validates client, film, and environment scope.
7. Film Runtime invokes the AI Engine.
8. AI Engine selects an approved provider/model configuration.
9. Generated artifacts are stored in object storage.
10. Job state is updated to completed or failed.
11. The frontend reads job state and artifact metadata.

Isolation model
---------------

Every film operation should carry a client/film/environment scope. A film runtime must reject requests that do not match its configured scope. Worker dispatch must propagate the same scope instead of allowing a caller to select an arbitrary film environment.

Asynchronous execution
----------------------

Long-running AI generation must not run inside a synchronous HTTP request. The API creates a job and returns a job identifier. Workers claim jobs, maintain leases, retry transient failures, and persist terminal state.

Failure boundaries
------------------

* API failure: job creation must remain transactional.
* Worker failure: an expired lease makes the job eligible for recovery.
* Provider timeout: retry according to the job retry policy.
* Permanent provider failure: mark the job failed with an actionable error.
* Artifact failure: preserve job failure information and avoid reporting success.
* Cross-film access: reject before AI execution.
