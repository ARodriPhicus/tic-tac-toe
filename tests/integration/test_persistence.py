"""Verifica que el estado de la partida sobrevive al 'reinicio' de la aplicación.

Se simula el reinicio creando una segunda instancia de la app (nuevo engine/sesiones)
apuntando al mismo fichero SQLite, tal como ocurriría al relanzar el proceso.
"""

from __future__ import annotations

import httpx
from tests._helpers import build_app, build_settings


async def _client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_game_state_survives_restart(tmp_path):
    db_path = str(tmp_path / "persist.db")
    settings = build_settings(db_path)

    # --- Primera ejecución: registro, partida y un par de movimientos. ---
    app1, engine1 = await build_app(settings)
    async with await _client_for(app1) as c1:
        await c1.post("/auth/register", json={"username": "ana", "password": "pw"})
        await c1.post("/auth/register", json={"username": "bob", "password": "pw"})
        tok_a = (await c1.post("/auth/login", json={"username": "ana", "password": "pw"})).json()[
            "access_token"
        ]
        tok_b = (await c1.post("/auth/login", json={"username": "bob", "password": "pw"})).json()[
            "access_token"
        ]
        ha = {"Authorization": f"Bearer {tok_a}"}
        hb = {"Authorization": f"Bearer {tok_b}"}

        game_id = (await c1.post("/games", headers=ha)).json()["id"]
        await c1.post(f"/games/{game_id}/join", headers=hb)
        await c1.post(f"/games/{game_id}/moves", json={"position": 0}, headers=ha)
        await c1.post(f"/games/{game_id}/moves", json={"position": 4}, headers=hb)
        before = (await c1.get(f"/games/{game_id}", headers=ha)).json()
    await engine1.dispose()

    # --- Reinicio: nueva instancia sobre el mismo fichero. ---
    app2, engine2 = await build_app(settings)
    async with await _client_for(app2) as c2:
        tok_a2 = (await c2.post("/auth/login", json={"username": "ana", "password": "pw"})).json()[
            "access_token"
        ]
        ha2 = {"Authorization": f"Bearer {tok_a2}"}
        after = (await c2.get(f"/games/{game_id}", headers=ha2)).json()
    await engine2.dispose()

    assert after["board"] == before["board"]
    assert after["current_turn"] == before["current_turn"]
    assert after["status"] == before["status"]
    assert after["board"][0] == "X" and after["board"][4] == "O"
