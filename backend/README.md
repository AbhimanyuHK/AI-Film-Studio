# AI Film Studio Control Plane Backend

Central SaaS backend responsibilities:

- Authentication and authorization
- Client and film registry
- Environment registry
- Deployment orchestration
- Subdomain/environment mapping
- Platform audit events
- Billing metadata

## Initial domain model

```text
Client 1 ── * Film 1 ── 1 FilmEnvironment 1 ── * Deployment
```

A `FilmEnvironment` is the security boundary for the production data plane. The control plane stores only control metadata and references; it must not become shared film memory.

## Planned API

- `POST /api/v1/clients`
- `GET /api/v1/clients/{client_id}`
- `POST /api/v1/films`
- `GET /api/v1/films/{film_id}`
- `POST /api/v1/films/{film_id}/environment`
- `GET /api/v1/films/{film_id}/environment`
- `POST /api/v1/films/{film_id}/deployments`
- `GET /api/v1/deployments/{deployment_id}`

## Security boundary

The control plane must not store scripts, generated video/audio/images, embeddings, film-specific prompts, LoRAs, fine-tuned models, or other production content. Those remain in the isolated film environment.

Implementation should use a typed API, database migrations, RBAC, validation, structured logging, and automated tests for authorization and isolation.
