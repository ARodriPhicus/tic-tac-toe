"""Tablero del tres en raya: representación, validación y render. Lógica pura y síncrona."""

from __future__ import annotations

from .exceptions import InvalidPosition

# Marcas y casilla vacía.
MARK_X = "X"
MARK_O = "O"
EMPTY = "."
MARKS = (MARK_X, MARK_O)

BOARD_DIM = 3  # tablero cuadrado de lado N (3 = tres en raya clásico)
BOARD_SIZE = BOARD_DIM * BOARD_DIM
EMPTY_BOARD = EMPTY * BOARD_SIZE


def _compute_winning_lines(dim: int) -> tuple[tuple[int, ...], ...]:
    """Genera todas las líneas ganadoras (filas, columnas y diagonales) de un tablero NxN.

    Los índices son sobre el tablero aplanado por filas (0..dim*dim-1).
    """
    rows = [tuple(r * dim + c for c in range(dim)) for r in range(dim)]
    cols = [tuple(r * dim + c for r in range(dim)) for c in range(dim)]
    main_diag = tuple(i * dim + i for i in range(dim))
    anti_diag = tuple(i * dim + (dim - 1 - i) for i in range(dim))
    return tuple(rows + cols + [main_diag, anti_diag])


# Líneas ganadoras derivadas del tamaño del tablero (no cableadas a mano).
WINNING_LINES: tuple[tuple[int, ...], ...] = _compute_winning_lines(BOARD_DIM)


def validate_position(position: int) -> None:
    """Lanza InvalidPosition si la casilla no está en el rango [0, BOARD_SIZE)."""
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
    """Devuelve la marca ganadora si alguna línea está completa con la misma marca, o None."""
    for line in WINNING_LINES:
        first = board[line[0]]
        if first != EMPTY and all(board[i] == first for i in line):
            return first
    return None


def is_full(board: str) -> bool:
    """True si no quedan casillas libres."""
    return EMPTY not in board


def render(board: str) -> str:
    """Render legible NxN del tablero (para CLI y respuestas de la API)."""
    cells = [c if c != EMPTY else " " for c in board]
    rows = [
        "|".join(f" {c} " for c in cells[i : i + BOARD_DIM])
        for i in range(0, BOARD_SIZE, BOARD_DIM)
    ]
    separator = "\n" + "+".join(["---"] * BOARD_DIM) + "\n"
    return separator.join(rows)
