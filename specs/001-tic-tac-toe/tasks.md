---
description: "Task list for Tic-Tac-Toe backend implementation"
---

# Tasks: Tic-Tac-Toe Backend

**Input**: Design documents from `specs/001-tic-tac-toe/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: incluidos (la prueba valora tests unitarios y la constitución los exige).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: US1 (jugar partida), US2 (persistencia), US3 (auth/historial/score)

---

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Crear estructura de paquetes `src/tictactoe/{domain,application,infrastructure,api,cli}` con `__init__.py`.
- [ ] T002 `pyproject.toml`: metadatos, dependencias runtime y `[dev]`, config de ruff y pytest (build con setuptools, `src/` layout).
- [ ] T003 [P] `src/tictactoe/config.py`: Settings (pydantic-settings) con `database_url`, `jwt_secret`, `jwt_expires_minutes`.

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T004 `domain/exceptions.py`: jerarquía de errores de dominio (`DomainError`, `InvalidPosition`, `CellOccupied`, `NotYourTurn`, `GameNotInProgress`, `PlayerNotInGame`).
- [ ] T005 `infrastructure/db.py`: engine async + `async_sessionmaker` + `Base` + `init_db()` (crea tablas).
- [ ] T006 `infrastructure/security.py`: hash/verify de contraseña (passlib bcrypt) + crear/decodificar JWT (PyJWT).
- [ ] T007 `application/ports.py`: Protocols `PlayerRepository`, `GameRepository`, `MoveRepository`.

## Phase 3: User Story 1 — Jugar una partida (P1) 🎯 MVP

- [ ] T008 [P] [US1] `domain/board.py`: tablero (cadena de 9), constantes de marcas, líneas ganadoras, render bonito, helpers (libre/ocupada).
- [ ] T009 [US1] `domain/game.py`: lógica pura — aplicar movimiento, validar turno/casilla/estado, detectar ganador/empate, calcular siguiente turno y resultado.
- [ ] T010 [P] [US1] `tests/unit/test_board.py`: render y utilidades del tablero.
- [ ] T011 [P] [US1] `tests/unit/test_game_rules.py`: todas las líneas ganadoras, empate, fuera de turno, casilla ocupada, posición fuera de rango, partida no en curso.

## Phase 4: User Story 2 — Persistencia (P1)

- [ ] T012 [US2] `infrastructure/persistence/models.py`: modelos SQLAlchemy `Player`, `Game`, `Move` (según data-model).
- [ ] T013 [US2] `infrastructure/persistence/repositories.py`: implementaciones SQLite de los puertos (CRUD + actualización de estado/score).
- [ ] T014 [US2] `tests/integration/test_persistence.py`: crear partida + movimientos, recrear engine/app y verificar que el estado se conserva.

## Phase 5: User Story 3 — Auth, historial y puntuación (P2)

- [ ] T015 [US3] `application/auth_service.py`: registro (hash), login (verifica + emite token), `get_current_player` desde token.
- [ ] T016 [US3] `application/game_service.py`: casos de uso — crear, unirse, mover (usa dominio + repos), listar, obtener, log de movimientos, actualizar puntuación al finalizar, leaderboard.
- [ ] T017 [US3] `api/schemas.py`: modelos Pydantic de request/response (auth, game, move, leaderboard) + render del tablero.
- [ ] T018 [US3] `api/deps.py`: wiring DI — sesión por request, repos, servicios, dependencia de autenticación (bearer).
- [ ] T019 [US3] `api/routers/auth.py`: `/auth/register`, `/auth/login`, `/auth/me`.
- [ ] T020 [US3] `api/routers/games.py`: `/games`, `/games/{id}/join`, `/games`, `/games/{id}`, `/games/{id}/moves` (POST/GET), `/leaderboard`.
- [ ] T021 [US3] `api/main.py`: app FastAPI con lifespan (`init_db`), inclusión de routers, metadatos OpenAPI.
- [ ] T022 [P] [US3] `tests/integration/test_auth_api.py`: registro, conflicto de username, login ok/ko, `/auth/me`.
- [ ] T023 [US3] `tests/integration/test_game_flow_api.py`: flujo completo registro→login→crear→unir→jugar→ganar; rechazo de movimientos inválidos vía API; log y leaderboard.

## Phase 6: CLI

- [ ] T024 [US1] `cli/__main__.py`: CLI mínimo que registra/login, crea/une, renderiza el tablero y juega una partida completa contra la API.

## Phase 7: Tests harness + CI + Docs

- [ ] T025 `tests/conftest.py`: fixtures de app con BD temporal y cliente `httpx.AsyncClient` (ASGITransport).
- [ ] T026 `.github/workflows/ci.yml`: GitHub Actions Python 3.12 → instalar → `ruff check` → `pytest`.
- [ ] T027 `README.md`: instalación, uso (API/CLI/curl), cómo correr tests, y sección "Decisiones técnicas relevantes".

## Dependencies / Order
- Setup (T001–T003) → Foundational (T004–T007) → resto.
- Dominio (T008–T011) no depende de infra; puede ir en paralelo a modelos.
- Servicios (T015–T016) dependen de dominio + puertos + repos.
- API (T017–T021) depende de servicios. Tests de integración (T022–T023) y CLI (T024) tras la API.
- Verificación final: `pytest -q` en verde + arranque de API + partida por CLI.
