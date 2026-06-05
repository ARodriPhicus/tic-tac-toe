"""Tablero del tres en raya: representación, validación y render. Lógica pura y síncrona."""

from __future__ import annotations

from .exceptions import InvalidPosition

# Marcas y casilla vacía.
MARK_X = "X"
MARK_O = "O"
EMPTY = "."
MARKS = (MARK_X, MARK_O)

BOARD_SIZE = 9
EMPTY_BOARD = EMPTY * BOARD_SIZE

# Las 8 líneas que dan la victoria (índices 0-8 por filas).
WINNING_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
    (0, 4, 8), (2, 4, 6),             # diagonales
)


def validate_position(position: int) -> None:
    """Lanza InvalidPosition si la casilla no está en el rango 0-8."""
    if not isinstance(position, int) or not (0 <= position < BOARD_SIZE):
        raise InvalidPosition(f"La posición debe estar entre 0 y {BOARD_SIZE - 1}.")


def is_cell_empty(board: str, position: int) -> bool:
    """Indica si la casilla está libre."""
    validate_position(position)
    return board[position] == EMPTY


def place_mark(board: str, position: int, mark: str) -> str:
    """Devuelve un nuevo tablero con `mark` colocada en `position` (no muta el original)."""
    validate_position(position)
    return board[:position] + mark + board[position + 1 :]


def winner(board: str) -> str | None:
    """Devuelve la marca ganadora si hay tres en línea, o None."""
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_full(board: str) -> bool:
    """True si no quedan casillas libres."""
    return EMPTY not in board


def render(board: str) -> str:
    """Render legible 3x3 del tablero (para CLI y respuestas de la API)."""
    cells = [c if c != EMPTY else " " for c in board]
    rows = [" {} | {} | {} ".format(*cells[i : i + 3]) for i in range(0, BOARD_SIZE, 3)]
    separator = "\n---+---+---\n"
    return separator.join(rows)
