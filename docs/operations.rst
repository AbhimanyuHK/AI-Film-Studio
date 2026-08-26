Operations
==========

Health
------

Monitor every service independently and monitor the complete job path. A green process health check does not prove that AI generation is working.

Key metrics
-----------

* API request latency and error rate;
* queue depth and oldest queued job age;
* running job count;
* retry count;
* stale lease count;
* AI provider latency and error rate;
* artifact upload failures;
* database connection pool saturation;
* CPU/GPU utilization and memory;
* S3 and database error rates.

Job recovery
------------

If a worker crashes while holding a lease, stale-job recovery should make the job eligible again. Operators should investigate repeated retries rather than manually marking jobs complete.

Incident response
-----------------

1. Identify the affected component.
2. Capture job/request identifiers.
3. Check recent deployments.
4. Inspect service and infrastructure logs.
5. Stop repeated destructive retries if required.
6. Recover or roll back using the deployment procedure.
7. Verify end-to-end health.
8. Record the incident and corrective action.

Scaling
-------

Scale workers for job throughput and AI inference capacity for model throughput. Scale the API independently from GPU workloads.
