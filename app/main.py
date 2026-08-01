from __future__ import annotations

import logging
import sys

from fastapi import FastAPI

from app.api.decision import router as decision_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tilahan Saathi Decision Fusion Engine",
    description="Hybrid AI Decision Support System for oilseed crop cultivation",
    version="1.0.0",
)

app.include_router(decision_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Tilahan Saathi Decision Fusion Engine starting up")