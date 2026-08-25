from fastapi import FastAPI

app = FastAPI(
    title="AI Film Studio Control Plane",
    version="0.1.0",
)


@app.get("/health", tags=["platform"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["platform"])
def ready() -> dict[str, str]:
    return {"status": "ready"}
