"""Endpoints de autenticación."""

from __future__ import annotations

from fastapi import APIRouter, status

from ..deps import AuthServiceDep, CurrentPlayer
from ..schemas import (
    LoginRequest,
    PlayerPublic,
    PlayerResponse,
    RegisterRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=PlayerPublic, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth: AuthServiceDep) -> PlayerPublic:
    player = await auth.register(payload.username, payload.password)
    return PlayerPublic.from_entity(player)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, auth: AuthServiceDep) -> TokenResponse:
    token = await auth.login(payload.username, payload.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=PlayerResponse)
async def me(current: CurrentPlayer) -> PlayerResponse:
    return PlayerResponse.from_entity(current)
