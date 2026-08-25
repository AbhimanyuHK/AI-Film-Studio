# AI Film Engine

The **AI Film Engine** is the AI execution layer of **AI Film Studio**. It converts a screenplay or film project into a structured, production-ready media pipeline covering story understanding, character and scene planning, image/video generation, voice and localization, lip-sync, subtitles, media assembly, and final rendering.

The engine is designed as a **provider-neutral, film-scoped, asynchronous AI runtime**. Heavy ML workloads execute in dedicated workers while the application layer manages jobs, authorization, orchestration, artifacts, retries, and production metadata.

---

## 1. Executive Summary

AI Film Engine provides the following capabilities:

- Screenplay and story analysis
- Character, environment, scene and shot extraction
- Storyboard planning
- Prompt/context construction for generation
- AI image generation
- AI video generation
- Character and visual consistency validation boundaries
- Speech generation and dubbing
- Speech transcription
- Translation and multilingual production
- Lip-sync integration
- Subtitle generation
- Music and sound-effect integration
- Video/audio assembly
- FFmpeg-based final rendering
- Film-scoped artifact storage
- AI job orchestration, retries and lifecycle management
- Provider/model abstraction
- GPU-worker execution model
- Client and film-level authorization
- Runtime/model configuration
- Production observability and metadata boundaries

The engine is intentionally **not tied to a single AI vendor**. Model providers can be changed through runtime configuration and adapters without redesigning the film pipeline.

---

## 2. End-to-End AI Pipeline

```text
                         SCREENPLAY / STORY
                                │
                                ▼
                       ┌──────────────────┐
                       │   Story Analysis │
                       │      / LLM       │
                       └────────┬─────────┘
                                │
                                ▼
                 Characters / Environments / Scenes
                                │
                                ▼
                         Storyboard / Shots
                                │
                                ▼
                       Prompt + Context Build
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
        Image Generation                 Character/Scene QA
                │                               │
                └───────────────┬───────────────┘
                                ▼
                        Video Generation
                                │
                                ▼
                         Video QA / Scoring
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
              TTS/Voice     Translation    Music/SFX
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                         Lip Sync / Dubbing
                                │
                                ▼
                           Subtitles
                                │
                                ▼
                        Film / Scene Assembly
                                │
                                ▼
                            FFmpeg Render
                                │
                                ▼
                       Final Film Artifacts
```

Each stage is represented as a job and remains associated with the same `client_id` and `film_id`.

---

## 3. Architecture

```text
ai-engine/
├── src/
│   └── ai_engine/
│       ├── core/          # jobs, contracts, state, request lifecycle
│       ├── security/      # client/film authorization
│       ├── runtime/       # model/provider lifecycle and runtime routing
│       ├── generation/    # generation contracts and adapters
│       ├── media/         # audio, subtitles, lip-sync and assembly
│       ├── storage/       # film-scoped artifact persistence
│       ├── pipeline/      # application and production orchestration
│       └── flat modules/  # backward-compatible existing implementations
│
├── config/                # runtime/environment configuration
├── tests/                 # unit and integration tests
└── README.md
```

The domain-oriented packages provide the clean architecture surface while existing flat modules are retained where required for backward compatibility.

---

## 4. Core Components

### Core

Responsible for the execution contract of the AI platform:

- `AIJob`
- `JobOperation`
- job status/state machine
- retry handling
- request context
- job validation
- parent/child job lineage

Typical lifecycle:

```text
QUEUED → RUNNING → COMPLETED
              ├→ RETRYING → RUNNING
              ├→ FAILED
              └→ CANCELLED
```

### Security

Authorization is performed before AI execution or artifact access.

Every operation is scoped by:

```text
client_id
film_id
job_id
```

This prevents accidental cross-client or cross-film context access.

### Runtime

The runtime layer handles:

- provider registration
- model configuration
- lazy model initialization
- runtime caching
- worker-owned ML dependencies
- provider/model selection
- runtime cleanup

The API process does not need to initialize large CUDA models.

### Generation

Generation boundaries cover:

- screenplay/story analysis
- characters and environments
- storyboard/shot planning
- image generation
- video generation
- audio generation

The generation layer uses provider-neutral contracts so individual model implementations can be replaced independently.

### Media

Media processing covers:

- transcription
- TTS/voice generation
- dubbing
- translation
- music
- sound effects
- lip-sync
- subtitle generation
- media composition
- final film assembly

