"""Configuración de la aplicación (12-factor: valores por defecto + override por entorno)."""

from __future__ import annotations

import logging
import secrets

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("tictactoe")


class Settings(BaseSettings):
    """Ajustes leídos de variables de entorno (prefijo TTT_) o de un fichero .env."""

    model_config = SettingsConfigDict(env_prefix="TTT_", env_file=".env", extra="ignore")

    # Conexión a la base de datos (SQLite async por defecto, fichero local => persistencia).
    database_url: str = "sqlite+aiosqlite:///./tictactoe.db"

    # Secreto para firmar los JWT. No se cablea ningún valor por defecto: si no se define
    # TTT_JWT_SECRET se genera uno aleatorio en arranque (ver validador). En producción
    # DEBE definirse para que las sesiones sobrevivan a reinicios y entre réplicas.
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24

    @model_validator(mode="after")
    def _ensure_jwt_secret(self) -> Settings:
        if not self.jwt_secret:
            # Secreto efímero y seguro: nunca se publica un secreto en el repositorio.
            self.jwt_secret = secrets.token_urlsafe(48)
            logger.warning(
                "TTT_JWT_SECRET no definido: se ha generado uno aleatorio. Las sesiones no "
                "sobrevivirán a un reinicio; define TTT_JWT_SECRET en producción."
            )
        return self


def get_settings() -> Settings:
    """Factory de Settings (punto único de inyección; sustituible en tests)."""
    return Settings()
