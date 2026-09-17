# Changelog

All notable changes to this project are documented in this file.

## Unreleased

## 0.1.1 - 2026-09-17

- Added branch-coverage reporting to CI.
- Added package build and metadata validation to CI.
- Added CodeQL static security analysis and reduced unnecessary scans for non-code changes.
- Added pull-request dependency review.
- Added a validated GitHub Release workflow.
- Added pre-commit hooks and release/support documentation.
- Expanded package metadata for discoverability.
- Removed the bundled runtime-derived legacy checkpoint while preserving legacy migration support.
- Generalized the PowerShell migration helper to accept a user-supplied checkpoint path.

## 0.1.0 - 2026-09-17

- Split the learning engine into a Python package.
- Added bounded positional features.
- Added alpha-beta search with quiescence and transposition tables.
- Added multiprocessing self-play.
- Added paired champion arenas.
- Added atomic checkpoint persistence.
- Added legacy checkpoint migration.
- Added JSONL training metrics.
- Added automated tests and CI.
