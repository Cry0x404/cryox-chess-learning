from __future__ import annotations

import math

from .constants import BOUNDS, PRIORS


def temporal_difference_update(
    trajectory: list[dict[str, float]],
    target: float,
    weights: dict[str, float],
    learning_rate: float,
    prior_regularization: float,
) -> dict[str, float]:
    if not trajectory:
        return dict(weights)

    updated = dict(weights)
    total = len(trajectory)

    for index, features in enumerate(trajectory):
        raw = sum(updated[name] * features[name] for name in PRIORS)
        prediction = math.tanh(raw / 4.5)
        local_target = target * (0.30 + 0.70 * (index + 1) / total)
        error = local_target - prediction

        for name, prior in PRIORS.items():
            delta = learning_rate * error * features[name]
            regularization = prior_regularization * (prior - updated[name])
            lower, upper = BOUNDS[name]
            updated[name] = max(
                lower,
                min(upper, updated[name] + delta + regularization),
            )

    return updated
