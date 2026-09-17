# Training

## Default configuration

The project uses a single training configuration. There are no named performance modes.

Resource usage and training quality are controlled directly through `config/training.toml`.

## Worker count

`workers = 0` selects an automatic value:

- up to four worker processes;
- at least one worker;
- reserves CPU capacity on systems with more than three logical processors.

Set an explicit worker count when deterministic resource allocation is required.

## Search depth

`self_play_depth` controls self-play search depth. Increasing the value can improve move quality but increases the cost of every generated position.

`arena.depth` should not be lower than one. A larger arena depth produces a stronger comparison at a higher compute cost.

## Candidate window

`candidate_window` determines how many self-play games are accumulated before a candidate is evaluated against the champion.

A larger window gives each candidate more training time before validation.

## Arena size

Arena games are paired by opening and color. Use an even game count.

Increasing `arena.games` reduces variance in promotion decisions.

## Acceptance threshold

The default threshold is `0.575`. A score of `0.500` is intentionally not sufficient because a candidate that merely ties the champion does not provide evidence of improvement.

## Checkpoints

Use `Ctrl+C` for normal shutdown. The trainer saves the checkpoint before exiting.

The checkpoint is also written periodically during training and after every arena.

## Metrics

`runtime/metrics.jsonl` records self-play batches and arena outcomes. Each line is an independent JSON object suitable for later analysis.

## Legacy migration

Earlier versions stored a small set of fields in `brain.json`.

Migration preserves:

- games
- generation
- accepted count
- rejected count

Compatible evaluator values are transferred where their semantics remain valid. Values with incompatible sign conventions are reset to bounded priors instead of being copied blindly.
