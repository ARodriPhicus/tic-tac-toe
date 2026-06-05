"""Errores del dominio del juego. Son agnósticos de transporte (no saben de HTTP)."""

from __future__ import annotations


class DomainError(Exception):
    """Error base del dominio."""


class InvalidPosition(DomainError):
    """La posición indicada está fuera del tablero (válidas: 0-8)."""


class CellOccupied(DomainError):
    """La casilla destino ya está ocupada."""


class NotYourTurn(DomainError):
    """Se intenta jugar fuera de turno."""


class GameNotInProgress(DomainError):
    """La partida no admite movimientos (esperando jugador o ya finalizada)."""


class PlayerNotInGame(DomainError):
    """El jugador no participa en la partida."""
