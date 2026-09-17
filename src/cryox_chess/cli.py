from __future__ import annotations

import argparse
import json
from pathlib import Path

from .arena import ArenaJob, run_arena
from .checkpoint import (
    load_checkpoint,
    migrate_legacy,
    save_checkpoint,
)
from .config import load_config
from .io import read_json
from .trainer import Trainer


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cryox-chess")
    parser.add_argument(
        "--config",
        default="config/training.toml",
    )

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("train")
    commands.add_parser("status")
    commands.add_parser("arena")

    migrate = commands.add_parser("migrate")
    migrate.add_argument("legacy_checkpoint")

    return parser


def _status(config_path: str) -> None:
    config = load_config(config_path)
    checkpoint = load_checkpoint(config.paths.checkpoint)
    payload = {
        "generation": checkpoint.generation,
        "games": checkpoint.games,
        "accepted": checkpoint.accepted,
        "rejected": checkpoint.rejected,
        "candidate_games": checkpoint.candidate_games,
        "total_positions": checkpoint.total_positions,
        "last_arena": checkpoint.last_arena,
    }
    print(json.dumps(payload, indent=2))


def _migrate(config_path: str, legacy_path: str) -> None:
    config = load_config(config_path)
    payload = read_json(Path(legacy_path).resolve())
    checkpoint = migrate_legacy(payload)
    save_checkpoint(config.paths.checkpoint, checkpoint)
    print(
        f"migrated generation={checkpoint.generation} "
        f"games={checkpoint.games} "
        f"to={config.paths.checkpoint}"
    )


def _arena(config_path: str) -> None:
    config = load_config(config_path)
    checkpoint = load_checkpoint(config.paths.checkpoint)
    result = run_arena(
        ArenaJob(
            candidate=dict(checkpoint.candidate_weights),
            champion=dict(checkpoint.champion_weights),
            games=config.arena.games,
            depth=config.arena.depth,
            max_plies=config.arena.max_plies,
            material_adjudication_cp=config.arena.material_adjudication_cp,
            quiescence_depth=config.search.quiescence_depth,
        )
    )
    print(
        json.dumps(
            {
                "score": result.score,
                "wins": result.wins,
                "draws": result.draws,
                "losses": result.losses,
                "games": result.games,
            },
            indent=2,
        )
    )


def main() -> None:
    arguments = _parser().parse_args()

    if arguments.command == "train":
        Trainer(load_config(arguments.config)).run()
    elif arguments.command == "status":
        _status(arguments.config)
    elif arguments.command == "migrate":
        _migrate(arguments.config, arguments.legacy_checkpoint)
    elif arguments.command == "arena":
        _arena(arguments.config)


if __name__ == "__main__":
    main()
