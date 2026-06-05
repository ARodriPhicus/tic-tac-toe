"""Casos de uso de autenticación: registro, login y resolución del jugador actual."""

from __future__ import annotations

from ..config import Settings
from ..infrastructure import security
from .dto import PlayerEntity
from .exceptions import InvalidCredentials, NotAuthenticated, UsernameTaken
from .ports import PlayerRepository


class AuthService:
    def __init__(self, players: PlayerRepository, settings: Settings) -> None:
        self._players = players
        self._settings = settings

    async def register(self, username: str, password: str) -> PlayerEntity:
        if await self._players.get_by_username(username):
            raise UsernameTaken(f"El usuario '{username}' ya existe.")
        player = PlayerEntity(
            username=username, hashed_password=security.hash_password(password)
        )
        return await self._players.add(player)

    async def login(self, username: str, password: str) -> str:
        player = await self._players.get_by_username(username)
        if player is None or not security.verify_password(password, player.hashed_password):
            raise InvalidCredentials("Usuario o contraseña incorrectos.")
        return security.create_access_token(player.id, self._settings)

    async def player_from_token(self, token: str) -> PlayerEntity:
        player_id = security.decode_access_token(token, self._settings)
        if player_id is None:
            raise NotAuthenticated("Token inválido o expirado.")
        player = await self._players.get_by_id(player_id)
        if player is None:
            raise NotAuthenticated("El jugador del token no existe.")
        return player
