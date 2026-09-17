import chess

from cryox_chess.constants import PRIORS
from cryox_chess.search import Searcher


def test_search_returns_legal_move():
    board = chess.Board()
    result = Searcher(PRIORS, quiescence_depth=1).search(board, depth=1)
    assert result.move in board.legal_moves
    assert result.nodes > 0


def test_search_finds_forced_mate_in_one():
    board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 w - - 0 1")
    result = Searcher(PRIORS, quiescence_depth=1).search(board, depth=2)
    board.push(result.move)
    assert board.is_checkmate()
