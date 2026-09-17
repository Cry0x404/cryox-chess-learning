from __future__ import annotations

import chess

from .constants import CENTER, PIECE_VALUES, PRIORS


def _phase(board: chess.Board) -> float:
    phase = 0
    phase += 4 * (
        len(board.pieces(chess.QUEEN, chess.WHITE))
        + len(board.pieces(chess.QUEEN, chess.BLACK))
    )
    phase += 2 * (
        len(board.pieces(chess.ROOK, chess.WHITE))
        + len(board.pieces(chess.ROOK, chess.BLACK))
    )
    phase += (
        len(board.pieces(chess.BISHOP, chess.WHITE))
        + len(board.pieces(chess.BISHOP, chess.BLACK))
        + len(board.pieces(chess.KNIGHT, chess.WHITE))
        + len(board.pieces(chess.KNIGHT, chess.BLACK))
    )
    return min(1.0, phase / 24.0)


def _pawn_files(board: chess.Board, color: chess.Color) -> list[int]:
    counts = [0] * 8
    for square in board.pieces(chess.PAWN, color):
        counts[chess.square_file(square)] += 1
    return counts


def _pawn_islands(counts: list[int]) -> int:
    islands = 0
    active = False
    for count in counts:
        if count and not active:
            islands += 1
            active = True
        elif not count:
            active = False
    return islands


def _is_passed(board: chess.Board, square: chess.Square, color: chess.Color) -> bool:
    file_index = chess.square_file(square)
    rank = chess.square_rank(square)
    for enemy_square in board.pieces(chess.PAWN, not color):
        enemy_file = chess.square_file(enemy_square)
        if abs(enemy_file - file_index) > 1:
            continue
        enemy_rank = chess.square_rank(enemy_square)
        if color == chess.WHITE and enemy_rank > rank:
            return False
        if color == chess.BLACK and enemy_rank < rank:
            return False
    return True


def _king_ring(board: chess.Board, color: chess.Color) -> list[chess.Square]:
    square = board.king(color)
    if square is None:
        return []
    return [square, *board.attacks(square)]


