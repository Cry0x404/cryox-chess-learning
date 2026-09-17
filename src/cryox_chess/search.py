from __future__ import annotations

from dataclasses import dataclass

import chess
import chess.polyglot

from .constants import PIECE_VALUES
from .evaluator import evaluate


@dataclass(slots=True)
class SearchResult:
    move: chess.Move | None
    score: float
    nodes: int


class Searcher:
    def __init__(self, weights: dict[str, float], quiescence_depth: int = 3) -> None:
        self.weights = weights
        self.quiescence_depth = quiescence_depth
        self.nodes = 0
        self.table: dict[int, tuple[int, float, str, chess.Move | None]] = {}
        self.killers: dict[int, tuple[chess.Move, ...]] = {}
        self.history: dict[tuple[int, int, int | None], int] = {}

    def _move_score(
        self,
        board: chess.Board,
        move: chess.Move,
        table_move: chess.Move | None,
        ply: int,
    ) -> int:
        if move == table_move:
            return 10_000_000

        score = 0
        if move.promotion:
            score += 900_000 + int(10_000 * PIECE_VALUES.get(move.promotion, 0.0))

        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            victim_value = PIECE_VALUES[victim.piece_type] if victim else 1.0
            attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 1.0
            score += 500_000 + int(10_000 * victim_value - 800 * attacker_value)

        if move in self.killers.get(ply, ()):
            score += 250_000

        score += self.history.get((move.from_square, move.to_square, move.promotion), 0)
        return score

    def ordered_moves(
        self,
        board: chess.Board,
        table_move: chess.Move | None = None,
        ply: int = 0,
        tactical_only: bool = False,
    ) -> list[chess.Move]:
        moves = [
            move
            for move in board.legal_moves
            if not tactical_only or board.is_capture(move) or move.promotion
        ]
        moves.sort(
            key=lambda move: self._move_score(board, move, table_move, ply),
            reverse=True,
        )
        return moves

    def _quiescence(
        self,
        board: chess.Board,
        alpha: float,
        beta: float,
        depth: int,
        ply: int,
    ) -> float:
        self.nodes += 1

        if board.is_checkmate():
            return -100000.0 + ply if board.turn == chess.WHITE else 100000.0 - ply

        stand_pat = evaluate(board, self.weights)

        if board.turn == chess.WHITE:
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)
            if depth <= 0:
                return stand_pat
            best = stand_pat
            for move in self.ordered_moves(board, ply=ply, tactical_only=True):
                board.push(move)
                value = self._quiescence(board, alpha, beta, depth - 1, ply + 1)
                board.pop()
                best = max(best, value)
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return best

        if stand_pat <= alpha:
            return stand_pat
        beta = min(beta, stand_pat)
        if depth <= 0:
            return stand_pat
        best = stand_pat
        for move in self.ordered_moves(board, ply=ply, tactical_only=True):
            board.push(move)
            value = self._quiescence(board, alpha, beta, depth - 1, ply + 1)
            board.pop()
            best = min(best, value)
            beta = min(beta, best)
            if alpha >= beta:
                break
        return best

    def _alphabeta(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        ply: int,
    ) -> float:
        self.nodes += 1

        if board.is_checkmate():
            return -100000.0 + ply if board.turn == chess.WHITE else 100000.0 - ply

        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        if depth <= 0:
            return self._quiescence(
                board,
                alpha,
                beta,
                self.quiescence_depth,
                ply,
            )

        key = chess.polyglot.zobrist_hash(board)
        entry = self.table.get(key)
        table_move = None

        if entry is not None:
            stored_depth, stored_score, flag, table_move = entry
            if stored_depth >= depth:
                if flag == "exact":
                    return stored_score
                if flag == "lower":
                    alpha = max(alpha, stored_score)
                elif flag == "upper":
                    beta = min(beta, stored_score)
                if alpha >= beta:
                    return stored_score

        original_alpha = alpha
        original_beta = beta
        moves = self.ordered_moves(board, table_move, ply)

        if board.turn == chess.WHITE:
            best = float("-inf")
            best_move = None
            for move in moves:
                tactical = board.is_capture(move) or bool(move.promotion)
                board.push(move)
                value = self._alphabeta(board, depth - 1, alpha, beta, ply + 1)
                board.pop()

                if value > best:
                    best = value
                    best_move = move

                alpha = max(alpha, best)
                if alpha >= beta:
                    if not tactical:
                        killers = list(self.killers.get(ply, ()))
                        if move not in killers:
                            killers.insert(0, move)
                            self.killers[ply] = tuple(killers[:2])
                        key_history = (
                            move.from_square,
                            move.to_square,
                            move.promotion,
                        )
                        self.history[key_history] = (
                            self.history.get(key_history, 0) + depth * depth
                        )
                    break
        else:
            best = float("inf")
            best_move = None
            for move in moves:
                tactical = board.is_capture(move) or bool(move.promotion)
                board.push(move)
                value = self._alphabeta(board, depth - 1, alpha, beta, ply + 1)
                board.pop()

                if value < best:
                    best = value
                    best_move = move

                beta = min(beta, best)
                if alpha >= beta:
                    if not tactical:
                        killers = list(self.killers.get(ply, ()))
                        if move not in killers:
                            killers.insert(0, move)
                            self.killers[ply] = tuple(killers[:2])
                        key_history = (
                            move.from_square,
                            move.to_square,
                            move.promotion,
                        )
                        self.history[key_history] = (
                            self.history.get(key_history, 0) + depth * depth
                        )
                    break

        if best <= original_alpha:
            flag = "upper"
        elif best >= original_beta:
            flag = "lower"
        else:
            flag = "exact"

        self.table[key] = (depth, best, flag, best_move)
        return best

    def search(self, board: chess.Board, depth: int) -> SearchResult:
        self.nodes = 0
        moves = self.ordered_moves(board)

        if not moves:
            return SearchResult(None, evaluate(board, self.weights), self.nodes)

        best_move = moves[0]
        best_score = float("-inf") if board.turn == chess.WHITE else float("inf")
        alpha = float("-inf")
        beta = float("inf")

        for move in moves:
            board.push(move)
            value = self._alphabeta(board, depth - 1, alpha, beta, 1)
            board.pop()

            if board.turn == chess.WHITE:
                if value > best_score:
                    best_score = value
                    best_move = move
                alpha = max(alpha, best_score)
            else:
                if value < best_score:
                    best_score = value
                    best_move = move
                beta = min(beta, best_score)

        return SearchResult(best_move, best_score, self.nodes)
