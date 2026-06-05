# Tic-Tac-Toe Backend Constitution

Principios de ingeniería que rigen este proyecto. Toda decisión de diseño, plan
e implementación debe poder justificarse contra estos principios.

## Core Principles

### I. Dominio puro y aislado (Domain-First)
La lógica del juego (tablero, turnos, validación de movimientos, detección de
ganador/empate) vive en un dominio sin dependencias de I/O, frameworks ni base de
datos. Debe ser determinista, sincrónico y 100% testeable de forma unitaria sin
levantar la aplicación. La infraestructura depende del dominio, nunca al revés.

### II. Interfaz por contrato (API + CLI)
La funcionalidad se expone mediante una API REST documentada (OpenAPI/Swagger) y,
adicionalmente, un CLI mínimo capaz de jugar una partida completa. El contrato de
la API es estable y validado: entradas inválidas producen errores claros con el
código HTTP adecuado; nunca un estado corrupto.

### III. Test-First (NO NEGOCIABLE)
Cada regla del juego y cada endpoint tiene pruebas. El dominio se cubre con tests
unitarios (todas las líneas ganadoras, empate, turno incorrecto, celda ocupada,
fuera de rango). Los flujos de API se cubren con tests de integración asíncronos.
No se da por terminada una funcionalidad sin sus tests en verde.

### IV. Asincronía donde aporta valor
La asincronía se usa solo donde aporta valor real: I/O de red (endpoints HTTP) y
acceso a base de datos (driver async). El dominio permanece síncrono porque es
cómputo puro y la concurrencia ahí solo añadiría complejidad sin beneficio.

### V. Inversión de dependencias y persistencia durable
Los casos de uso dependen de puertos (interfaces/Protocols), no de
implementaciones concretas. Las implementaciones (repositorios SQLite, seguridad)
se inyectan por wiring explícito, lo que permite sustituirlas en tests. El estado
de las partidas se persiste de forma durable y sobrevive a reinicios de la app.

## Additional Constraints (Technology & Quality)

- **Runtime**: Python 3.12. El código debe ejecutarse en un intérprete 3.12 limpio.
- **Stack**: FastAPI (API async + OpenAPI), SQLAlchemy async + SQLite (aiosqlite)
  para persistencia, Pydantic para validación de I/O, pytest para tests.
- **Calidad**: linting con Ruff; tipado con anotaciones; funciones pequeñas y con
  responsabilidad única; mensajes de error orientados al consumidor de la API.
- **Seguridad**: contraseñas siempre hasheadas; autenticación por token; ningún
  secreto en el repositorio.

## Development Workflow (Spec-Driven)

El desarrollo sigue el flujo de spec-kit y se versiona en Git por fases:
`constitution → specify → (clarify) → plan → tasks → (analyze) → implement`.
Cada fase produce un artefacto versionado en `specs/` y un commit independiente.
Los requisitos mínimos de la prueba son obligatorios; los valorables se abordan
solo tras cubrir los mínimos con calidad.

## Governance

Esta constitución prevalece sobre preferencias ad-hoc. Cualquier desviación
(p. ej. añadir complejidad no justificada) debe documentarse en el apartado
*Complexity Tracking* del plan con su justificación y la alternativa más simple
descartada. La trazabilidad spec ↔ plan ↔ tasks ↔ código debe mantenerse.

**Version**: 1.0.0 | **Ratified**: 2026-06-05 | **Last Amended**: 2026-06-05
