from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run("ai_engine.http_api:app", host=os.getenv("AI_ENGINE_HOST", "0.0.0.0"), port=int(os.getenv("AI_ENGINE_PORT", "8080")))


if __name__ == "__main__":
    main()
