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
