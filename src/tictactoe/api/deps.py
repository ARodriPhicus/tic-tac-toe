"""Wiring de dependencias (DI) por request usando FastAPI `Depends`.

Aquí se compone la aplicación: sesión por petición -> repositorios -> servicios -> auth.
Mantener el wiring en un único lugar facilita sustituir piezas (p. ej. en tests).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.auth_service import AuthService
from ..application.dto import PlayerEntity
from ..application.exceptions import NotAuthenticated
from ..application.game_service import GameService
from ..application.ports import PlayerRepository
from ..config import Settings
from ..infrastructure.persistence.repositories import (
    SqlGameRepository,
    SqlMoveRepository,
    SqlPlayerRepository,
)

_bearer = HTTPBearer(auto_error=False)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Una sesión por petición; commit al terminar bien, rollback ante error."""
    factory = request.app.state.session_factory
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_player_repo(session: SessionDep) -> PlayerRepository:
    return SqlPlayerRepository(session)


def get_auth_service(
    session: SessionDep, settings: SettingsDep
) -> AuthService:
    return AuthService(SqlPlayerRepository(session), settings)


def get_game_service(session: SessionDep) -> GameService:
    return GameService(
        SqlGameRepository(session),
        SqlMoveRepository(session),
        SqlPlayerRepository(session),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
GameServiceDep = Annotated[GameService, Depends(get_game_service)]


async def get_current_player(
    auth: AuthServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> PlayerEntity:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth.player_from_token(credentials.credentials)
    except NotAuthenticated as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentPlayer = Annotated[PlayerEntity, Depends(get_current_player)]
