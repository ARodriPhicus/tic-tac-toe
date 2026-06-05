"""Casos de uso de partida: crear, unirse, mover, consultar, log y leaderboard.

Orquesta el dominio puro (reglas) con la persistencia (repos), traduciendo entre la entidad
persistente (GameEntity) y el estado de dominio (GameState).
"""

from __future__ import annotations

from ..domain import board as b
from ..domain import game as g
from ..domain.exceptions import PlayerNotInGame
from .dto import GameEntity, MoveEntity, PlayerEntity
from .exceptions import AlreadyInGame, GameAlreadyFull, GameNotFound
from .ports import GameRepository, MoveRepository, PlayerRepository


class GameService:
    def __init__(
        self,
        games: GameRepository,
        moves: MoveRepository,
        players: PlayerRepository,
    ) -> None:
        self._games = games
        self._moves = moves
        self._players = players

    # --- helpers de mapeo entidad <-> dominio -------------------------------------------

    @staticmethod
    def _to_state(game: GameEntity) -> g.GameState:
        return g.GameState(
            board=game.board,
            current_turn=game.current_turn,
            status=g.GameStatus(game.status),
            result=g.GameResult(game.result) if game.result else None,
        )

    @staticmethod
    def _mark_for_player(game: GameEntity, player_id: int) -> str:
        if player_id == game.player_x_id:
            return b.MARK_X
        if player_id == game.player_o_id:
            return b.MARK_O
        raise PlayerNotInGame("No participas en esta partida.")

    @staticmethod
    def _require_participant(game: GameEntity, player_id: int) -> None:
        """Autorización: solo los dos jugadores de la partida pueden acceder a ella."""
        if player_id not in (game.player_x_id, game.player_o_id):
            raise PlayerNotInGame("No participas en esta partida.")

    # --- casos de uso --------------------------------------------------------------------

    async def create_game(self, creator_id: int) -> GameEntity:
        state = g.new_game()
        entity = GameEntity(
            player_x_id=creator_id,
            board=state.board,
            current_turn=state.current_turn,
            status=state.status.value,
        )
        return await self._games.add(entity)

    async def join_game(self, game_id: int, player_id: int) -> GameEntity:
        game = await self._require_game(game_id)
        if player_id == game.player_x_id:
            raise AlreadyInGame("Ya eres el jugador X de esta partida.")
        if game.player_o_id is not None:
            raise GameAlreadyFull("La partida ya tiene dos jugadores.")

        state = g.start(self._to_state(game))
        game.player_o_id = player_id
        game.status = state.status.value
        game.current_turn = state.current_turn
        await self._games.update(game)
        return game

    async def make_move(self, game_id: int, player_id: int, position: int) -> GameEntity:
        game = await self._require_game(game_id)
        mark = self._mark_for_player(game, player_id)  # valida pertenencia

        new_state = g.apply_move(self._to_state(game), position, mark)  # valida reglas

        # Persiste el nuevo estado de la partida.
        game.board = new_state.board
        game.current_turn = new_state.current_turn
        game.status = new_state.status.value
        game.result = new_state.result.value if new_state.result else None
        if new_state.winner_mark is not None:
            game.winner_id = (
                game.player_x_id if new_state.winner_mark == b.MARK_X else game.player_o_id
            )
        await self._games.update(game)

        # Registra el movimiento (log).
        move_number = await self._moves.count_for_game(game_id) + 1
        await self._moves.add(
            MoveEntity(
                game_id=game_id,
                player_id=player_id,
                position=position,
                mark=mark,
                move_number=move_number,
            )
        )

        # Actualiza la puntuación si la partida ha terminado.
        if new_state.status is g.GameStatus.FINISHED:
            await self._apply_scoring(game, new_state)

        return game

    async def get_game(self, game_id: int, player_id: int) -> GameEntity:
        game = await self._require_game(game_id)
        self._require_participant(game, player_id)
        return game

    async def list_games(self, player_id: int) -> list[GameEntity]:
        return await self._games.list_for_player(player_id)

    async def get_moves(self, game_id: int, player_id: int) -> list[MoveEntity]:
        game = await self._require_game(game_id)
        self._require_participant(game, player_id)
        return await self._moves.list_for_game(game_id)

    async def leaderboard(self) -> list[PlayerEntity]:
        return await self._players.list_all()

    # --- internos ------------------------------------------------------------------------

    async def _require_game(self, game_id: int) -> GameEntity:
        game = await self._games.get(game_id)
        if game is None:
            raise GameNotFound(f"La partida {game_id} no existe.")
        return game

    async def _apply_scoring(self, game: GameEntity, state: g.GameState) -> None:
        player_x = await self._players.get_by_id(game.player_x_id)
        player_o = await self._players.get_by_id(game.player_o_id) if game.player_o_id else None
        if player_x is None or player_o is None:
            return

        if state.result is g.GameResult.DRAW:
            player_x.draws += 1
            player_o.draws += 1
        elif state.result is g.GameResult.X_WON:
            player_x.wins += 1
            player_o.losses += 1
        elif state.result is g.GameResult.O_WON:
            player_o.wins += 1
            player_x.losses += 1

        await self._players.update(player_x)
        await self._players.update(player_o)
