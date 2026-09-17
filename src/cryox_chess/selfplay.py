from __future__ import annotations

import math
import random
from dataclasses import dataclass

import chess

from .constants import PRIORS
from .evaluator import reference_evaluate
from .features import extract_features
from .learning import temporal_difference_update
from .openings import apply_random_opening
from .search import Searcher


@dataclass(frozen=True, slots=True)
class SelfPlayJob:
    weights: dict[str, float]
    depth: int
    max_plies: int
    learning_rate: float
    prior_regularization: float
    exploration_initial: float
    exploration_floor: float
    quiescence_depth: int
    seed: int


@dataclass(frozen=True, slots=True)
class SelfPlayResult:
    weights: dict[str, float]
    target: float
    plies: int
    positions: int


def _target(board: chess.Board) -> float:
    if board.is_checkmate():
        return -1.0 if board.turn == chess.WHITE else 1.0
    if board.is_game_over():
        return 0.0
    return math.tanh(reference_evaluate(board) / 700.0)


def _select_move(
    board: chess.Board,
    weights: dict[str, float],
    depth: int,
    quiescence_depth: int,
    exploration: float,
    random_source: random.Random,
) -> chess.Move | None:
    moves = list(board.legal_moves)
    if not moves:
        return None

    searcher = Searcher(weights, quiescence_depth)

    if random_source.random() < exploration:
        ordered = searcher.ordered_moves(board)
        return random_source.choice(ordered[: min(6, len(ordered))])

    return searcher.search(board, depth).move


def run_self_play(job: SelfPlayJob) -> SelfPlayResult:
    random_source = random.Random(job.seed)
    board = chess.Board()
    apply_random_opening(board, random_source)
    trajectory: list[dict[str, float]] = []
    plies = 0

    while not board.is_game_over() and plies < job.max_plies:
        trajectory.append(extract_features(board))
        decay = 1.0 - plies / job.max_plies
        exploration = max(
            job.exploration_floor,
            job.exploration_initial * decay,
        )
        move = _select_move(
            board,
            job.weights,
            job.depth,
            job.quiescence_depth,
            exploration,
            random_source,
        )
        if move is None:
            break
        board.push(move)
        plies += 1

    target = _target(board)
    learned = temporal_difference_update(
        trajectory,
        target,
        job.weights,
        job.learning_rate,
        job.prior_regularization,
    )

    return SelfPlayResult(
        weights=learned,
        target=target,
        plies=plies,
        positions=len(trajectory),
    )


def merge_results(
    results: list[SelfPlayResult],
    base: dict[str, float],
) -> dict[str, float]:
    if not results:
        return dict(base)

    merged = {}
    for name in PRIORS:
        average = sum(result.weights[name] for result in results) / len(results)
        merged[name] = 0.85 * average + 0.15 * base[name]
    return merged
