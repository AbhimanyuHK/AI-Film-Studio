# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio. The existing engine architecture remains unchanged: model execution is film-scoped, jobs carry client/film identity, and generated artifacts remain inside the owning film storage boundary.

## Complete execution flow

```text
Screenplay
 -> script analysis / storyboard reasoning
 -> character + environment generation
 -> storyboard / shot planning
 -> image generation
 -> video generation
 -> voice / translation / dubbing
 -> music / SFX
 -> lip-sync / subtitles
 -> film assembly / final render
```

## Runtime implementation

The engine now has real worker-side runtime bindings in the existing architecture:

- `ollama_runtime.py` — local/open-source LLM execution through Ollama HTTP.
- `huggingface_runtime.py` — lazy Diffusers image/video execution on GPU workers.
- `configured_runtime.py` — stage router for LLM, image, video and configurable audio workers.
- `adapters.py` — production adapters now execute through the runtime instead of returning placeholder success responses.
- `production_pipeline.py` — sequential end-to-end AI stage execution.
- `provider_runtime.py` — lazy provider registry for deployment-specific runtimes.

Heavy ML imports remain lazy so API/test processes do not initialize CUDA models.

## Existing architecture

```text
Production Job
      |
      v
AIJob validation + film authorization
      |
      v
AI adapters / ProductionFilmPipeline
      |
      +--> Ollama (script / reasoning / translation)
      +--> Diffusers / FLUX (images)
      +--> Diffusers / HunyuanVideo (video)
      +--> configured audio worker (voice / dubbing / music / SFX)
      |
      v
Film-scoped artifacts
```

## Model configuration

Models remain configuration-driven. Current targets include Qwen2.5-VL for screenplay/storyboard reasoning, FLUX.1-dev for image generation, HunyuanVideo for video generation and Whisper-large-v3 for transcription. Model licensing, VRAM and deployment availability must be validated before production use.

The default local reasoning path uses Ollama and can be changed with `OLLAMA_ENDPOINT` and `OLLAMA_MODEL`. Audio-family stages use `AI_AUDIO_ENDPOINT` so TTS, dubbing, music, SFX and lip-sync implementations can be deployed independently without changing orchestration.

See `config/runtime.env.example` for the runtime variables.

## Film isolation

Every AI job carries `client_id`, `film_id`, `job_id`, `parent_job_id` and operation information. Authorization occurs before execution and artifact access. Storage keys remain film-scoped and the engine must never perform global cross-film context retrieval.

```text
Film A -> Film A jobs -> Film A GPU context -> Film A storage
Film B -> Film B jobs -> Film B GPU context -> Film B storage
```

## Artifact contract

Generated artifacts should carry `client_id`, `film_id`, `job_id`, `object_key`, `content_type`, `size_bytes` and SHA-256 integrity information.

## Multilingual production

The language catalog supports the configured production languages. Localization derives from a versioned master script; master-language assets are never overwritten.

## Implementation status

### Implemented

- Film/client authorization and worker context
- AI job contract, validation, retry and state machine
- Existing provider registry and lazy model lifecycle
- Runtime-backed script/LLM execution through Ollama
- Runtime-backed image generation through Diffusers
- Runtime-backed video generation through Diffusers
- Production AI adapter layer
- End-to-end production stage runner
- Existing character, environment, storyboard, consistency and image-validation components
- Existing transcription, language, subtitle, lip-sync and film-assembly boundaries
- Film-scoped artifact storage and S3 encryption/KMS support
- Runtime environment template and adapter tests

### Deployment bindings

Voice/TTS, dubbing, music, SFX and specialized lip-sync engines are intentionally exposed as worker/runtime endpoints because their model choices and GPU requirements vary by deployment. The orchestration is complete and does not require another repository restructure; production deployment only needs the selected worker implementations and their model artifacts.
