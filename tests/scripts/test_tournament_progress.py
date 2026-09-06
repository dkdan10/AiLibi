"""Continuation verifies recorded inputs and never silently replays finished seeds."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

import run_tournament as rt
from _tournament_progress import Attempt, ProgressRecord, TournamentProgress
from _report_output import atomic_write_bytes, atomic_write_report
from _tournament_progress import artifact_fingerprint, configuration_fingerprint, digest
from agents.tactical.crewmate_policy import CrewmatePolicy
from llm.budget import BudgetExceededError
from llm.client import LLMResponse
from llm.fake_provider import FakeProvider
from eval.report_schema import GameReport
from observation.action_intent import ActionIntent, EmergencyMeetingIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import HeadlessGame, TacticalAgent
from orchestrator.replay import ReplayLog, compute_cost_usd
from orchestrator.run_limits import RunDeadlineExceeded


def arguments(directory: Path, *, ticks: int = 2, games: int = 2) -> list[str]:
    return [
        "--output-dir",
        str(directory),
        "--num-games",
        str(games),
        "--max-ticks",
        str(ticks),
    ]


def progress(directory: Path) -> ProgressRecord:
    return ProgressRecord.model_validate_json(
        (directory / "tournament-progress.json").read_text()
    )


@pytest.mark.parametrize("existing_report", [False, True])
def test_first_seed_failure_does_not_publish_an_empty_report(
    tmp_path: Path, existing_report: bool
) -> None:
    report = tmp_path / "tournament-eval-report.json"
    before = b"previous published report\n"
    if existing_report:
        report.write_bytes(before)
    with pytest.raises(ValueError):
        rt.main([*arguments(tmp_path, games=1), "--num-players", "1"])
    if existing_report:
        assert report.read_bytes() == before
        assert progress(tmp_path).report_sha256 == digest(report)
    else:
        assert not report.exists()
        assert progress(tmp_path).report_sha256 is None
    assert not progress(tmp_path).attempts[0].accounting_complete


def test_failed_forced_run_does_not_attribute_preserved_old_recordings_to_new_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args = arguments(tmp_path, games=1)
    assert rt.main(args) == 0
    paths = [
        tmp_path / "replay-seed-0.jsonl",
        tmp_path / "replay-seed-0.audit.jsonl",
        tmp_path / "tournament-eval-report.json",
    ]
    before = {path: path.read_bytes() for path in paths}

    def fail_before_game(**kwargs: Any) -> Any:
        raise RuntimeError("first seed failed before recording")

    monkeypatch.setattr(rt, "run_tournament_eval", fail_before_game)
    with pytest.raises(RuntimeError, match="before recording"):
        rt.main([*args, "--force"])
    assert {path: path.read_bytes() for path in paths} == before
    attempt = progress(tmp_path).attempts[0]
    assert attempt.game is None
    assert not attempt.accounting_complete
    assert "no new attempt evidence" in (attempt.error or "")


@pytest.mark.parametrize("damage", ["missing", "empty", "lower_usage"])
def test_unresolved_capture_preserves_known_usage_and_blocks_all_allowance_consumers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = arguments(tmp_path, games=1)
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    saved = progress(tmp_path)
    ledger = TournamentProgress(
        path=tmp_path / "tournament-progress.json",
        report_path=tmp_path / "tournament-eval-report.json",
        output_dir=tmp_path,
        configuration=saved.configuration,
        fingerprint=saved.fingerprint,
        seeds=saved.seeds,
        resume=True,
        force=False,
    )
    attempt = ledger.record.attempts[0]
    known = (attempt.cost_usd, attempt.input_tokens, attempt.output_tokens)
    known_hashes = attempt.hashes.copy()
    assert all(known)
    path = tmp_path / attempt.replay
    original = path.read_bytes()
    if damage == "missing":
        path.unlink()
    elif damage == "empty":
        path.write_bytes(b"")
    else:
        # A valid tick prefix still cannot erase the checkpointed paid call.
        path.write_bytes(original.splitlines(keepends=True)[0])
    with pytest.raises(ValueError, match="[Uu]sage.*unresolved"):
        ledger.capture(attempt, error="interrupted capture")
    assert (attempt.cost_usd, attempt.input_tokens, attempt.output_tokens) == known
    assert attempt.hashes == known_hashes
    assert not attempt.accounting_complete
    assert attempt.status == "interrupted"
    ledger.save()
    with pytest.raises(ValueError, match="[Uu]sage.*unresolved"):
        ledger.totals()
    with pytest.raises(ValueError, match="[Uu]sage.*unresolved"):
        ledger.start(attempt.seed, retry=True)
    assert not (tmp_path / ".tournament-attempts").exists()
    # Restoring the actual evidence resolves accounting without inventing usage.
    path.write_bytes(original)
    restored = TournamentProgress(
        path=ledger.path,
        report_path=ledger.report_path,
        output_dir=tmp_path,
        configuration=saved.configuration,
        fingerprint=saved.fingerprint,
        seeds=saved.seeds,
        resume=True,
        force=False,
    )
    assert restored.totals() == known
    assert restored.record.attempts[0].accounting_complete


def test_capture_refuses_recording_changes_during_inspection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert rt.main(arguments(tmp_path, games=1)) == 0
    saved = progress(tmp_path)
    ledger = TournamentProgress(
        path=tmp_path / "tournament-progress.json",
        report_path=tmp_path / "tournament-eval-report.json",
        output_dir=tmp_path,
        configuration=saved.configuration,
        fingerprint=saved.fingerprint,
        seeds=saved.seeds,
        resume=True,
        force=False,
    )
    attempt = ledger.record.attempts[0]
    known_hashes = attempt.hashes.copy()
    original_load = ledger._load_game

    def change_after_load(candidate: Attempt) -> GameReport | None:
        game = original_load(candidate)
        path = tmp_path / candidate.replay
        path.write_bytes(path.read_bytes() + b"\n")
        return game

    monkeypatch.setattr(ledger, "_load_game", change_after_load)
    with pytest.raises(ValueError, match="changed during usage inspection"):
        ledger.capture(attempt)
    assert attempt.hashes == known_hashes
    assert not attempt.accounting_complete


@pytest.mark.parametrize("missing", [False, True])
def test_missing_or_empty_crashed_attempt_refuses_continuation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing: bool
) -> None:
    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = arguments(tmp_path, games=1)
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    saved = progress(tmp_path)
    attempt = saved.attempts[0]
    assert attempt.input_tokens > 0
    # Reproduce a killed process before its checkpoint, followed by deletion
    # or truncation of its only usage evidence. No trustworthy zero is possible.
    attempt.status = "running"
    attempt.hashes = {}
    attempt.game = None
    attempt.accounting_complete = False
    attempt.cost_usd = 0.0
    attempt.input_tokens = 0
    attempt.output_tokens = 0
    replay = tmp_path / attempt.replay
    if missing:
        replay.unlink()
    else:
        replay.write_bytes(b"")
    (tmp_path / "tournament-progress.json").write_text(saved.model_dump_json())
    prior_calls = provider.calls
    provider.abort_at = None
    with pytest.raises(ValueError, match="[Uu]sage.*unresolved"):
        rt.main([*args, "--resume", "--retry-incomplete"])
    assert provider.calls == prior_calls
    assert not (tmp_path / ".tournament-attempts").exists()


def test_second_seed_interruption_preserves_report_and_explicit_continuation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = HeadlessGame.run
    calls = 0

    def interrupt_second(game: HeadlessGame) -> Any:
        nonlocal calls
        calls += 1
        if calls == 2:
            append_tick = ReplayLog.record_tick

            def interrupt_tick(log: ReplayLog, *args: Any, **kwargs: Any) -> None:
                append_tick(log, *args, **kwargs)
                raise KeyboardInterrupt("injected interruption")

            with monkeypatch.context() as patch:
                patch.setattr(ReplayLog, "record_tick", interrupt_tick)
                return original(game)
        return original(game)

    monkeypatch.setattr(HeadlessGame, "run", interrupt_second)
    args = arguments(tmp_path)
    with pytest.raises(KeyboardInterrupt):
        rt.main(args)
    first_bytes = (tmp_path / "replay-seed-0.jsonl").read_bytes()
    saved = progress(tmp_path)
    assert [a.status for a in saved.attempts] == ["finished", "interrupted"]
    report = json.loads((tmp_path / "tournament-eval-report.json").read_text())
    assert len(report["report"]["games"]) == 2
    assert report["report"]["games"][0]["completion_status"] == "tick_limited"
    assert report["report"]["games"][1]["completion_status"] == "unfinished"
    with pytest.raises(ValueError, match="retry-incomplete"):
        rt.main([*args, "--resume"])
    assert calls == 2
    assert rt.main([*args, "--resume", "--retry-incomplete"]) == 0
    assert calls == 3
    assert (tmp_path / "replay-seed-0.jsonl").read_bytes() == first_bytes
    assert progress(tmp_path).status == "finished"
    assert rt.main([*args, "--resume"]) == 0
    assert calls == 3


@pytest.mark.parametrize(
    "changed",
    [
        "replay",
        "audit",
        "report",
        "deleted_report",
        "usage",
        "winner",
        "settings",
        "environment",
    ],
)
def test_mismatched_continuation_refuses_before_provider_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    changed: str,
) -> None:
    args = arguments(tmp_path, games=1)
    assert rt.main(args) == 0
    if changed in {"replay", "audit", "report"}:
        name = {
            "replay": "replay-seed-0.jsonl",
            "audit": "replay-seed-0.audit.jsonl",
            "report": "tournament-eval-report.json",
        }[changed]
        path = tmp_path / name
        path.write_bytes(path.read_bytes() + b"\n")
    elif changed == "deleted_report":
        (tmp_path / "tournament-eval-report.json").unlink()
    elif changed in {"usage", "winner"}:
        path = tmp_path / "tournament-progress.json"
        raw = json.loads(path.read_text())
        if changed == "usage":
            raw["attempts"][0]["input_tokens"] += 1
        else:
            raw["attempts"][0]["game"]["reason"] = "forged outcome explanation"
        path.write_text(json.dumps(raw))
    elif changed == "settings":
        args = arguments(tmp_path, ticks=3, games=1)
    else:
        monkeypatch.setenv("AILIBI_PROMPT_SET", "changed-family")

    def forbidden(**kwargs: Any) -> Any:
        raise AssertionError("Blocked continuation invoked evaluator")

    monkeypatch.setattr(rt, "run_tournament_eval", forbidden)
    with pytest.raises(ValueError, match="changed|differ|does not match"):
        rt.main([*args, "--resume"])


@pytest.mark.parametrize(
    "destination",
    [
        "replay-seed-0.jsonl",
        "replay-seed-0.audit.jsonl",
        "tournament-eval-report.json",
        ".tournament-attempts/progress.json",
    ],
)
def test_progress_aliases_are_rejected_before_work(
    tmp_path: Path, destination: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(**kwargs: Any) -> Any:
        raise AssertionError("Alias invoked evaluator")

    monkeypatch.setattr(rt, "run_tournament_eval", forbidden)
    with pytest.raises(ValueError, match="overlaps"):
        rt.main(
            [*arguments(tmp_path), "--progress-output", str(tmp_path / destination)]
        )


class EmergencyAgent(TacticalAgent):
    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        super().decide(packet, public_map)
        if self.agent_id == "p-1" and packet.tick == 0:
            return EmergencyMeetingIntent(type="emergency", actor=self.agent_id)
        return WaitIntent(type="wait", actor=self.agent_id)


class PaidProvider(FakeProvider):
    def __init__(self, *, cost: float = 0.01, abort_at: int | None = 2) -> None:
        super().__init__()
        self.calls = 0
        self.cost = cost
        self.abort_at = abort_at

    async def complete(self, **kwargs: Any) -> LLMResponse:
        self.calls += 1
        if self.calls == self.abort_at:
            raise RuntimeError("injected provider interruption")
        response = await super().complete(**kwargs)
        return response.model_copy(update={"cost_usd": self.cost})


def install_paid_run(monkeypatch: pytest.MonkeyPatch, provider: PaidProvider) -> None:
    def build_paid_client(*, env: Mapping[str, str] | None = None) -> PaidProvider:
        assert env is not None, "provider construction must receive the frozen settings"
        return provider

    monkeypatch.setattr("orchestrator.game.build_default_client", build_paid_client)
    monkeypatch.setattr(
        rt,
        "_resolve_agent_factory",
        lambda *args, **kwargs: (
            lambda agent_id, role: EmergencyAgent(
                agent_id=agent_id, role=role, policy=CrewmatePolicy(agent_id=agent_id)
            ),
            None,
        ),
    )


def test_retry_archives_pair_and_keeps_prior_spend_in_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = [*arguments(tmp_path, games=1), "--max-total-cost-usd", "0.5"]
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    paths = [tmp_path / f"replay-seed-0{suffix}.jsonl" for suffix in ("", ".audit")]
    original = [path.read_bytes() for path in paths]
    assert progress(tmp_path).attempts[0].cost_usd == 0.01
    provider.abort_at = None
    assert rt.main([*args, "--resume", "--retry-incomplete"]) == 0
    saved = progress(tmp_path)
    assert len(saved.attempts) == 2
    archived = saved.attempts[0]
    assert [
        (tmp_path / name).read_bytes() for name in (archived.replay, archived.audit)
    ] == original
    assert sum(a.cost_usd for a in saved.attempts) == pytest.approx(0.09)
    assert sum(a.cost_usd for a in saved.attempts) == pytest.approx(
        sum(compute_cost_usd(tmp_path / a.replay) for a in saved.attempts)
    )
    assert rt.main([*args, "--resume"]) == 0
    assert provider.calls == 10


def test_returned_overrun_remains_recorded_and_blocks_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = PaidProvider(cost=0.6, abort_at=None)
    install_paid_run(monkeypatch, provider)
    args = [*arguments(tmp_path, games=1), "--max-total-cost-usd", "0.5"]
    with pytest.raises(BudgetExceededError):
        rt.main(args)
    assert progress(tmp_path).attempts[0].cost_usd == 0.6
    assert provider.calls == 1
    with pytest.raises(BudgetExceededError):
        rt.main([*args, "--resume", "--retry-incomplete"])
    assert provider.calls == 1


def test_shared_cap_does_not_reset_between_seeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = PaidProvider(abort_at=None)
    install_paid_run(monkeypatch, provider)
    with pytest.raises(BudgetExceededError):
        rt.main([*arguments(tmp_path), "--max-total-cost-usd", "0.15"])
    saved = progress(tmp_path)
    assert saved.attempts[0].status == "finished"
    assert saved.attempts[1].status == "interrupted"
    assert 8 < provider.calls < 16
    assert sum(a.cost_usd for a in saved.attempts) == pytest.approx(
        provider.calls * 0.01
    )


@pytest.mark.parametrize(
    "flag",
    ["--max-total-cost-usd", "--max-total-input-tokens", "--max-total-output-tokens"],
)
def test_zero_cap_stops_before_any_provider_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag: str
) -> None:
    provider = PaidProvider(abort_at=None)
    install_paid_run(monkeypatch, provider)
    with pytest.raises(BudgetExceededError):
        rt.main([*arguments(tmp_path, games=1), flag, "0"])
    assert provider.calls == 0
    assert progress(tmp_path).attempts[0].cost_usd == 0


def test_zero_wall_limit_stops_before_seed_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(**kwargs: Any) -> Any:
        raise AssertionError("Expired wall deadline invoked evaluator")

    monkeypatch.setattr(rt, "run_tournament_eval", forbidden)
    with pytest.raises(RunDeadlineExceeded):
        rt.main([*arguments(tmp_path), "--max-wall-seconds", "0"])
    assert progress(tmp_path).attempts == []


def test_killed_after_recorded_stop_does_not_replay_finished_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args = arguments(tmp_path, games=1)
    assert rt.main(args) == 0
    path = tmp_path / "tournament-progress.json"
    raw = json.loads(path.read_text())
    raw["status"] = raw["attempts"][0]["status"] = "running"
    raw["attempts"][0]["hashes"] = {}
    raw["attempts"][0]["game"] = None
    path.write_text(json.dumps(raw))

    def forbidden(**kwargs: Any) -> Any:
        raise AssertionError("A verified finished recording was replayed")

    monkeypatch.setattr(rt, "run_tournament_eval", forbidden)
    assert rt.main([*args, "--resume"]) == 0
    assert progress(tmp_path).attempts[0].status == "finished"


def test_identical_paid_retry_is_another_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = [*arguments(tmp_path, games=1), "--max-total-cost-usd", "0.5"]
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    original = (tmp_path / "replay-seed-0.jsonl").read_bytes()
    provider.calls = 0
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main([*args, "--resume", "--retry-incomplete"])
    assert (tmp_path / "replay-seed-0.jsonl").read_bytes() == original
    saved = progress(tmp_path)
    assert [attempt.cost_usd for attempt in saved.attempts] == [0.01, 0.01]
    assert [attempt.number for attempt in saved.attempts] == [1, 2]


def test_publication_interruption_keeps_recoverable_input_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import _tournament_progress as checkpoint

    original = atomic_write_report
    report = tmp_path / "tournament-eval-report.json"

    def fail_report(path: Path, text: str) -> None:
        if path == report:
            raise OSError("injected report publication failure")
        original(path, text)

    monkeypatch.setattr(checkpoint, "atomic_write_report", fail_report)
    args = arguments(tmp_path, games=1)
    with pytest.raises(OSError, match="publication failure"):
        rt.main(args)
    assert progress(tmp_path).publication_pending
    assert not report.exists()
    monkeypatch.setattr(checkpoint, "atomic_write_report", original)
    assert rt.main([*args, "--resume"]) == 0
    assert not progress(tmp_path).publication_pending


def test_archive_copy_failure_retains_original_pair_and_can_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import _tournament_progress as checkpoint

    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = arguments(tmp_path, games=1)
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    paths = [tmp_path / f"replay-seed-0{suffix}.jsonl" for suffix in ("", ".audit")]
    original_bytes = [path.read_bytes() for path in paths]
    original = atomic_write_bytes

    def fail_audit(path: Path, text: bytes) -> None:
        if ".tournament-attempts" in path.parts and ".audit" in path.name:
            raise OSError("injected archive publication failure")
        original(path, text)

    monkeypatch.setattr(checkpoint, "atomic_write_bytes", fail_audit)
    provider.abort_at = None
    with pytest.raises(OSError, match="archive publication failure"):
        rt.main([*args, "--resume", "--retry-incomplete"])
    assert [path.read_bytes() for path in paths] == original_bytes
    assert provider.calls == 2
    monkeypatch.setattr(checkpoint, "atomic_write_bytes", original)
    assert rt.main([*args, "--resume", "--retry-incomplete"]) == 0


def test_archive_checkpoint_precedes_removal_and_recovers_mid_pair_clear(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = arguments(tmp_path, games=1)
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    original = Path.unlink
    audit = tmp_path / "replay-seed-0.audit.jsonl"

    def fail_unlink(path: Path, *args: Any, **kwargs: Any) -> None:
        if path == audit:
            raise OSError("injected interruption clearing old audit")
        original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_unlink)
    with pytest.raises(OSError, match="clearing old audit"):
        rt.main([*args, "--resume", "--retry-incomplete"])
    saved = progress(tmp_path)
    assert ".tournament-attempts" in saved.attempts[0].replay
    assert (tmp_path / saved.attempts[0].replay).exists()
    assert (tmp_path / saved.attempts[0].audit).exists()
    assert provider.calls == 2
    monkeypatch.setattr(Path, "unlink", original)
    provider.abort_at = None
    assert rt.main([*args, "--resume", "--retry-incomplete"]) == 0


def test_checkpoint_failure_does_not_hide_original_interruption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import _tournament_progress as checkpoint

    original = checkpoint.TournamentProgress.save
    interruption = KeyboardInterrupt("original interruption")

    def fail_game(**kwargs: Any) -> Any:
        raise interruption

    def fail_checkpoint(ledger: checkpoint.TournamentProgress) -> None:
        if (
            ledger.record.attempts
            and ledger.record.attempts[-1].status == "interrupted"
        ):
            raise OSError("checkpoint disk failure")
        original(ledger)

    monkeypatch.setattr(rt, "run_tournament_eval", fail_game)
    monkeypatch.setattr(checkpoint.TournamentProgress, "save", fail_checkpoint)
    with pytest.raises(KeyboardInterrupt) as excinfo:
        rt.main(arguments(tmp_path, games=1))
    assert excinfo.value is interruption
    assert any("checkpoint disk failure" in note for note in interruption.__notes__)
    assert progress(tmp_path).attempts[0].status == "running"


@pytest.mark.parametrize(
    "relative",
    [
        "engine/maps/canonical_1.yaml",
        "engine/maps/alternative.yml",
        "uv.lock",
        "pyproject.toml",
        "scripts/run_tournament.py",
        "training/coevo/factory.py",
    ],
)
def test_fingerprint_binds_map_locks_and_factory_source(
    tmp_path: Path, relative: str
) -> None:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("original input")
    before = configuration_fingerprint({}, tmp_path)
    path.write_text("changed input")
    assert configuration_fingerprint({}, tmp_path) != before


@pytest.mark.parametrize(
    "name", ["ANTHROPIC_BASE_URL", "HTTPS_PROXY", "FEATHERLESS_API_KEY"]
)
def test_fingerprint_binds_sdk_provider_inputs_without_recording_secrets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    monkeypatch.setenv(name, "first-provider-setting")
    before = configuration_fingerprint({}, tmp_path)
    monkeypatch.setenv(name, "second-secret-setting")
    after = configuration_fingerprint({}, tmp_path)
    assert before != after
    assert "secret" not in after


def test_external_artifact_configuration_is_bound_beside_weight_stamp(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "external-policy"
    artifact.mkdir()
    config = artifact / "config.json"
    config.write_text('{"hidden": 16}')
    (artifact / "stamp.json").write_text('{"weights_sha256": "unchanged"}')
    before = configuration_fingerprint(
        {"artifact": artifact_fingerprint(artifact)}, tmp_path
    )
    config.write_text('{"hidden": 32}')
    assert (
        configuration_fingerprint(
            {"artifact": artifact_fingerprint(artifact)}, tmp_path
        )
        != before
    )


def test_retry_preserves_valid_crlf_recording_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = PaidProvider()
    install_paid_run(monkeypatch, provider)
    args = arguments(tmp_path, games=1)
    with pytest.raises(RuntimeError, match="provider interruption"):
        rt.main(args)
    # Plant a valid checkpoint containing Windows-style JSONL bytes. The
    # semantic report is identical; only the recording's exact line endings differ.
    saved = progress(tmp_path)
    for name in (saved.attempts[0].replay, saved.attempts[0].audit):
        path = tmp_path / name
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        saved.attempts[0].hashes[name] = digest(path)
    (tmp_path / "tournament-progress.json").write_text(saved.model_dump_json())
    originals = [
        (tmp_path / name).read_bytes()
        for name in (saved.attempts[0].replay, saved.attempts[0].audit)
    ]
    provider.abort_at = None
    assert rt.main([*args, "--resume", "--retry-incomplete"]) == 0
    archived = progress(tmp_path).attempts[0]
    assert [
        (tmp_path / name).read_bytes() for name in (archived.replay, archived.audit)
    ] == originals


def test_resume_cannot_overwrite_untracked_pending_recordings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = HeadlessGame.run
    calls = 0

    def stop_first(game: HeadlessGame) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise KeyboardInterrupt("before first recording")
        return original(game)

    monkeypatch.setattr(HeadlessGame, "run", stop_first)
    args = arguments(tmp_path)
    with pytest.raises(KeyboardInterrupt):
        rt.main(args)
    foreign = tmp_path / "replay-seed-1.jsonl"
    foreign.write_bytes(b"independent recording")
    with pytest.raises(ValueError, match="Untracked recording"):
        rt.main([*args, "--resume", "--retry-incomplete"])
    assert calls == 1
    assert foreign.read_bytes() == b"independent recording"
