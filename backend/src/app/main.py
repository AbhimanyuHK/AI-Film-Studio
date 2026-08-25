from fastapi import FastAPI

from app.api import router as api_router

app = FastAPI(
    title="AI Film Studio Control Plane",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health", tags=["platform"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["platform"])
def ready() -> dict[str, str]:
    return {"status": "ready"}
