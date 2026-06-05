# Tic-Tac-Toe (Tres en Raya) — Backend

Backend para jugar al tres en raya entre dos jugadores, con validación completa de reglas,
**persistencia durable** (sobrevive a reinicios), autenticación, historial/puntuación y log de
movimientos. Se expone como **API REST** (FastAPI, con Swagger) y un **CLI mínimo**.

Desarrollado con **Spec-Driven Development** usando [GitHub Spec Kit](https://github.com/github/spec-kit):
toda la especificación, el plan y las tareas viven en [`specs/001-tic-tac-toe/`](specs/001-tic-tac-toe/)
y los principios del proyecto en [`.specify/memory/constitution.md`](.specify/memory/constitution.md).

---

## Requisitos

- **Python 3.12**

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Ejecutar la API

```bash
uvicorn tictactoe.api.main:app --reload
```

- Documentación interactiva (Swagger UI): http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json
- Healthcheck: http://127.0.0.1:8000/health

La base de datos SQLite se crea automáticamente (`./tictactoe.db` por defecto).

## Jugar por CLI

Con la API en marcha, en otra terminal:

```bash
python -m tictactoe.cli            # o: tictactoe-cli
# opcional: --api http://127.0.0.1:8000
```

El CLI registra/inicia sesión de los dos jugadores, crea y une la partida, y permite jugar
por turnos desde la consola validando toda la pila (HTTP → API → dominio → BD).

## Tests y linting

```bash
pytest          # 42 tests (unitarios de dominio + integración de API + persistencia)
ruff check .    # linting
```

---

## API (resumen)

Autenticación por **Bearer token** (JWT) en los endpoints protegidos (🔒).

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Registrar jugador |
| POST | `/auth/login` | Iniciar sesión → `access_token` |
| GET | `/auth/me` 🔒 | Datos y marcador del jugador actual |
| POST | `/games` 🔒 | Crear partida (creador = X) |
| POST | `/games/{id}/join` 🔒 | Unirse como O (la partida pasa a `in_progress`) |
| GET | `/games` 🔒 | Listar mis partidas |
| GET | `/games/{id}` 🔒 | Estado de una partida (incluye tablero renderizado) |
| POST | `/games/{id}/moves` 🔒 | Realizar un movimiento `{ "position": 0-8 }` |
| GET | `/games/{id}/moves` 🔒 | Log de movimientos en orden |
| GET | `/leaderboard` | Marcador global (victorias/derrotas/empates) |

Contrato detallado en [`specs/001-tic-tac-toe/contracts/openapi-outline.md`](specs/001-tic-tac-toe/contracts/openapi-outline.md).

### Ejemplo end-to-end (curl)

```bash
curl -s -X POST localhost:8000/auth/register -H 'content-type: application/json' -d '{"username":"ana","password":"pw"}'
curl -s -X POST localhost:8000/auth/register -H 'content-type: application/json' -d '{"username":"bob","password":"pw"}'
TA=$(curl -s -X POST localhost:8000/auth/login -H 'content-type: application/json' -d '{"username":"ana","password":"pw"}' | jq -r .access_token)
TB=$(curl -s -X POST localhost:8000/auth/login -H 'content-type: application/json' -d '{"username":"bob","password":"pw"}' | jq -r .access_token)
GID=$(curl -s -X POST localhost:8000/games -H "authorization: Bearer $TA" | jq -r .id)
curl -s -X POST localhost:8000/games/$GID/join -H "authorization: Bearer $TB" >/dev/null
curl -s -X POST localhost:8000/games/$GID/moves -H "authorization: Bearer $TA" -H 'content-type: application/json' -d '{"position":0}'
```

---

## Configuración

Variables de entorno (prefijo `TTT_`, también vía fichero `.env`):

| Variable | Por defecto | Descripción |
|----------|-------------|-------------|
| `TTT_DATABASE_URL` | `sqlite+aiosqlite:///./tictactoe.db` | URL de conexión (SQLAlchemy async) |
| `TTT_JWT_SECRET` | *(autogenerado si no se define)* | Secreto para firmar JWT. Si no se define, se genera uno **aleatorio** en arranque (no hay secretos en el repo). **Defínelo en producción** para que las sesiones sobrevivan a reinicios y entre réplicas |
| `TTT_JWT_EXPIRES_MINUTES` | `1440` | Caducidad del token |

---

## Arquitectura

Arquitectura **hexagonal ligera**: las dependencias apuntan hacia el dominio.

```
api  ─┐
cli  ─┤→ application (casos de uso + puertos) → domain (reglas puras)
      └→ infrastructure (SQLite, security) ──┘ implementa los puertos
```

```
src/tictactoe/
├── domain/           Reglas del juego: tablero, turnos, win/draw. Puro y síncrono.
├── application/      Casos de uso (game_service, auth_service), puertos (Protocols) y DTOs.
├── infrastructure/   BD async, seguridad (bcrypt + JWT), repositorios SQLite.
├── api/              FastAPI: routers, schemas Pydantic, wiring DI (deps.py), main.
└── cli/              Cliente de consola contra la API.
```

---

## Decisiones técnicas relevantes

- **Python 3.12 + FastAPI.** El requisito admitía Python 3.12 o Node 22; se eligió Python por
  disponibilidad y madurez. FastAPI aporta async nativo, validación con Pydantic y
  documentación OpenAPI/Swagger automática (cubre el valorable de *API REST documentada*).

- **Dominio puro y aislado.** Las reglas del juego (`domain/`) no dependen de framework, BD ni
  red: son funciones deterministas y síncronas sobre un tablero representado como cadena de 9
  caracteres. Esto las hace triviales de testear (todas las líneas ganadoras, empate, turnos,
  movimientos inválidos) sin levantar la app.

- **Asincronía donde aporta valor.** `async` en los endpoints HTTP y en el acceso a BD
  (SQLAlchemy async + `aiosqlite`), que es donde el I/O concurrente importa. El dominio se deja
  síncrono a propósito: meter async en cómputo puro solo añadiría complejidad. (El enunciado
  pide *“uso correcto de asincronía cuando aporte valor”*.)

- **Persistencia durable (requisito clave).** SQLite en fichero vía SQLAlchemy async. El estado
  completo de cada partida (tablero, turno, estado, resultado) y su log de movimientos se
  guardan, de modo que **al reiniciar la aplicación la partida continúa intacta**. Verificado
  por un test de integración que recrea la app sobre el mismo fichero.

- **Inversión de dependencias / DI.** Los repositorios se definen como `typing.Protocol`
  (`application/ports.py`) y se implementan en `infrastructure`. El ensamblado es **wiring
  manual explícito** con `Depends` de FastAPI (`api/deps.py`): una sesión por petición, repos y
  servicios construidos ahí. Sin “magia”, fácil de explicar y de sustituir en tests.

- **Separación de capas con DTOs.** Los repositorios traducen entre modelos ORM y *dataclasses*
  de aplicación, para que los servicios y el dominio no dependan de SQLAlchemy.

- **Autenticación y autorización.** Registro con contraseña hasheada (**bcrypt**) y login que
  emite un **JWT** (PyJWT) usado como bearer token; *stateless* y cómodo de consumir desde
  CLI/tests. Se usa `bcrypt` directamente (no `passlib`) por compatibilidad con bcrypt 5.x. La
  decodificación restringe el algoritmo (`HS256`) y rechaza tokens caducados, forjados con otro
  secreto o con `alg=none`. Además hay **control de acceso por recurso**: una partida y su log
  solo son accesibles para sus dos jugadores (evita IDOR); un tercero recibe `403`. El **secreto
  JWT nunca se cablea en el repo**: si no se define se genera uno aleatorio en arranque.

- **Manejo de errores uniforme.** Las excepciones de dominio/aplicación se mapean a códigos
  HTTP en un único lugar (`api/main.py`): p. ej. casilla ocupada → 409, fuera de turno → 403,
  partida inexistente → 404, no autenticado → 401. El estado nunca queda corrupto.

- **Testing.** `pytest` + `pytest-asyncio`; la integración usa `httpx.ASGITransport`
  (in-process, sin levantar servidor) con una BD SQLite temporal por test.

- **CI/CD.** GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) ejecuta
  lint (`ruff`) y tests (`pytest`) en Python 3.12 en cada push/PR.

### Alcance y simplificaciones

- Tablero estándar 3×3; el creador es X y el segundo en unirse es O.
- Sin frontend (sólo API + CLI), sin recuperación de contraseña ni OAuth, sin matchmaking.
- Un único nodo con almacenamiento local: suficiente para la escala de la prueba. Para
  producción multi-nodo se migraría SQLite → Postgres (mismo `GameRepository`, otra impl.) y
  se gestionaría el secreto JWT vía gestor de secretos.

---

## Proceso (Spec-Driven Development)

El desarrollo siguió el flujo de spec-kit, con un commit por fase:

1. **Constitution** — principios del proyecto.
2. **Specify** — [`spec.md`](specs/001-tic-tac-toe/spec.md): historias de usuario, requisitos, criterios de éxito.
3. **Plan** — [`plan.md`](specs/001-tic-tac-toe/plan.md) + research, data-model, contracts, quickstart.
4. **Tasks** — [`tasks.md`](specs/001-tic-tac-toe/tasks.md): tareas ordenadas por historia.
5. **Analyze** — [`analysis.md`](specs/001-tic-tac-toe/analysis.md): consistencia spec ↔ plan ↔ tasks.
6. **Implement** — código + tests.
