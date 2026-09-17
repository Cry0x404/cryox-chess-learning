from __future__ import annotations

import chess

SCHEMA_VERSION = 3

PIECE_VALUES = {
    chess.PAWN: 1.00,
    chess.KNIGHT: 3.15,
    chess.BISHOP: 3.25,
    chess.ROOK: 5.00,
    chess.QUEEN: 9.00,
    chess.KING: 0.0,
}

PRIORS = {
    "material": 1.00,
    "mobility": 0.10,
    "center_control": 0.16,
    "space": 0.08,
    "development": 0.12,
    "king_safety": 0.22,
    "king_pressure": 0.14,
    "bishop_pair": 0.18,
    "knight_outpost": 0.10,
    "knight_rim": 0.08,
    "passed_pawn": 0.24,
    "connected_passed": 0.18,
    "pawn_advance": 0.08,
    "isolated_pawn": 0.10,
    "doubled_pawn": 0.11,
    "pawn_islands": 0.08,
    "rook_open_file": 0.13,
    "rook_seventh": 0.12,
    "queen_discipline": 0.10,
    "hanging_piece": 0.24,
    "undefended_piece": 0.08,
    "piece_activity": 0.10,
    "castling_rights": 0.06,
    "endgame_king": 0.14,
    "promotion_threat": 0.30,
    "tempo": 0.04,
}

BOUNDS = {
    "material": (0.82, 1.30),
    "mobility": (0.02, 0.40),
    "center_control": (0.04, 0.55),
    "space": (0.01, 0.30),
    "development": (0.03, 0.45),
    "king_safety": (0.06, 0.80),
    "king_pressure": (0.03, 0.55),
    "bishop_pair": (0.05, 0.45),
    "knight_outpost": (0.02, 0.35),
    "knight_rim": (0.01, 0.30),
    "passed_pawn": (0.06, 0.70),
    "connected_passed": (0.04, 0.60),
    "pawn_advance": (0.02, 0.28),
    "isolated_pawn": (0.02, 0.38),
    "doubled_pawn": (0.02, 0.42),
    "pawn_islands": (0.01, 0.30),
    "rook_open_file": (0.03, 0.42),
    "rook_seventh": (0.03, 0.45),
    "queen_discipline": (0.02, 0.35),
    "hanging_piece": (0.06, 0.85),
    "undefended_piece": (0.01, 0.35),
    "piece_activity": (0.02, 0.40),
    "castling_rights": (0.01, 0.25),
    "endgame_king": (0.03, 0.55),
    "promotion_threat": (0.08, 1.00),
    "tempo": (0.01, 0.18),
}

OPENINGS = [
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
    ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4"],
    ["e2e4", "e7e6", "d2d4", "d7d5"],
    ["e2e4", "c7c6", "d2d4", "d7d5"],
    ["d2d4", "d7d5", "c2c4", "e7e6"],
    ["d2d4", "g8f6", "c2c4", "g7g6"],
    ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4"],
    ["c2c4", "e7e5", "b1c3", "g8f6"],
    ["g1f3", "d7d5", "g2g3", "g8f6"],
    ["e2e4", "e7e5", "f2f4"],
    ["e2e4", "d7d5", "e4d5", "d8d5"],
    ["d2d4", "f7f5", "g2g3", "g8f6"],
]

CENTER = (chess.D4, chess.E4, chess.D5, chess.E5)
