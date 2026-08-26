Workers
=======

Purpose
-------

Workers are the asynchronous execution layer. They claim durable jobs and dispatch them to Film Runtime and AI Engine.

Execution model
---------------

::

    PostgreSQL job
         |
         | claim + lease
         v
       Worker
         |
         +--> dependency check
         |
         +--> Film Runtime
         |
         +--> AI Engine
         |
         v
      job result

Reliability
-----------

Workers should be stateless. Durable state belongs in PostgreSQL and object storage. A worker must renew or complete its lease and should not assume in-memory state survives a restart.

Retries
-------

Retry transient failures such as temporary provider/network errors. Do not endlessly retry validation failures, authentication failures, unsupported models, or malformed requests. Jobs exceeding the retry limit become failed and should be observable for operator action.

Scaling
-------

Increase worker replicas for more throughput. Database locking and leases prevent multiple workers from claiming the same job simultaneously.

Operations
----------

Monitor queue depth, job age, running jobs, retry counts, lease expiry, provider latency, and terminal failures.
