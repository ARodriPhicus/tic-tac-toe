"""Aplicación FastAPI: composición, ciclo de vida (init BD) y mapeo de errores a HTTP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..application.exceptions import (
    AlreadyInGame,
    ApplicationError,
    GameAlreadyFull,
    GameNotFound,
    InvalidCredentials,
    NotAuthenticated,
    UsernameTaken,
)
from ..config import Settings, get_settings
from ..domain.exceptions import (
    CellOccupied,
    DomainError,
    GameNotInProgress,
    InvalidPosition,
    NotYourTurn,
    PlayerNotInGame,
)
from ..infrastructure.db import create_engine, create_session_factory, init_db
from .routers import auth, games

# Mapeo de excepciones de dominio/aplicación a códigos HTTP (contrato uniforme).
_ERROR_STATUS: dict[type[Exception], int] = {
    InvalidPosition: status.HTTP_400_BAD_REQUEST,
    CellOccupied: status.HTTP_409_CONFLICT,
    NotYourTurn: status.HTTP_403_FORBIDDEN,
    GameNotInProgress: status.HTTP_409_CONFLICT,
    PlayerNotInGame: status.HTTP_403_FORBIDDEN,
    UsernameTaken: status.HTTP_409_CONFLICT,
    InvalidCredentials: status.HTTP_401_UNAUTHORIZED,
    NotAuthenticated: status.HTTP_401_UNAUTHORIZED,
    GameNotFound: status.HTTP_404_NOT_FOUND,
    GameAlreadyFull: status.HTTP_409_CONFLICT,
    AlreadyInGame: status.HTTP_409_CONFLICT,
}


def _make_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(settings.database_url)
        await init_db(engine)
        app.state.settings = settings
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        try:
            yield
        finally:
            await engine.dispose()

    return lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    """Factory de la app (permite inyectar Settings en tests)."""
    settings = settings or get_settings()

    app = FastAPI(
        title="Tic-Tac-Toe API",
        version="0.1.0",
        description="Backend de Tres en Raya: partidas por turnos, persistencia, auth y score.",
        lifespan=_make_lifespan(settings),
    )

    @app.exception_handler(DomainError)
    @app.exception_handler(ApplicationError)
    async def _domain_error_handler(_: Request, exc: Exception) -> JSONResponse:
        code = _ERROR_STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": str(exc)})

    app.include_router(auth.router)
    app.include_router(games.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
