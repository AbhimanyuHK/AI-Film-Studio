Database
========

Purpose
-------

PostgreSQL is the durable control-plane store. It contains clients, films, environments, jobs, job dependencies, audit information, and deployment metadata.

Migrations
----------

Schema changes are applied in numeric order from ``database/``. Never edit a migration that has already been applied to a shared environment; create a new migration instead.

Deployment process
------------------

1. Provision PostgreSQL.
2. Configure the database connection through a secret/environment value.
3. Apply migrations in order.
4. Run application startup checks.
5. Verify indexes, constraints, and job leasing functions.

Backup and recovery
-------------------

Production PostgreSQL should use automated backups, retention appropriate to business requirements, and periodic restore testing. A backup that has never been restored is not a verified recovery strategy.

Data boundaries
---------------

Keep large binary media in S3. Database rows should reference artifacts and contain metadata, state, ownership, and lifecycle information.
