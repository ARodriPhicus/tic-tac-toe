# Feature Specification: Tic-Tac-Toe (Tres en Raya) Backend

**Feature Branch**: `001-tic-tac-toe`

**Created**: 2026-06-05

**Status**: Ready for Planning

**Input**: Prueba técnica — "Desarrolla el backend necesario de una pequeña aplicación que
permita jugar al Tic-Tac-Toe / Tres en raya. No es necesario desarrollar frontend. La
aplicación debe poder utilizarse mediante una interfaz mínima de tu elección, siempre que
permita jugar una partida completa y validar correctamente las reglas del juego, o desde la
consola usando un CLI básico."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Jugar una partida completa por turnos (Priority: P1)

Dos jugadores juegan una partida de tres en raya. El primero coloca su marca (X) en una
casilla libre, luego le toca al segundo (O), y así alternándose. El sistema impide jugar
fuera de turno o en casillas ocupadas, muestra el estado del tablero tras cada jugada y
declara el resultado (gana X, gana O o empate) cuando corresponde.

**Why this priority**: Es el corazón del producto y cubre los requisitos mínimos de la
prueba (2 jugadores con orden validado, validación de movimientos, visualización del
tablero y detección de ganador). Sin esto no hay juego.

**Independent Test**: Se puede probar de extremo a extremo creando una partida, alternando
movimientos válidos hasta una victoria o empate, y comprobando que los movimientos
inválidos son rechazados y el resultado final es correcto.

**Acceptance Scenarios**:

1. **Given** una partida nueva con dos jugadores, **When** el jugador X juega en una casilla
   libre, **Then** la casilla queda marcada con X y el turno pasa a O.
2. **Given** que es el turno de O, **When** X intenta volver a jugar, **Then** el sistema
   rechaza el movimiento por orden de turno y el tablero no cambia.
3. **Given** una casilla ya ocupada, **When** un jugador intenta jugar en ella, **Then** el
   sistema rechaza el movimiento por casilla ocupada.
4. **Given** un tablero donde X tiene dos en línea y la tercera casilla libre, **When** X
   completa la línea (fila, columna o diagonal), **Then** la partida termina con X como
   ganador y no se aceptan más movimientos.
5. **Given** un tablero lleno sin tres en línea, **When** se juega la última casilla,
   **Then** la partida termina en empate.

---

### User Story 2 - Persistir el estado de la partida (Priority: P1)

El estado de las partidas (tablero, turno, jugadores, resultado) debe conservarse aunque la
aplicación se reinicie, de modo que una partida en curso pueda continuarse después.

