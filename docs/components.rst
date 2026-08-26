Components
==========

Frontend
--------

The frontend is the browser-facing application. It should treat the backend as the authoritative API and should not contain provider credentials.

Backend
-------

The backend is the control plane. It handles authentication, authorization, clients, films, environments, jobs, and API-level validation. It should not perform long-running media generation directly.

Workers
-------

Workers consume durable jobs, acquire leases, execute retries, handle stale jobs, and dispatch work to Film Runtime and AI Engine. Workers are stateless and can be horizontally scaled.

AI Engine
---------

AI Engine is the inference boundary. It owns AI orchestration and provider adapters for supported modalities such as LLM, image, video, speech, translation, and lip-sync. Model selection is externally configurable and constrained by the approved model registry.

Film Runtime
------------

Film Runtime is the film-scoped execution boundary. It carries the active client, film, and environment context and controls access to film-specific data and artifacts.

Database
--------

PostgreSQL stores durable application state. Schema changes are versioned through ordered SQL migrations in ``database/``.

Storage
-------

S3 is used for large objects such as source media, generated images, generated video, audio, project exports, and final renders. Database rows should store metadata and object references rather than large binary payloads.

Terraform
---------

Terraform defines AWS infrastructure and IAM. Deployment should use plan/apply workflows and remote state appropriate for the target environment.

Models
------

``models/registry.yaml`` describes approved model identities, providers, capabilities, and governance metadata. Secrets and deployment-specific values do not belong in the registry.
