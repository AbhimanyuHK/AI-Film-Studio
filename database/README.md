# AI Film Studio Database

The database layer is intentionally split into two boundaries:

```text
                    AI Film Studio
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
      Control-plane DB       Film Environment DB
         PostgreSQL              PostgreSQL
              │                     │
      clients / films       scenes / shots / assets
      jobs / audit          characters / film state
              │                     │
              └──────────┬──────────┘
                         │
                    AI Engine
                         │
                         ▼
                Film-scoped object storage
```

## 1. Control-plane database

`001_control_plane.sql` defines durable platform state used by the backend:

- `clients`
- `films`
- `jobs`
- `audit_events`

This database contains control-plane metadata only. It does not become the shared store for film content.

### Job lifecycle

```text
queued → running → completed
             │
             ├→ retrying → running
             └→ failed
```

Jobs are designed for transactional worker claiming with PostgreSQL row locks and `SKIP LOCKED`.

## 2. Film database

`002_film_database_template.sql` is the schema template for an isolated film environment. Provision a separate database or equivalent PostgreSQL isolation boundary for each film environment.

It contains:

- `film_metadata`
- `characters`
- `scenes`
- `shots`
- `production_jobs`
- `film_assets`

The central control plane stores references and operational state; film-specific production state belongs to the film boundary.

## 3. Storage boundary

Large binary assets should not be stored in PostgreSQL.

```text
Film DB
   │
   └── asset metadata + object key
                    │
                    ▼
             Film-scoped S3
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      images      video        audio
```

Recommended key pattern:

```text
clients/{client_id}/films/{film_id}/environments/{environment_id}/assets/{asset_id}/...
```

Access to an object must be derived from the authenticated client/film/environment scope.

## 4. Backend integration

The backend SQLAlchemy models map to the control-plane schema. The reserved SQLAlchemy declarative attribute `metadata` is represented in Python as `metadata_json` while retaining the PostgreSQL column name `metadata`.

## 5. Initialization

For a new control-plane PostgreSQL instance:

```bash
psql "$DATABASE_URL" -f database/001_control_plane.sql
```

For a new isolated film database:

```bash
psql "$FILM_DATABASE_URL" -f database/002_film_database_template.sql
```

Production deployments should execute these definitions through the project's migration system rather than relying on ad-hoc manual SQL execution.

## 6. Technology stack

- PostgreSQL
- SQLAlchemy
- Alembic-compatible migration workflow
- JSONB for flexible metadata/results
- UUID identifiers
- PostgreSQL row locking for worker coordination
- S3/object storage for generated media

## 7. Data isolation rules

1. Never store content from multiple films in a shared film database.
2. Every control-plane film belongs to exactly one client.
3. Every AI job carries its film/environment scope.
4. Film assets are referenced by scoped object keys.
5. Generated media is stored outside PostgreSQL.
6. Cross-client and cross-film access is rejected at the application authorization boundary.
7. Audit events remain in the central control plane for operational governance.
