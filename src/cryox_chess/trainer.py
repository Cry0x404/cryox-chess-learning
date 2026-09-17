from __future__ import annotations

import signal
import time
from concurrent.futures import ProcessPoolExecutor

from .arena import ArenaJob, ArenaResult, run_arena
from .checkpoint import Checkpoint, load_checkpoint, save_checkpoint
from .config import AppConfig
from .evaluator import sanitize_weights, sanity_check
from .metrics import MetricsWriter
from .selfplay import SelfPlayJob, merge_results, run_self_play


class Trainer:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.checkpoint = load_checkpoint(config.paths.checkpoint)
        self.metrics = MetricsWriter(config.paths.metrics)
        self.stop_requested = False
        self.seed = int(time.time() * 1000) & 0x7FFFFFFF

    def _request_stop(self, *_: object) -> None:
        self.stop_requested = True

    def _save(self) -> None:
        save_checkpoint(self.config.paths.checkpoint, self.checkpoint)

    def _self_play_batch(self, executor: ProcessPoolExecutor) -> None:
        base = dict(self.checkpoint.candidate_weights)
        jobs = []

        for _ in range(self.config.training.batch_size):
            self.seed += 1
            jobs.append(
                SelfPlayJob(
                    weights=base,
                    depth=self.config.training.self_play_depth,
                    max_plies=self.config.training.self_play_max_plies,
                    learning_rate=self.config.training.learning_rate,
                    prior_regularization=self.config.training.prior_regularization,
                    exploration_initial=self.config.training.exploration_initial,
                    exploration_floor=self.config.training.exploration_floor,
                    quiescence_depth=self.config.search.quiescence_depth,
                    seed=self.seed,
                )
            )

        futures = [executor.submit(run_self_play, job) for job in jobs]
        results = [future.result() for future in futures]

        self.checkpoint.candidate_weights = sanitize_weights(
            merge_results(results, base)
        )
        self.checkpoint.games += len(results)
        self.checkpoint.candidate_games += len(results)
        self.checkpoint.total_positions += sum(result.positions for result in results)

        self.metrics.write(
            "self_play_batch",
            games=self.checkpoint.games,
            generation=self.checkpoint.generation,
            batch_size=len(results),
            positions=sum(result.positions for result in results),
            candidate_games=self.checkpoint.candidate_games,
        )

        if (
            self.checkpoint.games
            % self.config.training.checkpoint_interval_games
            == 0
        ):
            self._save()

    def _arena(self) -> ArenaResult:
        job = ArenaJob(
            candidate=dict(self.checkpoint.candidate_weights),
            champion=dict(self.checkpoint.champion_weights),
            games=self.config.arena.games,
            depth=self.config.arena.depth,
            max_plies=self.config.arena.max_plies,
            material_adjudication_cp=self.config.arena.material_adjudication_cp,
            quiescence_depth=self.config.search.quiescence_depth,
        )
        return run_arena(job)

    def _process_arena(self, result: ArenaResult) -> None:
        candidate = sanitize_weights(self.checkpoint.candidate_weights)
        accepted = (
            sanity_check(candidate)
            and result.score >= self.config.arena.acceptance_score
        )

        if accepted:
            self.checkpoint.champion_weights = dict(candidate)
            self.checkpoint.generation += 1
            self.checkpoint.accepted += 1
            self.checkpoint.hall_of_fame.append(
                {
                    "generation": self.checkpoint.generation,
                    "weights": dict(candidate),
                }
            )
            self.checkpoint.hall_of_fame = self.checkpoint.hall_of_fame[-8:]
            verdict = "accepted"
        else:
            self.checkpoint.candidate_weights = dict(
                self.checkpoint.champion_weights
            )
            self.checkpoint.rejected += 1
            verdict = "rejected"

        self.checkpoint.candidate_games = 0
        self.checkpoint.last_arena = {
            "score": result.score,
            "wins": result.wins,
            "draws": result.draws,
            "losses": result.losses,
            "games": result.games,
            "threshold": self.config.arena.acceptance_score,
            "verdict": verdict,
        }

        self.metrics.write(
            "arena",
            generation=self.checkpoint.generation,
            games=self.checkpoint.games,
            score=result.score,
            wins=result.wins,
            draws=result.draws,
            losses=result.losses,
            verdict=verdict,
        )

        print(
            f"{verdict.upper()} "
            f"generation={self.checkpoint.generation} "
            f"games={self.checkpoint.games} "
            f"score={result.score:.3f} "
            f"wdl={result.wins}/{result.draws}/{result.losses}"
        )

        self._save()

    def run(self) -> None:
        signal.signal(signal.SIGINT, self._request_stop)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._request_stop)

        print(
            f"generation={self.checkpoint.generation} "
            f"games={self.checkpoint.games} "
            f"workers={self.config.training.workers}"
        )

        with ProcessPoolExecutor(
            max_workers=self.config.training.workers
        ) as executor:
            while not self.stop_requested:
                self._self_play_batch(executor)

                if (
                    self.checkpoint.candidate_games
                    >= self.config.training.candidate_window
                ):
                    result = self._arena()
                    self._process_arena(result)

        self._save()
        print(
            f"saved generation={self.checkpoint.generation} "
            f"games={self.checkpoint.games}"
        )
