[![CI](https://github.com/Cry0x404/cryox-chess-learning/actions/workflows/ci.yml/badge.svg)](https://github.com/Cry0x404/cryox-chess-learning/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-111111)

# Cryox Chess Learning

Cryox Chess Learning is a persistent self-play training engine for chess. It combines a constrained positional evaluator, iterative alpha-beta search, quiescence search, transposition tables, multiprocessing self-play, paired arena matches, and checkpoint-based champion selection.

The repository contains only the learning and evaluation system. It does not include a graphical interface or a human-play client.

## Design goals

- Persistent training across sessions
- Conservative champion replacement
- Reproducible self-play from deterministic seeds
- Parallel CPU training
- Atomic checkpoint writes
- Automatic migration from the earlier single-file checkpoint format
- Bounded evaluator parameters to reduce destructive drift
- Paired arena games with color reversal
- Hall-of-fame retention for accepted generations
- Structured JSONL training metrics
- No external chess engine dependency

## Requirements

- Python 3.11 or newer
- `python-chess`

## Installation

```bash
git clone https://github.com/Cry0x404/cryox-chess-learning.git
cd cryox-chess-learning
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Training

```bash
cryox-chess train
```

or:

```bash
python -m cryox_chess train
```

The default configuration is stored in `config/training.toml`.

Training state is written to:

```text
runtime/checkpoint.json
runtime/metrics.jsonl
```

Stop training with `Ctrl+C`. The checkpoint is saved before the process exits.

## Legacy checkpoint migration

The repository includes a migration command for the earlier `brain.json` format:

```bash
cryox-chess migrate path\to\brain.json
```

The migrated state is written to the configured checkpoint path. Existing counters such as games, generation, accepted candidates, and rejected candidates are preserved.

To migrate the checkpoint bundled in this package:

```bash
cryox-chess migrate legacy/brain.json
```

## Inspecting a checkpoint

```bash
cryox-chess status
```

Example output:

```text
generation: 44
games: 1446
accepted: 43
rejected: 77
candidate_games: 0
total_positions: 0
```

## Arena evaluation

A saved candidate can be evaluated against the current champion:

```bash
cryox-chess arena
```

Arena games use paired openings and reversed colors. A candidate is accepted only when it clears the configured score threshold and passes evaluator sanity checks.

## Architecture

```text
Opening sampler
      |
      v
Parallel self-play workers
      |
      v
Feature trajectories
      |
      v
Temporal-difference update
      |
      v
Candidate evaluator
      |
      v
Paired arena
      |
      +---- reject ----> champion restored
      |
      +---- accept ----> new champion + hall of fame
```

The search stack uses:

- iterative deepening
- alpha-beta pruning
- quiescence search
- transposition tables
- tactical move ordering
- killer moves
- history heuristic

The evaluator models material, mobility, center control, space, development, king safety, king pressure, pawn structure, passed pawns, rook activity, piece stability, castling rights, endgame king activity, promotion pressure, and tempo.

See `docs/architecture.md`, `docs/training.md`, and `docs/checkpoints.md` for implementation details.

## Configuration

There is one training configuration rather than multiple performance modes. Resource usage is controlled directly through parameters such as worker count, search depth, batch size, and arena size.

Key settings:

```toml
workers = 0
self_play_depth = 2
batch_size = 8
candidate_window = 40
arena_games = 16
arena_depth = 2
```

`workers = 0` selects an automatic worker count based on the host CPU.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## License

MIT. See `LICENSE`.
