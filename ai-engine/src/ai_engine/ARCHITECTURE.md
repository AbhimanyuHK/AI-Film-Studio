# AI Engine Architecture

```text
ai_engine/
├── core/       jobs, contracts, state and request lifecycle
├── security/   client/film authorization
├── runtime/    provider and model runtime lifecycle
├── generation/ generation adapters and contracts
├── media/      audio, subtitles, lip-sync and assembly
├── storage/    film-scoped artifact persistence
└── pipeline/   end-to-end application orchestration
```

These are domain facades over the existing implementation modules. The flat modules remain compatible so the restructure does not break current imports.

Execution: pipeline → core → security → runtime → generation → media → storage.
