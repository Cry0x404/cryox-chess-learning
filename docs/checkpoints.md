# Checkpoints

## Format

The runtime checkpoint is a JSON document containing the complete persistent state required to resume training.

The current schema stores:

- `schema_version`
- `generation`
- `games`
- `accepted`
- `rejected`
- `candidate_games`
- `total_positions`
- `champion_weights`
- `candidate_weights`
- `hall_of_fame`
- `last_arena`

Compatibility aliases for `best_weights` and `weights` are emitted to simplify migration from earlier builds.

## Durability

Checkpoint writes are atomic. The new payload is serialized to a temporary sibling file and then moved over the destination. An interrupted serialization therefore cannot partially overwrite the previous checkpoint.

## Champion and candidate

The champion is the last evaluator that passed arena validation. The candidate receives self-play updates until it reaches the configured candidate window.

A failed arena restores the candidate to the champion. A successful arena promotes the candidate and records the new generation in the hall of fame.

## Legacy migration

Legacy checkpoints can be migrated with:

```bash
cryox-chess migrate path/to/brain.json
```

Counters are retained. Evaluator parameters are copied only when their old and new semantics are compatible. Incompatible values are initialized from bounded priors rather than transferred blindly.
