"""Utilidades compartidas por los tests (construcción de app y settings de prueba)."""

from __future__ import annotations

from tictactoe.api.main import create_app
from tictactoe.config import Settings
from tictactoe.infrastructure.db import create_engine, create_session_factory, init_db


def build_settings(db_path: str) -> Settings:
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db_path}",
        jwt_secret="test-secret-with-at-least-32-bytes-length!!",
    )


async def build_app(settings: Settings):
    """Crea la app y prepara su estado (engine/sesiones/esquema) sin depender del lifespan."""
    app = create_app(settings)
    engine = create_engine(settings.database_url)
    await init_db(engine)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    return app, engine
