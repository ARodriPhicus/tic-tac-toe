"""Seguridad: hash de contraseñas (bcrypt) y emisión/verificación de JWT.

Se usa la librería `bcrypt` directamente (sin passlib) por compatibilidad con bcrypt 5.x.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from ..config import Settings

# bcrypt admite como máximo 72 bytes de contraseña; se trunca de forma explícita.
_BCRYPT_MAX_BYTES = 72


def _encode(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contraseña."""
    return bcrypt.hashpw(_encode(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Comprueba una contraseña contra su hash."""
    try:
        return bcrypt.checkpw(_encode(password), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str | int, settings: Settings) -> str:
    """Emite un JWT firmado cuyo `sub` identifica al jugador."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> int | None:
    """Devuelve el id de jugador del token, o None si es inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
