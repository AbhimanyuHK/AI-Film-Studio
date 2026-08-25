# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio. The existing engine architecture remains unchanged: model execution is film-scoped, jobs carry client/film identity, and generated artifacts remain inside the owning film storage boundary.

## Complete AI execution flow

```text
Screenplay
   -> structured analysis
   -> character/environment bibles
   -> storyboard / shot plan
   -> stable shot prompts
   -> image generation
   -> image validation
   -> video generation
   -> audio / dubbing
   -> lip-sync / subtitles
   -> editing / final render
```

The runtime now connects the existing job contract, authorization, retry/state machine and AI pipeline through `AIService`/`FilmAIPipeline`. Provider instances are created lazily by `ProviderRegistry`, so GPU/model dependencies remain worker-only.

## Existing architecture

```text
Production Job
      |
      v
AIJob validation + film authorization
      |
      v
FilmAIPipeline
      |
      v
AIJobExecutor
      |
      +--> script analysis
      +--> image generation
      +--> video generation
      +--> audio generation
      +--> lip sync
      +--> film assembly
      |
      v
Film-scoped artifacts
```

## Provider runtime

`provider_runtime.py` provides a lightweight lazy registry. Applications register a stage with a `ProviderConfig` and factory. The factory is not invoked until that stage is requested. This keeps heavy ML imports and CUDA model loading out of API startup and test collection.

Provider configuration is deployment-specific. Credentials are read from environment variables and are never stored in source code.

Example configuration concept:

```text
stage: image_generation
provider: diffusers
model: FLUX.1-dev
endpoint: optional worker endpoint
api_key_env: optional secret variable
```

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

Models remain configuration-driven rather than embedded in orchestration. Current integration targets include Qwen2.5-VL for screenplay/storyboard reasoning, FLUX.1-dev for image generation, HunyuanVideo for video generation and Whisper-large-v3 for transcription. Each deployment must validate model licensing, hardware requirements and provider availability before production use.

## Film isolation

Every AI job carries:

```text
client_id
film_id
job_id
parent_job_id
operation
```

Authorization happens before execution and before artifact access. Generated artifacts use film-scoped storage keys. The engine must never retrieve context using a global filename or cross-film search.

```text
Film A -> Film A jobs -> Film A GPU context -> Film A storage
Film B -> Film B jobs -> Film B GPU context -> Film B storage
```

For high-security deployments, a separate cloud account/project, storage boundary and GPU worker pool can be provisioned per film. Shared infrastructure is only acceptable with strict tenant isolation controls.

## Artifact contract

Generated artifacts should carry:

```text
client_id
film_id
job_id
object_key
content_type
size_bytes
sha256 checksum
```

The checksum is used for integrity verification before promotion between stages.

## Multilingual production

The engine supports the configured language catalog including Kannada, Hindi, Tamil, Telugu, Malayalam, Marathi, Bengali, English US/UK, Mandarin, Japanese and French. Localization must derive from a versioned master script; master-language assets are never overwritten.

## Implementation status

### Implemented in the existing architecture

- AI stage contracts
- Film-scoped AI jobs
- Client/film authorization
- Request and worker context
- Job validation
- Retry/state machine
- AI job executor
- Complete AI pipeline orchestration
- `AIService` application facade
- Provider/model registry with lazy initialization
- Model configuration boundaries
- GPU worker boundary
- Film-scoped artifact storage
- S3 encryption/KMS support
- Artifact integrity metadata
- Structured screenplay analysis contracts
- Character/environment production bibles
- Storyboard and shot planning
- Stable shot prompt generation
- Film-scoped image generation contract
- Image output validation
- Subtitle/lip-sync/film assembly contracts

### Model integrations still deployment-specific

The engine deliberately does not download or initialize large models during repository import. A GPU deployment must bind real Qwen/vLLM, Diffusers/FLUX, HunyuanVideo, Whisper, TTS, translation and lip-sync runtimes to the provider registry. This is an infrastructure/deployment step rather than a control-plane dependency.

The architecture is ready for those runtimes without another repository restructure.
