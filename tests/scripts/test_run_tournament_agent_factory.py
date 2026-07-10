"""Unit tests for scripts/run_tournament.py ``--agent-factory`` wiring (Task 15.21).

Drives ``main()`` (bare-module import via ``tests/scripts/conftest.py``) on a tiny
seed range and a low tick budget so the fake-provider run is fast, and pins the
three DoD axes of the opt-in learned factory: (1) the flag defaults to
``fsm-default`` and that default path stays byte-identical to the pre-15.21 CLI
(NO ``agent_factory`` kwarg threaded through the harness seam); (2) a
``learned-champion`` run auto-stamps every recording with the champion's real
:class:`~orchestrator.replay.TacticalPolicyStamp`, asserted off the RECORDED BYTES
so the digest is the artifact actually loaded; (3) an explicit
``--tactical-policy-stamp`` that contradicts the champion is rejected loudly while
a field-for-field restatement is accepted. The fake LLM provider comes from the
root ``tests/conftest.py`` autouse fixture — no per-test provider setup.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

import run_tournament as rt
from agents.tactical.learned.factory import LearnedAgentFactory
from agents.tactical.learned.weights import committed_weights_sha256
from eval.balance_eval import run_tournament_eval as _real_run_tournament_eval
from eval.report_schema import TournamentReport
from orchestrator.game import AgentFactory
from orchestrator.replay import (
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
    read_tactical_policy_stamp,
)


def _expected_champion_stamp() -> TacticalPolicyStamp:
    """The champion stamp built from the learned factory's plain-string fields.

    Constructed the exact way ``_resolve_agent_factory`` builds the auto-stamp —
    field-by-field from ``_build_learned_champion_factory().stamp``'s five plain
    strings (the factory itself stays engine-free per Task 15.20) — so the tests
    never hard-code the champion's digest and follow the loaded artifact.
    """

    fields = rt._build_learned_champion_factory().stamp
    return TacticalPolicyStamp(
        policy_id=fields.policy_id,
        method=fields.method,
        encoder_version=fields.encoder_version,
        weights_sha256=fields.weights_sha256,
        anchor_policy=fields.anchor_policy,
    )


def _install_default_path_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, object]
) -> None:
    """Patch ``run_tournament.run_tournament_eval`` with the 15.9-era seam shape.

    The spy's signature has NO ``agent_factory`` parameter — the exact keyword-only
    shape the pre-15.21 harness (and tests/scripts/test_run_tournament.py) pins. If
    ``main`` ever passed ``agent_factory`` on the default path this call would raise
    TypeError, so this spy IS the byte-identity pin. It records the threaded stamp
    and delegates to the real harness (the same function object ``main`` calls) so
    ``main`` still produces a valid report end-to-end.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["tactical_policy_stamp"] = tactical_policy_stamp
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=max_ticks,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
        )

    monkeypatch.setattr(rt, "run_tournament_eval", spy)


def _install_factory_capturing_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, object]
) -> None:
    """Patch ``run_tournament.run_tournament_eval`` to capture the learned seam.

    The spy's signature carries a keyword-only ``agent_factory: AgentFactory`` with
    NO default, so ``main`` failing to thread the factory on the learned path also
    fails loud (TypeError). It records both the factory and the auto-stamp ``main``
    passes through, then delegates to the real harness (forwarding the factory) so
    ``main`` still produces a valid report end-to-end.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        agent_factory: AgentFactory,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["agent_factory"] = agent_factory
        captured["tactical_policy_stamp"] = tactical_policy_stamp
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            agent_factory=agent_factory,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=max_ticks,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
        )

    monkeypatch.setattr(rt, "run_tournament_eval", spy)


# -- parse layer --------------------------------------------------------------


def test_parse_defaults_to_fsm_default(tmp_path: Path) -> None:
    """The flag omitted parses to ``fsm-default`` (the scripted-FSM default)."""

    args = rt._parse_args(["--output-dir", str(tmp_path)])
    assert args.agent_factory == "fsm-default"


def test_parse_rejects_unknown_factory(tmp_path: Path) -> None:
    """An unknown ``--agent-factory`` choice is an argparse error (fail loud)."""

    with pytest.raises(SystemExit):
        rt._parse_args(["--output-dir", str(tmp_path), "--agent-factory", "bogus"])


# -- resolve layer ------------------------------------------------------------


def test_resolve_fsm_default_is_no_factory_no_auto_stamp() -> None:
    """``fsm-default`` resolves to ``(None, None)`` — no factory, no auto-stamp."""

    assert rt._resolve_agent_factory("fsm-default") == (None, None)


def test_resolve_learned_champion_builds_factory_and_stamp() -> None:
    """``learned-champion`` builds the 15.20 factory + the committed champion stamp."""

    factory, stamp = rt._resolve_agent_factory("learned-champion")
    assert isinstance(factory, LearnedAgentFactory)
    assert stamp == _expected_champion_stamp()
    # The auto-stamp carries the digest of the artifact actually loaded, never a
    # hard-coded sha (the committed sidecar the factory sha-verified on load).
    assert stamp is not None and stamp.weights_sha256 == committed_weights_sha256()


# -- main() default path (byte-identity) --------------------------------------


def test_main_default_path_omits_agent_factory_kwarg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The default factory path passes NO ``agent_factory`` kwarg (DoD byte-identity).

    The default-path spy has no ``agent_factory`` parameter, so if ``main`` threaded
    one this run would raise TypeError. Reaching rc == 0 with a ``None`` stamp is the
    pin that the pre-15.21 harness seam is untouched.
    """

    captured: dict[str, object] = {}
    _install_default_path_spy(monkeypatch, captured)

    rc = rt.main(
        ["--num-games", "1", "--output-dir", str(tmp_path), "--max-ticks", "2"]
    )

    assert rc == 0
    assert captured["tactical_policy_stamp"] is None


