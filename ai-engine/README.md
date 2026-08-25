# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio.

The control plane owns film isolation, jobs, assets and audit. This package owns model execution. Workers receive a film-scoped job payload and write generated artifacts to the corresponding film-scoped storage boundary.

## Architecture

```text
Production Job
      |
      v
GPU Job Scheduler
      |
      v
Film-scoped GPU Worker
      |
      v
Model Runtime / Model Manager
      |
      +-------------------+-------------------+
      |                   |                   |
     vLLM             Diffusers          Audio Runtime
      |                   |                   |
  LLM/VLM             Image/Video        ASR/TTS/Music
      |                   |                   |
      +-------------------+-------------------+
                          |
                          v
                    Artifact Metadata
                          |
                          v
                    Film-scoped S3
```

Heavy ML dependencies are loaded only by GPU workers. The API/control-plane process must not load CUDA models during startup or test collection.

## Production stages

- `script_analysis`: screenplay structure, scenes, characters, locations and shot requirements
- `character_generation`: reference/character assets and character identity references
- `environment_generation`: location and set references
- `storyboard`: shot-by-shot visual plan
- `shot_generation`: normalized shot prompts/specifications
- `video_generation`: image-to-video/text-to-video generation
- `voice_generation`: character voice tracks
- `transcription`: source dialogue/audio transcription
- `translation`: localized dialogue/scripts
- `dubbing`: language-specific dialogue tracks and synchronization
- `music_generation`: score/music tracks
- `sfx_generation`: shot-aligned sound effects
- `editing`: timeline assembly
- `upscaling`: resolution enhancement
- `final_render`: final deliverable generation

## Model strategy

Models are configuration-driven rather than embedded in the orchestration layer. A deployment can select a model per stage without changing the DAG or SaaS control plane.

Current configured production candidates include:

| Stage | Model | Runtime | VRAM target |
|---|---|---|---:|
| Script analysis / storyboard | Qwen2.5-VL-72B | vLLM/Hugging Face | 80 GB+
| Character generation | FLUX.1-dev | Diffusers | 24 GB+
| Environment generation | FLUX.1-dev | Diffusers | 24 GB+
| Video generation | HunyuanVideo | Diffusers | 80 GB+
| Transcription | Whisper-large-v3 | Hugging Face | 8 GB+

These are integration targets, not a claim that every model is already wired for production inference. Each model must use its supported pipeline and license before deployment.

## Worker configuration

GPU workers are configured with environment variables:

```text
GPU_WORKER_ID
GPU_DEVICE
GPU_WORKER_CONCURRENCY
FILM_ASSET_BUCKET
```

Workers are deliberately film/job scoped. A worker must never resolve an asset by a global filename or accept storage credentials belonging to another film deployment.

## Artifact contract

Every generated artifact should carry:

```text
film_id
object_key
content_type
size_bytes
sha256 checksum
```

The checksum provides integrity verification before an artifact is promoted to the next production stage.

## Model lifecycle

`ModelManager` lazily loads models inside GPU workers and caches them for reuse. Models can be unloaded to release GPU memory between workloads.

```text
worker start
   -> no model loaded
job arrives
   -> select stage/model
   -> lazy load
   -> execute
   -> cache for reuse
   -> optionally unload
```

## Isolation requirement

AI Film Studio is a multi-tenant SaaS, but **film data must never cross film boundaries**.

```text
Film A
  -> Film A job IDs
  -> Film A GPU context
  -> Film A S3 prefix/bucket
  -> Film A metadata

Film B
  -> Film B job IDs
  -> Film B GPU context
  -> Film B S3 prefix/bucket
  -> Film B metadata
```

For high-security client deployments, a separate cloud account/project, storage boundary and GPU worker pool can be provisioned for each film. Shared infrastructure is only acceptable when strict tenant isolation controls are enforced.

## Multilingual production

The studio supports the planned localization set:

- Kannada
- Hindi
- Tamil
- Telugu
- Malayalam
- Marathi
- Bengali
- English (US)
- English (UK)
- Chinese (Mandarin)
- Japanese
- French

Localization should originate from a versioned master script. Translations and dubbed assets are derived artifacts; the master-language assets are never overwritten.

## Implementation status

### Infrastructure implemented

- AI stage contracts
- Provider/model registry
- Model configuration
- GPU worker boundary
- Bounded GPU scheduler
- Lazy model lifecycle manager
- GPU health inspection
- Diffusers/vLLM backend boundaries
- Artifact integrity metadata
- Film-scoped execution contract
- Multilingual language configuration

### Actual model pipelines still to integrate

- Qwen-VL production inference for screenplay analysis/storyboarding
- FLUX production image pipeline and character consistency/LoRA
- HunyuanVideo production video pipeline
- Whisper transcription worker
- Translation worker
- multilingual TTS/voice pipeline
- lip-sync/dubbing pipeline
- music generation
- SFX generation
- timeline/video assembly
- 4K/8K enhancement
- final render and delivery

The current code intentionally separates these integrations from the control plane so models can be upgraded independently.
