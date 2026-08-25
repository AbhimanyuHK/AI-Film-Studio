from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import router as api_router
from app.environment_api import router as environment_router
from app.job_api import router as job_router
from app.asset_api import router as asset_router
from app.health import router as health_router

app = FastAPI(title="AI Film Studio Control Plane", version="0.1.0")

allowed_origins = [origin.strip() for origin in os.getenv("FRONTEND_CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(environment_router)
app.include_router(job_router)
app.include_router(asset_router)
app.include_router(health_router)


@app.get("/health", tags=["platform"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["platform"])
def ready() -> dict[str, str]:
    return {"status": "ready"}
