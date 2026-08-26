Quickstart
==========

Prerequisites
-------------

Install:

* Git
* Docker and Docker Compose
* Python 3.12 for local Python development
* Node.js for frontend development when running the frontend outside Docker

Clone
-----

::

    git clone https://github.com/AbhimanyuHK/AI-Film-Studio.git
    cd AI-Film-Studio

Configure environment
---------------------

Copy the example files relevant to the services you run. Never commit real secrets.

AI model configuration is externalized. For example:

::

    MODEL_PROVIDER=ollama
    LLM_MODEL=qwen2.5:7b
    IMAGE_MODEL=flux
    VIDEO_MODEL=wan
    STT_MODEL=whisper-large-v3
    TTS_MODEL=kokoro

For local Ollama execution, set ``OLLAMA_BASE_URL`` to the reachable Ollama endpoint.

Start the stack
---------------

::

    docker compose --env-file .env up --build

Check service health using the health endpoints documented by each service.

Run tests
---------

Backend and Python services use pytest. The frontend uses the package manager scripts defined by its ``package.json``. CI is the authoritative integration gate.

Production note
---------------

The local Compose stack is for development and integration testing. Production should use AWS-managed infrastructure, external secrets, TLS, IAM, monitoring, and the deployment workflows described in the deployment and AWS chapters.
