"""Tests de integración del flujo de partida vía API."""


async def _create_and_join(client, two_players):
    ana, bob = two_players["ana"], two_players["bob"]
    created = await client.post("/games", headers=ana["headers"])
    assert created.status_code == 201
    game_id = created.json()["id"]
    joined = await client.post(f"/games/{game_id}/join", headers=bob["headers"])
    assert joined.status_code == 200
    assert joined.json()["status"] == "in_progress"
    return game_id, ana, bob


async def _move(client, game_id, player, position):
    return await client.post(
        f"/games/{game_id}/moves", json={"position": position}, headers=player["headers"]
    )


async def test_full_game_x_wins(client, two_players):
    game_id, ana, bob = await _create_and_join(client, two_players)

    # X(ana): 0,1,2 (fila superior) intercalado con O(bob): 3,4
    assert (await _move(client, game_id, ana, 0)).status_code == 200
    assert (await _move(client, game_id, bob, 3)).status_code == 200
    assert (await _move(client, game_id, ana, 1)).status_code == 200
    assert (await _move(client, game_id, bob, 4)).status_code == 200
    final = await _move(client, game_id, ana, 2)
    assert final.status_code == 200
    body = final.json()
    assert body["status"] == "finished"
    assert body["result"] == "x_won"
    assert body["winner_id"] == ana["id"]

    # El leaderboard refleja la puntuación.
    lb = (await client.get("/leaderboard")).json()
    scores = {p["username"]: p for p in lb}
    assert scores["ana"]["wins"] == 1
    assert scores["bob"]["losses"] == 1

    # El log de movimientos está completo y en orden.
    log = (await client.get(f"/games/{game_id}/moves", headers=ana["headers"])).json()
    assert [m["move_number"] for m in log] == [1, 2, 3, 4, 5]
    assert log[0]["mark"] == "X" and log[0]["position"] == 0


async def test_move_out_of_turn_is_rejected(client, two_players):
    game_id, ana, bob = await _create_and_join(client, two_players)
    # Empieza X; si O intenta jugar primero -> 403 (no es su turno).
    res = await _move(client, game_id, bob, 0)
    assert res.status_code == 403


async def test_move_on_occupied_cell_is_rejected(client, two_players):
    game_id, ana, bob = await _create_and_join(client, two_players)
    await _move(client, game_id, ana, 0)
    res = await _move(client, game_id, bob, 0)
    assert res.status_code == 409


async def test_out_of_range_position_is_rejected(client, two_players):
    game_id, ana, bob = await _create_and_join(client, two_players)
    res = await _move(client, game_id, ana, 99)
    assert res.status_code == 422  # validado por Pydantic (ge=0, le=8)


async def test_non_participant_cannot_move(client, two_players):
    game_id, ana, bob = await _create_and_join(client, two_players)
    # Tercer jugador
    await client.post("/auth/register", json={"username": "eve", "password": "pw"})
    login = await client.post("/auth/login", json={"username": "eve", "password": "pw"})
    eve_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = await client.post(
        f"/games/{game_id}/moves", json={"position": 0}, headers=eve_headers
    )
    assert res.status_code == 403


async def test_cannot_move_before_second_player_joins(client, two_players):
    ana = two_players["ana"]
    game_id = (await client.post("/games", headers=ana["headers"])).json()["id"]
    res = await _move(client, game_id, ana, 0)
    assert res.status_code == 409  # GameNotInProgress


async def test_join_full_game_is_rejected(client, two_players):
    game_id, ana, bob = await _create_and_join(client, two_players)
    await client.post("/auth/register", json={"username": "eve", "password": "pw"})
    login = await client.post("/auth/login", json={"username": "eve", "password": "pw"})
    eve_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = await client.post(f"/games/{game_id}/join", headers=eve_headers)
    assert res.status_code == 409


async def test_get_unknown_game_is_404(client, two_players):
    res = await client.get("/games/9999", headers=two_players["ana"]["headers"])
    assert res.status_code == 404
