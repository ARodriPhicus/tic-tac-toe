"""Fixtures de test: app con BD temporal y cliente HTTP async (in-process, sin servidor)."""

from __future__ import annotations

import httpx
import pytest
import pytest_asyncio
from tests._helpers import build_app, build_settings


@pytest.fixture
def settings(tmp_path):
    return build_settings(str(tmp_path / "test.db"))


@pytest_asyncio.fixture
async def client(settings):
    app, engine = await build_app(settings)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await engine.dispose()


@pytest_asyncio.fixture
async def two_players(client):
    """Registra dos jugadores y devuelve sus cabeceras de autorización + ids."""
    out = {}
    for name in ("ana", "bob"):
        reg = await client.post("/auth/register", json={"username": name, "password": "pw"})
        login = await client.post("/auth/login", json={"username": name, "password": "pw"})
        token = login.json()["access_token"]
        out[name] = {
            "id": reg.json()["id"],
            "headers": {"Authorization": f"Bearer {token}"},
        }
    return out
