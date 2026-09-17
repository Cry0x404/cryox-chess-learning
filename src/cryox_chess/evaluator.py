from __future__ import annotations

import math

import chess

from .constants import BOUNDS, PRIORS
from .features import extract_features


def clamp_weight(name: str, value: float) -> float:
    lower, upper = BOUNDS[name]
    return max(lower, min(upper, float(value)))


def sanitize_weights(weights: dict[str, float]) -> dict[str, float]:
    result = {}
    for name, prior in PRIORS.items():
        try:
            value = float(weights.get(name, prior))
        except (TypeError, ValueError):
            value = prior
        if not math.isfinite(value):
            value = prior
        result[name] = clamp_weight(name, value)
    return result


def evaluate(board: chess.Board, weights: dict[str, float]) -> float:
    if board.is_checkmate():
        return -100000.0 if board.turn == chess.WHITE else 100000.0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0
    features = extract_features(board)
    return 100.0 * sum(weights[name] * features[name] for name in PRIORS)


def reference_evaluate(board: chess.Board) -> float:
    return evaluate(board, PRIORS)


def sanity_check(weights: dict[str, float]) -> bool:
    clean = sanitize_weights(weights)
    if any(not math.isfinite(value) for value in clean.values()):
        return False

    extra_white_queen = chess.Board("4k3/8/8/8/8/8/4Q3/4K3 w - - 0 1")
    extra_black_queen = chess.Board("4k3/4q3/8/8/8/8/8/4K3 w - - 0 1")

    if evaluate(extra_white_queen, clean) < 500:
        return False
    return evaluate(extra_black_queen, clean) <= -500