### Storage

Generated assets are treated as immutable film artifacts where practical and retain metadata such as:

```text
client_id
film_id
job_id
asset_id
asset_type
model/provider
model_version
input references
output location
checksum/integrity metadata
created_at
```

### Pipeline

The pipeline layer coordinates the individual stages into a complete film-generation workflow while delegating execution, authorization, retries and storage to the existing components.

---

## 5. Technology Stack

### Programming

- **Python 3.12+**
- Type hints and dataclasses
- Async/job-oriented application design where appropriate

### AI / ML

- **Hugging Face Transformers** — LLM/NLP model integration
- **Hugging Face Diffusers** — image/video diffusion model execution
- **Ollama** — local/open-source LLM runtime
- **Whisper** — speech-to-text/transcription
- Configurable TTS/audio runtimes
- Configurable lip-sync runtimes

The architecture intentionally avoids coupling the application to one proprietary model provider.

### Computer Vision / Media

- **FFmpeg** — video/audio processing and final rendering
- Image/video preprocessing and validation boundaries
- Subtitle generation
- Audio/video synchronization

### Backend / API Integration

- FastAPI-compatible application integration
- PostgreSQL-backed application architecture
- Background job/worker execution
- REST/service boundaries

### Storage

- **Amazon S3** for production film artifacts
- Local filesystem storage for development/testing where applicable
- Film-scoped object prefixes
- Artifact metadata and integrity tracking

### Infrastructure

- Docker-compatible workers
- Linux GPU workers
- NVIDIA CUDA-compatible infrastructure for large model workloads
- Environment-based runtime configuration
- CI/CD through GitHub Actions

### Development / Quality

- Pytest
- Static typing/type-aware interfaces
- Unit and integration test boundaries
- Explicit job lifecycle and retry semantics

---

## 6. Model Runtime Strategy

The engine separates **application orchestration** from **model execution**.

```text
                    AI Film Engine
                         │
                 Provider Registry
                         │
              Runtime Model Adapter
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       Ollama        Diffusers      Audio Worker
          │              │              │
          ▼              ▼              ▼
         LLM       Image / Video    TTS / Dubbing /
                                      Music / SFX /
                                      Lip-sync
```

This allows different models to be selected per environment or workload without changing the business pipeline.

Example deployment configuration concept:

```yaml
llm:
  provider: ollama
  model: qwen

image:
  provider: diffusers
  model: <configured-image-model>

video:
  provider: diffusers
  model: <configured-video-model>

audio:
  provider: worker
  endpoint: <configured-audio-worker>
```

Exact models should be selected based on GPU memory, latency, quality, licensing, throughput and commercial requirements.

---

## 7. GPU Worker Model

Large models are worker-owned rather than loaded by the API process.

```text
Client/API
    │
    ▼
Job Queue
    │
    ▼
AI Worker
    │
    ├── LLM runtime
    ├── Image model
    ├── Video model
    ├── Audio/TTS runtime
    └── Lip-sync runtime
    │
    ▼
Artifact Store
```

This separation allows the web/API tier to scale independently from GPU-heavy workloads.

For production, the infrastructure must provide compatible GPU hardware, CUDA/runtime dependencies, model weights, storage bandwidth and model licenses.

---

## 8. Film and Client Isolation

Isolation is a first-class requirement.

Every job contains:

```text
client_id
film_id
job_id
parent_job_id
operation
```

Authorization occurs before execution.

Artifact paths follow the same scope, conceptually:

```text
s3://<bucket>/clients/<client_id>/films/<film_id>/...
```

Therefore:

```text
Client A
└── Film A
    ├── screenplay
    ├── characters
    ├── storyboard
    ├── images
    ├── videos
    ├── audio
    ├── subtitles
    └── final-master

Client B
└── Film B
    ├── screenplay
    ├── characters
    ├── storyboard
    ├── images
    ├── videos
    ├── audio
    ├── subtitles
    └── final-master
```

The AI engine must never perform unrestricted global film-context retrieval.

---

## 9. Job Orchestration

A complete film is a job graph rather than one monolithic operation.

```text
Root Job: Story Analysis
        │
        ├── Image Generation
        │       └── Video Generation
        │
        ├── Audio Generation
        │       └── Lip Sync
        │
        └── Film Assembly
```

Parent/child job relationships provide traceability across the production workflow.

Failures are isolated to the relevant stage and can be retried according to the configured retry policy.

