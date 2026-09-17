from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from .constants import PRIORS, SCHEMA_VERSION
from .evaluator import sanitize_weights
from .io import atomic_json_write, read_json


@dataclass(slots=True)
class Checkpoint:
    schema_version: int = SCHEMA_VERSION
    generation: int = 1
    games: int = 0
    accepted: int = 0
    rejected: int = 0
    candidate_games: int = 0
    total_positions: int = 0
    champion_weights: dict[str, float] = field(
        default_factory=lambda: dict(PRIORS)
    )
    candidate_weights: dict[str, float] = field(
        default_factory=lambda: dict(PRIORS)
    )
    hall_of_fame: list[dict] = field(default_factory=list)
    last_arena: dict | None = None
    migrated_from_legacy: bool = False

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "generation": self.generation,
            "games": self.games,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "candidate_games": self.candidate_games,
            "total_positions": self.total_positions,
            "champion_weights": self.champion_weights,
            "candidate_weights": self.candidate_weights,
            "best_weights": self.champion_weights,
            "weights": self.candidate_weights,
            "hall_of_fame": self.hall_of_fame,
            "last_arena": self.last_arena,
            "migrated_from_legacy": self.migrated_from_legacy,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> Checkpoint:
        champion = sanitize_weights(
            payload.get("champion_weights")
            or payload.get("best_weights")
            or PRIORS
        )
        candidate = sanitize_weights(
            payload.get("candidate_weights")
            or payload.get("weights")
            or champion
        )
        generation = int(payload.get("generation", 1))
        hall = payload.get("hall_of_fame") or [
            {"generation": generation, "weights": dict(champion)}
        ]
        return cls(
            schema_version=SCHEMA_VERSION,
            generation=generation,
            games=int(payload.get("games", 0)),
            accepted=int(payload.get("accepted", 0)),
            rejected=int(payload.get("rejected", 0)),
            candidate_games=int(payload.get("candidate_games", 0)),
            total_positions=int(payload.get("total_positions", 0)),
            champion_weights=champion,
            candidate_weights=candidate,
            hall_of_fame=hall[-8:],
            last_arena=payload.get("last_arena"),
            migrated_from_legacy=bool(payload.get("migrated_from_legacy", False)),
        )


def new_checkpoint() -> Checkpoint:
    checkpoint = Checkpoint()
    checkpoint.hall_of_fame = [
        {"generation": 1, "weights": dict(checkpoint.champion_weights)}
    ]
    return checkpoint


def load_checkpoint(path: Path) -> Checkpoint:
    if not path.exists():
        return new_checkpoint()
    return Checkpoint.from_dict(read_json(path))


def save_checkpoint(path: Path, checkpoint: Checkpoint) -> None:
    atomic_json_write(path, checkpoint.to_dict())


def migrate_legacy(payload: dict) -> Checkpoint:
    legacy = payload.get("best_weights") or payload.get("weights") or {}
    weights = dict(PRIORS)

    mappings = {
        "material": "material",
        "mobility": "mobility",
        "center": "center_control",
        "king_safety": "king_safety",
        "bishop_pair": "bishop_pair",
        "rook_activity": "rook_open_file",
    }

    for old_name, new_name in mappings.items():
        value = float(legacy.get(old_name, 0.0) or 0.0)
        if value > 0:
            weights[new_name] = value

    pawn_push = abs(float(legacy.get("pawn_push", 0.0) or 0.0))
    if pawn_push:
        weights["pawn_advance"] = pawn_push * 0.18

    queen_early = float(legacy.get("queen_early", 0.0) or 0.0)
    if queen_early < 0:
        weights["queen_discipline"] = abs(queen_early)

    clean = sanitize_weights(weights)
    generation = int(payload.get("generation", 1))

    return Checkpoint(
        generation=generation,
        games=int(payload.get("games", 0)),
        accepted=int(payload.get("accepted", 0)),
        rejected=int(payload.get("rejected", 0)),
        champion_weights=dict(clean),
        candidate_weights=dict(clean),
        hall_of_fame=[
            {
                "generation": generation,
                "weights": dict(clean),
                "migrated_at": time.time(),
            }
        ],
        migrated_from_legacy=True,
    )
