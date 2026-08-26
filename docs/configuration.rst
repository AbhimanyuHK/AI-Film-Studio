Configuration
=============

Configuration principles
------------------------

Configuration is supplied from outside the application image. The same container image can be promoted across development, staging, and production with different environment values.

Environment files
-----------------

Example files are provided beside the services. They document supported variables without containing real credentials.

Typical AI variables:

::

    MODEL_PROVIDER=ollama
    LLM_MODEL=qwen2.5:7b
    IMAGE_MODEL=flux
    VIDEO_MODEL=wan
    STT_MODEL=whisper-large-v3
    TTS_MODEL=kokoro
    TRANSLATION_MODEL=nllb
    LIPSYNC_MODEL=wav2lip
    EMBEDDING_MODEL=nomic-embed-text
    OLLAMA_BASE_URL=http://localhost:11434

Secrets
-------

Do not put production secrets in Git. Use AWS Secrets Manager, SSM Parameter Store, GitHub Environment secrets, or an equivalent secret manager.

Examples include:

* ``JWT_SECRET``
* ``DATABASE_PASSWORD``
* ``AI_PROVIDER_API_KEY``
* ``AI_ENGINE_SERVICE_TOKEN``
* ``FILM_RUNTIME_SERVICE_TOKEN``

Model configuration
-------------------

Environment variables choose deployment defaults. ``models/registry.yaml`` remains the allowlist/governance layer. A request must not be able to select an unapproved production model merely by supplying an arbitrary model identifier.

Configuration precedence
------------------------

Recommended precedence is:

1. deployment/environment defaults;
2. approved model registry;
3. film-specific configuration where supported;
4. job-level overrides only when explicitly allowed by policy.

Never place provider API keys or passwords in YAML model registry files.
