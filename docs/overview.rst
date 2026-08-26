Platform Overview
==================

Purpose
-------

AI-Film-Studio provides a controlled workflow for creating films with AI models while keeping platform control, film-specific state, asynchronous execution, and model inference separated.

Core principles
---------------

* Backend owns the SaaS control plane and API.
* PostgreSQL stores durable control-plane state and job state.
* Workers execute asynchronous jobs and manage leases/retries.
* Film Runtime owns film-specific scope, context, assets, and runtime state.
* AI Engine owns model/provider execution.
* S3 stores generated and uploaded artifacts.
* Terraform defines AWS infrastructure.
* GitHub Actions provides CI and deployment automation.

High-level flow
---------------

::

    Frontend
       |
       v
    Backend API
       |
       +----> PostgreSQL
       |
       v
    Job Queue / Jobs
       |
       v
    Worker
       |
       v
    Film Runtime
       |
       v
    AI Engine
       |
       +----> LLM / Image / Video / Audio / Translation models
       |
       v
    S3 Artifacts

Repository map
--------------

``frontend/``
    Web application and user interface.

``backend/``
    API, authentication, authorization, control-plane operations, and job creation.

``database/``
    PostgreSQL schema and migrations.

``workers/``
    Background job execution, locking, leases, retries, and dispatch.

``film-runtime/``
    Film-scoped runtime and isolation boundary.

``ai-engine/``
    AI orchestration and provider/model execution boundary.

``ai/``
    AI configuration and policies.

``models/``
    Approved model registry and model governance metadata.

``terraform/``
    AWS infrastructure definitions.

``deployment/``
    Deployment commands, readiness checks, smoke tests, and operational material.

``docs/``
    This documentation site.
