"""Configuración de la aplicación (12-factor: valores por defecto + override por entorno)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes leídos de variables de entorno (prefijo TTT_) o de un fichero .env."""

    model_config = SettingsConfigDict(env_prefix="TTT_", env_file=".env", extra="ignore")

    # Conexión a la base de datos (SQLite async por defecto, fichero local => persistencia).
    database_url: str = "sqlite+aiosqlite:///./tictactoe.db"

    # Secreto para firmar los JWT. En producción DEBE sobreescribirse vía TTT_JWT_SECRET.
    jwt_secret: str = "dev-secret-change-me-please-32bytes-min"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24


def get_settings() -> Settings:
    """Factory de Settings (punto único de inyección; sustituible en tests)."""
    return Settings()
