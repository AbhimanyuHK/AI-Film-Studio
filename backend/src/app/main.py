from fastapi import FastAPI

from app.api import router as api_router
from app.environment_api import router as environment_router
from app.job_api import router as job_router
from app.asset_api import router as asset_router

app = FastAPI(
    title="AI Film Studio Control Plane",
    version="0.1.0",
)

app.include_router(api_router)
app.include_router(environment_router)
app.include_router(job_router)
app.include_router(asset_router)


@app.get("/health", tags=["platform"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["platform"])
def ready() -> dict[str, str]:
    return {"status": "ready"}
