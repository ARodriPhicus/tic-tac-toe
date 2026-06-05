"""Infraestructura de base de datos: engine async, factoría de sesiones e init del esquema."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos ORM."""


def create_engine(database_url: str) -> AsyncEngine:
    """Crea el engine async a partir de la URL de conexión."""
    return create_async_engine(database_url, future=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Crea la factoría de sesiones async ligada al engine."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db(engine: AsyncEngine) -> None:
    """Crea las tablas si no existen (suficiente para esta prueba; sin migraciones)."""
    # Importa los modelos para que queden registrados en Base.metadata.
    from .persistence import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
