"""Tests de integración de autenticación."""


async def test_register_and_login_flow(client):
    reg = await client.post("/auth/register", json={"username": "ana", "password": "pw"})
    assert reg.status_code == 201
    assert reg.json()["username"] == "ana"

    login = await client.post("/auth/login", json={"username": "ana", "password": "pw"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["username"] == "ana"
    assert body["wins"] == 0


async def test_duplicate_username_conflicts(client):
    await client.post("/auth/register", json={"username": "ana", "password": "pw"})
    dup = await client.post("/auth/register", json={"username": "ana", "password": "other"})
    assert dup.status_code == 409


async def test_login_with_wrong_password(client):
    await client.post("/auth/register", json={"username": "ana", "password": "pw"})
    bad = await client.post("/auth/login", json={"username": "ana", "password": "nope"})
    assert bad.status_code == 401


async def test_protected_endpoint_requires_token(client):
    res = await client.get("/auth/me")
    assert res.status_code == 401


async def test_invalid_token_is_rejected(client):
    res = await client.get("/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert res.status_code == 401