---

## 10. Multilingual Production

The engine supports a multilingual workflow through separate processing boundaries:

```text
Original Script
      ↓
Translation
      ↓
Language-specific Voice
      ↓
TTS / Dubbing
      ↓
Lip Sync
      ↓
Subtitles
      ↓
Localized Film
```

This allows the same visual film to produce multiple language releases without regenerating unrelated visual assets.

---

## 11. Artifact and Lineage Model

Every generated asset should be traceable to the job that produced it.

```text
Film
 └── Job
      └── Asset
           ├── model
           ├── model_version
           ├── prompt/input reference
           ├── parent asset/job
           ├── provider
           ├── checksum
           └── output location
```

This provides the foundation for reproducibility, auditing, debugging, cost tracking and model evaluation.

---

## 12. Observability and Operations

Production deployments should capture at least:

- job status
- execution duration
- attempt number
- provider/model
- model version
- input/output asset references
- failure reason
- GPU worker information
- token usage where applicable
- generated media duration/resolution
- estimated execution cost

This makes an AI generation job observable as a production workload rather than a black-box model call.

---

## 13. Quality Gates

The production pipeline should validate outputs between expensive stages.

Examples:

```text
Script validation
      ↓
Storyboard validation
      ↓
Image consistency validation
      ↓
Video quality validation
      ↓
Audio/video synchronization
      ↓
Subtitle validation
      ↓
Final render validation
```

Failed quality gates should prevent corrupted or incomplete artifacts from being promoted to the next production stage.

---

## 14. Resolution Strategy

The engine is designed to support multiple output resolutions, including high-resolution production workflows.

```text
Generation resolution
        ↓
Intermediate processing
        ↓
Upscaling / enhancement where configured
        ↓
Final mastering
```

4K/8K output is therefore treated as a **rendering and model-capability concern**, not as a hard-coded limitation of the orchestration layer.

Native model resolution, VRAM, temporal consistency, render time and storage requirements must be evaluated for the selected generation models.

---

## 15. Security Principles

1. Authorize before model execution.
2. Scope jobs to `client_id` and `film_id`.
3. Scope artifacts to the same film boundary.
4. Never use unrestricted cross-film context.
5. Keep credentials in environment/secret management rather than source code.
6. Keep heavy model runtimes isolated from the API process.
7. Record model/job lineage for auditability.

---

## 16. Example Application Surface

The domain packages expose a cleaner import surface while existing modules remain available for compatibility:

```python
from ai_engine.core import AIJob, JobOperation
from ai_engine.security import FilmAccessController
from ai_engine.runtime import ConfiguredRuntime
from ai_engine.generation import GenerationRequest
from ai_engine.media import AudioPipeline
from ai_engine.storage import ArtifactStore
from ai_engine.pipeline import AIService
```

The exact model/provider is selected by runtime configuration rather than embedded into the business pipeline.

---

## 17. Production Deployment

Recommended production topology:

```text
                    ┌─────────────────┐
                    │ Frontend / API  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ PostgreSQL      │
                    │ Jobs / Metadata │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Job Queue       │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
       GPU Worker       GPU Worker       Audio Worker
       LLM/Image        Video            TTS/Lip-sync
            │                │                │
            └────────────────┼────────────────┘
                             ▼
                       Amazon S3
                    Film-scoped assets
```

API servers should remain lightweight. GPU-heavy generation belongs in worker processes that can scale independently.

---

## 18. Development Principles

- Preserve the existing domain architecture.
- Prefer provider-neutral interfaces.
- Keep model loading lazy.
- Keep film/client isolation at every boundary.
- Treat generated media as versioned artifacts.
- Make jobs retryable and traceable.
- Keep model-specific code out of business orchestration.
- Validate expensive generated outputs before continuing.
- Keep production credentials outside source code.

---

## 19. Status

**AI application architecture:** Complete

**AI orchestration:** Complete

**Job lifecycle/retry model:** Complete

**Film/client isolation:** Implemented

**Provider/runtime abstraction:** Implemented

**Local/open-source runtime support:** Implemented through configured runtimes

**Production GPU execution:** Requires deployment-specific GPU infrastructure and model weights

**Provider-specific audio/lip-sync services:** Configurable through worker/runtime boundaries

The engine is therefore ready to serve as the AI execution layer for the broader AI Film Studio platform, with deployment-specific model selection and infrastructure configured independently from the core application architecture.
