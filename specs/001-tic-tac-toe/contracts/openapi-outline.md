# API Contract (outline): Tic-Tac-Toe Backend

Contrato de la API REST. La especificación OpenAPI completa la genera FastAPI en
`/openapi.json` y se explora en `/docs` (Swagger UI). Este documento fija el contrato
acordado en diseño.

Autenticación: `Authorization: Bearer <token>` en los endpoints protegidos (🔒).

## Auth

### POST /auth/register
- Body: `{ "username": str, "password": str }`
- 201: `{ "id": int, "username": str }`
- 409: username ya existe.

### POST /auth/login
- Body: `{ "username": str, "password": str }`
- 200: `{ "access_token": str, "token_type": "bearer" }`
- 401: credenciales inválidas.

### GET /auth/me 🔒
- 200: `{ "id": int, "username": str, "wins": int, "losses": int, "draws": int }`
- 401: no autenticado.

## Games

### POST /games 🔒
Crea una partida; el llamante queda como jugador X.
- 201: objeto Game.
- 401: no autenticado.

### POST /games/{id}/join 🔒
El llamante se une como jugador O y la partida pasa a `in_progress`.
- 200: objeto Game.
- 404: partida no existe · 409: ya tiene dos jugadores o el llamante ya está en ella.

### GET /games 🔒
Lista las partidas del jugador autenticado.
- 200: `[ Game, ... ]`

### GET /games/{id} 🔒
Estado de una partida (incluye render del tablero). Solo accesible para sus jugadores.
- 200: objeto Game · 403: el jugador no participa en la partida · 404: no existe.

### POST /games/{id}/moves 🔒
Realiza un movimiento.
- Body: `{ "position": int (0-8) }`
- 200: objeto Game actualizado.
- 400: posición fuera de rango · 401: no autenticado ·
  403: el jugador no pertenece a la partida o no es su turno ·
  404: partida no existe · 409: casilla ocupada / partida no en curso o finalizada.

### GET /games/{id}/moves 🔒
Log de movimientos de la partida, en orden. Solo accesible para sus jugadores.
- 200: `[ { "move_number": int, "player_id": int, "mark": "X|O", "position": int, "created_at": datetime }, ... ]`
- 403: el jugador no participa en la partida · 404: partida no existe.

### GET /leaderboard
Marcador global de jugadores.
- 200: `[ { "id": int, "username": str, "wins": int, "losses": int, "draws": int }, ... ]`

## Representación de Game (response)

```json
{
  "id": 1,
  "player_x_id": 1,
  "player_o_id": 2,
  "board": "X.O.X..O.",
  "board_pretty": "X | . | O\n--+---+--\n. | X | .\n--+---+--\n. | O | .",
  "current_turn": "X",
  "status": "in_progress",
  "result": null,
  "winner_id": null,
  "created_at": "2026-06-05T10:00:00Z",
  "updated_at": "2026-06-05T10:03:00Z"
}
```

## Errores

Formato uniforme de error (FastAPI): `{ "detail": "<mensaje>" }` con el código HTTP
correspondiente según la tabla de cada endpoint.
