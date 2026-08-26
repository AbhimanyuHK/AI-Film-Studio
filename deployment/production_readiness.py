"""Fail-fast production readiness gate.

This validates externally supplied configuration without printing secret values.
It is safe to run in CI, locally, or immediately before Terraform deployment.
"""
from __future__ import annotations

import os
import sys
from urllib.parse import urlparse

REQUIRED = {
    "AWS_REGION": "AWS region",
    "DATABASE_URL": "database connection string",
    "JWT_SECRET": "authentication secret",
    "AI_ENGINE_URL": "AI Engine URL",
    "AI_ENGINE_SERVICE_TOKEN": "AI Engine service token",
    "FILM_RUNTIME_URL": "Film Runtime URL",
    "FILM_RUNTIME_SERVICE_TOKEN": "Film Runtime service token",
    "S3_BUCKET": "artifact bucket",
    "MODEL_PROVIDER": "model provider",
    "LLM_MODEL": "LLM model",
    "IMAGE_MODEL": "image model",
    "VIDEO_MODEL": "video model",
    "STT_MODEL": "speech-to-text model",
    "TTS_MODEL": "text-to-speech model",
}

URLS = ("AI_ENGINE_URL", "FILM_RUNTIME_URL")


def main() -> int:
    missing = [key for key in REQUIRED if not os.getenv(key)]
    invalid = []
    for key in URLS:
        value = os.getenv(key, "")
        if value:
            parsed = urlparse(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                invalid.append(key)

    jwt = os.getenv("JWT_SECRET", "")
    if jwt and len(jwt) < 32:
        invalid.append("JWT_SECRET(<32 chars)")

    if missing or invalid:
        if missing:
            print("Missing required configuration:")
            for key in missing:
                print(f"  - {key}: {REQUIRED[key]}")
        if invalid:
            print("Invalid configuration:")
            for key in invalid:
                print(f"  - {key}")
        return 1

    print("Production configuration gate: PASS")
    print(f"AWS_REGION={os.environ['AWS_REGION']}")
    print(f"MODEL_PROVIDER={os.environ['MODEL_PROVIDER']}")
    for key in ("LLM_MODEL", "IMAGE_MODEL", "VIDEO_MODEL", "STT_MODEL", "TTS_MODEL"):
        print(f"{key}={os.environ[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