def _color_stats(
    board: chess.Board,
    color: chess.Color,
    middlegame: float,
    endgame: float,
) -> dict[str, float]:
    stats: dict[str, float] = {}

    stats["material"] = sum(
        PIECE_VALUES[piece_type] * len(board.pieces(piece_type, color))
        for piece_type in PIECE_VALUES
    )

    activity = 0.0
    central_activity = 0.0
    for piece_type in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
        for square in board.pieces(piece_type, color):
            activity += len(board.attacks(square))
            file_index = chess.square_file(square)
            rank = chess.square_rank(square)
            central_activity += max(
                0.0,
                3.5 - (abs(file_index - 3.5) + abs(rank - 3.5)) / 2.0,
            )

    stats["mobility"] = activity / 30.0
    stats["piece_activity"] = central_activity / 10.0

    center = 0.0
    for square in CENTER:
        center += 0.25 * len(board.attackers(color, square))
        piece = board.piece_at(square)
        if piece is not None and piece.color == color:
            center += 0.6
    stats["center_control"] = center

    space = 0
    for square in chess.scan_forward(board.occupied_co[color]):
        rank = chess.square_rank(square)
        if (color == chess.WHITE and rank >= 4) or (
            color == chess.BLACK and rank <= 3
        ):
            space += 1
    stats["space"] = space / 8.0

    start_squares = (
        (chess.B1, chess.G1, chess.C1, chess.F1)
        if color == chess.WHITE
        else (chess.B8, chess.G8, chess.C8, chess.F8)
    )
    undeveloped = 0
    for square in start_squares:
        piece = board.piece_at(square)
        if (
            piece is not None
            and piece.color == color
            and piece.piece_type in (chess.KNIGHT, chess.BISHOP)
        ):
            undeveloped += 1
    stats["development"] = (4 - undeveloped) / 4.0

    king_square = board.king(color)
    king_safety = 0.0
    if king_square is not None:
        file_index = chess.square_file(king_square)
        rank = chess.square_rank(king_square)
        shield_rank = rank + (1 if color == chess.WHITE else -1)
        if 0 <= shield_rank < 8:
            for shield_file in (file_index - 1, file_index, file_index + 1):
                if 0 <= shield_file < 8:
                    piece = board.piece_at(chess.square(shield_file, shield_rank))
                    if (
                        piece is not None
                        and piece.color == color
                        and piece.piece_type == chess.PAWN
                    ):
                        king_safety += 0.35
        attacks = sum(
            len(board.attackers(not color, square))
            for square in _king_ring(board, color)
        )
        king_safety -= 0.10 * attacks
    stats["king_safety"] = king_safety * middlegame

    opponent_ring = _king_ring(board, not color)
    stats["king_pressure"] = (
        sum(len(board.attackers(color, square)) for square in opponent_ring) / 10.0
    ) * middlegame

    stats["bishop_pair"] = float(len(board.pieces(chess.BISHOP, color)) >= 2)

    outposts = 0.0
    rim = 0.0
    for square in board.pieces(chess.KNIGHT, color):
        file_index = chess.square_file(square)
        rank = chess.square_rank(square)
        if file_index in (0, 7):
            rim += 1.0
        advanced = rank >= 3 if color == chess.WHITE else rank <= 4
        central = 2 <= file_index <= 5
        enemy_pawn_attack = any(
            (
                (piece := board.piece_at(attacker)) is not None
                and piece.color == (not color)
                and piece.piece_type == chess.PAWN
            )
            for attacker in board.attackers(not color, square)
        )
        if advanced and central and not enemy_pawn_attack:
            outposts += 1.0

    stats["knight_outpost"] = outposts
    stats["knight_rim"] = -rim

    own_files = _pawn_files(board, color)
    enemy_files = _pawn_files(board, not color)
    passed: list[chess.Square] = []
    pawn_advance = 0.0
    promotion_threat = 0.0

    for square in board.pieces(chess.PAWN, color):
        rank = chess.square_rank(square)
        advance = rank - 1 if color == chess.WHITE else 6 - rank
        pawn_advance += max(0, advance) / 6.0
        if _is_passed(board, square, color):
            passed.append(square)
        if (color == chess.WHITE and rank >= 5) or (
            color == chess.BLACK and rank <= 2
        ):
            promotion_threat += 1.0 + 0.5 * max(0, advance - 4)

    passed_set = set(passed)
    connected = 0.0
    for square in passed:
        file_index = chess.square_file(square)
        rank = chess.square_rank(square)
        for delta_file in (-1, 1):
            target_file = file_index + delta_file
            if not 0 <= target_file < 8:
                continue
            if any(
                chess.square(target_file, target_rank) in passed_set
                for target_rank in range(max(0, rank - 1), min(7, rank + 1) + 1)
            ):
                connected += 0.5

    isolated = 0
    doubled = 0
    for file_index, count in enumerate(own_files):
        if count:
            left = own_files[file_index - 1] if file_index else 0
            right = own_files[file_index + 1] if file_index < 7 else 0
            if left == 0 and right == 0:
                isolated += count
        if count > 1:
            doubled += count - 1

    stats["passed_pawn"] = float(len(passed))
    stats["connected_passed"] = connected
    stats["pawn_advance"] = pawn_advance / 4.0
    stats["isolated_pawn"] = -float(isolated)
    stats["doubled_pawn"] = -float(doubled)
    stats["pawn_islands"] = -float(_pawn_islands(own_files))
    stats["promotion_threat"] = promotion_threat

    rook_open = 0.0
    rook_seventh = 0.0
    for square in board.pieces(chess.ROOK, color):
        file_index = chess.square_file(square)
        rank = chess.square_rank(square)
        if own_files[file_index] == 0:
            rook_open += 1.0 if enemy_files[file_index] == 0 else 0.55
        if (color == chess.WHITE and rank == 6) or (
            color == chess.BLACK and rank == 1
        ):
            rook_seventh += 1.0

    stats["rook_open_file"] = rook_open
    stats["rook_seventh"] = rook_seventh

    queen_start = chess.D1 if color == chess.WHITE else chess.D8
    queen_square = next(iter(board.pieces(chess.QUEEN, color)), None)
    if board.fullmove_number <= 10 and queen_square is not None:
        stats["queen_discipline"] = float(queen_square == queen_start)
    else:
        stats["queen_discipline"] = 1.0

    hanging = 0.0
    undefended = 0.0
    for piece_type in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
        for square in board.pieces(piece_type, color):
            value = PIECE_VALUES[piece_type]
            attacked = board.is_attacked_by(not color, square)
            defended = board.is_attacked_by(color, square)
            if attacked and not defended:
                hanging += value
            elif not defended:
                undefended += value

    stats["hanging_piece"] = -hanging / 5.0
    stats["undefended_piece"] = -undefended / 10.0

    rights = 0.0
    if board.has_kingside_castling_rights(color):
        rights += 0.5
    if board.has_queenside_castling_rights(color):
        rights += 0.5
    stats["castling_rights"] = rights * middlegame

    if king_square is None:
        stats["endgame_king"] = 0.0
    else:
        file_index = chess.square_file(king_square)
        rank = chess.square_rank(king_square)
        distance = abs(file_index - 3.5) + abs(rank - 3.5)
        stats["endgame_king"] = max(0.0, 4.0 - distance) / 4.0 * endgame

    return stats


def extract_features(board: chess.Board) -> dict[str, float]:
    middlegame = _phase(board)
    endgame = 1.0 - middlegame
    white = _color_stats(board, chess.WHITE, middlegame, endgame)
    black = _color_stats(board, chess.BLACK, middlegame, endgame)
    features = {
        key: white.get(key, 0.0) - black.get(key, 0.0)
        for key in PRIORS
        if key != "tempo"
    }
    features["tempo"] = 1.0 if board.turn == chess.WHITE else -1.0
    return features
