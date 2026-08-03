from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.config import settings
from app.middleware import LoggingMiddleware

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KarigarJi backend starting — env=%s", settings.APP_ENV)
    yield
    logger.info("KarigarJi backend shutting down")


app = FastAPI(
    title="KarigarJi API",
    description="AI Fashion Design Platform — backend API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "prod" else None,
    redoc_url="/redoc" if settings.APP_ENV != "prod" else None,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}
