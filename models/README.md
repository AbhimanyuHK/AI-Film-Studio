# Production Model Registry

The registry is the policy boundary for approved AI models. Runtime configuration may select concrete versions, but production deployments must pin versions and provide licensing metadata.

## Required metadata

- name/version
- license
- commercial-use status
- redistribution requirements
- attribution requirements
- fine-tuning restrictions
- deployment compatibility

## Isolation

Base models can be standardized across environments. Film-specific LoRAs, fine-tuned checkpoints, embeddings and generated model artifacts must remain private to the film environment.

`registry.yaml` intentionally uses provider/model placeholders until a production deployment approves concrete providers and versions.
