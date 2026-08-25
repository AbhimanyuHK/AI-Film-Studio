from __future__ import annotations

import asyncio
import logging

from app.ai_worker import AIJobWorker

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await AIJobWorker().run()


if __name__ == "__main__":
    asyncio.run(main())
