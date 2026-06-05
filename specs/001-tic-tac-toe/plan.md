# Implementation Plan: Tic-Tac-Toe Backend

**Branch**: `001-tic-tac-toe` | **Date**: 2026-06-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-tic-tac-toe/spec.md`

## Summary

Backend para jugar al tres en raya entre dos jugadores, con validación completa de reglas,
persistencia durable, autenticación, historial/puntuación y log de movimientos. Se expone
como **API REST** (FastAPI, async, con OpenAPI/Swagger) y un **CLI mínimo** que juega una
partida completa contra esa API. La lógica del juego se aísla en un **dominio puro y
síncrono**; la persistencia usa **SQLite vía SQLAlchemy async**. La composición de
dependencias se resuelve por **wiring explícito** detrás de puertos (Protocols), lo que
permite sustituir repositorios en los tests.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, SQLAlchemy 2.x (async) + aiosqlite, Pydantic v2,
pydantic-settings, passlib[bcrypt] (hash de contraseñas), PyJWT (tokens), httpx (cliente CLI
y tests). Dev: pytest, pytest-asyncio, anyio, ruff.

**Storage**: SQLite (fichero en disco) mediante SQLAlchemy async (aiosqlite).

**Testing**: pytest + pytest-asyncio; tests unitarios del dominio y de integración de la API
con `httpx.ASGITransport` (sin levantar servidor real).

**Target Platform**: Servidor Linux (también macOS/WSL); Python 3.12.

**Project Type**: Web service (API REST) + CLI, proyecto único.

**Performance Goals**: No crítico (juego por turnos). Respuestas de API < 100 ms en local.

**Constraints**: Debe ejecutarse en Python 3.12 limpio; el estado debe sobrevivir a
reinicios; sin secretos en el repositorio.

**Scale/Scope**: Decenas de jugadores y partidas simultáneas; un único nodo de aplicación.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento |
|-----------|--------------|
| I. Dominio puro | Lógica de juego en `domain/`, sin I/O ni framework; síncrona y testeable. ✅ |
| II. Interfaz por contrato | API REST con OpenAPI + CLI mínimo; validación con Pydantic y errores HTTP claros. ✅ |
| III. Test-First | Tests unitarios del dominio + integración de API antes de dar por cerrada cada parte. ✅ |
| IV. Async donde aporta valor | Async en endpoints y acceso a BD; dominio síncrono. ✅ |
| V. DI + persistencia durable | Puertos (Protocols) + wiring; repos SQLite sustituibles; estado en SQLite. ✅ |

Sin violaciones → *Complexity Tracking* vacío.

## Project Structure

### Documentation (this feature)

```text
specs/001-tic-tac-toe/
├── plan.md              # Este archivo
├── research.md          # Decisiones técnicas (Phase 0)
├── data-model.md        # Entidades y esquema (Phase 1)
├── quickstart.md        # Cómo ejecutar y probar (Phase 1)
├── contracts/
│   └── openapi-outline.md   # Contrato de la API (Phase 1)
├── checklists/
│   └── requirements.md
└── tasks.md             # Generado por /speckit-tasks
```

### Source Code (repository root)

```text
src/tictactoe/
├── domain/
│   ├── __init__.py
│   ├── board.py            # Tablero, marcas, posiciones, render
│   ├── game.py             # Reglas: turnos, validación, win/draw (puro, síncrono)
│   └── exceptions.py       # Errores de dominio (InvalidMove, NotYourTurn, ...)
├── application/
│   ├── __init__.py
│   ├── ports.py            # Protocols: PlayerRepository, GameRepository, MoveRepository
│   ├── dto.py              # Tipos de transferencia entre capas
│   ├── game_service.py     # Casos de uso de partida (crear, unirse, mover, consultar)
│   └── auth_service.py     # Registro, login, verificación de token
├── infrastructure/
│   ├── __init__.py
│   ├── db.py               # Engine/sesión async, init de esquema
│   ├── security.py         # Hash de contraseñas + emisión/verificación de JWT
│   └── persistence/
│       ├── __init__.py
│       ├── models.py       # Modelos SQLAlchemy (Player, Game, Move)
│       └── repositories.py # Implementaciones SQLite de los puertos
├── api/
│   ├── __init__.py
│   ├── main.py             # App FastAPI, lifespan (init BD), routers
│   ├── deps.py             # Wiring DI vía Depends (sesión, repos, servicios, auth)
│   ├── schemas.py          # Modelos Pydantic de request/response
│   └── routers/
│       ├── __init__.py
│       ├── auth.py         # /auth/register, /auth/login, /auth/me
│       └── games.py        # /games..., /games/{id}/moves, /leaderboard
├── cli/
│   ├── __init__.py
│   └── __main__.py         # CLI mínimo que juega una partida contra la API
├── config.py               # Settings (pydantic-settings): DB_URL, JWT_SECRET, ...
└── __init__.py

tests/
├── conftest.py             # Fixtures: app, cliente async, BD temporal
├── unit/
│   ├── test_board.py
│   └── test_game_rules.py  # turnos, líneas ganadoras, empate, inválidos
└── integration/
    ├── test_auth_api.py
    ├── test_game_flow_api.py
    └── test_persistence.py # estado sobrevive a recrear la app/engine

.github/workflows/ci.yml    # Lint (ruff) + tests (pytest) en Python 3.12
pyproject.toml              # Metadatos, deps, config de ruff/pytest
README.md                   # Uso + decisiones técnicas
```

**Structure Decision**: Proyecto único con arquitectura hexagonal ligera (domain →
application → infrastructure/api). El dominio no importa nada de las capas externas; la API
depende de la aplicación; la infraestructura implementa los puertos de la aplicación. Esto
materializa los principios I y V de la constitución y facilita los tests.

## Complexity Tracking

> Sin violaciones de la constitución. No aplica.
