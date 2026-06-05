"""Tests de las reglas del juego (dominio puro)."""

import pytest

from tictactoe.domain import board as b
from tictactoe.domain import game as g
from tictactoe.domain.exceptions import (
    CellOccupied,
    GameNotInProgress,
    InvalidPosition,
    NotYourTurn,
)


def _in_progress(board=b.EMPTY_BOARD, turn=b.MARK_X):
    return g.GameState(board=board, current_turn=turn, status=g.GameStatus.IN_PROGRESS)


def test_new_game_waits_for_player():
    state = g.new_game()
    assert state.status is g.GameStatus.WAITING_FOR_PLAYER
    assert state.board == b.EMPTY_BOARD
    assert state.current_turn == b.MARK_X


def test_start_sets_in_progress_and_x_first():
    state = g.start(g.new_game())
    assert state.status is g.GameStatus.IN_PROGRESS
    assert state.current_turn == b.MARK_X


def test_cannot_move_before_start():
    with pytest.raises(GameNotInProgress):
        g.apply_move(g.new_game(), 0, b.MARK_X)


def test_move_alternates_turn():
    state = g.apply_move(_in_progress(), 0, b.MARK_X)
    assert state.board[0] == b.MARK_X
    assert state.current_turn == b.MARK_O


def test_out_of_turn_is_rejected():
    with pytest.raises(NotYourTurn):
        g.apply_move(_in_progress(turn=b.MARK_X), 0, b.MARK_O)


def test_occupied_cell_is_rejected():
    state = g.apply_move(_in_progress(), 4, b.MARK_X)  # X en el centro, turno O
    with pytest.raises(CellOccupied):
        g.apply_move(state, 4, b.MARK_O)


def test_out_of_range_is_rejected():
    with pytest.raises(InvalidPosition):
        g.apply_move(_in_progress(), 9, b.MARK_X)


@pytest.mark.parametrize("line", g.b.WINNING_LINES)
def test_all_winning_lines_for_x(line):
    # Construye un tablero donde X ocupa la línea ganadora.
    board = list(b.EMPTY_BOARD)
    for i in line:
        board[i] = b.MARK_X
    state = g.GameState(
        board="".join(board), current_turn=b.MARK_X, status=g.GameStatus.IN_PROGRESS
    )
    # Re-resolvemos colocando la última marca de la línea para pasar por apply_move.
    last = line[-1]
    board[last] = b.EMPTY
    state = g.GameState(
        board="".join(board), current_turn=b.MARK_X, status=g.GameStatus.IN_PROGRESS
    )
    final = g.apply_move(state, last, b.MARK_X)
    assert final.status is g.GameStatus.FINISHED
    assert final.result is g.GameResult.X_WON
    assert final.winner_mark == b.MARK_X


def test_o_can_win():
    # O completa la columna izquierda.
    state = g.GameState(board="O..O.X.X.", current_turn=b.MARK_O, status=g.GameStatus.IN_PROGRESS)
    final = g.apply_move(state, 6, b.MARK_O)
    assert final.result is g.GameResult.O_WON


def test_draw_when_board_full_without_line():
    # Tablero a falta de una casilla, sin ganador; la última jugada produce empate.
    # X O X / X O O / O X .  -> al poner X en 8 no hay 3 en línea.
    state = g.GameState(board="XOXXOOOX.", current_turn=b.MARK_X, status=g.GameStatus.IN_PROGRESS)
    final = g.apply_move(state, 8, b.MARK_X)
    assert final.status is g.GameStatus.FINISHED
    assert final.result is g.GameResult.DRAW
    assert final.winner_mark is None


def test_no_moves_after_finished():
    finished = g.GameState(
        board="XXX......",
        current_turn=b.MARK_X,
        status=g.GameStatus.FINISHED,
        result=g.GameResult.X_WON,
    )
    with pytest.raises(GameNotInProgress):
        g.apply_move(finished, 5, b.MARK_O)
