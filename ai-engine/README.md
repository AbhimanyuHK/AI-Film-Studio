# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio.

The control plane owns film isolation, jobs, assets and audit. This package owns model execution. Workers receive a film-scoped job payload and write generated artifacts to the corresponding film-scoped storage boundary.

## Current pipeline

```text
Screenplay
   -> Qwen structured analysis
   -> Character + Environment Bible
   -> Storyboard / Shot Plan
   -> Stable Shot Prompt
   -> Image Generation
   -> Image Validation
   -> Video Generation
   -> Audio / Dubbing
   -> Editing / Final Render
```

The character/environment bibles are reusable sources of truth for downstream generation. Shot prompts carry those continuity anchors into image/video generation.

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
- `character_generation`: reference/character assets and identity references
- `environment_generation`: location and set references
- `storyboard`: shot-by-shot visual plan
- `shot_generation`: normalized shot prompts/specifications
- `image_generation`: cinematic reference/keyframe generation
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

Models are configuration-driven rather than embedded in orchestration. A deployment can select a model per stage without changing the SaaS control plane.

Current configured candidates include:

| Stage | Model | Runtime | VRAM target |
|---|---|---|---:|
| Script analysis / storyboard | Qwen2.5-VL-72B | vLLM/Hugging Face | 80 GB+ |
| Character generation | FLUX.1-dev | Diffusers | 24 GB+ |
| Environment generation | FLUX.1-dev | Diffusers | 24 GB+ |
| Video generation | HunyuanVideo | Diffusers | 80 GB+ |
| Transcription | Whisper-large-v3 | Hugging Face | 8 GB+ |

These are integration targets. Each model must use its supported pipeline and license before deployment.

## Implemented AI

### 1. Structured screenplay analysis

`script_analysis.py` converts screenplay text into typed `ScreenplayAnalysis` containing title, logline, characters, locations and scenes. `qwen_backend.py` provides the structured-Qwen adapter boundary.

### 2. Production bibles

`character_bible.py` creates reusable character and environment bibles. Character bibles contain identity, age range, appearance, wardrobe, personality and a stable visual anchor. Environment bibles contain architecture, lighting, palette and continuity anchors.

### 3. Storyboard / shot planning

`storyboard.py` creates typed shots from scenes and production bibles. Each shot carries camera, lens, movement, lighting, action, dialogue, characters, location and continuity anchors.

`shot_prompts.py` converts a shot into a normalized prompt for downstream generation.

### 4. Film-scoped image generation contract

`image_generation.py` defines the image generation request/result contract and executes an already-loaded image pipeline. Requests require `film_id` and `shot_id`, keeping generated work traceable to the owning film. Model loading remains in `ModelManager`.

### 5. Image validation

`image_validation.py` validates generated dimensions before an artifact is promoted to the next stage.

## Worker configuration

```text
GPU_WORKER_ID
GPU_DEVICE
GPU_WORKER_CONCURRENCY
FILM_ASSET_BUCKET
```

Workers are film/job scoped. A worker must never resolve an asset by a global filename or accept storage credentials belonging to another film deployment.

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

AI Film Studio is multi-tenant, but **film data must never cross film boundaries**.

```text
Film A -> Film A jobs -> Film A GPU context -> Film A storage
Film B -> Film B jobs -> Film B GPU context -> Film B storage
```

For high-security client deployments, a separate cloud account/project, storage boundary and GPU worker pool can be provisioned for each film. Shared infrastructure is only acceptable when strict tenant isolation controls are enforced.

## Multilingual production

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

Localization originates from a versioned master script. Translations and dubbed assets are derived artifacts; the master-language assets are never overwritten.

## Implementation status

### Implemented

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
- Structured screenplay analysis
- Qwen structured-inference adapter boundary
- Character production bible generation
- Environment production bible generation
- Stable visual prompt generation
- Storyboard and shot planning
- Normalized shot prompt generation
- Film-scoped image generation contract
- Image output dimension validation

### Still to integrate

- Live Qwen/vLLM production client
- Real FLUX/Diffusers pipeline loading and generation
- Character reference conditioning and LoRA identity consistency
- HunyuanVideo production video pipeline
- Shot continuity/quality scoring
- Whisper transcription worker
- Translation worker
- multilingual TTS/voice pipeline
- lip-sync/dubbing pipeline
- music generation
- SFX generation
- timeline/video assembly
- 4K/8K enhancement
- final render and delivery

The code deliberately keeps provider-specific model loading separate from the control plane so models can be upgraded independently.
