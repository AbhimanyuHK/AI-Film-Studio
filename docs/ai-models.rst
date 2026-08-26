AI Models and Providers
========================

Model architecture
------------------

AI-Film-Studio keeps model selection separate from business logic. The AI Engine receives external configuration and uses provider/model adapters. The model registry defines what is approved.

Supported capability categories
-------------------------------

* LLM / text generation
* image generation
* video generation
* speech-to-text
* text-to-speech
* translation
* lip-sync
* embeddings
* reranking

Changing a model
----------------

A deployment can change a model through environment configuration without changing application source code. For example:

::

    LLM_MODEL=qwen2.5:7b

can be changed to another approved model and the service restarted.

Provider credentials
--------------------

Credentials are injected at runtime. They should not be stored in ``models/registry.yaml`` or source files.

Ollama
------

For local/self-hosted LLM workflows, configure:

::

    MODEL_PROVIDER=ollama
    OLLAMA_BASE_URL=http://ollama:11434
    LLM_MODEL=qwen2.5:7b

The exact model must exist in the Ollama environment before production execution.

Production providers
--------------------

A production provider adapter should expose a stable interface to the AI Engine. The application should treat provider failures as retryable or terminal according to error classification and should persist useful error information in the job state.

Model governance
----------------

Before enabling a model in production, verify:

* model identifier and version;
* provider;
* supported modality;
* commercial license;
* data/privacy requirements;
* GPU/CPU requirements;
* expected latency and cost;
* maximum context/input limits;
* output safety and validation requirements.
