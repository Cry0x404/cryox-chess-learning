# Roadmap

This roadmap describes engineering direction rather than release commitments.

## Reliability

- Expand evaluator invariants and regression tests.
- Add checkpoint corruption and interrupted-write tests.
- Add deterministic self-play fixtures for seeded training runs.
- Add long-running training smoke tests outside the standard CI path.

## Search

- Improve transposition-table replacement policy.
- Add aspiration windows after search stability is measured.
- Evaluate principal-variation search and late-move reductions behind benchmarks.
- Add search diagnostics for nodes, cutoffs, and table hit rate.

## Learning

- Add richer training telemetry and generation comparisons.
- Measure candidate acceptance variance across paired opening suites.
- Add explicit regression gates for evaluator behavior.
- Evaluate adaptive learning-rate schedules without weakening champion gating.

## Packaging

- Maintain validated wheel and source-distribution builds.
- Publish to PyPI only after package naming and public compatibility expectations are stable.
- Define compatibility policy before a 1.0 release.
