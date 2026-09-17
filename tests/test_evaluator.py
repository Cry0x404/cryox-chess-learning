import chess

from cryox_chess.constants import PRIORS
from cryox_chess.evaluator import evaluate, sanity_check


def test_material_advantage_has_correct_sign():
    white = chess.Board("4k3/8/8/8/8/8/4Q3/4K3 w - - 0 1")
    black = chess.Board("4k3/4q3/8/8/8/8/8/4K3 w - - 0 1")
    assert evaluate(white, PRIORS) > 0
    assert evaluate(black, PRIORS) < 0


def test_default_weights_pass_sanity_check():
    assert sanity_check(PRIORS)
