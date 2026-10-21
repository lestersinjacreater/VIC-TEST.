"""FastAPI application factory.

Run locally:  uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import BACKEND_DIR, get_settings
from app.db import get_engine, session_factory
from app.errors import install_handlers
from app.ml import model
from app.routers.api import router
from app.services import reports, seed

log = logging.getLogger("linda")


def run_migrations() -> None:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", get_settings().database_url)
    cfg.attributes["configure_logger"] = False
    with get_engine().begin() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")


def init_app_data() -> None:
    run_migrations()
    with session_factory()() as db:
        if not seed.is_seeded(db):
            counts = seed.seed(db)
            log.info("Seeded demo data: %s", counts)
        reports.purge_expired(db)
    model.metrics()  # loads or trains the model once


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if settings.auto_init:
            init_app_data()
        yield

    app = FastAPI(
        lifespan=lifespan,
        title="LINDA API",
        description="Scam intelligence that connects the dots. Demo "
                    "backend: all data is synthetic or simulated.",
        version="1.0.0",
    )
    install_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "X-Linda-Client"],
    )

    @app.middleware("http")
    async def access_log_and_headers(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        # Path only: no query strings, bodies or client identifiers.
        log.info("%s %s %s %.0fms", request.method, request.url.path,
                 response.status_code,
                 (time.perf_counter() - start) * 1000)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(router)

    @app.get("/")
    def root():
        return {"name": "LINDA API", "docs": "/docs", "health": "/api/health"}

    return app


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
app = create_app()
