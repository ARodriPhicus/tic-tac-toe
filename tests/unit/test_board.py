"""Tests del tablero (lógica pura)."""

import pytest

from tictactoe.domain import board as b
from tictactoe.domain.exceptions import InvalidPosition


def test_empty_board_shape():
    assert b.EMPTY_BOARD == "........."
    assert len(b.EMPTY_BOARD) == b.BOARD_SIZE


def test_place_mark_is_immutable():
    original = b.EMPTY_BOARD
    result = b.place_mark(original, 4, b.MARK_X)
    assert result[4] == b.MARK_X
    assert original == b.EMPTY_BOARD  # no muta el original


@pytest.mark.parametrize("pos", [-1, 9, 100])
def test_validate_position_rejects_out_of_range(pos):
    with pytest.raises(InvalidPosition):
        b.validate_position(pos)


def test_is_cell_empty():
    board = b.place_mark(b.EMPTY_BOARD, 0, b.MARK_X)
    assert not b.is_cell_empty(board, 0)
    assert b.is_cell_empty(board, 1)


def test_winner_detects_row():
    board = "XXX......"
    assert b.winner(board) == b.MARK_X


def test_winner_none_when_no_line():
    assert b.winner("XOXOXO...") is None


def test_is_full():
    assert b.is_full("XOXOXOXOX")
    assert not b.is_full("XOXOXOXO.")


def test_render_contains_marks_and_separators():
    rendered = b.render("XOX......")
    assert "X" in rendered and "O" in rendered
    assert "---+---+---" in rendered


def test_winning_lines_are_generated_for_3x3():
    # 3 filas + 3 columnas + 2 diagonales = 8 líneas, todas de longitud 3.
    lines = set(b.WINNING_LINES)
    assert len(b.WINNING_LINES) == 8
    assert all(len(line) == 3 for line in b.WINNING_LINES)
    assert (0, 1, 2) in lines  # primera fila
    assert (0, 3, 6) in lines  # primera columna
    assert (0, 4, 8) in lines and (2, 4, 6) in lines  # diagonales


def test_winning_lines_generalize_to_other_sizes():
    # La generación es por código: para un tablero 4x4 hay 4+4+2 = 10 líneas de longitud 4.
    lines = b._compute_winning_lines(4)
    assert len(lines) == 10
    assert all(len(line) == 4 for line in lines)
    assert (0, 1, 2, 3) in lines       # primera fila
    assert (0, 4, 8, 12) in lines      # primera columna
    assert (0, 5, 10, 15) in lines     # diagonal principal
    assert (3, 6, 9, 12) in lines      # diagonal secundaria
