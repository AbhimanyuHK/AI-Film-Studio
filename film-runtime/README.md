# Film Runtime

This component is deployed separately into each film's isolated AWS environment.

It owns:
- Film database
- Film object storage
- Film RAG/vector index
- Film-specific prompts and knowledge
- Character and location assets
- Film-specific LoRAs/fine-tuned models
- Production jobs and AI orchestration

A runtime must never access another film environment.
