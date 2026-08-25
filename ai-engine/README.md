# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio. The engine now has a **domain-oriented package structure** while preserving the existing implementation modules for backward compatibility.

## Architecture

```text
ai-engine/
├── src/ai_engine/
│   ├── core/          # jobs, contracts, state, request context
│   ├── security/      # client/film authorization
│   ├── runtime/       # model/provider runtime lifecycle
│   ├── generation/    # generation adapters and contracts
│   ├── media/         # audio, subtitles, lip-sync, assembly
│   ├── storage/       # film-scoped artifact persistence
│   ├── pipeline/      # application and production orchestration
│   │
│   └── existing modules remain as compatibility implementation modules
│
├── config/            # runtime configuration
└── tests/              # engine tests
```

The new packages are stable facades over the existing implementation. This deliberately avoids a large import-breaking file move while providing a clean architecture for all new development.

## Complete AI execution flow

```text
Screenplay
    ↓
Script analysis / reasoning
    ↓
Character + environment construction
    ↓
Storyboard / shot planning
    ↓
Image generation
    ↓
Character consistency / image validation
    ↓
Video generation
    ↓
Voice / translation / dubbing
    ↓
Music / SFX
    ↓
Lip-sync / subtitles
    ↓
Film assembly
    ↓
FFmpeg final render
    ↓
Film-scoped artifacts
```

## Package responsibilities

### `core/`

Owns the execution contract:

- `AIJob`
- `JobOperation`
- job validation
- job state machine
- retry lifecycle
- request context
- worker context

### `security/`

Owns the authorization boundary. A worker must be authorized for the requested `client_id` and `film_id` before model execution.

### `runtime/`

Owns model/provider lifecycle:

- lazy provider registry
- configured runtime routing
- Ollama runtime
- Hugging Face / Diffusers runtime
- runtime model adapters

Heavy ML dependencies remain lazy so API/test processes do not initialize CUDA models.

### `generation/`

Owns generation contracts and adapters for script analysis, image generation, video generation and audio-family operations.

### `media/`

Owns audio processing, translation/dubbing boundaries, subtitles, lip-sync and final film assembly.

### `storage/`

Owns film-scoped artifact persistence. Generated assets must remain associated with their `client_id`, `film_id` and `job_id`.

### `pipeline/`

Owns application-level orchestration. It coordinates the complete production flow without allowing individual stages to bypass authorization or job lifecycle controls.

## Runtime models

The runtime is configuration-driven. Current targets include:

- Qwen2.5-VL / Ollama-compatible reasoning for screenplay and storyboard analysis
- FLUX.1-dev / Diffusers for image generation
- HunyuanVideo / Diffusers for video generation
- Whisper-large-v3 for transcription
- Configured audio workers for TTS, dubbing, music, SFX and specialized lip-sync

Model licensing, VRAM requirements, weights and production availability must be validated for the selected deployment.

## Film isolation

Every AI job carries:

```text
client_id
film_id
job_id
parent_job_id
operation
```

The execution sequence is:

```text
Production Job
      ↓
Core job validation
      ↓
Film/client authorization
      ↓
Runtime/model execution
      ↓
Generation
      ↓
Media processing
      ↓
Film-scoped artifact storage
```

The engine must never perform global cross-film context retrieval.

```text
Film A → Film A jobs → Film A model context → Film A artifacts
Film B → Film B jobs → Film B model context → Film B artifacts
```

## Artifact contract

Generated artifacts should carry:

```text
client_id
film_id
job_id
object_key
content_type
size_bytes
sha256
```

S3 deployments should use film-scoped prefixes and encryption/KMS according to the environment policy.

## Multilingual production

Localization derives from a versioned master script. Master-language assets are immutable; translated, dubbed and lip-synced outputs are separate artifacts.

## Operational model

The API/backend submits jobs. AI workers perform heavy inference. This separation keeps CUDA/model dependencies out of the API process and permits independent scaling of LLM, image, video and audio workers.

```text
Backend/API
    ↓
Job queue
    ↓
AI worker
    ├── LLM runtime
    ├── Image GPU runtime
    ├── Video GPU runtime
    └── Audio worker
    ↓
Film-scoped artifact store
```

## Implementation status

The engine includes the complete application-level AI orchestration, security, job lifecycle, provider runtime abstraction, model adapters, generation boundaries, localization/media boundaries, artifact persistence and final assembly path. Actual production execution additionally requires the selected model weights, compatible GPU workers and deployment-specific audio/lip-sync services.

## New import surface

New code should prefer the domain packages:

```python
from ai_engine.core import AIJob, JobOperation
from ai_engine.security import FilmAccessController
from ai_engine.runtime import ConfiguredRuntime
from ai_engine.generation import GenerationRequest
from ai_engine.media import AudioPipeline
from ai_engine.storage import ArtifactStore
from ai_engine.pipeline import AIService
```

The original flat modules remain available so existing integrations are not broken by the restructure.
