# Quickstart: Tic-Tac-Toe Backend

Cómo ejecutar y validar la solución (resumen; ver README para detalle).

## Requisitos
- Python 3.12

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Arrancar la API
```bash
uvicorn tictactoe.api.main:app --reload
# Swagger UI: http://127.0.0.1:8000/docs
```

## Jugar por CLI (contra la API en marcha)
```bash
python -m tictactoe.cli
```

## Tests
```bash
pytest -q
```

## Verificación de persistencia (manual)
1. Arranca la API, crea una partida y juega un par de movimientos.
2. Detén el proceso (Ctrl+C) y vuelve a arrancarlo.
3. `GET /games/{id}` → el tablero y el turno se conservan.

## Flujo mínimo por API (curl)
```bash
# Registro de dos jugadores
curl -s -X POST localhost:8000/auth/register -H 'content-type: application/json' -d '{"username":"ana","password":"secret"}'
curl -s -X POST localhost:8000/auth/register -H 'content-type: application/json' -d '{"username":"bob","password":"secret"}'
# Login
TOKEN_A=$(curl -s -X POST localhost:8000/auth/login -H 'content-type: application/json' -d '{"username":"ana","password":"secret"}' | jq -r .access_token)
TOKEN_B=$(curl -s -X POST localhost:8000/auth/login -H 'content-type: application/json' -d '{"username":"bob","password":"secret"}' | jq -r .access_token)
# Crear y unirse
GID=$(curl -s -X POST localhost:8000/games -H "authorization: Bearer $TOKEN_A" | jq -r .id)
curl -s -X POST localhost:8000/games/$GID/join -H "authorization: Bearer $TOKEN_B" >/dev/null
# Jugar
curl -s -X POST localhost:8000/games/$GID/moves -H "authorization: Bearer $TOKEN_A" -H 'content-type: application/json' -d '{"position":0}'
```
