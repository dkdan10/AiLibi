"""Persist tournament attempts and verify the inputs used for continuation."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
import uuid
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from _report_output import (
    atomic_write_bytes,
    atomic_write_report,
    preflight_report_output,
)
from eval.balance_eval import build_tournament_report, load_tournament_report
from eval.meeting_quality import TournamentEvalReport, build_tournament_eval_report
from eval.report_schema import GameReport
from engine.world import load_canonical_map
from orchestrator.seeder import seed_initial_state
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    FailedCallReplayEntry,
    MeetingReplayEntry,
    read_all_entries,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration_fingerprint(configuration: dict[str, Any], root: Path) -> str:
    """Bind resolved settings, source/templates, and environment without secrets."""
    source = hashlib.sha256()
    for package in (
        "engine",
        "observation",
        "agents",
        "meetings",
        "llm",
        "orchestrator",
        "eval",
        "training",
    ):
        for path in sorted((root / package).rglob("*")):
            suffixes = (
                {".py"}
                if package == "training"
                else {".py", ".j2", ".jinja2", ".json", ".yaml", ".yml"}
            )
            if path.is_file() and path.suffix in suffixes:
                source.update(str(path.relative_to(root)).encode())
                source.update(path.read_bytes())
    for name in (
        "uv.lock",
        "pyproject.toml",
        ".python-version",
        "scripts/run_tournament.py",
        "scripts/_tournament_progress.py",
        "scripts/_report_output.py",
    ):
        path = root / name
        if path.is_file():
            source.update(name.encode())
            source.update(path.read_bytes())
    # Adapters also inherit SDK routing/credentials and HTTPX proxy/TLS settings.
    # Hash values into the fingerprint; never persist credentials in the sidecar.
    provider_keys = {
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_CUSTOM_HEADERS",
        "FEATHERLESS_API_KEY",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
    }
    payload = {
        "configuration": configuration,
        "source": source.hexdigest(),
        "environment": {
            key: hashlib.sha256(value.encode()).hexdigest()
            for key, value in os.environ.items()
            if key.startswith("AILIBI_") or key in provider_keys
        },
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def artifact_fingerprint(directory: Path | None) -> dict[str, str] | None:
    """Bind external policy artifacts in addition to their advertised weight stamp."""
    if directory is None:
        return None
    return {
        name: digest(path)
        for name in ("weights.json", "weights.json.sha256", "stamp.json", "config.json")
        if (path := directory / name).is_file()
    }


class Attempt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: int
    number: int = Field(ge=1)
    status: Literal["running", "finished", "interrupted"]
    replay: str
    audit: str
    hashes: dict[str, str] = Field(default_factory=dict)
    game: GameReport | None = None
    cost_usd: float = Field(default=0.0, ge=0, allow_inf_nan=False)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    accounting_complete: bool = False
    error: str | None = None


class ProgressRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_version: Literal[1] = 1
    run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    fingerprint: str
    configuration: dict[str, Any]
    seeds: list[int]
    attempts: list[Attempt] = Field(default_factory=list)
    status: Literal["running", "finished", "interrupted"] = "interrupted"
    elapsed_seconds: float = Field(default=0.0, ge=0, allow_inf_nan=False)
    updated_at: float = 0.0
    report_sha256: str | None = None
    previous_report_sha256: str | None = None
    publication_pending: bool = False


class TournamentProgress:
    """One writer's checkpoint journal; concurrent writers are unsupported.

    A report describes each seed's latest attempt. All attempts, including
    archived retries, contribute to the cumulative usage retained here.
    """

    def __init__(
        self,
        *,
        path: Path,
        report_path: Path,
        output_dir: Path,
        configuration: dict[str, Any],
        fingerprint: str,
        seeds: list[int],
        resume: bool,
        force: bool,
        started: float | None = None,
    ) -> None:
        self.path = path
        self.report_path = report_path
        self.output_dir = output_dir
        self._started = time.monotonic() if started is None else started
        self._elapsed_before = 0.0
        if resume:
            self.record = ProgressRecord.model_validate_json(path.read_text())
            if self.record.fingerprint != fingerprint or self.record.seeds != seeds:
                raise ValueError(
                    "Continuation configuration differs from saved tournament"
                )
            if self.record.configuration != configuration:
                raise ValueError(
                    "Continuation paths or settings differ from saved tournament"
                )
            self._validate_inputs()
            for seed in seeds:
                if self.latest(seed) is None:
                    for suffix in ("", ".audit"):
                        pending = output_dir / f"replay-seed-{seed}{suffix}.jsonl"
                        if pending.exists():
                            raise ValueError(
                                f"Untracked recording exists for pending seed {seed}: {pending}"
                            )
            self._elapsed_before = self.record.elapsed_seconds
            if self.record.status == "running":
                # A killed process cannot checkpoint its final monotonic time.
                # Count the unobserved interval conservatively, including downtime.
                self._elapsed_before += max(0.0, time.time() - self.record.updated_at)
            for attempt in self.record.attempts:
                if attempt.status == "running":
                    self.capture(
                        attempt, error="Previous process stopped before checkpoint"
                    )
                    if attempt.game is not None and attempt.game.completion_status in {
                        "completed",
                        "tick_limited",
                    }:
                        attempt.status = "finished"
                        attempt.error = None
        else:
            if path.exists() and not force:
                raise FileExistsError(
                    f"Tournament progress exists: {path}; use --resume or --force"
                )
            self.record = ProgressRecord(
                run_id=uuid.uuid4().hex,
                fingerprint=fingerprint,
                configuration=configuration,
                seeds=seeds,
            )

    @property
    def elapsed_seconds(self) -> float:
        return self._elapsed_before + time.monotonic() - self._started

    def paths(self, attempt: Attempt) -> tuple[Path, Path]:
        paths = (
            self.output_dir / attempt.replay,
            self.output_dir / attempt.audit,
        )
        for path, suffix in zip(paths, ("", ".audit"), strict=True):
            if not path.resolve().is_relative_to(self.output_dir.resolve()):
                raise ValueError(f"Attempt recording escapes output directory: {path}")
            if path.name != f"replay-seed-{attempt.seed}{suffix}.jsonl":
                raise ValueError(f"Unexpected attempt recording filename: {path}")
        return paths

    def _hashes(self, attempt: Attempt) -> dict[str, str]:
        return {
            str(path.relative_to(self.output_dir)): digest(path)
            for path in self.paths(attempt)
            if path.exists()
        }

    def _load_game(self, attempt: Attempt) -> GameReport | None:
        replay, _ = self.paths(attempt)
        if not replay.exists() or not replay.stat().st_size:
            return None
        config = self.record.configuration
        state = seed_initial_state(
            seed=attempt.seed,
            game_map=load_canonical_map(),
            num_players=config["num_players"],
            num_impostors=config["num_impostors"],
            tasks_per_crewmate=config["tasks_per_crewmate"],
        )
        report = load_tournament_report(
            replay.parent,
            roles_by_seed={
                attempt.seed: {
                    pid: player.role for pid, player in state.players.items()
                }
            },
            tasks_per_crewmate=config["tasks_per_crewmate"],
        )
        return report.games[0]

    def _validate_inputs(self) -> None:
        allowed_reports = {self.record.report_sha256}
        if self.record.publication_pending:
            allowed_reports.add(self.record.previous_report_sha256)
        actual = digest(self.report_path) if self.report_path.exists() else None
        if actual not in allowed_reports:
            raise ValueError("Saved report bytes changed; continuation refused")
        identities: set[tuple[int, int]] = set()
        for attempt in self.record.attempts:
            if (
                attempt.seed not in self.record.seeds
                or (attempt.seed, attempt.number) in identities
            ):
                raise ValueError("Invalid or duplicate attempt identity")
            identities.add((attempt.seed, attempt.number))
            paths = self.paths(attempt)
            preflight_report_output(paths[0], (paths[1], self.path, self.report_path))
            preflight_report_output(paths[1], (paths[0], self.path, self.report_path))
            preflight_report_output(self.path, (*paths, self.report_path))
            preflight_report_output(self.report_path, (*paths, self.path))
            if attempt.status != "running":
                if self._hashes(attempt) != attempt.hashes:
                    raise ValueError(f"Recording bytes changed for seed {attempt.seed}")
                game = self._load_game(attempt)
                if game != attempt.game:
                    raise ValueError(
                        f"Saved report does not match recording for seed {attempt.seed}"
                    )
                if game is not None and (
                    not math.isclose(
                        attempt.cost_usd, game.cost.total_cost_usd, abs_tol=1e-12
                    )
                    or attempt.input_tokens != game.cost.total_input_tokens
                    or attempt.output_tokens != game.cost.total_output_tokens
                ):
                    raise ValueError(
                        f"Saved usage does not match recording for seed {attempt.seed}"
                    )

    def latest(self, seed: int) -> Attempt | None:
        return next((a for a in reversed(self.record.attempts) if a.seed == seed), None)

    def totals(self) -> tuple[float, int, int]:
        return (
            sum(a.cost_usd for a in self.record.attempts),
            sum(a.input_tokens for a in self.record.attempts),
            sum(a.output_tokens for a in self.record.attempts),
        )

    def capture(self, attempt: Attempt, *, error: str | None = None) -> None:
        attempt.hashes = self._hashes(attempt)
        replay, _ = self.paths(attempt)
        attempt.status = "interrupted" if error is not None else "finished"
        attempt.error = error
        if replay.exists() and replay.stat().st_size:
            entries = read_all_entries(replay)
            calls = [
                call
                for entry in entries
                if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry))
                for call in entry.llm_calls
            ]
            failures = [
                entry for entry in entries if isinstance(entry, FailedCallReplayEntry)
            ]
            attempt.cost_usd = sum(c.cost_usd for c in calls) + sum(
                f.cost_usd for f in failures
            )
            attempt.input_tokens = sum(c.input_tokens for c in calls) + sum(
                f.input_tokens for f in failures
            )
            attempt.output_tokens = sum(c.output_tokens for c in calls) + sum(
                f.output_tokens for f in failures
            )
        attempt.accounting_complete = True
        attempt.game = self._load_game(attempt)
        if error is None and (
            attempt.game is None
            or attempt.game.completion_status in {"aborted", "unfinished"}
        ):
            attempt.status = "interrupted"
            attempt.error = (
                "Recording did not finish or reach its configured tick limit"
            )

    def start(self, seed: int, *, retry: bool) -> Attempt:
        previous = self.latest(seed)
        if previous is not None:
            if previous.status == "finished":
                raise ValueError(f"Seed {seed} is already finished")
            if not retry:
                raise ValueError(
                    f"Seed {seed} was interrupted; use --retry-incomplete with --resume"
                )
            archive = (
                self.output_dir
                / ".tournament-attempts"
                / self.record.run_id
                / f"{seed}-{previous.number}"
            )
            destinations = tuple(archive / path.name for path in self.paths(previous))
            protected = (*self.paths(previous), self.path, self.report_path)
            if self.paths(previous) != destinations:
                for destination in destinations:
                    preflight_report_output(
                        destination,
                        (*protected, *(p for p in destinations if p != destination)),
                    )
                for source, destination in zip(
                    self.paths(previous), destinations, strict=True
                ):
                    if source.exists():
                        if destination.exists() and digest(source) != digest(
                            destination
                        ):
                            raise ValueError(
                                f"Archived attempt already has different bytes: {destination}"
                            )
                        atomic_write_bytes(destination, source.read_bytes())
                previous.replay, previous.audit = (
                    str(p.relative_to(self.output_dir)) for p in destinations
                )
                previous.hashes = self._hashes(previous)
                self.save()
            # Archive ownership is durable before canonical names are cleared.
            # Identical new generations still represent distinct paid attempts.
            for archived in destinations:
                canonical = self.output_dir / archived.name
                if canonical.exists():
                    if not archived.exists() or digest(canonical) != digest(archived):
                        raise ValueError(
                            f"Unexpected recording appeared before retry: {canonical}"
                        )
                    canonical.unlink()
        attempt = Attempt(
            seed=seed,
            number=1 if previous is None else previous.number + 1,
            status="running",
            replay=f"replay-seed-{seed}.jsonl",
            audit=f"replay-seed-{seed}.audit.jsonl",
        )
        self.record.attempts.append(attempt)
        self.record.status = "running"
        self.save()
        return attempt

    def save(self) -> None:
        self.record.elapsed_seconds = self.elapsed_seconds
        self.record.updated_at = time.time()
        atomic_write_report(self.path, self.record.model_dump_json(indent=2) + "\n")

    def publish(self, *, finished: bool = False) -> None:
        games = [
            a.game
            for seed in self.record.seeds
            if (a := self.latest(seed)) is not None and a.game is not None
        ]
        report = build_tournament_eval_report(
            build_tournament_report(
                games=games,
                seeds=list(dict.fromkeys(a.seed for a in self.record.attempts)),
            )
        )
        text = report.model_dump_json(indent=2) + "\n"
        TournamentEvalReport.model_validate_json(text)
        self.record.previous_report_sha256 = (
            digest(self.report_path) if self.report_path.exists() else None
        )
        self.record.report_sha256 = hashlib.sha256(text.encode()).hexdigest()
        self.record.publication_pending = True
        self.record.status = (
            "finished"
            if finished
            and all(
                (a := self.latest(seed)) is not None and a.status == "finished"
                for seed in self.record.seeds
            )
            else "interrupted"
        )
        self.save()
        atomic_write_report(self.report_path, text)
        self.record.previous_report_sha256 = None
        self.record.publication_pending = False
        self.save()
