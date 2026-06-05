"""Errores de la capa de aplicación (casos de uso). Independientes de HTTP."""

from __future__ import annotations


class ApplicationError(Exception):
    """Error base de aplicación."""


class UsernameTaken(ApplicationError):
    """El nombre de usuario ya existe."""


class InvalidCredentials(ApplicationError):
    """Usuario o contraseña incorrectos."""


class NotAuthenticated(ApplicationError):
    """Falta autenticación o el token es inválido."""


class GameNotFound(ApplicationError):
    """La partida solicitada no existe."""


class GameAlreadyFull(ApplicationError):
    """La partida ya tiene dos jugadores."""


class AlreadyInGame(ApplicationError):
    """El jugador ya participa en la partida."""
