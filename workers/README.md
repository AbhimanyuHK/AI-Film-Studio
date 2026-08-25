# Production Workers

The worker service is the durable asynchronous execution layer between the control-plane job queue and the AI Engine.

```text
Backend API
   ↓
PostgreSQL jobs
   ↓
workers/
   ↓
AI Engine
   ↓
film-runtime / film artifacts
```

## Responsibilities

- Claim queued/retrying jobs transactionally with `FOR UPDATE SKIP LOCKED`.
- Assign a worker lease and worker ID.
- Increment attempt counters.
- Dispatch film-scoped requests to the AI Engine.
- Mark jobs completed, failed or retrying.
- Release leases after completion.
- Never execute a job outside its film/environment scope.

The worker does not implement LLM, image, video, audio or RAG inference. Those responsibilities remain in `ai-engine` and `film-runtime`.

## Configuration

Required:

```text
DATABASE_URL=postgresql://...
```

Optional:

```text
AI_ENGINE_URL=http://ai-engine:8080
WORKER_ID=worker-1
WORKER_POLL_SECONDS=2
WORKER_LEASE_SECONDS=300
```

## Container

```bash
docker build -t ai-film-studio-worker workers
docker run --env-file .env ai-film-studio-worker
```

## Production behavior

The worker is stateless and should be horizontally scalable. PostgreSQL locking prevents multiple workers from claiming the same job. Failed transient calls are retried until `max_attempts`; terminal failures are persisted in the job record.
