from __future__ import annotations

from dataclasses import dataclass

import chess

from .evaluator import reference_evaluate
from .openings import apply_indexed_opening
from .search import Searcher


@dataclass(frozen=True, slots=True)
class ArenaJob:
    candidate: dict[str, float]
    champion: dict[str, float]
    games: int
    depth: int
    max_plies: int
    material_adjudication_cp: int
    quiescence_depth: int


@dataclass(frozen=True, slots=True)
class ArenaResult:
    score: float
    wins: int
    draws: int
    losses: int
    games: int


def _adjudicate(
    board: chess.Board,
    candidate_is_white: bool,
    threshold: int,
) -> float:
    if board.is_checkmate():
        white_won = board.turn == chess.BLACK
        return 1.0 if white_won == candidate_is_white else 0.0

    if board.is_game_over():
        return 0.5

    score = reference_evaluate(board)
    candidate_score = score if candidate_is_white else -score

    if candidate_score > threshold:
        return 1.0
    if candidate_score < -threshold:
        return 0.0
    return 0.5


def run_arena(job: ArenaJob) -> ArenaResult:
    total = 0.0
    wins = 0
    draws = 0
    losses = 0

    for game_index in range(job.games):
        board = chess.Board()
        apply_indexed_opening(board, game_index)
        candidate_is_white = game_index % 2 == 0
        remaining = job.max_plies

        while not board.is_game_over() and remaining > 0:
            use_candidate = (board.turn == chess.WHITE) == candidate_is_white
            weights = job.candidate if use_candidate else job.champion
            searcher = Searcher(weights, job.quiescence_depth)
            result = searcher.search(board, job.depth)
            if result.move is None:
                break
            board.push(result.move)
            remaining -= 1

        score = _adjudicate(
            board,
            candidate_is_white,
            job.material_adjudication_cp,
        )
        total += score

        if score > 0.75:
            wins += 1
        elif score < 0.25:
            losses += 1
        else:
            draws += 1

    return ArenaResult(
        score=total / job.games,
        wins=wins,
        draws=draws,
        losses=losses,
        games=job.games,
    )
