from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PathsConfig:
    checkpoint: Path
    metrics: Path


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    workers: int
    batch_size: int
    candidate_window: int
    self_play_depth: int
    self_play_max_plies: int
    learning_rate: float
    exploration_initial: float
    exploration_floor: float
    prior_regularization: float
    checkpoint_interval_games: int


@dataclass(frozen=True, slots=True)
class ArenaConfig:
    games: int
    depth: int
    max_plies: int
    acceptance_score: float
    material_adjudication_cp: int


@dataclass(frozen=True, slots=True)
class SearchConfig:
    quiescence_depth: int


@dataclass(frozen=True, slots=True)
class AppConfig:
    paths: PathsConfig
    training: TrainingConfig
    arena: ArenaConfig
    search: SearchConfig


def _resolve_workers(value: int) -> int:
    if value > 0:
        return value
    count = os.cpu_count() or 2
    return max(1, min(4, count - 2 if count > 3 else 1))


def load_config(path: str | Path = "config/training.toml") -> AppConfig:
    config_path = Path(path).resolve()
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    base = config_path.parent.parent
    paths = data["paths"]
    training = data["training"]
    arena = data["arena"]
    search = data["search"]
    return AppConfig(
        paths=PathsConfig(
            checkpoint=(base / paths["checkpoint"]).resolve(),
            metrics=(base / paths["metrics"]).resolve(),
        ),
        training=TrainingConfig(
            workers=_resolve_workers(int(training["workers"])),
            batch_size=int(training["batch_size"]),
            candidate_window=int(training["candidate_window"]),
            self_play_depth=int(training["self_play_depth"]),
            self_play_max_plies=int(training["self_play_max_plies"]),
            learning_rate=float(training["learning_rate"]),
            exploration_initial=float(training["exploration_initial"]),
            exploration_floor=float(training["exploration_floor"]),
            prior_regularization=float(training["prior_regularization"]),
            checkpoint_interval_games=int(training["checkpoint_interval_games"]),
        ),
        arena=ArenaConfig(
            games=int(arena["games"]),
            depth=int(arena["depth"]),
            max_plies=int(arena["max_plies"]),
            acceptance_score=float(arena["acceptance_score"]),
            material_adjudication_cp=int(arena["material_adjudication_cp"]),
        ),
        search=SearchConfig(
            quiescence_depth=int(search["quiescence_depth"]),
        ),
    )
