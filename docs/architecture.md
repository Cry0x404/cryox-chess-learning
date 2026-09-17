# Architecture

## Overview

The engine separates chess state evaluation, search, self-play, learning, arena validation, checkpoint persistence, and process orchestration into independent modules.

The training loop never promotes a candidate directly. Learned evaluator weights remain isolated until the candidate completes an arena against the current champion.

## Evaluator

The evaluator is a bounded linear model over position features. Each feature is defined from White's perspective so that a positive value represents an advantage for White.

The feature set includes:

- material balance
- mobility
- center control
- space
- development
- king safety
- pressure around the opposing king
- bishop pair
- knight outposts
- knight rim placement
- passed pawns
- connected passed pawns
- pawn advancement
- isolated pawns
- doubled pawns
- pawn islands
- open and semi-open rook files
- rook activity on the seventh rank
- early queen discipline
- hanging pieces
- undefended pieces
- general piece activity
- castling rights
- endgame king activity
- promotion threats
- tempo

Every weight has a defined lower and upper bound. The bounds prevent a short sequence of noisy games from reversing basic chess priors.

## Search

The policy improvement step uses alpha-beta search with:

- tactical move ordering
- transposition tables keyed by Zobrist hash
- quiescence search
- killer move ordering
- history heuristic
- mate-distance scoring

Self-play workers run independent searches and produce trajectories.

## Learning

Each trajectory is converted to a bounded target in `[-1, 1]`.

Completed games use the game result. Truncated games use a conservative reference evaluator bootstrap. Temporal-difference updates assign greater credit to positions closer to the final target.

A small pull toward the fixed prior is applied at each update to limit catastrophic parameter drift.

## Parallel self-play

The trainer uses a process pool rather than threads. Python chess search is CPU-bound, so separate processes avoid the interpreter lock and allow multiple games to run concurrently.

Each worker receives an immutable copy of the candidate weights and a deterministic random seed.

Worker updates are averaged and blended with the pre-batch candidate before being stored.

## Candidate gating

After a configured number of candidate games, the candidate enters a paired arena.

Each opening is tested with both colors. Arena games use no exploration. Truncated games are adjudicated by a fixed reference evaluator rather than the candidate or champion evaluator.

A candidate must:

1. pass evaluator sanity checks;
2. meet the configured arena score threshold.

Rejected candidates are replaced with the current champion. Accepted candidates become the next generation and are appended to the hall of fame.

## Persistence

Checkpoint writes are atomic. The complete JSON payload is written to a temporary file and moved into place only after serialization succeeds.

The checkpoint stores:

- generation
- total self-play games
- accepted candidates
- rejected candidates
- current candidate weights
- champion weights
- candidate games since the last arena
- total positions
- hall of fame
- last arena result

Training metrics are appended to a JSONL stream independently of the checkpoint.
