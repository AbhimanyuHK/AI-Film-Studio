# AI Film Studio Database

The database layer provides durable control-plane state and isolated film-environment state for the AI Film Studio platform.

```text
                         AI Film Studio
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          Control-plane DB         Film Environment DB
             PostgreSQL                PostgreSQL
                 │                         │
        clients / films / jobs     scenes / shots / assets
        audit / worker leases      film production state
                 │                         │
                 └────────────┬────────────┘
                              │
                           AI Engine
                              │
                              ▼
                    Film-scoped S3 storage
```

## Database boundaries

### Control plane

`001_control_plane.sql` defines durable platform state:

- `clients`
- `films`
- `jobs`
- `audit_events`

The control plane stores identifiers, operational state, authorization scope, job metadata and audit information. It is not a shared repository for film content.

### Film environment

`002_film_database_template.sql` defines the schema template for an isolated film environment:

- `film_metadata`
- `characters`
- `scenes`
- `shots`
- `production_jobs`
- `film_assets`

A production deployment can provision this schema in a separate PostgreSQL database or an equivalent isolated PostgreSQL boundary for each film environment.

## Job queue hardening

`003_integrity_and_worker.sql` adds production queue protections:

- worker ownership
- worker lease expiration
- retry counters
- idempotency keys
- claimable-job indexes
- worker-lease indexes
- status constraints
- client/film status constraints
- automatic `updated_at` triggers

The worker claim pattern is transactional:

```sql
SELECT ...
FROM jobs
WHERE status IN ('queued', 'retrying')
  AND scheduled_at <= now()
  AND (lease_until IS NULL OR lease_until < now())
ORDER BY scheduled_at
FOR UPDATE SKIP LOCKED;
```

The selected row is then marked `running` with a worker ID and lease in the same transaction.

## Job lifecycle

```text
QUEUED
  │
  ▼
RUNNING ───────────────► COMPLETED
  │
  ├── transient error ─► RETRYING ──► RUNNING
  │
  └── terminal error ──► FAILED

RUNNING ── cancellation ──► CANCELLED
```

The database is the durable source of job state, so an API or worker restart does not lose the production queue.

## Idempotency

AI jobs may be retried because GPU workers, provider services or network calls can fail. The control plane therefore supports an optional `idempotency_key` scoped to a film.

Repeated submission of the same logical job can be detected without creating duplicate work.

## Storage boundary

Large media files must not be stored in PostgreSQL.

```text
Film database
     │
     └── asset metadata + object key
                    │
                    ▼
            Film-scoped S3
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        images     video     audio
```

Recommended object-key structure:

```text
clients/{client_id}/films/{film_id}/environments/{environment_id}/assets/{asset_id}/...
```

The application must derive and validate this scope from the authenticated principal rather than trusting arbitrary client/film IDs supplied by the browser.

## Backend integration

The backend uses SQLAlchemy against PostgreSQL. The SQLAlchemy Declarative API reserves the Python attribute name `metadata`; therefore application models use `metadata_json` where necessary while PostgreSQL can retain the column name `metadata`.

The backend currently uses async SQLAlchemy/`asyncpg`. fileciteturn212file0L2-L2

## Initialization

Development control-plane database:

```bash
psql "$DATABASE_URL" -f database/001_control_plane.sql
psql "$DATABASE_URL" -f database/003_integrity_and_worker.sql
```

Development film environment:

```bash
psql "$FILM_DATABASE_URL" -f database/002_film_database_template.sql
```

Production environments should run these definitions through a versioned migration mechanism rather than applying arbitrary SQL manually.

## Technology stack

- PostgreSQL
- SQLAlchemy 2.x
- asyncpg
- Alembic-compatible migrations
- JSONB
- UUID / `pgcrypto`
- PostgreSQL row-level locking
- `FOR UPDATE SKIP LOCKED`
- Transactional worker leases
- S3/object storage for generated media

## Data isolation rules

1. Every film belongs to exactly one client.
2. Every AI job carries client/film/environment scope.
3. Film production state belongs to the film environment.
4. Generated media remains outside PostgreSQL.
5. Object keys are film/environment scoped.
6. Cross-client and cross-film access is rejected at the application authorization boundary.
7. Audit events remain in the central control plane.
8. Worker claims must be transactional.
9. Retried jobs must be idempotency-aware.
10. Stale worker leases must be recoverable.

## Database readiness

The database layer now provides the schema foundation required by the complete platform flow:

```text
Frontend
   ↓
FastAPI Backend
   ↓
PostgreSQL
   ↓
Persistent AI Job Worker
   ↓
AI Engine
   ↓
GPU / Models
   ↓
S3 Film Artifacts
```
