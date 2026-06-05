"""Entidades de transferencia entre capas (independientes del ORM y del dominio puro).

Permiten que los servicios y la API no dependan de SQLAlchemy: los repositorios mapean
estas dataclasses a/desde los modelos persistentes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlayerEntity:
    username: str
    hashed_password: str
    id: int | None = None
    wins: int = 0
    losses: int = 0
    draws: int = 0


@dataclass
class GameEntity:
    player_x_id: int
    board: str
    current_turn: str
    status: str
    id: int | None = None
    player_o_id: int | None = None
    result: str | None = None
    winner_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class MoveEntity:
    game_id: int
    player_id: int
    position: int
    mark: str
    move_number: int
    id: int | None = None
    created_at: datetime | None = None
