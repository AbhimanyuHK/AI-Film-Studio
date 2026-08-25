# AI Film Studio — Control Plane Backend

The **AI Film Studio backend** is the SaaS control plane and orchestration boundary between clients, films, isolated film environments, persistent job state, and the AI Engine.

It is intentionally separate from the AI inference/data plane. The backend manages identity, authorization, metadata, jobs, orchestration, deployment state, and communication with the AI Engine; generated production assets remain in film-scoped storage.

## Architecture

```text
                         AI FILM STUDIO
                              │
                    ┌─────────▼─────────┐
                    │   FastAPI Backend │
                    │    Control Plane  │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
     PostgreSQL          Job Graph/Queue      Auth/RBAC
          │                   │
          │                   ▼
          │              AI Worker
          │                   │
          │                   ▼
          │             AI Engine API
          │                   │
          │                   ▼
          │              GPU / Models
          │
          └────────────── Job State

                    AI Engine
                        │
                        ▼
                Film-scoped Artifacts
                        │
                        ▼
                         S3
```

## Responsibilities

### Control plane

- Authentication and authorization
- Client and film registry
- Film environment registry
- Environment/deployment metadata
- RBAC and film-level isolation
- AI job creation and persistence
- Pipeline dependency orchestration
- Worker lease/claim management
- Retry and failure state management
- Job cancellation
- AI Engine communication
- AI Engine health monitoring
- Platform audit events
- Billing/usage metadata

### Data plane boundary

The backend must **not become shared film memory**. Production content remains in the isolated film environment.

The control plane should not persist:

- screenplay contents
- generated images
- generated video/audio
- film-specific embeddings
- prompts containing production secrets/content
- LoRAs or fine-tuned model weights
- model-generated production assets

It stores identifiers, status, metadata, references, and audit information required to operate the platform.

## Technology Stack

| Area | Technology |
|---|---|
| API | Python, FastAPI |
| Validation | Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Job persistence | PostgreSQL |
| Job concurrency | PostgreSQL row locking / `SKIP LOCKED` |
| Worker | Python worker process |
| AI integration | Internal AI Engine HTTP API |
| Storage boundary | Film-scoped object storage / S3 |
| Authentication | JWT/OIDC-compatible application boundary |
| Authorization | Client/film/environment scoped RBAC |
| Containers | Docker |
| CI | GitHub Actions |
| Testing | pytest / FastAPI TestClient |

## AI Job Architecture

Jobs are persisted in PostgreSQL rather than held only in process memory.

```text
API Request
    │
    ▼
Create AI Job
    │
    ▼
PostgreSQL
    │
    ▼
QUEUED
    │
    ▼
Worker claims job
(FOR UPDATE SKIP LOCKED)
    │
    ▼
RUNNING
    │
    ├── success ──► COMPLETED
    │
    └── error ────► RETRYING ──► RUNNING
                         │
                         └──────► FAILED
```

A worker lease allows stale jobs to be recovered after worker failure.

## Film Pipeline

The backend persists and orchestrates the production dependency graph:

```text
script_analysis
       │
       ├── character_generation
       ├── environment_generation
       │
       └──────────────┐
                      ▼
                  storyboard
                      │
                 shot_generation
                      │
               video_generation
                      │
                 ┌────┴────┐
                 │         │
          voice_generation translation
                 │         │
                 └────┬────┘
                      ▼
                    dubbing
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        music        SFX        video
          └───────────┼───────────┘
                      ▼
                   editing
                      ▼
                  upscaling
                      ▼
                 final_render
```

The worker does not execute a downstream job until its required dependencies have completed.

## Backend ↔ AI Engine Contract

The backend communicates with the AI Engine through an explicit HTTP boundary.

### Health

```http
GET /health
```

### Execute job

```http
POST /v1/jobs/execute
Content-Type: application/json
```

Example payload:

```json
{
  "job_id": "job-123",
  "client_id": "client-123",
  "film_id": "film-123",
  "environment_id": "env-123",
  "operation": "video_generation",
  "payload": {
    "prompt": "A cinematic establishing shot"
  }
}
```

The AI Engine receives the same client/film/environment scope so the inference layer cannot silently operate outside the backend authorization boundary.

## Job API

The backend exposes the operational job surface used by the application:

```text
POST /api/v1/films/{film_id}/production/start
POST /api/v1/films/{film_id}/jobs
GET  /api/v1/films/{film_id}/jobs
GET  /api/v1/jobs/{job_id}
POST /api/v1/jobs/{job_id}/cancel
GET  /api/v1/ai-engine/health
```

The existing client, film, environment and deployment APIs remain part of the control-plane contract.

## Security Boundary

The fundamental isolation hierarchy is:

```text
Principal
   │
   ▼
Client
   │
   ▼
Film
   │
   ▼
Film Environment
   │
   ▼
AI Job
   │
   ▼
AI Engine
   │
   ▼
Film-scoped Artifact Storage
```

Every job must retain its `client_id`, `film_id`, and environment scope. Cross-client and cross-film access must be rejected before execution.

## PostgreSQL Model

The backend maintains control-plane records for:

```text
clients
films
film_environments
deployments
ai_jobs
ai_job_attempts
pipeline dependencies
platform audit events
```

Production artifacts are referenced by identifiers rather than copied into the control-plane database.

## Worker Execution

Run the worker separately from the API process:

```bash
python -m app.ai_worker_main
```

The worker repeatedly:

1. Finds executable jobs whose dependencies are complete.
2. Claims the job transactionally.
3. Sends the scoped job to the AI Engine.
4. Persists the result/status.
5. Retries transient failures.
6. Recovers stale leases.

This keeps long-running AI/video workloads out of the FastAPI request process.

## Configuration

Typical deployment configuration includes:

```text
DATABASE_URL
AI_ENGINE_URL
AI_ENGINE_TIMEOUT_SECONDS
AI_WORKER_ID
AI_WORKER_POLL_SECONDS
AI_JOB_LEASE_SECONDS
JWT/OIDC configuration
S3/object-storage configuration
```

The backend should never contain model weights or GPU-specific runtime dependencies.

## Deployment Topology

```text
                Load Balancer
                     │
                     ▼
              FastAPI API Pods
                     │
             ┌───────┴───────┐
             ▼               ▼
        PostgreSQL       AI Job Queue
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              CPU Worker       GPU AI Worker
                                      │
                                      ▼
                                  AI Engine
                                      │
                                      ▼
                                     S3
```

The control plane can scale independently from GPU inference workers.

## Testing

Backend tests should cover:

- API health
- client/film authorization
- environment isolation
- AI job creation
- dependency ordering
- worker job claiming
- retry behavior
- stale lease recovery
- cancellation
- AI Engine request/response contract
- AI Engine unavailable/failure behavior
- cross-film isolation

## Production Principles

1. **The backend is the control plane.**
2. **The AI Engine is the inference/data-plane service.**
3. **PostgreSQL is the durable source of job state.**
4. **Long-running generation never blocks an HTTP request.**
5. **Every AI operation is client/film scoped.**
6. **Production artifacts remain in isolated object storage.**
7. **Workers must be restartable and idempotency-aware.**
8. **AI model/GPU dependencies stay outside the API container.**
9. **All important state transitions are observable and auditable.**
10. **A film environment remains the primary production security boundary.**

## Current Implementation

The backend now contains the control-plane foundation, persistent AI job lifecycle, dependency-aware worker execution, AI Engine transport client, health integration, retry/recovery behavior, and the AI Engine execution contract.

The remaining deployment-specific configuration is the concrete GPU/model runtime used by each AI worker. That runtime is intentionally isolated from the FastAPI control plane.
