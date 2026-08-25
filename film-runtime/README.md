# AI Film Studio — Film Runtime

`film-runtime` is the **isolated execution environment for one film**. It is deployed separately for each film environment, normally inside that film's AWS account/VPC or an equivalent isolated runtime boundary.

The central backend controls clients, films, authorization and platform jobs. The film runtime owns the film's private production context and enforces the final film-isolation boundary before work reaches the AI Engine.

## Responsibilities

- Film-scoped PostgreSQL database
- Film-scoped S3/object storage
- Film knowledge/RAG boundary
- Screenplay, film-bible and production context
- Characters, locations, scenes and shots
- Film-specific prompts
- Film-specific model/LoRA configuration
- Production job state inside the film environment
- AI Engine execution boundary
- Artifact metadata and references
- Runtime scope enforcement

A runtime is configured for exactly one `client_id`, `film_id` and `environment_id` and must reject requests for any other scope.

## Architecture

```text
                    CONTROL PLANE
                         │
                    FastAPI Backend
                         │
                 authenticated job
                         │
                         ▼
              ┌──────────────────────┐
              │     FILM RUNTIME     │
              │  one film / one env  │
              ├──────────────────────┤
              │ Scope Enforcement    │
              │ Film PostgreSQL      │
              │ Film Knowledge/RAG   │
              │ Prompts              │
              │ Model Registry       │
              │ Asset Metadata       │
              └──────────┬───────────┘
                         │
                         ▼
                     AI Engine
                         │
                    GPU / Models
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Film PostgreSQL       Film-scoped S3
```

## Why this is separate from `ai-engine`

The separation is intentional:

- **`ai/`** — model registry, workflows, policies and AI resources
- **`ai-engine/`** — provider-neutral AI execution and model adapters
- **`film-runtime/`** — private film context, film data, assets, prompts, RAG and isolation
- **`backend/`** — SaaS control plane, authentication, authorization and platform job state
- **`database/`** — central database schemas
- **`frontend/`** — application UI

The AI Engine should not decide which film's data it is allowed to access. The film runtime supplies and enforces that boundary.

## Runtime API

### Health

```http
GET /health
```

### Scope verification

```http
GET /v1/scope
X-Client-Id: <configured-client>
X-Film-Id: <configured-film>
X-Environment-Id: <configured-environment>
```

### Execute production job

```http
POST /v1/jobs/execute
X-Client-Id: <configured-client>
X-Film-Id: <configured-film>
X-Environment-Id: <configured-environment>
```

```json
{
  "job_id": "job-123",
  "operation": "storyboard",
  "payload": {
    "film_id": "film-123",
    "environment_id": "env-123",
    "scenes": []
  }
}
```

Supported production operations include:

```text
script_analysis
character_generation
environment_generation
storyboard
shot_generation
video_generation
voice_generation
translation
dubbing
music
sfx
editing
upscaling
final_render
```

### Film knowledge

```http
POST /v1/knowledge
GET  /v1/knowledge/search?q=...
```

Knowledge is persisted in the film database. The current implementation provides deterministic lexical retrieval and an interchangeable retrieval boundary; production deployments can enable pgvector or a managed vector service without changing the runtime API.

## Database

`database/001_runtime.sql` provisions:

- `film_metadata`
- `characters`
- `scenes`
- `shots`
- `production_jobs`
- `film_assets`
- `knowledge_chunks`

The SQLAlchemy models avoid the reserved Declarative attribute name `metadata` by exposing it as `metadata_json` while preserving the database column name `metadata`.

## Object storage

Large binary artifacts are stored in S3, not PostgreSQL.

Recommended prefix:

```text
clients/{client_id}/films/{film_id}/environments/{environment_id}/assets/{asset_id}/...
```

The runtime's configured S3 prefix is part of the isolation boundary. Presigned URLs are generated only from the runtime's configured bucket.

## Knowledge and RAG

Film knowledge can contain:

- screenplay chunks
- film bible
- character biographies
- location descriptions
- continuity notes
- approved visual references
- production rules
- localization notes

The runtime persists source/content metadata and exposes a retrieval API. A production vector implementation can use `pgvector` in the same isolated PostgreSQL environment or another isolated vector service.

## Model and prompt isolation

`config/model-registry.yaml` describes the capabilities available to the film runtime. Film-specific LoRAs and fine-tuned model assets must remain inside the film environment.

`config/prompts/system.txt` defines the minimum runtime system policy: never access another film, preserve continuity, and return auditable structured results.

Provider credentials and model weights must never be sent to the browser.

## Security

The runtime rejects a request when any of these does not exactly match its configured scope:

```text
X-Client-Id
X-Film-Id
X-Environment-Id
```

The same values are checked in job payloads when supplied.

```text
Request
   ↓
Client check
   ↓
Film check
   ↓
Environment check
   ↓
Production operation
   ↓
AI Engine
```

This provides defense in depth. Authorization is still required in the central backend; runtime isolation is the final enforcement boundary.

## Technology Stack

- Python 3.11+
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy 2.x async
- asyncpg
- PostgreSQL
- JSONB
- pgvector-ready retrieval boundary
- boto3 / Amazon S3
- Docker
- Uvicorn
- pytest

## Configuration

Copy `.env.example` and configure:

```text
RUNTIME_CLIENT_ID
RUNTIME_FILM_ID
RUNTIME_ENVIRONMENT_ID
RUNTIME_SHARED_SECRET
DATABASE_URL
S3_BUCKET
S3_PREFIX
AWS_REGION
AI_ENGINE_URL
MAX_CONTEXT_CHARS
```

A runtime should receive these values from AWS Secrets Manager/SSM or an equivalent secret/configuration service rather than committing them to source control.

## Local development

```bash
cd film-runtime
pip install -e '.[test]'
psql "$DATABASE_URL" -f database/001_runtime.sql
film-runtime
```

The service listens on port `8081`.

## Docker

```bash
docker build -t ai-film-studio-film-runtime ./film-runtime
docker run --env-file ./film-runtime/.env -p 8081:8081 ai-film-studio-film-runtime
```

## Production deployment

A film runtime should be deployed as an independently managed workload:

```text
AWS Film Environment
├── Runtime API
├── Runtime worker/execution boundary
├── Film PostgreSQL
├── Film S3 bucket/prefix
├── Film secrets
├── Film model/LoRA storage
└── Optional vector index
```

Network policy should allow only the required control-plane and AI-engine paths. The runtime should have no route to another film environment.

## Production principles

1. One runtime instance/environment maps to one film environment.
2. Never trust film IDs from the request without scope validation.
3. Never share film databases or private model assets across tenants.
4. Store media in object storage, not PostgreSQL.
5. Keep provider/model credentials server-side.
6. Make production jobs idempotent.
7. Keep artifact metadata and lineage auditable.
8. Keep retrieval film-scoped.
9. Treat the runtime as a security boundary, not just an application service.
10. Keep heavy inference implementation in `ai-engine` rather than duplicating it here.

## Implementation status

The film runtime now contains the executable service boundary, scope enforcement, persistent film-domain models, production job executor, knowledge persistence/retrieval API, S3 artifact store, model registry, prompt policy, isolated database schema, Docker packaging, environment configuration and isolation tests.

The concrete GPU/model provider remains intentionally owned by `ai-engine`; the runtime controls which film context is made available to that execution layer.
