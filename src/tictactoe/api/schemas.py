"""Modelos Pydantic de entrada/salida de la API REST."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ..application.dto import GameEntity, MoveEntity, PlayerEntity
from ..domain import board as b


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PlayerResponse(BaseModel):
    id: int
    username: str
    wins: int
    losses: int
    draws: int

    @classmethod
    def from_entity(cls, p: PlayerEntity) -> PlayerResponse:
        return cls(
            id=p.id, username=p.username, wins=p.wins, losses=p.losses, draws=p.draws
        )


class PlayerPublic(BaseModel):
    id: int
    username: str

    @classmethod
    def from_entity(cls, p: PlayerEntity) -> PlayerPublic:
        return cls(id=p.id, username=p.username)


class MoveRequest(BaseModel):
    position: int = Field(ge=0, le=8, description="Casilla 0-8 (por filas).")


class MoveResponse(BaseModel):
    move_number: int
    player_id: int
    mark: str
    position: int
    created_at: datetime | None = None

    @classmethod
    def from_entity(cls, m: MoveEntity) -> MoveResponse:
        return cls(
            move_number=m.move_number,
            player_id=m.player_id,
            mark=m.mark,
            position=m.position,
            created_at=m.created_at,
        )


class GameResponse(BaseModel):
    id: int
    player_x_id: int
    player_o_id: int | None
    board: str
    board_pretty: str
    current_turn: str
    status: str
    result: str | None
    winner_id: int | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_entity(cls, game: GameEntity) -> GameResponse:
        return cls(
            id=game.id,
            player_x_id=game.player_x_id,
            player_o_id=game.player_o_id,
            board=game.board,
            board_pretty=b.render(game.board),
            current_turn=game.current_turn,
            status=game.status,
            result=game.result,
            winner_id=game.winner_id,
            created_at=game.created_at,
            updated_at=game.updated_at,
        )
