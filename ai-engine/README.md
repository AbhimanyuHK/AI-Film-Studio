# AI Film Engine

Provider-neutral AI execution layer for AI Film Studio.

The control plane owns film isolation, jobs, assets and audit. This package owns model execution. Workers receive a job payload and write generated artifacts to the film-scoped storage boundary.

## Initial production stages

- `script_analysis`: screenplay structure, scenes, characters, locations, shot requirements
- `character_generation`: reference/character assets
- `environment_generation`: location and set references
- `storyboard`: shot-by-shot visual plan
- `shot_generation`: normalized shot prompts/specifications
- `video_generation`: image/video generation worker interface
- `voice_generation`: character voice tracks
- `translation`: localized dialogue/scripts
- `dubbing`: language-specific dialogue tracks
- `music_generation`: score/music tracks
- `sfx_generation`: shot-aligned sound effects
- `editing`: timeline assembly
- `upscaling`: resolution enhancement
- `final_render`: final deliverable generation

Models are deliberately configured outside the orchestration code so production deployments can select licensed open-source models per environment.
