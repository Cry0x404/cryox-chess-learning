from cryox_chess.constants import PRIORS
from cryox_chess.selfplay import SelfPlayJob, run_self_play


def test_short_selfplay_produces_positions():
    result = run_self_play(
        SelfPlayJob(
            weights=dict(PRIORS),
            depth=1,
            max_plies=6,
            learning_rate=0.001,
            prior_regularization=0.00004,
            exploration_initial=0.1,
            exploration_floor=0.02,
            quiescence_depth=1,
            seed=7,
        )
    )
    assert result.positions > 0
    assert result.plies > 0
