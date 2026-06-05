<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

# Tic-Tac-Toe Backend — Agent Context

**Active feature**: `specs/001-tic-tac-toe/` (spec, plan, research, data-model, contracts, tasks).

**Stack**: Python 3.12 · FastAPI + Uvicorn · SQLAlchemy async + aiosqlite (SQLite) ·
Pydantic v2 · passlib[bcrypt] + PyJWT (auth) · httpx (CLI/tests) · pytest + pytest-asyncio · ruff.

**Architecture** (hexagonal ligera): `src/tictactoe/domain` (lógica pura síncrona) →
`application` (casos de uso + puertos/Protocols) → `infrastructure` (SQLite repos, security) +
`api` (FastAPI, wiring DI por `Depends`) + `cli` (cliente HTTP).

**Key commands**:
- Run API: `uvicorn tictactoe.api.main:app --reload` (Swagger en `/docs`)
- CLI: `python -m tictactoe.cli`
- Tests: `pytest -q`  · Lint: `ruff check`

**Principles** (`.specify/memory/constitution.md`): dominio puro/testeable, async solo en I/O,
DI por puertos, persistencia durable que sobrevive a reinicios, tests para cada regla y endpoint.
