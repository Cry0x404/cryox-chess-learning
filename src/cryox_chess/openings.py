from __future__ import annotations

import random

import chess

from .constants import OPENINGS


def apply_random_opening(
    board: chess.Board,
    random_source: random.Random,
) -> None:
    line = random_source.choice(OPENINGS)
    prefix = random_source.randint(0, len(line))
    for uci in line[:prefix]:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            break
        board.push(move)


def apply_indexed_opening(
    board: chess.Board,
    game_index: int,
) -> None:
    line = OPENINGS[(game_index // 2) % len(OPENINGS)]
    prefix = min(
        len(line),
        2 + ((game_index // 2) % max(1, min(4, len(line)))),
    )
    for uci in line[:prefix]:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            break
        board.push(move)
