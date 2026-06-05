"""CLI mínimo para jugar una partida completa de tres en raya contra la API REST.

Uso (con la API arrancada en http://127.0.0.1:8000):

    python -m tictactoe.cli

Permite registrar/iniciar sesión de dos jugadores, crear/unirse a una partida y jugar por
turnos desde la consola. Se comunica exclusivamente vía HTTP, validando toda la pila.
"""

from __future__ import annotations

import argparse
import sys

import httpx


class ApiError(RuntimeError):
    pass


class Client:
    def __init__(self, base_url: str) -> None:
        self._http = httpx.Client(base_url=base_url, timeout=10.0)

    def _detail(self, resp: httpx.Response) -> str:
        try:
            return resp.json().get("detail", resp.text)
        except Exception:
            return resp.text

    def auth(self, username: str, password: str) -> dict[str, str]:
        """Registra (si hace falta) e inicia sesión; devuelve la cabecera de autorización."""
        self._http.post("/auth/register", json={"username": username, "password": password})
        resp = self._http.post("/auth/login", json={"username": username, "password": password})
        if resp.status_code != 200:
            raise ApiError(f"Login falló para {username}: {self._detail(resp)}")
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def create_game(self, headers: dict[str, str]) -> dict:
        resp = self._http.post("/games", headers=headers)
        if resp.status_code != 201:
            raise ApiError(f"No se pudo crear la partida: {self._detail(resp)}")
        return resp.json()

    def join_game(self, game_id: int, headers: dict[str, str]) -> dict:
        resp = self._http.post(f"/games/{game_id}/join", headers=headers)
        if resp.status_code != 200:
            raise ApiError(f"No se pudo unir a la partida: {self._detail(resp)}")
        return resp.json()

    def move(self, game_id: int, position: int, headers: dict[str, str]) -> tuple[int, dict]:
        resp = self._http.post(
            f"/games/{game_id}/moves", json={"position": position}, headers=headers
        )
        try:
            body = resp.json()
        except Exception:
            body = {"detail": resp.text}
        return resp.status_code, body

    def close(self) -> None:
        self._http.close()


def _print_board(board_pretty: str) -> None:
    print("\n" + board_pretty + "\n")


def _ask_position(player_name: str, mark: str) -> int | None:
    raw = input(f"Turno de {player_name} ({mark}) — casilla 0-8 (q para salir): ").strip()
    if raw.lower() in {"q", "quit", "exit"}:
        return None
    if not raw.isdigit():
        print("  Entrada no válida; introduce un número del 0 al 8.")
        return _ask_position(player_name, mark)
    return int(raw)


def play(base_url: str) -> int:
    print("== Tres en Raya (CLI) ==")
    print("Casillas:\n 0 | 1 | 2\n---+---+---\n 3 | 4 | 5\n---+---+---\n 6 | 7 | 8\n")
    client = Client(base_url)
    try:
        name_x = input("Nombre del jugador X: ").strip() or "playerX"
        name_o = input("Nombre del jugador O: ").strip() or "playerO"
        headers_x = client.auth(name_x, "cli-password")
        headers_o = client.auth(name_o, "cli-password")

        game = client.create_game(headers_x)
        game = client.join_game(game["id"], headers_o)
        game_id = game["id"]

        marks = {"X": (name_x, headers_x), "O": (name_o, headers_o)}
        _print_board(game["board_pretty"])

        while game["status"] == "in_progress":
            turn = game["current_turn"]
            player_name, headers = marks[turn]
            position = _ask_position(player_name, turn)
            if position is None:
                print("Partida abandonada.")
                return 0
            status_code, body = client.move(game_id, position, headers)
            if status_code != 200:
                print(f"  Movimiento rechazado: {body.get('detail', body)}")
                continue
            game = body
            _print_board(game["board_pretty"])

        result = game.get("result")
        if result == "draw":
            print("¡Empate!")
        elif result == "x_won":
            print(f"¡Gana {name_x} (X)!")
        elif result == "o_won":
            print(f"¡Gana {name_o} (O)!")
        return 0
    except (ApiError, httpx.HTTPError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("¿Está la API en marcha? (uvicorn tictactoe.api.main:app)", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nInterrumpido.")
        return 0
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI de Tres en Raya (cliente de la API REST).")
    parser.add_argument(
        "--api",
        default="http://127.0.0.1:8000",
        help="URL base de la API (por defecto: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()
    return play(args.api)


if __name__ == "__main__":
    raise SystemExit(main())
