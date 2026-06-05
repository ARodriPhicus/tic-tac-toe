# Data Model: Tic-Tac-Toe Backend

Fase 1 del plan. Entidades persistentes (SQLite) y reglas de estado.

## Entidades

### Player
| Campo | Tipo | Notas |
|-------|------|-------|
| id | int (PK) | autoincremental |
| username | str | único, no nulo |
| hashed_password | str | bcrypt, nunca en claro |
| wins | int | por defecto 0 |
| losses | int | por defecto 0 |
| draws | int | por defecto 0 |
| created_at | datetime | UTC |

### Game
| Campo | Tipo | Notas |
|-------|------|-------|
| id | int (PK) | autoincremental |
| player_x_id | int (FK→Player) | creador, juega X |
| player_o_id | int (FK→Player), nullable | se rellena al unirse el 2º jugador |
| board | str(9) | casillas 0–8; caracteres `X`, `O`, `.` |
| current_turn | str(1) | `X` u `O` (de quién es el turno) |
| status | enum | `waiting_for_player`, `in_progress`, `finished` |
| result | enum, nullable | `x_won`, `o_won`, `draw` (cuando `finished`) |
| winner_id | int (FK→Player), nullable | jugador ganador, si lo hay |
| created_at | datetime | UTC |
| updated_at | datetime | UTC, se actualiza en cada jugada |

### Move
| Campo | Tipo | Notas |
|-------|------|-------|
| id | int (PK) | autoincremental |
| game_id | int (FK→Game) | partida a la que pertenece |
| player_id | int (FK→Player) | quién jugó |
| position | int | casilla 0–8 |
| mark | str(1) | `X` u `O` |
| move_number | int | orden dentro de la partida (1..9) |
| created_at | datetime | UTC |

El conjunto ordenado de `Move` de una partida es su **log**.

## Transiciones de estado de Game

```
waiting_for_player --(2º jugador se une)--> in_progress
in_progress --(movimiento que completa 3 en línea)--> finished (result=x_won|o_won, winner_id)
in_progress --(movimiento que llena el tablero sin línea)--> finished (result=draw)
```

- En `waiting_for_player` no se aceptan movimientos.
- En `finished` no se aceptan movimientos.
- `current_turn` arranca en `X` y alterna tras cada movimiento válido mientras la partida
  siga `in_progress`.

## Reglas de validación de movimiento (dominio)

1. La partida debe estar `in_progress` (si no → error de estado).
2. `position` debe estar en 0–8 (si no → entrada inválida).
3. La casilla debe estar libre (`.`) (si no → casilla ocupada).
4. La marca del movimiento debe coincidir con `current_turn` (si no → fuera de turno).
5. El jugador que mueve debe ser el dueño de esa marca en la partida (si no → no autorizado).

## Líneas ganadoras (índices del tablero)

```
Filas:      (0,1,2) (3,4,5) (6,7,8)
Columnas:   (0,3,6) (1,4,7) (2,5,8)
Diagonales: (0,4,8) (2,4,6)
```

Una partida la gana la marca que ocupe las tres casillas de alguna línea. Si no hay línea y
el tablero está lleno → empate.

## Efectos sobre la puntuación al finalizar

- Victoria: `winner.wins += 1`, `loser.losses += 1`.
- Empate: `draws += 1` para ambos jugadores.