def test_main_explicit_fsm_default_flag_still_omits_agent_factory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Passing ``--agent-factory fsm-default`` explicitly is the omitted-flag path.

    The argparse default makes the explicit and omitted forms indistinguishable, so
    the same no-``agent_factory``-kwarg spy still holds.
    """

    captured: dict[str, object] = {}
    _install_default_path_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "2",
            "--agent-factory",
            "fsm-default",
        ]
    )

    assert rc == 0
    assert captured["tactical_policy_stamp"] is None


def test_main_fsm_default_with_explicit_fsm_stamp_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``fsm-default`` + explicit ``--tactical-policy-stamp fsm-default`` is back-compat.

    Without the learned factory the explicit stamp passes through unchanged — the
    Task-15.9 surface, still threaded on the default (no-``agent_factory``-kwarg) path.
    """

    captured: dict[str, object] = {}
    _install_default_path_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "2",
            "--agent-factory",
            "fsm-default",
            "--tactical-policy-stamp",
            "fsm-default",
        ]
    )

    assert rc == 0
    assert captured["tactical_policy_stamp"] == fsm_default_tactical_policy_stamp()


# -- main() learned path (opt-in factory + auto-stamp) ------------------------


def test_main_learned_champion_threads_factory_and_auto_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``learned-champion`` threads the 15.20 factory and the champion auto-stamp."""

    captured: dict[str, object] = {}
    _install_factory_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "2",
            "--agent-factory",
            "learned-champion",
        ]
    )

    assert rc == 0
    assert isinstance(captured["agent_factory"], LearnedAgentFactory)
    assert captured["tactical_policy_stamp"] == _expected_champion_stamp()


def test_main_learned_champion_auto_stamps_replay_on_disk(tmp_path: Path) -> None:
    """The DoD e2e: a real ``learned-champion`` run auto-stamps the replay on disk.

    No spy — the production seam runs end-to-end at ``--max-ticks 200`` on the 4p/1i
    seed 0 roster, which lands a ``game_over`` record. The stamp is asserted from the
    RECORDED BYTES via ``read_tactical_policy_stamp``, never from the launch config,
    and ``weights_sha256`` is the committed sidecar the factory loaded — so the
    Task-15.18 finalist-eval proof cannot be forgotten. The fake provider comes from
    the root conftest autouse fixture.
    """

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
            "--agent-factory",
            "learned-champion",
        ]
    )

    assert rc == 0
    stamp = read_tactical_policy_stamp(tmp_path / "replay-seed-0.jsonl")
    assert stamp == _expected_champion_stamp()
    assert stamp is not None
    assert stamp.weights_sha256 == committed_weights_sha256()


# -- main() learned path mis-stamp guard --------------------------------------


def test_main_learned_champion_rejects_fsm_default_stamp(tmp_path: Path) -> None:
    """A learned recording can never carry the FSM label — reject it, name the field.

    The guard fires in ``main`` before any game runs; the champion and FSM stamps
    first differ on ``policy_id``, so that field is named in the error.
    """

    with pytest.raises(SystemExit, match="policy_id"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--max-ticks",
                "2",
                "--agent-factory",
                "learned-champion",
                "--tactical-policy-stamp",
                "fsm-default",
            ]
        )


def test_main_learned_champion_rejects_contradicting_sha_stamp_file(
    tmp_path: Path,
) -> None:
    """An explicit stamp matching the champion but for a wrong sha is rejected.

    The contradiction is on ``weights_sha256`` only (every other field matches), so
    that field is the one the fail-loud error names.
    """

    fields = _expected_champion_stamp().model_dump()
    fields["weights_sha256"] = "0" * 64
    path = tmp_path / "contradicting.json"
    path.write_text(TacticalPolicyStamp(**fields).model_dump_json(), encoding="utf-8")

    with pytest.raises(SystemExit, match="weights_sha256"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--max-ticks",
                "2",
                "--agent-factory",
                "learned-champion",
                "--tactical-policy-stamp",
                str(path),
            ]
        )


def test_main_learned_champion_accepts_matching_explicit_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A field-for-field restatement of the champion stamp is accepted (not a clash).

    Contradiction is rejected; an idempotent restatement threads through as the
    champion auto-stamp.
    """

    path = tmp_path / "champion.json"
    path.write_text(_expected_champion_stamp().model_dump_json(), encoding="utf-8")

    captured: dict[str, object] = {}
    _install_factory_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "2",
            "--agent-factory",
            "learned-champion",
            "--tactical-policy-stamp",
            str(path),
        ]
    )

    assert rc == 0
    assert captured["tactical_policy_stamp"] == _expected_champion_stamp()
