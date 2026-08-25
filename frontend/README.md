# AI Film Studio Frontend

The frontend is the **SaaS control-plane UI** for AI Film Studio. It communicates with the FastAPI backend; it does **not** call model providers or GPU workers directly.

## Architecture

```text
Browser
  │
  ▼
React + TypeScript + Vite
  │
  │ X-Actor-Id / authenticated session boundary
  ▼
FastAPI Backend
  │
  ├── PostgreSQL job state
  ├── AI job worker
  └── AI Engine
          │
          ▼
      GPU / Models
          │
          ▼
      Film-scoped S3
```

## Implemented Integration

- Client onboarding
- Film creation and selection
- Screenplay/production brief input
- Complete production-pipeline start
- Live job polling
- Pipeline stage status
- Job attempt visibility
- Job cancellation
- AI Engine health status
- Backend health boundary
- Error/success feedback
- Client/film-scoped API calls
- Responsive production dashboard

The UI polls the selected film's jobs while production is active so users can see queued, running, retrying, completed, and failed stages without refreshing.

## API Integration

```text
GET  /health
GET  /api/v1/ai-engine/health
POST /api/v1/clients
GET  /api/v1/clients/{client_id}/films
POST /api/v1/films
GET  /api/v1/films/{film_id}
POST /api/v1/films/{film_id}/production/start
POST /api/v1/films/{film_id}/jobs
GET  /api/v1/films/{film_id}/jobs
GET  /api/v1/jobs/{job_id}
POST /api/v1/jobs/{job_id}/cancel
```

The browser never receives model credentials and never connects directly to Ollama, Diffusers, GPU workers, private S3 buckets, or provider APIs.

## Technology Stack

- React
- TypeScript
- Vite
- Fetch API
- CSS
- FastAPI backend integration
- PostgreSQL-backed job state through the backend
- AI Engine health and job lifecycle integration

## Local Development

```bash
npm install
npm run dev
```

By default the frontend expects:

```text
http://localhost:8000
```

Override it with `VITE_API_BASE_URL`. The backend should allow the frontend origin using `FRONTEND_CORS_ORIGINS=http://localhost:5173`.

## Authentication Boundary

The current backend uses `X-Actor-Id` as an explicit development identity. The frontend generates and persists a browser actor identifier for development integration.

This is **not production authentication**. Production deployment should replace it with the platform's OIDC/JWT session and send the resulting credentials to the backend. AI provider credentials must never be exposed to the browser.

## Production Flow

```text
User
 ↓
Frontend
 ↓
Authenticated Backend API
 ↓
Film authorization
 ↓
PostgreSQL
 ↓
Persistent AI job graph
 ↓
AI Worker
 ↓
AI Engine
 ↓
GPU model runtime
 ↓
Film-scoped artifacts
 ↓
Backend asset metadata
 ↓
Frontend
```

The frontend is therefore a control-plane client rather than an AI inference client.
