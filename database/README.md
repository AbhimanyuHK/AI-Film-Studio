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
        environments / audit       film production state
                 │                         │
                 └────────────┬────────────┘
                              │
                           AI Engine
                              │
                              ▼
                    Film-scoped S3 storage
```

## Migration order

```text
001_control_plane.sql
        ↓
002_film_database_template.sql
        ↓
003_integrity_and_worker.sql
        ↓
004_environments_and_dependencies.sql
```

For production, apply these through the deployment/migration mechanism in exactly this order.

## Control plane

`001_control_plane.sql` defines:

- `clients`
- `films`
- `jobs`
- `audit_events`

The control plane stores identifiers, operational state, authorization scope, job metadata and audit information. It is not a shared repository for large film content.

## Film environment

`002_film_database_template.sql` defines the isolated film data boundary:

- `film_metadata`
- `characters`
- `scenes`
- `shots`
- `production_jobs`
- `film_assets`

Production can provision this schema in a separate PostgreSQL database for each film environment.

## Queue and worker hardening

`003_integrity_and_worker.sql` adds:

- worker ownership
- lease expiration
- retry counters
- idempotency keys
- queue indexes
- worker-lease indexes
- valid job status constraints
- automatic `updated_at` triggers

Workers claim jobs with PostgreSQL row locking and `SKIP LOCKED` so multiple workers can safely consume the same queue.

## Environments and dependency graph

`004_environments_and_dependencies.sql` adds the missing control-plane relationships:

- `film_environments`
- `deployments`
- `job_dependencies`
- film source/target language fields
- lease recovery function

A production film must have an environment before production jobs can be started.

The film pipeline is represented as a DAG:

```text
script_analysis
   ├── character_generation
   ├── environment_generation
   ├── voice_generation
   ├── translation
   └── music_generation
          │
character + environment + script
          ↓
      storyboard
          ↓
    shot_generation
          ↓
    video_generation
          ↓
editing ← dubbing ← voice + translation
   ↑          ↑
 music       sfx
   │
   ↓
upscaling
   ↓
final_render
```

A job is eligible only when all declared dependency jobs have completed successfully.

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

RUNNING ── lease expires ──► RETRYING / FAILED

QUEUED / RETRYING ── cancellation ──► CANCELLED
```

Worker leases make crash recovery deterministic. A worker that disappears does not permanently strand a job.

## Idempotency

AI jobs support an optional film-scoped `idempotency_key`. Repeated requests with the same key return the existing logical job instead of creating duplicate work.

## Storage boundary

Large media files are not stored in PostgreSQL.

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

## Backend integration

The backend uses SQLAlchemy 2.x with asyncpg. SQLAlchemy's Declarative API reserves the Python attribute name `metadata`, so the backend maps the PostgreSQL `metadata` column to the Python attribute `metadata_json`.

Film records persist `source_language` and `target_languages`, environments persist their AWS deployment identity, and jobs persist worker lease/idempotency state.

## Development initialization

```bash
psql "$DATABASE_URL" -f database/001_control_plane.sql
psql "$DATABASE_URL" -f database/002_film_database_template.sql
psql "$DATABASE_URL" -f database/003_integrity_and_worker.sql
psql "$DATABASE_URL" -f database/004_environments_and_dependencies.sql
```

The root Docker Compose stack mounts the same ordered migrations into PostgreSQL initialization.

## Production requirements

1. Use a managed PostgreSQL service.
2. Do not use development credentials.
3. Keep PostgreSQL private; expose only the application connection path.
4. Store credentials in a secret manager.
5. Back up and regularly test restoration.
6. Apply migrations transactionally/versionedly.
7. Enforce film/client authorization in the API and runtime.
8. Store media in scoped object storage rather than PostgreSQL.
9. Use job leases and idempotency for every asynchronous production workload.

## Technology stack

- PostgreSQL 16+
- SQLAlchemy 2.x
- asyncpg
- JSONB
- UUID / `pgcrypto`
- PostgreSQL row-level locking
- `FOR UPDATE SKIP LOCKED`
- Worker leases
- Idempotent job submission
- S3/object storage for generated media