**Why this priority**: Es un requisito mínimo explícito de la prueba ("Mantener el estado de
la partida aunque se reinicie la aplicación").

**Independent Test**: Crear una partida y hacer algunos movimientos; reiniciar la aplicación;
consultar la partida y verificar que el tablero y el turno se conservan exactamente, pudiendo
seguir jugando.

**Acceptance Scenarios**:

1. **Given** una partida con varios movimientos jugados, **When** la aplicación se detiene y
   se vuelve a arrancar, **Then** al consultar la partida el tablero y el turno son idénticos
   a antes del reinicio.
2. **Given** una partida finalizada, **When** la aplicación se reinicia, **Then** el resultado
   (ganador/empate) y el historial se conservan.

---

### User Story 3 - Identidad de jugador, historial y puntuación (Priority: P2)

Los jugadores se registran e inician sesión para tener identidad propia. El sistema permite
múltiples jugadores y múltiples partidas simultáneas, lleva un historial de partidas jugadas
y un marcador (victorias, derrotas, empates) por jugador, y permite consultar el log de
movimientos de cada partida.

**Why this priority**: Cubre requisitos valorables (autenticación y sesiones, múltiples
partidas/jugadores, control de partidas con puntuación, log consultable). Aporta valor pero
no es imprescindible para jugar una partida.

**Independent Test**: Registrar dos jugadores, jugar una partida hasta el final y comprobar
que el marcador de cada jugador y el historial reflejan el resultado, y que el log de
movimientos de la partida se puede consultar.

**Acceptance Scenarios**:

1. **Given** un nombre de usuario no registrado, **When** el jugador se registra, **Then**
   queda creado y puede iniciar sesión para obtener un token de acceso.
2. **Given** un jugador autenticado, **When** crea una partida, **Then** queda como jugador X
   y la partida espera a que un segundo jugador se una como O.
3. **Given** una partida finalizada con ganador, **When** se consulta la puntuación de los
   jugadores, **Then** el ganador suma una victoria y el otro una derrota (o ambos un empate).
4. **Given** una partida con movimientos, **When** se consulta su log, **Then** se obtienen
   los movimientos en orden con jugador, casilla y número de jugada.

---

### Edge Cases

- Intentar jugar en una partida que ya ha terminado → rechazado (partida finalizada).
- Intentar jugar en una partida que aún no tiene segundo jugador → rechazado (faltan jugadores).
- Casilla fuera del rango válido del tablero (0–8) → rechazado por entrada inválida.
- Un tercer jugador intenta unirse a una partida ya completa → rechazado.
- Un jugador que no pertenece a la partida intenta mover → rechazado (no autorizado).
- Registrar un nombre de usuario ya existente → rechazado (conflicto).
- Acceder a endpoints protegidos sin token o con token inválido → rechazado (no autenticado).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir crear una partida de tres en raya entre dos jugadores.
- **FR-002**: El sistema MUST validar el orden de turnos: X juega primero y los turnos se
  alternan; un movimiento fuera de turno MUST ser rechazado.
- **FR-003**: El sistema MUST validar cada movimiento e impedir movimientos no válidos
  (casilla ocupada, casilla fuera de rango, partida no iniciada o ya finalizada).
- **FR-004**: El sistema MUST permitir visualizar el estado actual del tablero y de quién es
  el turno.
- **FR-005**: El sistema MUST detectar y declarar el resultado de la partida: victoria (tres
  en línea en fila, columna o diagonal) o empate (tablero lleno sin línea).
- **FR-006**: El sistema MUST persistir el estado de las partidas de forma durable, de modo
  que sobreviva al reinicio de la aplicación.
- **FR-007**: El sistema MUST permitir el registro e inicio de sesión de jugadores y proteger
  las operaciones de juego mediante autenticación.
- **FR-008**: El sistema MUST soportar múltiples jugadores y múltiples partidas simultáneas.
- **FR-009**: El sistema MUST llevar un control de partidas jugadas y la puntuación
  (victorias, derrotas, empates) por jugador.
- **FR-010**: El sistema MUST registrar el log de movimientos de cada partida y permitir su
  consulta en orden.
- **FR-011**: El sistema MUST exponer la funcionalidad mediante una interfaz utilizable (API
  documentada) y un CLI mínimo capaz de jugar una partida completa.
- **FR-012**: El sistema MUST devolver errores claros y con el significado adecuado ante
  entradas inválidas o acciones no permitidas, sin corromper el estado.

### Key Entities *(include if feature involves data)*

- **Player (Jugador)**: Identidad con nombre de usuario único y credencial. Acumula marcador:
  victorias, derrotas y empates.
- **Game (Partida)**: Representa una partida entre dos jugadores (X y O). Contiene el estado
  del tablero (9 casillas), de quién es el turno, el estado (esperando jugador, en curso,
  finalizada) y el resultado (ganador o empate).
- **Move (Movimiento)**: Una jugada dentro de una partida: jugador que la realiza, casilla,
  marca y número de orden. El conjunto de movimientos de una partida constituye su log.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede jugar una partida completa (desde la creación hasta un
  resultado válido) usando exclusivamente la interfaz mínima, sin intervención manual sobre
  el almacenamiento.
- **SC-002**: El 100% de los movimientos inválidos (fuera de turno, casilla ocupada, fuera de
  rango, partida finalizada) son rechazados sin alterar el estado del tablero.
- **SC-003**: Todas las condiciones de victoria (3 filas, 3 columnas, 2 diagonales) y el
  empate se detectan correctamente en el 100% de los casos.
- **SC-004**: Tras reiniciar la aplicación, el estado de una partida en curso se recupera de
  forma idéntica en el 100% de los casos.
- **SC-005**: El marcador y el historial reflejan el resultado de cada partida finalizada de
  forma consistente.

## Assumptions

- El tablero es el estándar de 3×3 (9 casillas indexadas 0–8) y las marcas son X y O.
- El creador de la partida juega con X; el segundo jugador en unirse juega con O.
- La autenticación es por token de portador (bearer) sobre usuario/contraseña; no se
  requiere recuperación de contraseña ni proveedores externos (OAuth) para esta versión.
- No se implementa rendición, revancha automática ni emparejamiento (matchmaking): el segundo
  jugador se une explícitamente a una partida concreta.
- No hay frontend; la validación de reglas se demuestra vía API y CLI.
- Un único nodo de aplicación con almacenamiento local es suficiente para la escala de la prueba.
