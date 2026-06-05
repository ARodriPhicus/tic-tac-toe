"""Reglas del tres en raya. Núcleo de dominio: puro, síncrono y sin dependencias externas.

No conoce jugadores concretos ni persistencia: razona en términos de marcas (X/O) y tablero.
El mapeo marca <-> jugador y la persistencia son responsabilidad de la capa de aplicación.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from . import board as b
from .exceptions import CellOccupied, GameNotInProgress, NotYourTurn


class GameStatus(StrEnum):
    """Estado del ciclo de vida de una partida."""

    WAITING_FOR_PLAYER = "waiting_for_player"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class GameResult(StrEnum):
    """Resultado de una partida finalizada."""

    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"


@dataclass(frozen=True)
class GameState:
    """Estado inmutable de una partida en un instante dado."""

    board: str
    current_turn: str  # b.MARK_X o b.MARK_O
    status: GameStatus
    result: GameResult | None = None

    @property
    def winner_mark(self) -> str | None:
        """Marca ganadora (X/O) o None si no hay ganador."""
        if self.result is GameResult.X_WON:
            return b.MARK_X
        if self.result is GameResult.O_WON:
            return b.MARK_O
        return None


def new_game() -> GameState:
    """Partida recién creada: tablero vacío, esperando al segundo jugador. X jugará primero."""
    return GameState(
        board=b.EMPTY_BOARD,
        current_turn=b.MARK_X,
        status=GameStatus.WAITING_FOR_PLAYER,
    )


def start(state: GameState) -> GameState:
    """Pone la partida en curso cuando se une el segundo jugador."""
    if state.status is not GameStatus.WAITING_FOR_PLAYER:
        raise GameNotInProgress("La partida ya está iniciada o finalizada.")
    return GameState(
        board=state.board,
        current_turn=b.MARK_X,
        status=GameStatus.IN_PROGRESS,
    )


def _resolve(board: str) -> tuple[GameStatus, GameResult | None]:
    """Determina el estado/resultado tras colocar una marca."""
    win = b.winner(board)
    if win == b.MARK_X:
        return GameStatus.FINISHED, GameResult.X_WON
    if win == b.MARK_O:
        return GameStatus.FINISHED, GameResult.O_WON
    if b.is_full(board):
        return GameStatus.FINISHED, GameResult.DRAW
    return GameStatus.IN_PROGRESS, None


def apply_move(state: GameState, position: int, mark: str) -> GameState:
    """Aplica un movimiento y devuelve el nuevo estado (no muta el de entrada).

    Valida: partida en curso, casilla en rango (vía board), turno correcto y casilla libre.
    """
    if state.status is not GameStatus.IN_PROGRESS:
        raise GameNotInProgress("La partida no admite movimientos en este momento.")
    if mark != state.current_turn:
        raise NotYourTurn(f"Le toca jugar a {state.current_turn}.")
    if not b.is_cell_empty(state.board, position):  # también valida el rango de la posición
        raise CellOccupied("La casilla ya está ocupada.")

    next_board = b.place_mark(state.board, position, mark)
    status, result = _resolve(next_board)
    next_turn = b.MARK_O if mark == b.MARK_X else b.MARK_X
    return GameState(
        board=next_board,
        current_turn=state.current_turn if status is GameStatus.FINISHED else next_turn,
        status=status,
        result=result,
    )
