from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

router = APIRouter(tags=["platform"])


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready/db")
async def database_ready(session: AsyncSession = __import__("fastapi").Depends(get_db)) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}
