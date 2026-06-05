"""Endpoints de partidas, movimientos y leaderboard."""

from __future__ import annotations

from fastapi import APIRouter, status

from ..deps import CurrentPlayer, GameServiceDep
from ..schemas import GameResponse, MoveRequest, MoveResponse, PlayerResponse

router = APIRouter(tags=["games"])


@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(current: CurrentPlayer, games: GameServiceDep) -> GameResponse:
    game = await games.create_game(current.id)
    return GameResponse.from_entity(game)


@router.post("/games/{game_id}/join", response_model=GameResponse)
async def join_game(
    game_id: int, current: CurrentPlayer, games: GameServiceDep
) -> GameResponse:
    game = await games.join_game(game_id, current.id)
    return GameResponse.from_entity(game)


@router.get("/games", response_model=list[GameResponse])
async def list_games(current: CurrentPlayer, games: GameServiceDep) -> list[GameResponse]:
    items = await games.list_games(current.id)
    return [GameResponse.from_entity(g) for g in items]


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int, current: CurrentPlayer, games: GameServiceDep
) -> GameResponse:
    game = await games.get_game(game_id)
    return GameResponse.from_entity(game)


@router.post("/games/{game_id}/moves", response_model=GameResponse)
async def make_move(
    game_id: int, payload: MoveRequest, current: CurrentPlayer, games: GameServiceDep
) -> GameResponse:
    game = await games.make_move(game_id, current.id, payload.position)
    return GameResponse.from_entity(game)


@router.get("/games/{game_id}/moves", response_model=list[MoveResponse])
async def list_moves(
    game_id: int, current: CurrentPlayer, games: GameServiceDep
) -> list[MoveResponse]:
    moves = await games.get_moves(game_id)
    return [MoveResponse.from_entity(m) for m in moves]


@router.get("/leaderboard", response_model=list[PlayerResponse])
async def leaderboard(games: GameServiceDep) -> list[PlayerResponse]:
    players = await games.leaderboard()
    return [PlayerResponse.from_entity(p) for p in players]
