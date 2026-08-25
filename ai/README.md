# AI Platform Resources

The `ai/` directory is the AI platform resource and policy layer for AI Film Studio. It complements `ai-engine/` and does not duplicate inference or orchestration Python code.

## Responsibility

`ai/` owns declarative AI resources:

- model registry and capability mapping
- production workflow definitions
- quality gates and evaluation policy
- environment-specific AI configuration
- AI governance and runtime policy

`ai-engine/` owns executable AI behavior: provider adapters, generation, validation, localization, assembly, job execution and runtime integration.

## Structure

```text
ai/
├── configs/
│   ├── development.yaml
│   └── production.yaml
├── evaluation/
│   └── quality-gates.yaml
├── model-registry.yaml
├── workflows/
│   └── film-production.yaml
└── README.md
```

## Model registry

`model-registry.yaml` maps logical capabilities to providers and models. Development may use configurable model identifiers; production requires explicit model versions. Secrets and credentials are never committed here.

## Production workflow

`workflows/film-production.yaml` defines the dependency graph:

```text
script_analysis
      ├── character_generation
      ├── environment_generation
      │            │
      └────────────┴──► storyboard
                           │
                      shot_generation
                           │
                      video_generation
                           │
                  ┌────────┴────────┐
             voice_generation   translation
                  │                 │
                  └───────┬─────────┘
                          ▼
                       dubbing
                          │
               music + SFX + video
                          │
                       editing
                          │
                       upscaling
                          │
                     final_render
```

The backend persists the operational graph as AI jobs; the AI Engine executes individual operations.

## Quality gates

`evaluation/quality-gates.yaml` defines fail-closed validation requirements for screenplay, image, video, audio, localization and final-render outputs. Final rendering and safety/policy failures require human review. The policies are enforced by executable validators in `ai-engine/validation/`.

## Environment configuration

| Capability | Development | Production |
|---|---|---|
| Model versions | Can be unpinned | Must be explicit |
| AI Engine URL | Local/default | Environment configuration |
| Artifact bucket | Development bucket | Production bucket |
| Film scope | Required | Required |
| Provider auth | Development-compatible | Required |
| Final-render review | Configurable | Required |

No provider API key, access token, secret, model weight, generated asset or production screenplay should be committed here.

## End-to-end architecture

```text
Frontend
   ↓
FastAPI Backend
   ↓
PostgreSQL AI Jobs
   ↓
AI Worker
   ↓
AI Engine
   ├── resolves model/provider from AI resources
   ├── executes generation
   ├── validates output
   └── writes film-scoped artifacts
             ↓
            S3
```

## Boundary rules

1. `ai/` contains configuration and governance, not inference implementation.
2. `ai-engine/` contains executable AI functionality.
3. Backend owns authorization and durable job state.
4. Model credentials come from runtime secrets/environment configuration.
5. Every operation is scoped to a client, film and environment.
6. Production model versions are pinned.
7. Required quality gates fail closed.
8. Human review remains mandatory for configured high-impact production gates.

## Status

The `ai/` resource layer is complete for the current platform architecture: model registry, production workflow, environment configuration and quality-gate policies are now defined for the Backend/AI Engine boundary.
