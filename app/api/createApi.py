from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.errors import registerErrorHandlers
from app.api.frontendFiles import registerFrontendFiles
from app.api.routers import apiRouter
from app.config.settings import Settings, get_settings
from app.infrastructure.persistence.database import DatabaseBootstrapper
from app.infrastructure.persistence.database.session import SessionLocal, engine
from app.infrastructure.tasks import LocalTaskManager


def createApi(
    *,
    settings: Settings | None = None,
    database_engine: Engine | None = None,
    session_factory: sessionmaker[Session] | None = None,
    bootstrap_database: bool = True,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_engine = database_engine or engine
    resolved_session_factory = session_factory or SessionLocal

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if bootstrap_database:
            DatabaseBootstrapper(
                resolved_engine,
                resolved_session_factory,
            ).bootstrap()
        yield
        app.state.taskManager.shutdown(wait=False)

    application = FastAPI(
        title=resolved_settings.app_name,
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    application.state.databaseEngine = resolved_engine
    application.state.sessionFactory = resolved_session_factory
    application.state.taskManager = LocalTaskManager(
        resolved_settings.task_worker_count
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.corsOriginList,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )
    registerErrorHandlers(application)
    application.include_router(apiRouter, prefix="/api")
    if resolved_settings.frontendDirectoryPath is not None:
        registerFrontendFiles(
            application,
            resolved_settings.frontendDirectoryPath,
        )
    return application
