AWS Infrastructure
===================

Reference topology
------------------

A production deployment can use:

::

    Route 53
       |
       v
    CloudFront / ALB
       |
       +---- Frontend
       |
       +---- Backend
               |
               +---- RDS PostgreSQL
               +---- SQS / job queue
               +---- S3
               +---- Workers
                       |
                       +---- Film Runtime
                       +---- AI Engine / GPU

Security boundaries
-------------------

* Keep RDS private.
* Restrict security groups to required service paths.
* Use IAM roles instead of static AWS credentials where possible.
* Encrypt S3 and database storage.
* Store secrets in Secrets Manager or SSM.
* Terminate public TLS at a managed load balancer or CloudFront.
* Use WAF for public HTTP entry points.

GPU infrastructure
------------------

GPU hosting depends on the selected models. Validate GPU memory, driver/CUDA compatibility, model licensing, startup time, concurrency, and expected cost before selecting an instance type.

Observability
-------------

Production should collect service logs, request/job identifiers, job latency, queue depth, model/provider latency, error counts, and infrastructure health. Never log provider API keys, JWT secrets, database passwords, or sensitive user content.
