# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio. The engine is now organized by domain while retaining existing implementation modules for backward compatibility.

## Architecture

```text
ai-engine/
├── src/ai_engine/
│   ├── core/       # jobs, contracts, state, request lifecycle
│   ├── security/   # client/film authorization
│   ├── runtime/    # model/provider lifecycle
│   ├── generation/ # generation adapters
│   ├── media/      # audio, subtitles, lip-sync, assembly
│   ├── storage/    # film-scoped artifacts
│   ├── pipeline/   # application orchestration
│   └── existing flat modules remain as compatibility modules
├── config/
└── tests/
```

## Complete AI flow

```text
Screenplay → analysis → characters/environments → storyboard →
image generation → consistency/validation → video generation →
voice/translation/dubbing → music/SFX → lip-sync/subtitles →
film assembly → FFmpeg final render → film-scoped artifacts
```

## Responsibilities

- **core** — AI jobs, operations, validation, state/retry lifecycle and request context.
- **security** — authorization for `client_id` + `film_id` before execution.
- **runtime** — lazy provider registry, configured routing, Ollama, Diffusers and runtime adapters.
- **generation** — script/image/video/audio generation contracts and adapters.
- **media** — audio, localization, subtitles, lip-sync and assembly boundaries.
- **storage** — film-scoped artifact persistence and integrity metadata.
- **pipeline** — complete production orchestration.

## Runtime targets

Configuration supports Ollama/open-source reasoning, Diffusers image/video runtimes, Whisper transcription and configurable audio workers for TTS, dubbing, music, SFX and specialized lip-sync. Production still requires compatible GPU workers, model weights, licenses and deployment-specific audio services.

## Isolation

Every job carries `client_id`, `film_id`, `job_id`, `parent_job_id` and operation. Authorization occurs before model execution and artifact access. No global cross-film context retrieval is permitted.

```text
Film A → Film A jobs → Film A runtime context → Film A artifacts
Film B → Film B jobs → Film B runtime context → Film B artifacts
```

## Operational model

```text
Backend/API → Job queue → AI worker → model runtime → film-scoped artifact store
```

Heavy ML dependencies remain worker-owned and lazy-loaded so API/test processes do not initialize CUDA models.

## New import surface

```python
from ai_engine.core import AIJob, JobOperation
from ai_engine.security import FilmAccessController
from ai_engine.runtime import ConfiguredRuntime
from ai_engine.generation import GenerationRequest
from ai_engine.media import AudioPipeline
from ai_engine.storage import ArtifactStore
from ai_engine.pipeline import AIService
```

The original flat modules remain available for existing integrations.
