"""Implementaciones SQLite (SQLAlchemy async) de los puertos de persistencia.

Mapean entre las entidades de aplicación (dataclasses) y los modelos ORM, de modo que la
capa de aplicación no dependa de SQLAlchemy.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dto import GameEntity, MoveEntity, PlayerEntity
from .models import GameModel, MoveModel, PlayerModel


def _to_player_entity(m: PlayerModel) -> PlayerEntity:
    return PlayerEntity(
        id=m.id,
        username=m.username,
        hashed_password=m.hashed_password,
        wins=m.wins,
        losses=m.losses,
        draws=m.draws,
    )


def _to_game_entity(m: GameModel) -> GameEntity:
    return GameEntity(
        id=m.id,
        player_x_id=m.player_x_id,
        player_o_id=m.player_o_id,
        board=m.board,
        current_turn=m.current_turn,
        status=m.status,
        result=m.result,
        winner_id=m.winner_id,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _to_move_entity(m: MoveModel) -> MoveEntity:
    return MoveEntity(
        id=m.id,
        game_id=m.game_id,
        player_id=m.player_id,
        position=m.position,
        mark=m.mark,
        move_number=m.move_number,
        created_at=m.created_at,
    )


class SqlPlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, player: PlayerEntity) -> PlayerEntity:
        model = PlayerModel(username=player.username, hashed_password=player.hashed_password)
        self._session.add(model)
        await self._session.flush()
        return _to_player_entity(model)

    async def get_by_id(self, player_id: int) -> PlayerEntity | None:
        model = await self._session.get(PlayerModel, player_id)
        return _to_player_entity(model) if model else None

    async def get_by_username(self, username: str) -> PlayerEntity | None:
        result = await self._session.execute(
            select(PlayerModel).where(PlayerModel.username == username)
        )
        model = result.scalar_one_or_none()
        return _to_player_entity(model) if model else None

    async def update(self, player: PlayerEntity) -> None:
        model = await self._session.get(PlayerModel, player.id)
        if model is None:
            return
        model.wins = player.wins
        model.losses = player.losses
        model.draws = player.draws
        await self._session.flush()

    async def list_all(self) -> list[PlayerEntity]:
        result = await self._session.execute(
            select(PlayerModel).order_by(
                PlayerModel.wins.desc(), PlayerModel.draws.desc(), PlayerModel.username
            )
        )
        return [_to_player_entity(m) for m in result.scalars().all()]


class SqlGameRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, game: GameEntity) -> GameEntity:
        model = GameModel(
            player_x_id=game.player_x_id,
            player_o_id=game.player_o_id,
            board=game.board,
            current_turn=game.current_turn,
            status=game.status,
            result=game.result,
            winner_id=game.winner_id,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_game_entity(model)

    async def get(self, game_id: int) -> GameEntity | None:
        model = await self._session.get(GameModel, game_id)
        return _to_game_entity(model) if model else None

    async def list_for_player(self, player_id: int) -> list[GameEntity]:
        result = await self._session.execute(
            select(GameModel)
            .where(
                (GameModel.player_x_id == player_id) | (GameModel.player_o_id == player_id)
            )
            .order_by(GameModel.created_at.desc())
        )
        return [_to_game_entity(m) for m in result.scalars().all()]

    async def update(self, game: GameEntity) -> None:
        model = await self._session.get(GameModel, game.id)
        if model is None:
            return
        model.player_o_id = game.player_o_id
        model.board = game.board
        model.current_turn = game.current_turn
        model.status = game.status
        model.result = game.result
        model.winner_id = game.winner_id
        await self._session.flush()


class SqlMoveRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, move: MoveEntity) -> MoveEntity:
        model = MoveModel(
            game_id=move.game_id,
            player_id=move.player_id,
            position=move.position,
            mark=move.mark,
            move_number=move.move_number,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_move_entity(model)

    async def list_for_game(self, game_id: int) -> list[MoveEntity]:
        result = await self._session.execute(
            select(MoveModel)
            .where(MoveModel.game_id == game_id)
            .order_by(MoveModel.move_number)
        )
        return [_to_move_entity(m) for m in result.scalars().all()]

    async def count_for_game(self, game_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(MoveModel).where(MoveModel.game_id == game_id)
        )
        return int(result.scalar_one())
