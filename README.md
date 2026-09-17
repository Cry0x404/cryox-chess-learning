[![CI](https://github.com/Cry0x404/cryox-chess-learning/actions/workflows/ci.yml/badge.svg)](https://github.com/Cry0x404/cryox-chess-learning/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Cry0x404/cryox-chess-learning/actions/workflows/codeql.yml/badge.svg)](https://github.com/Cry0x404/cryox-chess-learning/actions/workflows/codeql.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-111111)
![Status](https://img.shields.io/badge/status-alpha-6f42c1)

# Cryox Chess Learning

Cryox Chess Learning is a persistent self-play training engine for chess. It combines a constrained positional evaluator, alpha-beta search, quiescence search, transposition tables, multiprocessing self-play, paired arena matches, and checkpoint-based champion selection.

The repository contains only the learning and evaluation system. It does not include a graphical interface or a human-play client.

## Project status

The project is currently in alpha. Checkpoint compatibility is preserved where practical, but search and training internals may continue to evolve before a stable API is declared.

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

```bash
cryox-chess migrate path\to\brain.json
```

On Windows, the helper script accepts the checkpoint path as its first argument:

```powershell
.\scripts\migrate-legacy.ps1 path\to\brain.json
```

Legacy checkpoints are intentionally not committed to the repository. Migration operates on a user-supplied checkpoint and preserves compatible training counters and evaluator state while resetting fields whose old semantics cannot be transferred safely.

## Inspecting a checkpoint

```bash
cryox-chess status
```

## Arena evaluation

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

The search stack includes alpha-beta pruning, quiescence search, transposition tables, tactical move ordering, killer moves, and a history heuristic.

The evaluator models material, mobility, center control, space, development, king safety, king pressure, pawn structure, passed pawns, rook activity, piece stability, castling rights, endgame king activity, promotion pressure, and tempo.

See `docs/architecture.md`, `docs/training.md`, `docs/checkpoints.md`, and `docs/roadmap.md` for implementation details.

## Configuration

There is one training configuration rather than named performance modes. Resource usage is controlled directly through worker count, search depth, batch size, arena size, and related parameters.

```toml
workers = 0
self_play_depth = 2
batch_size = 8
candidate_window = 40
arena_games = 16
arena_depth = 2
```

`workers = 0` selects an automatic worker count based on the host CPU.

## Quality gates

Every change to `main` is validated on Python 3.11, 3.12, and 3.13. CI runs Ruff, the test suite with branch coverage, and a package build check. CodeQL performs static security analysis separately.

Local validation:

```bash
pip install -e ".[dev]"
ruff check .
pytest --cov=cryox_chess --cov-branch
```

Optional pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

## Releases

Release artifacts are built from the repository's declared version and validated before publication. The release workflow produces both a source distribution and a wheel.

See `RELEASING.md` for the release procedure.

## Contributing and security

Contribution guidelines are in `CONTRIBUTING.md`. Security-sensitive reports should follow `SECURITY.md`. General usage and support guidance is in `SUPPORT.md`.

## License

MIT. See `LICENSE`.
