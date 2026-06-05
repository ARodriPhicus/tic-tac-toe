# Research & Technical Decisions: Tic-Tac-Toe Backend

Fase 0 del plan. Cada decisión incluye alternativas consideradas y justificación.

## D1 — Lenguaje y runtime: Python 3.12
- **Decisión**: Python 3.12.
- **Alternativas**: Node 22 / TypeScript.
- **Justificación**: El requisito admite Python 3.12 o Node 22; en el entorno solo está
  disponible Python 3.12 (Node es v20). Python encaja con un dominio claro y testeable y un
  stack web maduro.

## D2 — Framework web: FastAPI
- **Decisión**: FastAPI + Uvicorn.
- **Alternativas**: Flask, Django REST, aiohttp.
- **Justificación**: Async nativo (principio IV), validación con Pydantic, documentación
  OpenAPI/Swagger automática (satisface el valorable de API REST documentada con esfuerzo
  mínimo), e inyección de dependencias integrada (`Depends`) que encaja con el wiring por
  puertos.

## D3 — Persistencia: SQLite + SQLAlchemy async (aiosqlite)
- **Decisión**: SQLite en fichero, accedido con SQLAlchemy 2.x async sobre aiosqlite.
- **Alternativas**: Postgres (sobredimensionado para la prueba), ficheros JSON (frágil,
  sin integridad), almacenamiento en memoria (no sobrevive a reinicios).
- **Justificación**: Cumple el requisito de **persistencia durable tras reinicio** sin
  infraestructura externa; el driver async mantiene la coherencia con FastAPI. El tablero se
  guarda como cadena de 9 caracteres, fácil de inspeccionar y reconstruir.

## D4 — Representación del estado del juego
- **Decisión**: El tablero es una cadena de 9 caracteres (`X`, `O`, `.`), casillas 0–8 por
  filas. El turno y el estado/resultado se derivan o se almacenan explícitamente.
- **Alternativas**: Matriz 3×3, lista de listas.
- **Justificación**: Una cadena es trivial de persistir, comparar y renderizar, y el dominio
  la convierte a una estructura interna para razonar. Determinista y fácil de testear.

## D5 — Autenticación: JWT bearer sobre usuario/contraseña
- **Decisión**: Registro con contraseña hasheada (bcrypt vía passlib) y login que emite un
  JWT firmado (PyJWT) usado como bearer token.
- **Alternativas**: Sesiones con cookie + store, OAuth2 externo, API keys.
- **Justificación**: Stateless y simple de consumir desde CLI/tests; cubre el valorable de
  autenticación y sesiones sin dependencias externas. El secreto se lee de configuración.

## D6 — Inversión de dependencias: puertos (Protocols) + wiring por Depends
- **Decisión**: Repositorios definidos como `typing.Protocol` en `application/ports.py`;
  implementaciones SQLite en `infrastructure`; ensamblado en `api/deps.py` con `Depends`.
- **Alternativas**: Contenedor DI de terceros (p. ej. `dependency-injector`), acceso directo
  a la BD desde los endpoints.
- **Justificación**: El wiring manual es explícito, sin magia, fácil de explicar en la
  revisión técnica y suficiente para esta escala; permite inyectar repos en memoria/fakes en
  los tests (principio V). Cubre el valorable de inyección de dependencias.

## D7 — Asincronía donde aporta valor
- **Decisión**: Endpoints y acceso a BD async; dominio síncrono.
- **Justificación**: El I/O (HTTP, BD) se beneficia de async bajo carga concurrente; el
  cálculo del juego es puro y sin I/O, por lo que async ahí solo añadiría complejidad
  (principio IV, y el enunciado pide "uso correcto de asincronía cuando aporte valor").

## D8 — Tests
- **Decisión**: pytest + pytest-asyncio; integración con `httpx.AsyncClient` +
  `ASGITransport` (in-process, sin servidor); BD SQLite temporal por test.
- **Justificación**: Rápido y determinista; cubre dominio (unit) y contrato/flujo de API
  (integration), incluida la verificación de persistencia recreando el engine.

## D9 — CI/CD
- **Decisión**: GitHub Actions con Python 3.12: instalar, `ruff check`, `pytest`.
- **Justificación**: Cubre el valorable de CI/CD con la plataforma donde vivirá el repo.

## D10 — CLI
- **Decisión**: CLI mínimo (`python -m tictactoe.cli`) que habla con la API por HTTP
  (registro/login, crear/unir, render del tablero, jugar) usando httpx.
- **Justificación**: Demuestra una partida completa a través de toda la pila (no atajos al
  dominio), reutilizando el mismo contrato que cualquier otro cliente.
